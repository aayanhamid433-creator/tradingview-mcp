#!/usr/bin/env python3
"""engine_v4_rsi2_m15.py — F6 RSI2_M15: two-bar RSI exhaustion fade on M15 with ATR stop/target and a 60-minute
maximum hold. Specification: results/PREREGISTRATION_v4.md §0 (shared conventions) and §2 F6, frozen 2026-11-12 before
any v4 run. Nothing here may be re-tuned after a result has been seen.

Mechanics are engine_v3.py's, copied where they apply (fill_entry, the M1 loop, open_pos/close_pos, counters, output):
  * BID M1 bars, ask = bid + spread (0.25), slippage 0.05 per fill, commission 0 (E.BASE_CONFIG);
  * M15 = m1.resample("15min", label="left", closed="left") OHLC dropna; E.indicators (ATR14 = Wilder RMA of the true
    range); warmup 200 M15 bars; session-day key of a bar = (t + 1h).date (m1_day / m15_day / skey);
  * decisions only at the close of a closed M15 bar i, after bar i's M1 bars have been simulated; an order placed at that
    close acts on the M1 bars of bar i+1 onward (the first simulated M1 bar for a market order);
  * market fill: long = bid open + spread + slip, short = bid open - slip (fill_entry with level None);
  * gap rule: a fill at/beyond the order's own stop or target is not taken (SKIP_gap_fill_past_stop / _target); the
    session day stays open for a later signal;
  * same-minute stop: long, fill bar's bid low <= stop -> closed at (bid low - slip if bid low < stop else stop - slip);
    short, ask high >= stop -> stop + slip; reason stop_same_minute;
  * open position, per M1 bar, in this order: session_gap_exit when the bar's session key differs from the position's
    (long bid open - slip / short ask open + slip); time_exit at the first bar with minute-of-day >= 20:50 (same prices);
    stop (long bid low <= stop -> min(stop, bid open) - slip; short ask high >= stop -> max(stop, ask open) + slip);
    target on a strict trade-through (long bid high > target; short ask low < target) filled at the target; stop first
    when both print in one minute (ambiguous flag, counter); then max_hold: bar_time - entry_time >= max_hold - 1 min ->
    closed at that bar's close (timestamp + 1 min) at bid close - slip (long) / bid close + spread + slip (short);
  * no rounding of any level; planned_risk = |fill - stop|; pnl_per_oz = sign x (exit - fill) - commission;
    realised_R = pnl_per_oz / planned_risk; signal_time = signal bar close, signal_bar_open = signal bar open.

F6 rules (frozen):
  RSI(n) on M15 closes over consecutive M15 bars (across the daily break, like the EMA/ATR): d = close - previous close,
  gain = max(d, 0), loss = max(-d, 0), avg_gain = E.wilder_rma(gain, n), avg_loss = E.wilder_rma(loss, n),
  RSI = 100 - 100 / (1 + avg_gain / avg_loss); avg_loss == 0 -> 100 (50 if avg_gain is also 0). The first bar has no
  previous close: d[0] = 0 (E.indicators treats the first true range the same way); irrelevant after the warmup.
  1) decisions only at the close of M15 bars whose OPEN time is in [07:00, 15:45] (minute-of-day 420..945, fills
     nominally 07:15-16:00);
  2) RSI(rsi_len) <= rsi_x -> long; RSI(rsi_len) >= 100 - rsi_x -> short; the bar is skipped if ATR14 or RSI is NaN;
  3) one trade per session day = the first signal whose order is FILLED; no signal is evaluated while an order is
     pending, while a position is open, or after the day's trade; a gap-rule or blackout skip does NOT consume the day;
  4) levels fixed at signal time from the signal bar (the last closed bar): long stop = signal low - stop_atr x ATR14,
     long target = signal close + target_atr x ATR14; short stop = signal high + stop_atr x ATR14, short target = signal
     close - target_atr x ATR14 (ATR14 of the signal bar);
  5) blackout: the order is dropped (SKIP_news_blackout) when its fill minute — the first M1 bar after the signal bar's
     close, nominally the close time — OPENS in [13:25, 13:35] inclusive (in practice the 13:15 signal bar); the check
     is made on the actual fill bar's minute-of-day;
  6) entry: pending kind "market" -> fill_entry; gap rule; same-minute stop;
  7) open position per M1 bar: session_gap_exit; time_exit; stop; target; stop first; max_hold (engine_v3 definition);
  8) trades with hold_minutes < 3 are flagged (column hold_lt3; account rule: their profit is deducted).
  No partial exits, trailing, news calendar or re-entry.

Variants (frozen): RSI2_BASE (rsi_len=2) and RSI2_RSI3 (rsi_len=3); both rsi_x=5, stop_atr=1.5, target_atr=1.0,
max_hold_minutes=60, window 07:00-15:45, blackout 13:25-13:35, time_exit 20:50, one trade per session day.
Perturbation (robustness report only, never selection): rsi_x, stop_atr, target_atr, max_hold_minutes at 0.8x and 1.2x,
one at a time (integer parameters rounded, skipped if unchanged), pooled validation + final-test trades.

Usage:
  python3 engine_v4_rsi2_m15.py --variant RSI2_BASE            # -> results/V4_RSI2_BASE/{trades,skips}.csv, config.json
  python3 engine_v4_rsi2_m15.py --all                          # both variants, at most 2 processes
  python3 engine_v4_rsi2_m15.py --perturb RSI2_BASE            # -> results/V4_RSI2_BASE/perturb.json (trades.csv untouched)
  python3 engine_v4_rsi2_m15.py --variant RSI2_BASE --max-hold 15   # feasibility check -> results/V4_RSI2_BASE_h15/
"""
import argparse, json, pathlib, datetime as dt, time, math
import numpy as np, pandas as pd
import engine as E
import engine_v2 as V2

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
FAMILY = "RSI2"

V4_CONFIG = dict(E.BASE_CONFIG)
for _k in ("adx_threshold", "adx_rising_lookback", "adx_cancel_below", "entry_offset", "stop_buffer_min", "stop_buffer_atr",
           "deep_break_atr", "target_lookback", "min_rr", "rearm", "expiry_bars", "pending_cutoff",
           "max_trades_per_day", "news_filter", "news_window_min"):
    V4_CONFIG.pop(_k, None)   # v1 pullback parameters are not used by this family
V4_CONFIG.update(dict(
    version="v4.0-rsi2_m15", family=FAMILY,
    rsi_len=2,                 # integer, structural (RSI2_RSI3: 3); not perturbed
    rsi_x=5.0,                 # long if RSI <= rsi_x, short if RSI >= 100 - rsi_x   [numeric]
    stop_atr=1.5,              # stop = signal low/high -/+ stop_atr x ATR14(signal bar)   [numeric]
    target_atr=1.0,            # target = signal close +/- target_atr x ATR14(signal bar) [numeric]
    max_hold_minutes=60,       # engine_v3 definition                                     [numeric, integer]
    signal_start="07:00", signal_end="15:45",       # by signal-bar OPEN, inclusive       [fixed]
    blackout_start="13:25", blackout_end="13:35",   # fill minute open, inclusive         [fixed]
    time_exit="20:50", warmup_bars=200, one_trade_per_day=True,
))

# ---- PRE-REGISTERED VARIANT LIST (PREREGISTRATION_v4.md, frozen 2026-11-12) ----
VARIANTS = {
    "RSI2_BASE": dict(rsi_len=2),
    "RSI2_RSI3": dict(rsi_len=3),
}
NUMERIC_PARAMS = ("rsi_x", "stop_atr", "target_atr", "max_hold_minutes")
INTEGER_PARAMS = ("max_hold_minutes",)
PERTURB_MULTS = (0.8, 1.2)
PERIODS = {"development": ("2021-01-04", "2024-07-01"), "validation": ("2024-07-01", "2025-09-01"),
           "final_test": ("2025-09-01", "2026-11-01")}   # by signal_bar_open; same as analyze.PERIODS

hhmm = E.hhmm
ONE_MIN = np.timedelta64(1, "m")


def rsi_wilder(close, n: int) -> np.ndarray:
    """Wilder RSI(n) on consecutive closes: avg gain / avg loss by E.wilder_rma (seed = simple mean of the first n,
    then recursive). NaN until both averages exist; avg_loss == 0 -> 100 (50 if avg_gain is also 0)."""
    c = np.asarray(close, dtype=float)
    d = np.diff(c, prepend=c[0])          # d[0] = 0: no previous close for the first bar
    gain = np.maximum(d, 0.0); loss = np.maximum(-d, 0.0)
    ag = E.wilder_rma(gain, n); al = E.wilder_rma(loss, n)
    out = np.full(len(c), np.nan)
    ok = ~(np.isnan(ag) | np.isnan(al))
    with np.errstate(divide="ignore", invalid="ignore"):
        val = 100.0 - 100.0 / (1.0 + ag / al)
    val = np.where(al == 0.0, np.where(ag == 0.0, 50.0, 100.0), val)
    out[ok] = val[ok]
    return out


def run(cfg: dict, m1: pd.DataFrame, out_dir):
    """Run one configuration. out_dir None -> nothing is written (used by --perturb)."""
    t0 = time.time()
    if out_dir is not None: out_dir.mkdir(parents=True, exist_ok=True)
    fam = cfg["family"]
    m15 = m1.resample("15min", label="left", closed="left").agg(open=("open", "first"), high=("high", "max"),
                                                                 low=("low", "min"), close=("close", "last")).dropna()
    ind = E.indicators(m15, cfg)
    hi, lo, cl, atr = ind.high.values, ind.low.values, ind.close.values, ind.atr.values
    rsi = rsi_wilder(cl, int(cfg["rsi_len"]))
    t15 = ind.index
    mod15 = (t15.hour * 60 + t15.minute).values
    skey = (t15 + pd.Timedelta(hours=1)).date
    daily = V2.daily_frame(m1)
    dpos = {k: i for i, k in enumerate(daily.index)}
    spread, slip, comm = cfg["spread"], cfg["slippage"], cfg["commission_rt"]
    texit_min = hhmm(cfg["time_exit"])
    max_hold = cfg["max_hold_minutes"]
    hold_td = np.timedelta64(int(max_hold) - 1, "m") if max_hold else None
    m1_t = m1.index.values; m1_o, m1_h, m1_l, m1_c = (m1[k].values for k in ("open", "high", "low", "close"))
    m1_mod = (m1.index.hour * 60 + m1.index.minute).values
    # session-day number of each M1 / M15 bar (23:00 start). Intraday positions and orders may not outlive their session
    # day: on days where the feed ends before 20:50 they are closed / cancelled at the first bar of the next session day.
    m1_day = (m1.index.values + np.timedelta64(1, "h")).astype("datetime64[D]")
    m15_day = (t15.values + np.timedelta64(1, "h")).astype("datetime64[D]")
    bar_start = np.searchsorted(m1_t, t15.values, side="left")
    bar_end = np.searchsorted(m1_t, (t15 + pd.Timedelta(minutes=15)).values, side="left")
    sig_lo, sig_hi = hhmm(cfg["signal_start"]), hhmm(cfg["signal_end"])
    blk_lo, blk_hi = hhmm(cfg["blackout_start"]), hhmm(cfg["blackout_end"])
    rsi_x, stop_k, tgt_k = float(cfg["rsi_x"]), float(cfg["stop_atr"]), float(cfg["target_atr"])

    def prev_day(k):
        i = dpos.get(k)
        return None if i is None or i == 0 else daily.iloc[i - 1]

    trades, skips = [], []
    pending = None; pos = None
    day = dict(key=None, entries=0, done=False, pdy=None)
    counters = dict(ambiguous_stop_target=0, both_sides_same_minute=0, same_minute_stop=0, gap_fill_skipped=0,
                    news_blackout_skipped=0, session_ended_cancelled=0, signals_long=0, signals_short=0,
                    signal_bars_suppressed_day_done=0)

    def log_skip(t, side, reason, **kw): skips.append(dict(signal_time=t, side=side, reason=reason, **kw))

    def open_pos(side, t, fill, level, stop, target, meta):
        risk = abs(level - stop)
        return dict(variant=cfg["variant"], family=fam, side=side, signal_time=meta["signal_time"], signal_bar_open=meta["signal_bar_open"],
                    entry_time=t, entry_price=fill, level=level, initial_stop=stop, stop=stop, target=target, planned_risk=risk,
                    hh=fill, ll=fill, ambiguous=False, day=m1_day[np.searchsorted(m1_t, t)], **{k: v for k, v in meta.items() if k not in ("signal_time", "signal_bar_open")})

    def close_pos(p, t, px, reason):
        sign = 1.0 if p["side"] == "long" else -1.0
        pnl = sign * (px - p["entry_price"]) - comm
        rec = dict(p); rec.update(exit_time=t, exit_price=px, exit_reason=reason, pnl_per_oz=pnl, realised_R=pnl / p["planned_risk"],
                                  final_stop=p["stop"])
        for k in ("hh", "ll", "stop", "day"): rec.pop(k, None)
        trades.append(rec)

    def fill_entry(side, j, level_or_none, stop, target, meta):
        """engine_v3.fill_entry: fill a buy/sell stop (level given) or a market order (level None) on M1 bar j; gap rule;
        same-minute stop check. A filled order consumes the session day (one trade per day)."""
        nonlocal pos
        bo, bh, bl = m1_o[j], m1_h[j], m1_l[j]; ao, ah = bo + spread, bh + spread
        fill = ((max(level_or_none, ao) if level_or_none is not None else ao) + slip) if side == "long" else ((min(level_or_none, bo) if level_or_none is not None else bo) - slip)
        past_stop = (fill <= stop) if side == "long" else (fill >= stop)
        past_tgt = target is not None and ((fill >= target) if side == "long" else (fill <= target))
        if past_stop or past_tgt:   # the first print after a gap is already beyond the planned stop or target: the order is not taken
            counters["gap_fill_skipped"] += 1
            log_skip(meta["signal_time"], side, "SKIP_gap_fill_past_stop" if past_stop else "SKIP_gap_fill_past_target", fill=fill, stop=stop, target=target,
                     fill_time=m1_t[j]); return
        if side == "long":
            level = level_or_none if level_or_none is not None else fill
            pos = open_pos("long", m1_t[j], fill, level, stop, target, meta); day["entries"] += 1; day["done"] = True
            if bl <= stop:
                counters["same_minute_stop"] += 1
                close_pos(pos, m1_t[j], (min(stop, bl) - slip if bl < stop else stop - slip), "stop_same_minute"); pos = None
        else:
            level = level_or_none if level_or_none is not None else fill
            pos = open_pos("short", m1_t[j], fill, level, stop, target, meta); day["entries"] += 1; day["done"] = True
            if ah >= stop:
                counters["same_minute_stop"] += 1
                close_pos(pos, m1_t[j], stop + slip, "stop_same_minute"); pos = None

    for i in range(cfg["warmup_bars"], len(ind)):
        k = skey[i]
        if k != day["key"]:
            # ---- new session day (23:00): reset per-day state; daily quantities are previous-session-day values
            day.update(key=k, entries=0, done=False, pdy=prev_day(k))
        # ---- 1) simulate the M1 bars of bar i against the standing order / open position (engine_v3 loop)
        if pending is not None or pos is not None:
            for j in range(bar_start[i], bar_end[i]):
                bo, bh, bl, bc, mod = m1_o[j], m1_h[j], m1_l[j], m1_c[j], m1_mod[j]
                ao, ah, al = bo + spread, bh + spread, bl + spread
                if pos is not None:
                    side = pos["side"]
                    if m1_day[j] != pos["day"]:
                        close_pos(pos, m1_t[j], bo - slip if side == "long" else ao + slip, "session_gap_exit"); pos = None; continue
                    if mod >= texit_min:
                        close_pos(pos, m1_t[j], bo - slip if side == "long" else ao + slip, "time_exit"); pos = None; continue
                    if side == "long":
                        hit_stop = bl <= pos["stop"]; hit_tgt = pos["target"] is not None and bh > pos["target"]
                        stop_px = min(pos["stop"], bo) - slip
                    else:
                        hit_stop = ah >= pos["stop"]; hit_tgt = pos["target"] is not None and al < pos["target"]
                        stop_px = max(pos["stop"], ao) + slip
                    if hit_stop and hit_tgt:
                        counters["ambiguous_stop_target"] += 1; pos["ambiguous"] = True
                        hit_tgt = False   # stop first (BASE_CONFIG ambiguity)
                    if hit_stop:
                        reason = "stop" if pos["stop"] == pos["initial_stop"] else "trail_stop"
                        close_pos(pos, m1_t[j], stop_px, reason); pos = None; continue
                    if hit_tgt:
                        close_pos(pos, m1_t[j], pos["target"], "target"); pos = None; continue
                    if hold_td is not None and m1_t[j] - pos["entry_time"] >= hold_td:
                        px = bc - slip if side == "long" else bc + spread + slip
                        close_pos(pos, m1_t[j] + ONE_MIN, px, "max_hold"); pos = None; continue
                elif pending is not None:
                    if pending["cancel_min"] is not None and mod >= pending["cancel_min"]:
                        log_skip(pending["meta"]["signal_time"], pending["side"], "CANCEL_unfilled_at_cutoff"); pending = None; continue
                    if pending.get("day") is not None and m1_day[j] != pending["day"]:
                        counters["session_ended_cancelled"] += 1
                        log_skip(pending["meta"]["signal_time"], pending["side"], "CANCEL_session_ended", fill_time=m1_t[j]); pending = None; continue
                    if pending["kind"] == "market":
                        side = pending["side"]; meta = pending["meta"]
                        pending = None
                        if blk_lo <= mod <= blk_hi:   # F6 rule 5: fill minute opens inside the 13:25-13:35 blackout -> order dropped, day stays open
                            counters["news_blackout_skipped"] += 1
                            log_skip(meta["signal_time"], side, "SKIP_news_blackout", fill_time=m1_t[j], stop=meta["stop"], target=meta["target"]); continue
                        stop, target = meta.pop("stop"), meta.pop("target")
                        fill_entry(side, j, None, stop, target, meta)
                        continue
        # ---- 2) decision at the close of bar i (bar i is closed; bar i+1 has not started)
        if not (sig_lo <= mod15[i] <= sig_hi): continue
        if np.isnan(atr[i]) or np.isnan(rsi[i]): continue
        if rsi[i] <= rsi_x: side = "long"
        elif rsi[i] >= 100.0 - rsi_x: side = "short"
        else: continue
        if pos is not None or pending is not None or (cfg["one_trade_per_day"] and day["done"]):
            counters["signal_bars_suppressed_day_done"] += 1; continue   # rule 3: nothing is evaluated while pending/open/after the day's trade
        counters["signals_long" if side == "long" else "signals_short"] += 1
        if side == "long": stop, target = lo[i] - stop_k * atr[i], cl[i] + tgt_k * atr[i]
        else: stop, target = hi[i] + stop_k * atr[i], cl[i] - tgt_k * atr[i]
        pdy = day["pdy"]
        d1atr = pdy.atr14 if pdy is not None and not np.isnan(pdy.atr14) else np.nan
        close_ts = t15[i] + pd.Timedelta(minutes=15)
        pending = dict(kind="market", side=side, cancel_min=None, day=m15_day[i],
                       meta=dict(signal_time=close_ts, signal_bar_open=t15[i], stop=stop, target=target, rsi=rsi[i], atr=atr[i],
                                 signal_close=cl[i], signal_high=hi[i], signal_low=lo[i], d1atr=d1atr))
    # end of data: an open position is closed at the last bar's close (flagged) so that it is counted (engine_v3)
    if pos is not None:
        j = len(m1_t) - 1
        close_pos(pos, m1_t[j], m1_c[j] - slip if pos["side"] == "long" else m1_c[j] + spread + slip, "end_of_data"); pos = None
    tr = pd.DataFrame(trades)
    if len(tr):
        tr["hold_minutes"] = (pd.to_datetime(tr.exit_time) - pd.to_datetime(tr.entry_time)).dt.total_seconds() / 60
        tr["signal_date"] = pd.to_datetime(tr.signal_bar_open).dt.date
        tr["hold_lt3"] = tr.hold_minutes < 3   # account rule: profit of trades held < 3 min is deducted
    sk = pd.DataFrame(skips)
    n_session_days = int(len(daily))
    meta = dict(config=cfg, n_trades=int(len(tr)), n_skips=int(len(sk)), counters=counters, m15_bars=int(len(ind)), m1_bars=int(len(m1)),
                n_session_days=n_session_days, trades_per_session_day=(len(tr) / n_session_days if n_session_days else None),
                exit_reasons=(tr.exit_reason.value_counts().to_dict() if len(tr) else {}),
                skip_reasons=(sk.reason.value_counts().to_dict() if len(sk) else {}),
                n_hold_lt3=(int(tr.hold_lt3.sum()) if len(tr) else 0),
                data_start=str(m1.index[0]), data_end=str(m1.index[-1]), run_seconds=round(time.time() - t0, 1),
                run_time_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    if out_dir is not None:
        tr.to_csv(out_dir / "trades.csv", index=False)
        sk.to_csv(out_dir / "skips.csv", index=False)
        (out_dir / "config.json").write_text(json.dumps(meta, indent=2, default=str))
    return tr, sk, meta


def make_cfg(name: str, max_hold=None):
    """Config and output directory name for a frozen variant id ('RSI2_BASE' or 'V4_RSI2_BASE'); --max-hold N writes to
    a separate '<dir>_h<N>' directory so that the registered run is never overwritten."""
    key = name[3:] if name.startswith("V4_") and name[3:] in VARIANTS else name
    if key not in VARIANTS: raise SystemExit(f"unknown variant {name!r}; known: {list(VARIANTS)}")
    cfg = dict(V4_CONFIG); cfg.update(VARIANTS[key])
    out_name = f"V4_{key}"
    if max_hold is not None:
        cfg["max_hold_minutes"] = int(max_hold); out_name += f"_h{int(max_hold)}"
    cfg["variant"] = out_name; cfg["variant_id"] = key
    return cfg, out_name


def oos_stats(tr: pd.DataFrame):
    """Pooled validation + final-test trades (by signal_bar_open): n, mean R, profit factor, max drawdown in R."""
    if not len(tr): return dict(n_oos=0, meanR_oos=None, pf_oos=None, dd_oos=None)
    sbo = pd.to_datetime(tr.signal_bar_open, utc=True)
    a, b = pd.Timestamp(PERIODS["validation"][0], tz="UTC"), pd.Timestamp(PERIODS["final_test"][1], tz="UTC")
    r = tr.realised_R.values[((sbo >= a) & (sbo < b)).values]
    if len(r) == 0: return dict(n_oos=0, meanR_oos=None, pf_oos=None, dd_oos=None)
    wins, losses = r[r > 0].sum(), abs(r[r <= 0].sum())
    pf = (wins / losses) if losses > 0 else None
    cum = np.cumsum(r); dd = float((cum - np.maximum.accumulate(cum)).min())
    return dict(n_oos=int(len(r)), meanR_oos=float(r.mean()), pf_oos=(float(pf) if pf is not None and math.isfinite(pf) else None), dd_oos=dd)


_M1 = None
def _worker(args):
    name, max_hold = args
    cfg, out_name = make_cfg(name, max_hold)
    tr, sk, meta = run(cfg, _M1, RESULTS / out_name)
    extra = f" meanR={tr.realised_R.mean():+.3f} totalR={tr.realised_R.sum():+.1f} exits={meta['exit_reasons']}" if len(tr) else ""
    return f"{out_name}: trades={len(tr)} skips={len(sk)} counters={meta['counters']} secs={meta['run_seconds']}{extra}"


def _perturb_worker(args):
    name, param, mult, value = args
    cfg, _ = make_cfg(name); cfg[param] = value; cfg["variant"] = f"V4_{cfg['variant_id']}_perturb_{param}_{mult}"
    tr, sk, meta = run(cfg, _M1, None)
    st = oos_stats(tr)
    return dict(param=param, mult=mult, value=value, **st, n_all=int(len(tr)), run_seconds=meta["run_seconds"])


def perturb(name: str, jobs: int = 2):
    """+-20% one-at-a-time perturbation of the numeric parameters; pooled validation + final-test statistics only; the
    base trades.csv is not touched (perturbation runs write nothing)."""
    cfg, out_name = make_cfg(name)
    jobs_list = []
    for p in NUMERIC_PARAMS:
        base = cfg[p]
        for mult in PERTURB_MULTS:
            v = base * mult
            if p in INTEGER_PARAMS: v = int(round(v))
            if v == base: print(f"perturb {p} x{mult}: unchanged ({v}), skipped"); continue
            jobs_list.append((name, p, mult, v))
    rows = []
    if jobs > 1 and len(jobs_list) > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(min(jobs, 2)) as pool:
            for r in pool.imap(_perturb_worker, jobs_list): rows.append(r); print(r, flush=True)
    else:
        for a in jobs_list: r = _perturb_worker(a); rows.append(r); print(r, flush=True)
    out = RESULTS / out_name; out.mkdir(parents=True, exist_ok=True)
    (out / "perturb.json").write_text(json.dumps(rows, indent=2, default=str))
    base_tr = pd.read_csv(out / "trades.csv") if (out / "trades.csv").exists() else None
    if base_tr is not None and len(base_tr): print(f"base ({out_name}, from trades.csv): {oos_stats(base_tr)}")
    print(f"wrote {out / 'perturb.json'} ({len(rows)} rows)")
    return rows


def main():
    global _M1
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--variant", help="variant id, e.g. RSI2_BASE"); ap.add_argument("--all", action="store_true")
    ap.add_argument("--perturb", help="variant id: +-20%% one-at-a-time perturbation -> results/V4_<ID>/perturb.json")
    ap.add_argument("--max-hold", type=int, default=None, help="override max_hold_minutes (feasibility check); writes to results/V4_<ID>_h<N>/")
    ap.add_argument("--jobs", type=int, default=2); ap.add_argument("--data", default=str(E.DATA)); ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list: print("\n".join(f"{v}: {VARIANTS[v]}" for v in VARIANTS)); return
    _M1 = pd.read_parquet(a.data)
    t0 = time.time()
    if a.perturb:
        perturb(a.perturb, jobs=min(a.jobs, 2)); print(f"total wall time {time.time() - t0:.0f} s"); return
    names = list(VARIANTS) if a.all else [a.variant or "RSI2_BASE"]
    args = [(n, a.max_hold) for n in names]
    if len(names) > 1 and a.jobs > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(min(a.jobs, 2)) as pool:   # at most 2 processes
            for line in pool.imap_unordered(_worker, args): print(line, flush=True)
    else:
        for arg in args: print(_worker(arg), flush=True)
    print(f"total wall time {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
