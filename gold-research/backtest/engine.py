#!/usr/bin/env python3
"""Backtest engine for GOLD_PLAYBOOK v1.0 ("Holy Grail" intraday adaptation) on XAUUSD M1 data.

Implements exactly the frozen rules in ../GOLD_PLAYBOOK_v1.md. Signals use closed M15 bars;
fills are simulated on M1 bars that occur strictly AFTER the signal bar closed.
Prices in the data are BID. Ask = bid + spread (constant, from the cost model).

Usage:
  python3 engine.py --variant V0_base            # one variant
  python3 engine.py --all                        # every pre-registered variant
Outputs (in ../results/<variant>/): trades.csv, skips.csv, config.json
"""
import argparse, json, pathlib, datetime as dt
import numpy as np, pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "xauusd_m1_utc.parquet"
RESULTS = HERE.parent / "results"

BASE_CONFIG = dict(
    version="v1.0",
    adx_len=14, ema_len=20, atr_len=14,
    adx_threshold=30.0, adx_rising_lookback=10, adx_cancel_below=25.0,
    entry_offset=0.10, stop_buffer_min=0.30, stop_buffer_atr=0.10,
    deep_break_atr=0.5, target_lookback=20, min_rr=1.0,
    rearm=True, expiry_bars=4,
    signal_start="07:00", signal_end="15:45", pending_cutoff="16:00", time_exit="20:50",
    max_trades_per_day=3,
    spread=0.25, slippage=0.05, commission_rt=0.0,
    ambiguity="stop_first",            # or "target_first"
    news_filter=None,                  # None or "approx"
    news_window_min=15,
    warmup_bars=200,
)

# Pre-registered variants (GOLD_PLAYBOOK_v1.md §13). Nothing else may be added without logging it.
VARIANTS = {
    "V0_base": {},
    "V1_cost_stress": dict(spread=0.50, slippage=0.15),
    "V2_raw_account": dict(spread=0.10, slippage=0.05, commission_rt=0.07),
    "V3_adx25": dict(adx_threshold=25.0, adx_cancel_below=20.0),
    "V4_adx35": dict(adx_threshold=35.0, adx_cancel_below=30.0),
    "V5_london_only": dict(signal_start="07:00", signal_end="11:45", pending_cutoff="12:00"),
    "V6_newyork_only": dict(signal_start="12:00", signal_end="15:45", pending_cutoff="16:00"),
    "V7_min_rr_1_5": dict(min_rr=1.5),
    "V8_no_rearm": dict(rearm=False),
    "V9_target_first": dict(ambiguity="target_first"),
    "V10_news_approx": dict(news_filter="approx"),
}

# FOMC statement dates (second day of each meeting). FROM MODEL MEMORY — NOT VERIFIED against
# federalreserve.gov in this session. Used only by the APPROXIMATE news-filter variant.
FOMC_DATES_UNVERIFIED = [
    "2021-01-27","2021-03-17","2021-04-28","2021-06-16","2021-07-28","2021-09-22","2021-11-03","2021-12-15",
    "2022-01-26","2022-03-16","2022-05-04","2022-06-15","2022-07-27","2022-09-21","2022-11-02","2022-12-14",
    "2023-02-01","2023-03-22","2023-05-03","2023-06-14","2023-07-26","2023-09-20","2023-11-01","2023-12-13",
    "2024-01-31","2024-03-20","2024-05-01","2024-06-12","2024-07-31","2024-09-18","2024-11-07","2024-12-18",
    "2025-01-29","2025-03-19","2025-05-07","2025-06-18","2025-07-30","2025-09-17","2025-10-29","2025-12-10",
    "2026-01-28","2026-03-18","2026-04-29","2026-06-17","2026-07-29","2026-09-16","2026-10-28","2026-12-09",
]

def us_dst_active(d: dt.date) -> bool:
    """US DST: second Sunday of March 02:00 local to first Sunday of November."""
    mar = dt.date(d.year, 3, 1); start = mar + dt.timedelta(days=(6 - mar.weekday()) % 7 + 7)
    nov = dt.date(d.year, 11, 1); end = nov + dt.timedelta(days=(6 - nov.weekday()) % 7)
    return start <= d < end

def approx_news_windows(start: dt.date, end: dt.date, half_width_min: int):
    """Approximate high-impact windows in UTC: NFP (first Friday, 08:30 ET) and FOMC statement (14:00 ET)."""
    wins = []
    d = dt.date(start.year, start.month, 1)
    while d <= end:
        first_friday = d + dt.timedelta(days=(4 - d.weekday()) % 7)
        et_offset = 4 if us_dst_active(first_friday) else 5
        t = dt.datetime(first_friday.year, first_friday.month, first_friday.day, 8 + et_offset, 30, tzinfo=dt.timezone.utc)
        wins.append((t - dt.timedelta(minutes=half_width_min), t + dt.timedelta(minutes=half_width_min), "NFP_approx"))
        d = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    for s in FOMC_DATES_UNVERIFIED:
        fd = dt.date.fromisoformat(s)
        if start <= fd <= end:
            et_offset = 4 if us_dst_active(fd) else 5
            t = dt.datetime(fd.year, fd.month, fd.day, 14 + et_offset, 0, tzinfo=dt.timezone.utc)
            wins.append((t - dt.timedelta(minutes=half_width_min), t + dt.timedelta(minutes=half_width_min + 60), "FOMC_unverified"))
    return sorted(wins)

# ---------------------------------------------------------------- indicators (Wilder)
def wilder_rma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full_like(x, np.nan, dtype=float)
    if len(x) < n: return out
    out[n - 1] = np.nanmean(x[:n])
    a = 1.0 / n
    for i in range(n, len(x)):
        out[i] = out[i - 1] + a * (x[i] - out[i - 1])
    return out

def indicators(m15: pd.DataFrame, cfg) -> pd.DataFrame:
    h, l, c = m15.high.values, m15.low.values, m15.close.values
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum.reduce([h - l, np.abs(h - pc), np.abs(l - pc)])
    up = h - np.roll(h, 1); dn = np.roll(l, 1) - l; up[0] = dn[0] = 0
    plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
    minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)
    n = cfg["adx_len"]
    atr_n = wilder_rma(tr, n)
    pdi = 100 * wilder_rma(plus_dm, n) / atr_n
    mdi = 100 * wilder_rma(minus_dm, n) / atr_n
    dx = 100 * np.abs(pdi - mdi) / np.where((pdi + mdi) == 0, np.nan, pdi + mdi)
    adx = wilder_rma(np.nan_to_num(dx, nan=0.0), n)
    adx[: 2 * n] = np.nan
    out = m15.copy()
    out["ema"] = pd.Series(c, index=m15.index).ewm(span=cfg["ema_len"], adjust=False).mean().values
    out["atr"] = wilder_rma(tr, cfg["atr_len"])
    out["pdi"], out["mdi"], out["adx"] = pdi, mdi, adx
    return out

# ---------------------------------------------------------------- engine
def hhmm(s): h, m = map(int, s.split(":")); return h * 60 + m

def run(cfg: dict, m1: pd.DataFrame, out_dir: pathlib.Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    m15 = m1.resample("15min", label="left", closed="left").agg(open=("open", "first"), high=("high", "max"),
                                                                 low=("low", "min"), close=("close", "last")).dropna()
    ind = indicators(m15, cfg)
    # ADX "armed": ADX>thr now AND some bar in [t-L, t] with ADX>thr and rising
    adx = ind.adx.values; thr = cfg["adx_threshold"]; L = cfg["adx_rising_lookback"]
    rising_above = (adx > thr) & (adx > np.roll(adx, 1))
    rising_recent = pd.Series(rising_above).rolling(L + 1, min_periods=1).max().values.astype(bool)
    armed = (adx > thr) & rising_recent
    long_dir = ind.pdi.values > ind.mdi.values
    touch_long = (ind.low.values <= ind.ema.values) & (ind.high.values >= ind.ema.values)
    touch_short = touch_long  # symmetric geometry; direction decided by DI
    hi, lo, cl, ema, atr = ind.high.values, ind.low.values, ind.close.values, ind.ema.values, ind.atr.values
    t15 = ind.index  # bar open times (UTC)
    minute_of_day = (t15.hour * 60 + t15.minute).values
    sig_lo, sig_hi = hhmm(cfg["signal_start"]), hhmm(cfg["signal_end"])
    cutoff_min, texit_min = hhmm(cfg["pending_cutoff"]), hhmm(cfg["time_exit"])
    spread, slip, comm = cfg["spread"], cfg["slippage"], cfg["commission_rt"]
    # M1 arrays and index ranges per M15 bar
    m1_t = m1.index.values; m1_o, m1_h, m1_l, m1_c = (m1[k].values for k in ("open", "high", "low", "close"))
    m1_mod = (m1.index.hour * 60 + m1.index.minute).values
    bar_start_idx = np.searchsorted(m1_t, t15.values, side="left")
    bar_end_idx = np.searchsorted(m1_t, (t15 + pd.Timedelta(minutes=15)).values, side="left")
    news = approx_news_windows(t15[0].date(), t15[-1].date(), cfg["news_window_min"]) if cfg["news_filter"] else []
    news_starts = np.array([np.datetime64(a.replace(tzinfo=None)) for a, _, _ in news]); news_ends = np.array([np.datetime64(b.replace(tzinfo=None)) for _, b, _ in news])
    def in_news(ts64):
        if len(news_starts) == 0: return False
        i = np.searchsorted(news_starts, ts64, side="right") - 1
        return i >= 0 and ts64 < news_ends[i]

    trades, skips = [], []
    pending = None; pos = None; trades_today = {}
    ambiguous_bars = 0

    def log_skip(i, side, reason, **kw):
        skips.append(dict(signal_bar_open=t15[i], side=side, reason=reason, **kw))

    for i in range(cfg["warmup_bars"], len(ind)):
        # ---- 1) simulate M1 bars of bar i against orders standing at the close of bar i-1
        if pending is not None or pos is not None:
            run_low, run_high = np.inf, -np.inf
            for j in range(bar_start_idx[i], bar_end_idx[i]):
                bo, bh, bl, bc, mod = m1_o[j], m1_h[j], m1_l[j], m1_c[j], m1_mod[j]
                ao, ah, al = bo + spread, bh + spread, bl + spread
                run_low, run_high = min(run_low, bl), max(run_high, bh)
                if pos is not None:
                    side = pos["side"]
                    if mod >= texit_min:
                        px = bo - slip if side == "long" else ao + slip
                        close_pos(pos, trades, m1_t[j], px, "time_exit", comm); pos = None; continue
                    if side == "long":
                        hit_stop = bl <= pos["stop"]; hit_tgt = bh > pos["target"]
                        stop_px = min(pos["stop"], bo) - slip; tgt_px = pos["target"]
                    else:
                        hit_stop = ah >= pos["stop"]; hit_tgt = al < pos["target"]
                        stop_px = max(pos["stop"], ao) + slip; tgt_px = pos["target"]
                    if hit_stop and hit_tgt:
                        ambiguous_bars += 1; pos["ambiguous"] = True
                        if cfg["ambiguity"] == "stop_first": hit_tgt = False
                        else: hit_stop = False
                    if hit_stop:
                        close_pos(pos, trades, m1_t[j], stop_px, "stop", comm); pos = None; continue
                    if hit_tgt:
                        close_pos(pos, trades, m1_t[j], tgt_px, "target", comm); pos = None; continue
                elif pending is not None:
                    if mod >= cutoff_min:
                        log_skip(pending["first_idx"], pending["side"], "CANCEL_cutoff_time", level=pending["level"]); pending = None; continue
                    if cfg["news_filter"] and in_news(m1_t[j]):
                        log_skip(pending["first_idx"], pending["side"], "CANCEL_news_window", level=pending["level"]); pending = None; continue
                    day = pd.Timestamp(m1_t[j]).date()
                    if pending["side"] == "long" and ah >= pending["level"]:
                        fill = max(pending["level"], ao) + slip
                        swing = min(pending["seq_low"], run_low)
                        stop = swing - pending["buffer"]
                        pos = open_pos(pending, m1_t[j], fill, stop)
                        trades_today[day] = trades_today.get(day, 0) + 1
                        pending = None
                        if bl <= stop:  # same-minute adverse move: conservative stop
                            close_pos(pos, trades, m1_t[j], min(stop, bl) - slip if bl < stop else stop - slip, "stop_same_minute", comm); pos = None
                        continue
                    if pending["side"] == "short" and bl <= pending["level"]:
                        fill = min(pending["level"], bo) - slip
                        swing = max(pending["seq_high"], run_high)
                        stop = swing + pending["buffer"]
                        pos = open_pos(pending, m1_t[j], fill, stop)
                        trades_today[day] = trades_today.get(day, 0) + 1
                        pending = None
                        if ah >= stop:
                            close_pos(pos, trades, m1_t[j], stop + slip, "stop_same_minute", comm); pos = None
                        continue
        # ---- 2) decisions at the close of bar i (bar i is now closed)
        if np.isnan(adx[i]) or np.isnan(atr[i]): continue
        mod_i = minute_of_day[i]
        close_ts = (t15[i] + pd.Timedelta(minutes=15)).to_datetime64()
        if pending is not None:
            side = pending["side"]
            deep = (cl[i] < ema[i] - cfg["deep_break_atr"] * atr[i]) if side == "long" else (cl[i] > ema[i] + cfg["deep_break_atr"] * atr[i])
            if deep: log_skip(pending["first_idx"], side, "CANCEL_deep_break"); pending = None
            elif adx[i] < cfg["adx_cancel_below"]: log_skip(pending["first_idx"], side, "CANCEL_adx_fell"); pending = None
            elif i >= pending["last_touch_idx"] + cfg["expiry_bars"]: log_skip(pending["first_idx"], side, "EXPIRED_unfilled"); pending = None
            else:
                # bar i closed with the order still unfilled: its extreme belongs to the pullback sequence (playbook §6)
                pending["seq_low"] = min(pending["seq_low"], lo[i]); pending["seq_high"] = max(pending["seq_high"], hi[i])
            if pending is not None and cfg["rearm"] and armed[i] and touch_long[i] and ((side == "long") == bool(long_dir[i])) and sig_lo <= mod_i <= sig_hi:
                if side == "long":
                    pending["level"] = hi[i] + cfg["entry_offset"]; pending["seq_low"] = min(pending["seq_low"], lo[i])
                    stop_est = pending["seq_low"] - pending["buffer"]; rr = (pending["target"] - pending["level"]) / (pending["level"] - stop_est)
                else:
                    pending["level"] = lo[i] - cfg["entry_offset"]; pending["seq_high"] = max(pending["seq_high"], hi[i])
                    stop_est = pending["seq_high"] + pending["buffer"]; rr = (pending["level"] - pending["target"]) / (stop_est - pending["level"])
                pending["last_touch_idx"] = i; pending["last_touch_open"] = t15[i]; pending["rearms"] += 1; pending["rr_at_placement"] = rr
                if rr < cfg["min_rr"]: log_skip(pending["first_idx"], side, "CANCEL_rr_too_low_after_rearm", rr=rr); pending = None
        if pending is None and pos is None and sig_lo <= mod_i <= sig_hi and armed[i] and touch_long[i]:
            side = "long" if long_dir[i] else "short"
            day = (t15[i] + pd.Timedelta(minutes=15)).date()
            if trades_today.get(day, 0) >= cfg["max_trades_per_day"]:
                log_skip(i, side, "WAIT_daily_cap"); continue
            if cfg["news_filter"] and in_news(close_ts):
                log_skip(i, side, "WAIT_news_window"); continue
            buffer = max(cfg["stop_buffer_min"], cfg["stop_buffer_atr"] * atr[i])
            w0 = max(0, i - cfg["target_lookback"] + 1)
            if side == "long":
                level = hi[i] + cfg["entry_offset"]; target = hi[w0:i + 1].max(); stop_est = lo[i] - buffer
                rr = (target - level) / (level - stop_est)
            else:
                level = lo[i] - cfg["entry_offset"]; target = lo[w0:i + 1].min(); stop_est = hi[i] + buffer
                rr = (level - target) / (stop_est - level)
            if rr < cfg["min_rr"]:
                log_skip(i, side, "WAIT_rr_too_low", rr=rr, level=level, target=target, stop_est=stop_est); continue
            pending = dict(side=side, level=level, target=target, buffer=buffer, first_idx=i, last_touch_idx=i, last_touch_open=t15[i],
                           seq_low=lo[i], seq_high=hi[i], signal_bar_open=t15[i], adx=adx[i], atr=atr[i], ema=ema[i],
                           rr_at_placement=rr, rearms=0, session="London" if mod_i < 12 * 60 else "NewYork")
    # end loop: force-close anything left (should not happen because of time exit)
    tr = pd.DataFrame(trades)
    if len(tr):
        tr["planned_risk"] = (tr.level - tr.stop).abs()
        sign = np.where(tr.side == "long", 1.0, -1.0)
        tr["pnl_per_oz"] = sign * (tr.exit_price - tr.entry_price) - comm
        tr["realised_R"] = tr.pnl_per_oz / tr.planned_risk
        tr["hold_minutes"] = (pd.to_datetime(tr.exit_time) - pd.to_datetime(tr.entry_time)).dt.total_seconds() / 60
        tr["signal_date"] = pd.to_datetime(tr.signal_bar_open).dt.date
    tr.to_csv(out_dir / "trades.csv", index=False)
    pd.DataFrame(skips).to_csv(out_dir / "skips.csv", index=False)
    meta = dict(config=cfg, n_trades=int(len(tr)), n_skips=len(skips), ambiguous_bars=ambiguous_bars,
                m15_bars=int(len(ind)), m1_bars=int(len(m1)), data_start=str(m1.index[0]), data_end=str(m1.index[-1]),
                run_time_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    (out_dir / "config.json").write_text(json.dumps(meta, indent=2, default=str))
    return tr, pd.DataFrame(skips), meta

def open_pos(p, t, fill, stop):
    return dict(side=p["side"], signal_bar_open=p["signal_bar_open"], last_touch_open=p["last_touch_open"], session=p["session"], level=p["level"], target=p["target"],
                entry_time=t, entry_price=fill, stop=stop, adx_at_signal=p["adx"], atr_at_signal=p["atr"], ema_at_signal=p["ema"],
                rr_at_placement=p["rr_at_placement"], rearms=p["rearms"], ambiguous=False)

def close_pos(pos, trades, t, px, reason, comm):
    rec = dict(pos); rec.update(exit_time=t, exit_price=px, exit_reason=reason); trades.append(rec)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--variant"); ap.add_argument("--all", action="store_true")
    ap.add_argument("--data", default=str(DATA))
    a = ap.parse_args()
    m1 = pd.read_parquet(a.data)
    names = list(VARIANTS) if a.all else [a.variant or "V0_base"]
    for name in names:
        cfg = dict(BASE_CONFIG); cfg.update(VARIANTS[name]); cfg["variant"] = name
        tr, sk, meta = run(cfg, m1, RESULTS / name)
        print(f"{name}: trades={len(tr)} skips={len(sk)} ambiguous_m1_bars={meta['ambiguous_bars']}"
              + (f" meanR={tr.realised_R.mean():.3f}" if len(tr) else ""))

if __name__ == "__main__":
    main()
