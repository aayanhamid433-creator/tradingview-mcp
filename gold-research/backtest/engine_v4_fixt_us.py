#!/usr/bin/env python3
"""engine_v4_fixt_us.py — F7 FIXT_US: fixed-time continuation of the first US hour(s) on XAUUSD M1.

Specification: results/PREREGISTRATION_v4.md §0 (shared conventions) and §F7 (rules, params, variants), frozen
2026-11-12 before any v4 run. Nothing here may be re-tuned after a result has been seen. The net move of a 13:30-anchored
window of W closed M15 bars sets the direction; market entry at the window's end; stop at the window's opposite extreme,
D1ATR-floored/capped, never moved; no target (FIXT_US_15M: 1.0 x the 13:30 bar range and a 15-minute maximum hold);
20:50 time exit. One attempt per session day.

Shared mechanics, COPIED from backtest/engine_v3.py (which copies engine.py / engine_v2.py):
  * data: pd.read_parquet(data/xauusd_m1_utc.parquet), BID M1 bars, tz-aware index labelled UTC (PROFILE_v4_dev §0: the
    clock behaves as London local time; NO conversion anywhere; every time below is on this clock);
  * costs E.BASE_CONFIG: spread 0.25 (ask = bid + spread), slippage 0.05 per fill, commission 0;
  * M15 = m1.resample("15min", label="left", closed="left") OHLC dropna; E.indicators (ATR14 = Wilder RMA of the true
    range; ADX computed for parity, unused); warmup 200 M15 bars;
  * session key k = (t + 1h).date for every bar (m1_day / skey / m15_day); daily = engine_v2.daily_frame(m1); pdy = the
    daily row before k (prev_day); D1ATR = pdy.atr14 (previous session day only, never the current one);
  * decisions only at the close of a closed M15 bar i, after bar i's M1 bars have been simulated; the order acts on the
    M1 bars of bar i+1 onward (the first simulated M1 bar for a market order);
  * market fill: long = bid open + spread + slippage, short = bid open - slippage, on the first simulated M1 bar;
  * gap rule: a fill already at/beyond the order's own stop or target is not taken (SKIP_gap_fill_past_stop / _target);
  * same-minute stop: long, fill bar's bid low <= stop -> closed at (bid low - slip if bid low < stop else stop - slip);
    short, ask high >= stop -> stop + slip; reason stop_same_minute;
  * open position, per M1 bar, in this order: (1) session_gap_exit when the bar's session key differs from the position's
    (long bid open - slip / short ask open + slip); (2) time_exit at the first bar with minute-of-day >= 20:50 (same
    prices); (3) stop: long bid low <= stop -> min(stop, bid open) - slip; short ask high >= stop -> max(stop, ask open)
    + slip; target on a strict trade-through (long bid high > target; short ask low < target) filled at the target; stop
    first when both print in one minute (ambiguous flag, counter); (4) max_hold (only where set): bar_time - entry_time
    >= max_hold_minutes - 1 min -> closed at that bar's close (timestamp + 1 min) at bid close - slip (long) / bid close +
    spread + slip (short), reason max_hold;
  * no rounding of any level; planned_risk = |fill - stop| (market order: measured from the fill); pnl_per_oz =
    sign x (exit - fill) - commission; realised_R = pnl_per_oz / planned_risk; end_of_data close of an open position at
    the last bar (flagged, counted; cannot happen here: the data ends on a Friday after 20:50).

F7 rules (frozen; PREREGISTRATION_v4 §F7):
  WINDOW: the W consecutive M15 bars whose open times are 13:30 + 15n, n = 0..W-1 (minute-of-day 810 + 15n), all with the
  current session key. The decision fires at the close of the bar with minute-of-day 810 + 15(W-1) (W=4: the 14:15 bar,
  decision 14:30; W=8: the 15:15 bar, decision 15:30; W=1: the 13:30 bar, decision 13:45); the day is then DONE whatever
  follows (one attempt per session day).
  SKIPS: any window bar missing / non-consecutive / of another session day -> SKIP_window_bars_missing; pdy missing or
  D1ATR NaN or ATR14(M15) of the last window bar NaN -> SKIP_atr_undefined.
  DECISION: move = close(last window bar) - open(first window bar); gate |move| >= gate_move_atr x ATR14(M15, last window
  bar) else SKIP_gate_small_move; long if move > 0, short if move < 0.
  ENTRY: pending kind "market", filled at the open of the first M1 bar at/after the decision time (long bid open + 0.25 +
  0.05; short bid open - 0.05); if that bar opens more than entry_tolerance_min (5) minutes after the decision time ->
  SKIP_late_open.
  STOP: raw_stop = min(bid lows of the window bars) - stop_buffer (long) / max(bid highs) + stop_buffer (short), at the
  decision. At the fill minute: (i) gap rule against raw_stop (long fill <= raw_stop / short fill >= raw_stop ->
  SKIP_gap_fill_past_stop); (ii) dist = min(max(|fill - raw_stop|, stop_floor_d1atr x D1ATR), stop_cap_d1atr x D1ATR);
  final stop = fill - dist (long) / fill + dist (short), never moved; (iii) same-minute stop check against the final
  stop; planned_risk = dist.
  TARGET: none (1H / 2H); 15M: fill +/- target_mult x (high - low of the 13:30 bar), strict trade-through.
  EXIT: stop; time_exit at the first M1 bar with minute-of-day >= 20:50; session_gap_exit; 15M additionally
  max_hold_minutes = 15 (engine_v3 definition). No trailing, partial, re-entry or news gate.
  BOOKKEEPING: signal_time = decision bar close, signal_bar_open = the decision (last window) bar's open; periods by
  signal_bar_open; hold_minutes < 3 flagged (hold_lt3; account rule: their profit is deducted).

Judgement calls (literal readings, stated here and in the run report):
  * A session day whose decision bar (minute-of-day 810 + 15(W-1)) does not exist in the M15 series (feed gap, early
    close, one-hour Sunday stub session) has no M15 close at which the decision could fire. Such a day is logged as
    SKIP_window_bars_missing with detail "decision_bar_absent" at the next session detection (or at the end of the data),
    signal_time = the day's nominal decision time, so that every session day after the warmup has exactly one trade or
    skip row. (Feb-Jul 2023 has 58 days with a 14:00-15:00 feed gap: the 14:15 decision bar of FIXT_US_1H is absent.)
  * SKIP_late_open is tested before the session-change cancel: a feed gap that runs past the next session start is a
    late open too (> 5 minutes), so CANCEL_session_ended is unreachable and kept only for parity with engine_v3.
  * The gap rule uses raw_stop (as specified); the final stop lies between the fill and raw_stop or at a D1ATR distance,
    so a fill can never be beyond its final stop. For 15M the target is defined from the fill, so
    SKIP_gap_fill_past_target can fire only when the 13:30 bar range is zero (never in this data).
  * move == 0 cannot pass the gate (|0| >= gate x ATR only if ATR == 0); it is logged as SKIP_gate_small_move.
  * The ATR14 gate uses the ATR of the last window bar (bar i, closed at the decision), i.e. E.indicators' Wilder ATR
    including bar i's own true range; D1ATR is pdy.atr14 of the previous session day.
  * trades_per_session_day in config.json divides by len(daily) (every session-day key in the data, including the
    one-hour Sunday stubs), as engine_v4_rsi2_m15 does; n_session_days_after_warmup is given alongside.
  * --perturb runs in memory and writes only perturb.json; the base trades.csv is never touched. Its rows for the
    pre-registered "+-1 M15 bar shift of the window" robustness check carry mult = null and check = "window_shift":
    W-1 / W+1 bars anchored at 13:30 (decision one bar earlier / later) and the W-bar window anchored at 13:15 / 13:45.
  * --max-hold N writes to results/V4_<ID>_h<N>/ so that the registered run is never overwritten.

Usage:
  python3 engine_v4_fixt_us.py --variant FIXT_US_1H           # -> results/V4_FIXT_US_1H/{trades,skips}.csv, config.json
  python3 engine_v4_fixt_us.py --all [--jobs 2]               # all three variants, at most 2 processes
  python3 engine_v4_fixt_us.py --perturb FIXT_US_1H           # -> results/V4_FIXT_US_1H/perturb.json (trades.csv untouched)
  python3 engine_v4_fixt_us.py --variant FIXT_US_1H --max-hold 15   # feasibility check -> results/V4_FIXT_US_1H_h15/
  python3 engine_v4_fixt_us.py --stats FIXT_US_1H             # period metrics via analyze.metrics / analyze.PERIODS (print only)
"""
import argparse, json, pathlib, datetime as dt, time, math
import numpy as np, pandas as pd
import engine as E
import engine_v2 as V2

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
FAMILY = "FIXT_US"
PREFIX = "V4_"

V4_CONFIG = dict(E.BASE_CONFIG)
for _k in ("adx_threshold", "adx_rising_lookback", "adx_cancel_below", "entry_offset", "stop_buffer_min", "stop_buffer_atr",
           "deep_break_atr", "target_lookback", "min_rr", "rearm", "expiry_bars", "pending_cutoff", "signal_start", "signal_end",
           "max_trades_per_day", "news_filter", "news_window_min"):
    V4_CONFIG.pop(_k, None)   # v1 pullback parameters are not used by this family
V4_CONFIG.update(dict(
    version="v4.0-fixt_us", family=FAMILY,
    window_start="13:30",        # [fixed] open time of the first window bar
    window_bars=4,               # W [integer, structural, not perturbed; +-1 bar shift reported as a robustness check]
    gate_move_atr=0.5,           # |move| >= gate_move_atr x ATR14(M15, last window bar)     [numeric]
    stop_buffer=0.10,            # USD beyond the window's opposite extreme                   [numeric]
    stop_floor_d1atr=0.25,       # stop distance floor in previous-session-day ATR14          [numeric]
    stop_cap_d1atr=0.60,         # stop distance cap in previous-session-day ATR14            [numeric]
    target_mult=None,            # 15M only: target = fill +/- target_mult x (13:30 bar range) [numeric]
    max_hold_minutes=None,       # 15M only: engine_v3 definition                             [numeric, integer]
    time_exit="20:50", entry_tolerance_min=5, warmup_bars=200, one_trade_per_day=True,
))

# ---- PRE-REGISTERED VARIANT LIST (PREREGISTRATION_v4.md §F7, frozen 2026-11-12) ----
VARIANTS = {
    "FIXT_US_1H":  dict(window_bars=4, gate_move_atr=0.5, stop_buffer=0.10, stop_floor_d1atr=0.25, stop_cap_d1atr=0.60, target_mult=None, max_hold_minutes=None),
    "FIXT_US_2H":  dict(window_bars=8, gate_move_atr=0.5, stop_buffer=0.10, stop_floor_d1atr=0.25, stop_cap_d1atr=0.60, target_mult=None, max_hold_minutes=None),
    "FIXT_US_15M": dict(window_bars=1, gate_move_atr=0.3, stop_buffer=0.10, stop_floor_d1atr=0.10, stop_cap_d1atr=0.60, target_mult=1.0, max_hold_minutes=15),
}
NUMERIC_PARAMS = ("gate_move_atr", "stop_buffer", "stop_floor_d1atr", "stop_cap_d1atr", "target_mult", "max_hold_minutes")
INTEGER_PARAMS = ("max_hold_minutes",)
PERTURB_MULTS = (0.8, 1.2)
PERIODS = {"development": ("2021-01-04", "2024-07-01"), "validation": ("2024-07-01", "2025-09-01"),
           "final_test": ("2025-09-01", "2026-11-01")}   # by signal_bar_open; identical to analyze.PERIODS

hhmm = E.hhmm
ONE_MIN = np.timedelta64(1, "m")


def run(cfg: dict, m1: pd.DataFrame, out_dir):
    """Run one configuration. out_dir None -> nothing is written (used by --perturb)."""
    t0 = time.time()
    if out_dir is not None: out_dir.mkdir(parents=True, exist_ok=True)
    fam = cfg["family"]
    m15 = m1.resample("15min", label="left", closed="left").agg(open=("open", "first"), high=("high", "max"),
                                                                 low=("low", "min"), close=("close", "last")).dropna()
    ind = E.indicators(m15, cfg)
    op, hi, lo, cl, atr = ind.open.values, ind.high.values, ind.low.values, ind.close.values, ind.atr.values
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
    # F7 parameters
    W = int(cfg["window_bars"]); ws = hhmm(cfg["window_start"]); dec_mod = ws + 15 * (W - 1)
    if W < 1 or dec_mod >= 24 * 60: raise ValueError(f"window_bars={W} / window_start={cfg['window_start']} out of range")
    tol_td = np.timedelta64(int(cfg["entry_tolerance_min"]), "m")
    gate_k, buf = float(cfg["gate_move_atr"]), float(cfg["stop_buffer"])
    floor_k, cap_k = float(cfg["stop_floor_d1atr"]), float(cfg["stop_cap_d1atr"])
    tgt_mult = None if cfg["target_mult"] is None else float(cfg["target_mult"])

    def prev_day(k):
        i = dpos.get(k)
        return None if i is None or i == 0 else daily.iloc[i - 1]

    def nominal_times(k):
        """Nominal decision bar open / close of session day k (calendar date k, the window lies before 23:00)."""
        base = pd.Timestamp(k).tz_localize("UTC")
        return base + pd.Timedelta(minutes=dec_mod), base + pd.Timedelta(minutes=dec_mod + 15)

    trades, skips = [], []
    pending = None; pos = None
    day = dict(key=None, entries=0, done=False, pdy=None)
    counters = dict(ambiguous_stop_target=0, both_sides_same_minute=0, same_minute_stop=0, gap_fill_skipped=0,
                    late_open_skipped=0, session_ended_cancelled=0, decisions=0, decision_bar_absent=0,
                    window_bars_missing=0, atr_undefined=0, gate_small_move=0, position_open_at_decision=0,
                    signals_long=0, signals_short=0, stop_floored=0, stop_capped=0, days_after_warmup=0)

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

    def fill_entry(side, j, raw_stop, d1atr, meta):
        """engine_v3.fill_entry for a market order (level None), with the F7 stop built at the fill: (i) gap rule against
        raw_stop; (ii) dist = min(max(|fill - raw_stop|, floor x D1ATR), cap x D1ATR), final stop = fill -/+ dist;
        (iii) same-minute stop check against the final stop. planned_risk = dist (= |fill - stop|)."""
        nonlocal pos
        bo, bh, bl = m1_o[j], m1_h[j], m1_l[j]; ao, ah = bo + spread, bh + spread
        fill = (ao + slip) if side == "long" else (bo - slip)
        past_stop = (fill <= raw_stop) if side == "long" else (fill >= raw_stop)
        if past_stop:   # the first print after a gap is already beyond the planned stop: the order is not taken
            counters["gap_fill_skipped"] += 1
            log_skip(meta["signal_time"], side, "SKIP_gap_fill_past_stop", signal_bar_open=meta["signal_bar_open"], fill=fill, stop=raw_stop,
                     fill_time=m1_t[j]); return
        raw_dist = abs(fill - raw_stop)
        floor_d, cap_d = floor_k * d1atr, cap_k * d1atr
        dist = min(max(raw_dist, floor_d), cap_d)
        stop = fill - dist if side == "long" else fill + dist
        target = None
        if tgt_mult is not None:
            target = fill + tgt_mult * meta["range_first_bar"] if side == "long" else fill - tgt_mult * meta["range_first_bar"]
            past_tgt = (fill >= target) if side == "long" else (fill <= target)
            if past_tgt:
                counters["gap_fill_skipped"] += 1
                log_skip(meta["signal_time"], side, "SKIP_gap_fill_past_target", signal_bar_open=meta["signal_bar_open"], fill=fill, stop=stop,
                         target=target, fill_time=m1_t[j]); return
        floored, capped = raw_dist < floor_d, raw_dist > cap_d
        counters["stop_floored"] += int(floored); counters["stop_capped"] += int(capped)
        meta.update(raw_stop_dist=raw_dist, stop_dist=dist, stop_floored=floored, stop_capped=capped,
                    fill_lag_min=float((m1_t[j] - meta["decision_time"]) / ONE_MIN))
        pos = open_pos(side, m1_t[j], fill, fill, stop, target, meta); day["entries"] += 1
        if side == "long":
            if bl <= stop:
                counters["same_minute_stop"] += 1
                close_pos(pos, m1_t[j], (min(stop, bl) - slip if bl < stop else stop - slip), "stop_same_minute"); pos = None
        else:
            if ah >= stop:
                counters["same_minute_stop"] += 1
                close_pos(pos, m1_t[j], stop + slip, "stop_same_minute"); pos = None

    def close_day_without_decision(k):
        """Judgement call: the decision bar of session day k never existed -> one SKIP_window_bars_missing row for the day."""
        counters["decision_bar_absent"] += 1; counters["window_bars_missing"] += 1
        nom_open, nom_close = nominal_times(k)
        log_skip(nom_close, "both", "SKIP_window_bars_missing", signal_bar_open=nom_open, detail="decision_bar_absent")

    for i in range(cfg["warmup_bars"], len(ind)):
        k = skey[i]
        if k != day["key"]:
            # ---- new session day (23:00): close the book on the previous day, reset per-day state; daily quantities are
            # previous-session-day values
            if day["key"] is not None and not day["done"]: close_day_without_decision(day["key"])
            day.update(key=k, entries=0, done=False, pdy=prev_day(k)); counters["days_after_warmup"] += 1
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
                    side = pending["side"]; meta = pending["meta"]
                    lag = m1_t[j] - meta["decision_time"]
                    if lag > tol_td:   # F7: the first M1 bar at/after the decision time opens > entry_tolerance_min late (feed gap)
                        counters["late_open_skipped"] += 1
                        log_skip(meta["signal_time"], side, "SKIP_late_open", signal_bar_open=meta["signal_bar_open"], fill_time=m1_t[j],
                                 lag_min=float(lag / ONE_MIN)); pending = None; continue
                    if m1_day[j] != pending["day"]:   # unreachable (a session change is always > 5 min late); kept for parity with engine_v3
                        counters["session_ended_cancelled"] += 1
                        log_skip(meta["signal_time"], side, "CANCEL_session_ended", signal_bar_open=meta["signal_bar_open"], fill_time=m1_t[j]); pending = None; continue
                    pending = None
                    fill_entry(side, j, meta["raw_stop"], meta["d1atr"], meta)
                    continue
        # ---- 2) decision at the close of bar i (bar i is closed; bar i+1 has not started)
        if mod15[i] != dec_mod or day["done"]: continue
        day["done"] = True   # one attempt per session day, whatever follows
        counters["decisions"] += 1
        close_ts = t15[i] + pd.Timedelta(minutes=15)
        if pos is not None or pending is not None:   # cannot happen (the previous day's position/order is resolved before this bar); diagnostic
            counters["position_open_at_decision"] += 1
            log_skip(close_ts, "both", "SKIP_position_open", signal_bar_open=t15[i]); continue
        idx = list(range(i - W + 1, i + 1))
        if idx[0] < 0 or any(skey[q] != k or mod15[q] != ws + 15 * n for n, q in enumerate(idx)):
            counters["window_bars_missing"] += 1
            log_skip(close_ts, "both", "SKIP_window_bars_missing", signal_bar_open=t15[i], detail="window_bar_missing_or_nonconsecutive"); continue
        pdy = day["pdy"]
        d1atr = pdy.atr14 if pdy is not None and not np.isnan(pdy.atr14) else np.nan
        if np.isnan(d1atr) or np.isnan(atr[i]):
            counters["atr_undefined"] += 1
            log_skip(close_ts, "both", "SKIP_atr_undefined", signal_bar_open=t15[i], d1atr=d1atr, atr_m15=atr[i]); continue
        move = cl[i] - op[idx[0]]
        gate = gate_k * atr[i]
        if abs(move) < gate or move == 0.0:
            counters["gate_small_move"] += 1
            log_skip(close_ts, "both", "SKIP_gate_small_move", signal_bar_open=t15[i], move=move, gate=gate, atr_m15=atr[i], d1atr=d1atr); continue
        side = "long" if move > 0 else "short"
        counters["signals_long" if side == "long" else "signals_short"] += 1
        whi, wlo = float(hi[idx].max()), float(lo[idx].min())
        raw_stop = (wlo - buf) if side == "long" else (whi + buf)
        pending = dict(kind="market", side=side, day=m15_day[i],
                       meta=dict(signal_time=close_ts, signal_bar_open=t15[i], decision_time=close_ts.to_datetime64(), window_bars=W,
                                 window_first_open=t15[idx[0]], move=move, gate=gate, atr_m15=atr[i], d1atr=d1atr,
                                 window_high=whi, window_low=wlo, raw_stop=raw_stop, range_first_bar=float(hi[idx[0]] - lo[idx[0]])))
    # end of data: an open position is closed at the last bar's close (flagged) so that it is counted (engine_v3)
    if pos is not None:
        j = len(m1_t) - 1
        close_pos(pos, m1_t[j], m1_c[j] - slip if pos["side"] == "long" else m1_c[j] + spread + slip, "end_of_data"); pos = None
    if pending is not None:
        log_skip(pending["meta"]["signal_time"], pending["side"], "CANCEL_end_of_data", signal_bar_open=pending["meta"]["signal_bar_open"]); pending = None
    if day["key"] is not None and not day["done"]: close_day_without_decision(day["key"])
    tr = pd.DataFrame(trades)
    if len(tr):
        tr.drop(columns=["decision_time"], inplace=True, errors="ignore")
        tr["hold_minutes"] = (pd.to_datetime(tr.exit_time) - pd.to_datetime(tr.entry_time)).dt.total_seconds() / 60
        tr["signal_date"] = pd.to_datetime(tr.signal_bar_open).dt.date
        tr["hold_lt3"] = tr.hold_minutes < 3   # account rule: profit of trades held < 3 min is deducted
    sk = pd.DataFrame(skips)
    n_session_days = int(len(daily))
    meta = dict(config=cfg, n_trades=int(len(tr)), n_skips=int(len(sk)), counters=counters, m15_bars=int(len(ind)), m1_bars=int(len(m1)),
                n_session_days=n_session_days, n_session_days_after_warmup=int(counters["days_after_warmup"]),
                trades_per_session_day=(len(tr) / n_session_days if n_session_days else None),
                trades_per_session_day_after_warmup=(len(tr) / counters["days_after_warmup"] if counters["days_after_warmup"] else None),
                exit_reasons=(tr.exit_reason.value_counts().to_dict() if len(tr) else {}),
                skip_reasons=(sk.reason.value_counts().to_dict() if len(sk) else {}),
                n_hold_lt3=(int(tr.hold_lt3.sum()) if len(tr) else 0),
                n_target_hold_lt3=(int((tr.hold_lt3 & (tr.exit_reason == "target")).sum()) if len(tr) else 0),
                data_start=str(m1.index[0]), data_end=str(m1.index[-1]), run_seconds=round(time.time() - t0, 1),
                run_time_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    if out_dir is not None:
        tr.to_csv(out_dir / "trades.csv", index=False)
        sk.to_csv(out_dir / "skips.csv", index=False)
        (out_dir / "config.json").write_text(json.dumps(meta, indent=2, default=str))
    return tr, sk, meta


def make_cfg(name: str, max_hold=None, **overrides):
    """Config and output directory name for a frozen variant id ('FIXT_US_1H' or 'V4_FIXT_US_1H'); --max-hold N writes to a
    separate '<dir>_h<N>' directory so that the registered run is never overwritten."""
    key = name[len(PREFIX):] if name.startswith(PREFIX) and name[len(PREFIX):] in VARIANTS else name
    if key not in VARIANTS: raise SystemExit(f"unknown variant {name!r}; known: {list(VARIANTS)}")
    cfg = dict(V4_CONFIG); cfg.update(VARIANTS[key]); cfg.update(overrides)
    out_name = f"{PREFIX}{key}"
    if max_hold is not None:
        cfg["max_hold_minutes"] = int(max_hold); out_name += f"_h{int(max_hold)}"
    cfg["variant"] = out_name; cfg["variant_id"] = key
    return cfg, out_name


def _period_mask(tr: pd.DataFrame, a: str, b: str):
    sbo = pd.to_datetime(tr.signal_bar_open, utc=True)
    return ((sbo >= pd.Timestamp(a, tz="UTC")) & (sbo < pd.Timestamp(b, tz="UTC"))).values


def _basic(r: np.ndarray):
    if len(r) == 0: return dict(n=0, meanR=None, pf=None, dd=None)
    wins, losses = r[r > 0].sum(), abs(r[r <= 0].sum())
    pf = (wins / losses) if losses > 0 else None
    cum = np.cumsum(r); dd = float((cum - np.maximum.accumulate(cum)).min())
    return dict(n=int(len(r)), meanR=float(r.mean()), pf=(float(pf) if pf is not None and math.isfinite(pf) else None), dd=dd)


def oos_stats(tr: pd.DataFrame):
    """Pooled validation + final-test trades (by signal_bar_open) and development trades: n, mean R, PF, max DD in R."""
    if not len(tr):
        return dict(n_oos=0, meanR_oos=None, pf_oos=None, dd_oos=None, n_dev=0, meanR_dev=None, pf_dev=None, dd_dev=None)
    r = tr.realised_R.values
    o = _basic(r[_period_mask(tr, PERIODS["validation"][0], PERIODS["final_test"][1])])
    d = _basic(r[_period_mask(tr, *PERIODS["development"])])
    return dict(n_oos=o["n"], meanR_oos=o["meanR"], pf_oos=o["pf"], dd_oos=o["dd"], n_dev=d["n"], meanR_dev=d["meanR"], pf_dev=d["pf"], dd_dev=d["dd"])


_M1 = None
def _worker(args):
    name, max_hold = args
    cfg, out_name = make_cfg(name, max_hold)
    tr, sk, meta = run(cfg, _M1, RESULTS / out_name)
    extra = f" meanR={tr.realised_R.mean():+.3f} totalR={tr.realised_R.sum():+.1f} exits={meta['exit_reasons']}" if len(tr) else ""
    return f"{out_name}: trades={len(tr)} skips={len(sk)} counters={meta['counters']} secs={meta['run_seconds']}{extra}"


def _perturb_worker(args):
    name, param, mult, value, check = args
    cfg, _ = make_cfg(name); cfg[param] = value; cfg["variant"] = f"{PREFIX}{cfg['variant_id']}_perturb_{param}_{value}"
    tr, sk, meta = run(cfg, _M1, None)
    st = oos_stats(tr)
    row = dict(param=param, mult=mult, value=value, base_value=VARIANTS[cfg["variant_id"]].get(param, V4_CONFIG.get(param)), **st,
               n_all=int(len(tr)), run_seconds=meta["run_seconds"])
    if check: row["check"] = check
    return row


def perturb(name: str, jobs: int = 2):
    """+-20% one-at-a-time perturbation of the numeric parameters (integers rounded, skipped if unchanged); pooled validation +
    final-test statistics (development alongside); the base trades.csv is not touched (perturbation runs write nothing).
    Appends the pre-registered +-1 M15 bar window-shift robustness rows (mult null, check = "window_shift")."""
    cfg, out_name = make_cfg(name)
    jobs_list = []
    for p in NUMERIC_PARAMS:
        base = cfg[p]
        if base is None: print(f"perturb {p}: not a parameter of {name} (None), skipped"); continue
        for mult in PERTURB_MULTS:
            v = base * mult
            if p in INTEGER_PARAMS: v = int(round(v))
            if v == base: print(f"perturb {p} x{mult}: unchanged ({v}), skipped"); continue
            jobs_list.append((name, p, mult, v, None))
    W = int(cfg["window_bars"])
    for v in (W - 1, W + 1):
        if v >= 1: jobs_list.append((name, "window_bars", None, v, "window_shift"))
    for v in ("13:15", "13:45"):
        jobs_list.append((name, "window_start", None, v, "window_shift"))
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


def stats(name: str):
    """Period metrics of a finished run through analyze.metrics / analyze.PERIODS (as analyze_v3 does); print only."""
    import analyze as A
    out_name = name if name.startswith(PREFIX) else PREFIX + name
    d = RESULTS / out_name
    t = pd.read_csv(d / "trades.csv", parse_dates=["signal_time", "signal_bar_open", "entry_time", "exit_time"])
    for c in ["signal_time", "signal_bar_open", "entry_time", "exit_time"]:
        if t[c].dt.tz is None: t[c] = t[c].dt.tz_localize("UTC")
    t["period"] = "none"
    for pn, (a, b) in A.PERIODS.items():
        m = (t.signal_bar_open >= pd.Timestamp(a, tz="UTC")) & (t.signal_bar_open < pd.Timestamp(b, tz="UTC")); t.loc[m, "period"] = pn
    meta = json.loads((d / "config.json").read_text())
    res = dict(variant=out_name, n_session_days=meta["n_session_days"], n_session_days_after_warmup=meta.get("n_session_days_after_warmup"),
               trades_per_session_day=len(t) / meta["n_session_days"], median_hold_min=float(t.hold_minutes.median()) if len(t) else None,
               share_within_15min=float((t.hold_minutes <= 15).mean()) if len(t) else None, exit_reasons=meta["exit_reasons"],
               skip_reasons=meta["skip_reasons"], n_hold_lt3=meta["n_hold_lt3"], n_target_hold_lt3=meta.get("n_target_hold_lt3"), periods={})
    def pick(m):
        if not m.get("n"): return dict(n=0)
        pf = m["profit_factor"]
        return dict(n=m["n"], mean_R=m["mean_R"], profit_factor=(None if pf == float("inf") else pf), max_drawdown_R=m["max_drawdown_R"],
                    total_R=m["total_R"], win_rate=m["win_rate"], boot_ci90=m["boot_ci90"], mean_R_ex_top5=m["mean_R_ex_top5"],
                    median_hold_min=m["median_hold_min"], exits=m["exits"])
    for pn, (a, b) in A.PERIODS.items(): res["periods"][pn] = pick(A.metrics(t[t.period == pn], a, b))
    oos = t[t.period.isin(["validation", "final_test"])]
    res["periods"]["validation+final_test"] = pick(A.metrics(oos, A.PERIODS["validation"][0], A.PERIODS["final_test"][1]))
    res["periods"]["all"] = pick(A.metrics(t, A.PERIODS["development"][0], A.PERIODS["final_test"][1]))
    print(json.dumps(res, indent=2, default=str))
    return res


def main():
    global _M1
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--variant", help="variant id, e.g. FIXT_US_1H"); ap.add_argument("--all", action="store_true")
    ap.add_argument("--perturb", help="variant id: +-20%% one-at-a-time perturbation -> results/V4_<ID>/perturb.json")
    ap.add_argument("--stats", help="variant id: print period metrics of a finished run (analyze.metrics)")
    ap.add_argument("--max-hold", type=int, default=None, help="override max_hold_minutes (feasibility check); writes to results/V4_<ID>_h<N>/")
    ap.add_argument("--jobs", type=int, default=2); ap.add_argument("--data", default=str(E.DATA)); ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list: print("\n".join(f"{PREFIX}{v}: {VARIANTS[v]}" for v in VARIANTS)); return
    if a.stats: stats(a.stats); return
    _M1 = pd.read_parquet(a.data)
    t0 = time.time()
    if a.perturb:
        perturb(a.perturb, jobs=min(a.jobs, 2)); print(f"total wall time {time.time() - t0:.0f} s"); return
    names = list(VARIANTS) if a.all else [a.variant or "FIXT_US_1H"]
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
