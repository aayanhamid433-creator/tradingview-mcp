#!/usr/bin/env python3
"""Backtest engine for GOLD_PLAYBOOK_v2_CANDIDATE.md (layered build) on XAUUSD M1 data.

Reuses engine.py (v1.0) indicators and conventions. Adds:
  L0  signal window 07:00-16:45 UTC, pending cut-off 17:00, approximate news gate, daily stop (3 consecutive
      losses or -2 R closed), weekly stop (-4 R), Monday gap gate, stop-distance sanity cap
  L1  daily bias from the previous closed session-day bar: SMA200 trend state, 12-1 momentum vote,
      size multiplier 0.5 on disagreement; undefined bias (warm-up) = no trades
  L2  Asian range 23:00-07:00 UTC, prior-day high/low, D1 ATR(14)
  L3  Trigger A = v1.0 Holy Grail pullback (unchanged); Trigger B = Asian-range breakout (default OFF)
  L5  first target T1 (20-bar momentum extreme, capped at prior-day H/L + 1 ATR), 50 % partial at T1 with
      stop to entry +/- 0.10, Chandelier trail 3 x ATR14(M15) on the remainder, 20:50 UTC time exit
All P&L is in R of the initial stop. size_mult is recorded; realised_R_weighted = realised_R * size_mult.

Usage: python3 engine_v2.py --all | --variant V2_0 | --check   (--check runs the v1-compat regression test)
Outputs: ../results/<variant>/trades.csv, skips.csv, config.json
"""
import argparse, json, pathlib, datetime as dt
import numpy as np, pandas as pd
import engine as E

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"

V2_CONFIG = dict(E.BASE_CONFIG)
V2_CONFIG.update(dict(
    version="v2.0-candidate",
    signal_start="07:00", signal_end="16:45", pending_cutoff="17:00", time_exit="20:50",
    min_rr=1.5,
    bias_mode="sma200_mom",        # "sma200_mom" | "sma200" | None
    bias_disagree_mult=0.5,
    news_gate="approx",            # "approx" | None   (NFP first Friday 08:30 ET +-3 min; FOMC 14:00 ET -5/+45 min; CPI/PCE/GDP dates unavailable)
    daily_stop_losses=3, daily_stop_R=-2.0, weekly_stop_R=-4.0,
    monday_gap_gate=True,
    stop_sanity_d1atr=0.6,
    target_cap_atr=1.0,
    partial_exit=True, partial_frac=0.5, be_offset=0.10,
    trail_mult=3.0,
    trigger_a=True, trigger_b=False,
    confirm_close=False,               # touch bar must close on the trend side of the EMA
    daily_fallback=None,               # Trigger C "one trade every day": None | "bias" (daily SMA200 side) | "di" (+DI vs -DI on M15)
    daily_fallback_time="13:30",       # if the session day has had no entry by this bar OPEN (UTC), enter at market on the next minute
    fallback_stop_atr=1.5,             # stop = k x ATR14(M15); T1 = min_rr x that distance; partial/trail/time exit as usual
    trig_b_start="07:00", trig_b_end="10:45", trig_b_adx=20.0, trig_b_valid_bars=2, trig_b_stop_cap_atr=2.0,
))

VARIANTS = {
    "V2_0":            {},
    "V2_A_nobias":     dict(bias_mode=None),
    "V2_B_sma_only":   dict(bias_mode="sma200", bias_disagree_mult=1.0),
    "V2_C_trigB_only": dict(trigger_a=False, trigger_b=True),
    "V2_D_trigAB":     dict(trigger_a=True, trigger_b=True),
    "V2_E_rr1":        dict(min_rr=1.0),
    "V2_F_v1exits":    dict(partial_exit=False, trail_mult=None, target_cap_atr=None),
    "V2_G_nostops":    dict(daily_stop_losses=None, daily_stop_R=None, weekly_stop_R=None),
    "V2_H_coststress": dict(spread=0.50, slippage=0.15),
    "V2_I_v1window":   dict(signal_start="07:00", signal_end="15:45", pending_cutoff="16:00"),
    # v2.2 candidates (added 2026-11-12; fourth look at the same data, see VALIDATION_REPORT_v2.md caveat)
    "V2_J_ny_only":    dict(signal_start="12:00", signal_end="15:45", pending_cutoff="16:00"),
    "V2_K_confirm":    dict(signal_start="07:00", signal_end="15:45", pending_cutoff="16:00", confirm_close=True),
    "V2_L_ny_confirm": dict(signal_start="12:00", signal_end="15:45", pending_cutoff="16:00", confirm_close=True),
    # "one trade every day" candidates (added 2026-11-12 at Aayan's request; pre-registered before running, fifth look at the data)
    "V2_M_daily_bias":      dict(signal_start="07:00", signal_end="15:45", pending_cutoff="16:00", confirm_close=True, daily_fallback="bias"),
    "V2_N_daily_di_nobias": dict(signal_start="07:00", signal_end="15:45", pending_cutoff="16:00", confirm_close=True, daily_fallback="di", bias_mode=None),
    "V2_O_daily_bias_0800": dict(signal_start="07:00", signal_end="15:45", pending_cutoff="16:00", confirm_close=True, daily_fallback="bias", daily_fallback_time="08:00"),
    # regression check: must reproduce V0_base exactly
    "V2_v1compat":     dict(signal_start="07:00", signal_end="15:45", pending_cutoff="16:00", min_rr=1.0, bias_mode=None,
                            news_gate=None, daily_stop_losses=None, daily_stop_R=None, weekly_stop_R=None, monday_gap_gate=False,
                            stop_sanity_d1atr=None, target_cap_atr=None, partial_exit=False, trail_mult=None),
}

def hhmm(s): return E.hhmm(s)

def news_windows(start: dt.date, end: dt.date):
    """Approximate: NFP first Friday 08:30 ET +-3 min; FOMC statement 14:00 ET -5 / +45 min (unverified dates)."""
    wins = []
    d = dt.date(start.year, start.month, 1)
    while d <= end:
        ff = d + dt.timedelta(days=(4 - d.weekday()) % 7)
        off = 4 if E.us_dst_active(ff) else 5
        t = dt.datetime(ff.year, ff.month, ff.day, 8 + off, 30)
        wins.append((np.datetime64(t - dt.timedelta(minutes=3)), np.datetime64(t + dt.timedelta(minutes=3))))
        d = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    for s in E.FOMC_DATES_UNVERIFIED:
        fd = dt.date.fromisoformat(s)
        if start <= fd <= end:
            off = 4 if E.us_dst_active(fd) else 5
            t = dt.datetime(fd.year, fd.month, fd.day, 14 + off, 0)
            wins.append((np.datetime64(t - dt.timedelta(minutes=5)), np.datetime64(t + dt.timedelta(minutes=45))))
    wins.sort()
    return np.array([a for a, _ in wins]), np.array([b for _, b in wins])

def daily_frame(m1: pd.DataFrame):
    """Session-day bars (23:00 UTC -> 22:00 UTC), labelled by the calendar date on which the session ENDS."""
    d = m1.copy(); d.index = d.index + pd.Timedelta(hours=1)
    daily = d.resample("1D").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last")).dropna()
    daily["sma200"] = daily.close.rolling(200).mean()
    daily["mom"] = daily.close.shift(21) / daily.close.shift(252) - 1
    pc = daily.close.shift(1)
    tr = pd.concat([daily.high - daily.low, (daily.high - pc).abs(), (daily.low - pc).abs()], axis=1).max(axis=1)
    daily["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    daily.index = daily.index.date  # session-day key
    return daily

def run(cfg: dict, m1: pd.DataFrame, out_dir: pathlib.Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    m15 = m1.resample("15min", label="left", closed="left").agg(open=("open", "first"), high=("high", "max"),
                                                                 low=("low", "min"), close=("close", "last")).dropna()
    ind = E.indicators(m15, cfg)
    adx = ind.adx.values; thr = cfg["adx_threshold"]; L = cfg["adx_rising_lookback"]
    rising_recent = pd.Series((adx > thr) & (adx > np.roll(adx, 1))).rolling(L + 1, min_periods=1).max().values.astype(bool)
    armed = (adx > thr) & rising_recent
    long_dir = ind.pdi.values > ind.mdi.values
    touch = (ind.low.values <= ind.ema.values) & (ind.high.values >= ind.ema.values)
    hi, lo, cl, ema, atr = ind.high.values, ind.low.values, ind.close.values, ind.ema.values, ind.atr.values
    t15 = ind.index
    mod15 = (t15.hour * 60 + t15.minute).values
    # session-day key of each M15 bar (day on which the 23:00->22:00 session ends)
    skey = (t15 + pd.Timedelta(hours=1)).date
    daily = daily_frame(m1)
    dkeys = list(daily.index); dpos = {k: i for i, k in enumerate(dkeys)}
    sig_lo, sig_hi = hhmm(cfg["signal_start"]), hhmm(cfg["signal_end"])
    cutoff_min, texit_min = hhmm(cfg["pending_cutoff"]), hhmm(cfg["time_exit"])
    tb_lo, tb_hi = hhmm(cfg["trig_b_start"]), hhmm(cfg["trig_b_end"])
    fb_min = hhmm(cfg["daily_fallback_time"])
    spread, slip, comm = cfg["spread"], cfg["slippage"], cfg["commission_rt"]
    m1_t = m1.index.values; m1_o, m1_h, m1_l, m1_c = (m1[k].values for k in ("open", "high", "low", "close"))
    m1_mod = (m1.index.hour * 60 + m1.index.minute).values
    bar_start = np.searchsorted(m1_t, t15.values, side="left")
    bar_end = np.searchsorted(m1_t, (t15 + pd.Timedelta(minutes=15)).values, side="left")
    # Asian range per session day: M1 bars 23:00 (prev calendar day) -> 06:59 UTC
    m1_skey = (m1.index + pd.Timedelta(hours=1)).date
    asia_mask = (m1.index.hour >= 23) | (m1.index.hour < 7)
    asia = pd.DataFrame({"k": m1_skey[asia_mask], "h": m1_h[asia_mask], "l": m1_l[asia_mask]}).groupby("k").agg(h=("h", "max"), l=("l", "min"))
    asia_hi = asia.h.to_dict(); asia_lo = asia.l.to_dict()
    ns, ne = news_windows(t15[0].date(), t15[-1].date()) if cfg["news_gate"] else (np.array([]), np.array([]))
    def in_news(ts64):
        if len(ns) == 0: return False
        i = np.searchsorted(ns, ts64, side="right") - 1
        return i >= 0 and ts64 < ne[i]

    def prev_day(k):
        """Previous completed session-day row for session-day key k (bias, PDH/PDL, D1 ATR)."""
        i = dpos.get(k)
        if i is None or i == 0: return None
        return daily.iloc[i - 1]

    trades, skips = [], []
    pending = None; pos = None
    day_state = dict(key=None, closedR=0.0, consec_losses=0, entries=0, halted=False, gap_block_until=None)
    week_state = dict(key=None, closedR=0.0, halted=False)
    ambiguous = 0

    def log_skip(i, side, reason, **kw): skips.append(dict(signal_bar_open=t15[i], side=side, reason=reason, **kw))

    def bias_for(k):
        """Return (allowed_side or 'both' or None, size_mult)."""
        if cfg["bias_mode"] is None: return "both", 1.0
        pdy = prev_day(k)
        if pdy is None or np.isnan(pdy.sma200): return None, 0.0
        trend = "long" if pdy.close > pdy.sma200 else "short"
        if cfg["bias_mode"] == "sma200": return trend, 1.0
        if np.isnan(pdy.mom): return None, 0.0
        mom = "long" if pdy.mom > 0 else "short"
        return trend, (1.0 if mom == trend else cfg["bias_disagree_mult"])

    def book(rec):
        trades.append(rec)
        r = rec["realised_R_weighted"]
        day_state["closedR"] += r; week_state["closedR"] += r
        day_state["consec_losses"] = day_state["consec_losses"] + 1 if rec["realised_R"] <= 0 else 0
        if cfg["daily_stop_losses"] is not None and day_state["consec_losses"] >= cfg["daily_stop_losses"]: day_state["halted"] = True
        if cfg["daily_stop_R"] is not None and day_state["closedR"] <= cfg["daily_stop_R"]: day_state["halted"] = True
        if cfg["weekly_stop_R"] is not None and week_state["closedR"] <= cfg["weekly_stop_R"]: week_state["halted"] = True

    def close_out(p, t, px, reason):
        """Close the remaining quantity; compute realised R including any partial."""
        sign = 1.0 if p["side"] == "long" else -1.0
        risk = abs(p["level"] - p["initial_stop"])
        if p["t1_filled"]:
            pnl = sign * (cfg["partial_frac"] * (p["t1_price"] - p["entry_price"]) + (1 - cfg["partial_frac"]) * (px - p["entry_price"])) - comm
        else:
            pnl = sign * (px - p["entry_price"]) - comm
        rec = dict(p); rec.update(exit_time=t, exit_price=px, exit_reason=reason, planned_risk=risk, pnl_per_oz=pnl,
                                  realised_R=pnl / risk, realised_R_weighted=pnl / risk * p["size_mult"])
        for k in ("hh", "ll"): rec.pop(k, None)
        book(rec)

    for i in range(cfg["warmup_bars"], len(ind)):
        k = skey[i]
        if k != day_state["key"]:
            # new session day: reset daily state; Monday gap gate
            day_state.update(key=k, closedR=0.0, consec_losses=0, entries=0, halted=False, gap_block_until=None)
            wk = pd.Timestamp(k).isocalendar()[:2]
            if wk != week_state["key"]: week_state.update(key=wk, closedR=0.0, halted=False)
            if cfg["monday_gap_gate"] and pd.Timestamp(k).dayofweek == 0:
                pdy = prev_day(k)
                if pdy is not None and not np.isnan(pdy.atr14) and dpos.get(k) is not None:
                    gap = abs(daily.iloc[dpos[k]].open - pdy.close)
                    if gap > pdy.atr14: day_state["gap_block_until"] = 8 * 60
        # ---- 1) simulate M1 bars of bar i against standing orders
        if pending is not None or pos is not None:
            run_low, run_high = np.inf, -np.inf
            for j in range(bar_start[i], bar_end[i]):
                bo, bh, bl, mod = m1_o[j], m1_h[j], m1_l[j], m1_mod[j]
                ao, ah, al = bo + spread, bh + spread, bl + spread
                run_low, run_high = min(run_low, bl), max(run_high, bh)
                if pos is not None:
                    side = pos["side"]
                    if mod >= texit_min:
                        close_out(pos, m1_t[j], bo - slip if side == "long" else ao + slip, "time_exit"); pos = None; continue
                    if side == "long":
                        hit_stop = bl <= pos["stop"]; hit_tgt = (not pos["t1_filled"]) and bh > pos["target"]
                        stop_px = min(pos["stop"], bo) - slip
                    else:
                        hit_stop = ah >= pos["stop"]; hit_tgt = (not pos["t1_filled"]) and al < pos["target"]
                        stop_px = max(pos["stop"], ao) + slip
                    if hit_stop and hit_tgt:
                        ambiguous += 1; pos["ambiguous"] = True
                        if cfg["ambiguity"] == "stop_first": hit_tgt = False
                        else: hit_stop = False
                    if hit_stop:
                        reason = "stop" if not pos["t1_filled"] else ("trail_stop" if pos["stop"] != pos["be_stop"] else "breakeven_stop")
                        close_out(pos, m1_t[j], stop_px, reason); pos = None; continue
                    if hit_tgt:
                        if cfg["partial_exit"]:
                            pos["t1_filled"] = True; pos["t1_price"] = pos["target"]; pos["t1_time"] = m1_t[j]
                            be = pos["entry_price"] + cfg["be_offset"] if side == "long" else pos["entry_price"] - cfg["be_offset"]
                            pos["be_stop"] = be; pos["stop"] = be if (side == "long" and be > pos["stop"]) or (side == "short" and be < pos["stop"]) else pos["stop"]
                        else:
                            close_out(pos, m1_t[j], pos["target"], "target"); pos = None; continue
                    # trail on the remainder (Chandelier on running extreme, ratchet only, not beyond current bar's extreme)
                    if pos is not None and pos["t1_filled"] and cfg["trail_mult"] is not None:
                        pos["hh"] = max(pos["hh"], bh); pos["ll"] = min(pos["ll"], bl)
                        if side == "long":
                            new = pos["hh"] - cfg["trail_mult"] * atr[i - 1]  # ATR of the last CLOSED M15 bar (no look-ahead)
                            if new > pos["stop"] and new < bl: pos["stop"] = new
                        else:
                            new = pos["ll"] + cfg["trail_mult"] * atr[i - 1]
                            if new < pos["stop"] and new > ah: pos["stop"] = new
                elif pending is not None:
                    if mod >= cutoff_min:
                        log_skip(pending["first_idx"], pending["side"], "CANCEL_cutoff_time", trig=pending["trig"]); pending = None; continue
                    if cfg["news_gate"] and in_news(m1_t[j]):
                        log_skip(pending["first_idx"], pending["side"], "CANCEL_news_window", trig=pending["trig"]); pending = None; continue
                    if pending["side"] == "long" and ah >= pending["level"]:
                        fill = max(pending["level"], ao) + slip
                        stop = (min(pending["seq_low"], run_low) - pending["buffer"]) if pending["trig"] == "A" else pending["fixed_stop"]
                        pos = open_pos(pending, m1_t[j], fill, stop); day_state["entries"] += 1; pending = None
                        if bl <= stop: close_out(pos, m1_t[j], (min(stop, bl) - slip if bl < stop else stop - slip), "stop_same_minute"); pos = None
                        continue
                    if pending["side"] == "short" and bl <= pending["level"]:
                        fill = min(pending["level"], bo) - slip
                        stop = (max(pending["seq_high"], run_high) + pending["buffer"]) if pending["trig"] == "A" else pending["fixed_stop"]
                        pos = open_pos(pending, m1_t[j], fill, stop); day_state["entries"] += 1; pending = None
                        if ah >= stop: close_out(pos, m1_t[j], stop + slip, "stop_same_minute"); pos = None
                        continue
        # ---- 2) decisions at the close of bar i
        if np.isnan(adx[i]) or np.isnan(atr[i]): continue
        mod_i = mod15[i]
        close_ts = (t15[i] + pd.Timedelta(minutes=15)).to_datetime64()
        in_window = sig_lo <= mod_i <= sig_hi
        # pending management (Trigger A only re-arms)
        if pending is not None:
            side = pending["side"]
            if pending["trig"] == "A":
                deep = (cl[i] < ema[i] - cfg["deep_break_atr"] * atr[i]) if side == "long" else (cl[i] > ema[i] + cfg["deep_break_atr"] * atr[i])
                if deep: log_skip(pending["first_idx"], side, "CANCEL_deep_break", trig="A"); pending = None
                elif adx[i] < cfg["adx_cancel_below"]: log_skip(pending["first_idx"], side, "CANCEL_adx_fell", trig="A"); pending = None
                elif i >= pending["last_touch_idx"] + cfg["expiry_bars"]: log_skip(pending["first_idx"], side, "EXPIRED_unfilled", trig="A"); pending = None
                else:
                    pending["seq_low"] = min(pending["seq_low"], lo[i]); pending["seq_high"] = max(pending["seq_high"], hi[i])
                conf_ok = (not cfg["confirm_close"]) or (cl[i] >= ema[i] if side == "long" else cl[i] <= ema[i])
                if pending is not None and cfg["rearm"] and armed[i] and touch[i] and ((side == "long") == bool(long_dir[i])) and in_window and conf_ok:
                    if side == "long":
                        pending["level"] = hi[i] + cfg["entry_offset"]; pending["seq_low"] = min(pending["seq_low"], lo[i])
                        stop_est = pending["seq_low"] - pending["buffer"]; rr = (pending["target"] - pending["level"]) / (pending["level"] - stop_est)
                    else:
                        pending["level"] = lo[i] - cfg["entry_offset"]; pending["seq_high"] = max(pending["seq_high"], hi[i])
                        stop_est = pending["seq_high"] + pending["buffer"]; rr = (pending["level"] - pending["target"]) / (stop_est - pending["level"])
                    pending["last_touch_idx"] = i; pending["last_touch_open"] = t15[i]; pending["rearms"] += 1; pending["rr_at_placement"] = rr
                    if rr < cfg["min_rr"]: log_skip(pending["first_idx"], side, "CANCEL_rr_too_low_after_rearm", rr=rr, trig="A"); pending = None
            else:
                if i >= pending["last_touch_idx"] + cfg["trig_b_valid_bars"]: log_skip(pending["first_idx"], side, "EXPIRED_unfilled", trig="B"); pending = None
        if pending is not None or pos is not None or not in_window: continue
        # L0 gates
        if day_state["halted"] or week_state["halted"]:
            if armed[i] and touch[i]: log_skip(i, "long" if long_dir[i] else "short", "WAIT_daily_or_weekly_stop")
            continue
        if day_state["gap_block_until"] is not None and mod_i < day_state["gap_block_until"]:
            if armed[i] and touch[i]: log_skip(i, "long" if long_dir[i] else "short", "WAIT_monday_gap")
            continue
        if day_state["entries"] >= cfg["max_trades_per_day"]:
            if armed[i] and touch[i]: log_skip(i, "long" if long_dir[i] else "short", "WAIT_daily_cap")
            continue
        allowed, mult = bias_for(k)
        pdy = prev_day(k)
        d1atr = pdy.atr14 if pdy is not None else np.nan
        pdh = pdy.high if pdy is not None else np.nan; pdl = pdy.low if pdy is not None else np.nan
        buffer = max(cfg["stop_buffer_min"], cfg["stop_buffer_atr"] * atr[i])
        # ---- Trigger A
        if cfg["trigger_a"] and armed[i] and touch[i]:
            side = "long" if long_dir[i] else "short"
            if cfg["confirm_close"] and ((side == "long" and cl[i] < ema[i]) or (side == "short" and cl[i] > ema[i])):
                log_skip(i, side, "WAIT_no_close_confirmation"); continue
            if allowed is None: log_skip(i, side, "WAIT_bias_undefined"); continue
            if allowed != "both" and allowed != side: log_skip(i, side, "WAIT_bias_direction", bias=allowed); continue
            if cfg["news_gate"] and in_news(close_ts): log_skip(i, side, "WAIT_news_window"); continue
            w0 = max(0, i - cfg["target_lookback"] + 1)
            if side == "long":
                level = hi[i] + cfg["entry_offset"]; target = hi[w0:i + 1].max(); stop_est = lo[i] - buffer
                if cfg["target_cap_atr"] is not None and not np.isnan(pdh) and target > pdh + cfg["target_cap_atr"] * atr[i] and pdh > level: target = pdh
                rr = (target - level) / (level - stop_est)
            else:
                level = lo[i] - cfg["entry_offset"]; target = lo[w0:i + 1].min(); stop_est = hi[i] + buffer
                if cfg["target_cap_atr"] is not None and not np.isnan(pdl) and target < pdl - cfg["target_cap_atr"] * atr[i] and pdl < level: target = pdl
                rr = (level - target) / (stop_est - level)
            if cfg["stop_sanity_d1atr"] is not None and not np.isnan(d1atr) and abs(level - stop_est) > cfg["stop_sanity_d1atr"] * d1atr:
                log_skip(i, side, "WAIT_stop_too_wide", trig="A"); continue
            if rr < cfg["min_rr"]: log_skip(i, side, "WAIT_rr_too_low", rr=rr, trig="A"); continue
            pending = dict(trig="A", side=side, level=level, target=target, buffer=buffer, first_idx=i, last_touch_idx=i, last_touch_open=t15[i],
                           seq_low=lo[i], seq_high=hi[i], signal_bar_open=t15[i], adx=adx[i], atr=atr[i], ema=ema[i], rr_at_placement=rr, rearms=0,
                           session="London" if mod_i < 12 * 60 else "NewYork", size_mult=mult, bias=allowed, fixed_stop=None)
            continue
        # ---- Trigger B (Asian range breakout)
        if cfg["trigger_b"] and tb_lo <= mod_i <= tb_hi and adx[i] > cfg["trig_b_adx"] and k in asia_hi:
            ah_, al_ = asia_hi[k], asia_lo[k]; rng = ah_ - al_
            side = None
            if cl[i] > ah_ and (hi[i - 1] <= ah_ or True) and (allowed in ("both", "long")): side = "long"
            elif cl[i] < al_ and (allowed in ("both", "short")): side = "short"
            if side is None or rng <= 0: continue
            if cfg["news_gate"] and in_news(close_ts): log_skip(i, side, "WAIT_news_window", trig="B"); continue
            if side == "long":
                level = hi[i] + cfg["entry_offset"]; stop = max(al_ - buffer, level - cfg["trig_b_stop_cap_atr"] * atr[i]); target = level + rng
            else:
                level = lo[i] - cfg["entry_offset"]; stop = min(ah_ + buffer, level + cfg["trig_b_stop_cap_atr"] * atr[i]); target = level - rng
            rr = abs(target - level) / abs(level - stop)
            if cfg["stop_sanity_d1atr"] is not None and not np.isnan(d1atr) and abs(level - stop) > cfg["stop_sanity_d1atr"] * d1atr:
                log_skip(i, side, "WAIT_stop_too_wide", trig="B"); continue
            if rr < cfg["min_rr"]: log_skip(i, side, "WAIT_rr_too_low", rr=rr, trig="B"); continue
            pending = dict(trig="B", side=side, level=level, target=target, buffer=buffer, first_idx=i, last_touch_idx=i, last_touch_open=t15[i],
                           seq_low=lo[i], seq_high=hi[i], signal_bar_open=t15[i], adx=adx[i], atr=atr[i], ema=ema[i], rr_at_placement=rr, rearms=0,
                           session="London" if mod_i < 12 * 60 else "NewYork", size_mult=mult, bias=allowed, fixed_stop=stop)
        # ---- Trigger C ("one trade every day"): no entry yet today by the fallback bar -> market order next minute
        if cfg["daily_fallback"] and mod_i == fb_min and day_state["entries"] == 0:
            if cfg["daily_fallback"] == "bias":
                if allowed is None: log_skip(i, "none", "WAIT_bias_undefined", trig="C"); continue
                if allowed == "both": side = "long" if long_dir[i] else "short"
                else: side = allowed
            else:
                side = "long" if long_dir[i] else "short"
                if allowed is None: log_skip(i, side, "WAIT_bias_undefined", trig="C"); continue
                if allowed != "both" and allowed != side: log_skip(i, side, "WAIT_bias_direction", bias=allowed, trig="C"); continue
            if cfg["news_gate"] and in_news(close_ts): log_skip(i, side, "WAIT_news_window", trig="C"); continue
            dist = cfg["fallback_stop_atr"] * atr[i]
            if side == "long":
                level = -np.inf; stop = cl[i] - dist; target = cl[i] + cfg["min_rr"] * dist
            else:
                level = np.inf; stop = cl[i] + dist; target = cl[i] - cfg["min_rr"] * dist
            if cfg["stop_sanity_d1atr"] is not None and not np.isnan(d1atr) and dist > cfg["stop_sanity_d1atr"] * d1atr:
                log_skip(i, side, "WAIT_stop_too_wide", trig="C"); continue
            pending = dict(trig="C", side=side, level=level, target=target, buffer=buffer, first_idx=i, last_touch_idx=i, last_touch_open=t15[i],
                           seq_low=lo[i], seq_high=hi[i], signal_bar_open=t15[i], adx=adx[i], atr=atr[i], ema=ema[i], rr_at_placement=cfg["min_rr"], rearms=0,
                           session="London" if mod_i < 12 * 60 else "NewYork", size_mult=mult, bias=allowed, fixed_stop=stop)
    tr = pd.DataFrame(trades)
    if len(tr):
        tr["hold_minutes"] = (pd.to_datetime(tr.exit_time) - pd.to_datetime(tr.entry_time)).dt.total_seconds() / 60
        tr["signal_date"] = pd.to_datetime(tr.signal_bar_open).dt.date
    tr.to_csv(out_dir / "trades.csv", index=False)
    pd.DataFrame(skips).to_csv(out_dir / "skips.csv", index=False)
    meta = dict(config=cfg, n_trades=int(len(tr)), n_skips=len(skips), ambiguous_bars=ambiguous, m15_bars=int(len(ind)), m1_bars=int(len(m1)),
                data_start=str(m1.index[0]), data_end=str(m1.index[-1]), run_time_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    (out_dir / "config.json").write_text(json.dumps(meta, indent=2, default=str))
    return tr, pd.DataFrame(skips), meta

def open_pos(p, t, fill, stop):
    level = fill if p["trig"] == "C" else p["level"]   # market order: planned risk is measured from the fill
    return dict(trig=p["trig"], side=p["side"], signal_bar_open=p["signal_bar_open"], last_touch_open=p["last_touch_open"], session=p["session"],
                bias=p["bias"], size_mult=p["size_mult"], level=level, target=p["target"], entry_time=t, entry_price=fill,
                stop=stop, initial_stop=stop, be_stop=None, t1_filled=False, t1_price=np.nan, t1_time=pd.NaT, hh=fill, ll=fill,
                adx_at_signal=p["adx"], atr_at_signal=p["atr"], ema_at_signal=p["ema"], rr_at_placement=p["rr_at_placement"], rearms=p["rearms"], ambiguous=False)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--variant"); ap.add_argument("--all", action="store_true"); ap.add_argument("--check", action="store_true")
    ap.add_argument("--data", default=str(E.DATA))
    a = ap.parse_args()
    m1 = pd.read_parquet(a.data)
    if a.check:
        cfg = dict(V2_CONFIG); cfg.update(VARIANTS["V2_v1compat"]); cfg["variant"] = "V2_v1compat"
        tr, sk, meta = run(cfg, m1, RESULTS / "V2_v1compat")
        v0 = pd.read_csv(RESULTS / "V0_base" / "trades.csv")
        same_n = len(tr) == len(v0)
        same = same_n and np.allclose(tr.realised_R.values, v0.realised_R.values) and (pd.to_datetime(tr.entry_time).values == pd.to_datetime(v0.entry_time).values).all()
        print(f"v1-compat check: v2 trades={len(tr)} v0 trades={len(v0)} identical={same}")
        if not same: raise SystemExit(1)
        return
    names = list(VARIANTS) if a.all else [a.variant or "V2_0"]
    for name in names:
        cfg = dict(V2_CONFIG); cfg.update(VARIANTS[name]); cfg["variant"] = name
        tr, sk, meta = run(cfg, m1, RESULTS / name)
        extra = f" meanR={tr.realised_R.mean():.3f} meanRw={tr.realised_R_weighted.mean():.3f} totalRw={tr.realised_R_weighted.sum():+.1f}" if len(tr) else ""
        print(f"{name}: trades={len(tr)} skips={len(sk)} ambiguous={meta['ambiguous_bars']}{extra}")

if __name__ == "__main__":
    main()
