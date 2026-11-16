#!/usr/bin/env python3
"""engine_v4_asia_hold.py — F5 ASIA_HOLD: fixed-time hold through the Asian block (session reopen -> 06:50) on XAUUSD M1.

Pre-registered in results/PREREGISTRATION_v4.md (§0 shared conventions, §2 F5 rules; frozen 2026-11-12 before the first
run). Direction from a previous-session-day rule, 1.0 x D1ATR disaster stop set at the fill and never moved, no target,
time exit at the first M1 bar with session minute >= 470 (06:50 on the dataset clock). One market order per session day.

Shared mechanics, COPIED from backtest/engine_v3.py (which copies engine.py / engine_v2.py):
  * data: pd.read_parquet(data/xauusd_m1_utc.parquet), BID M1 bars, tz-aware index labelled UTC (PROFILE_v4_dev §0: the
    clock behaves as London local time; NO conversion anywhere, every time below is on this clock);
  * costs E.BASE_CONFIG: spread 0.25 (ask = bid + spread), slippage 0.05 per fill, commission 0;
  * M15 = m1.resample("15min", label="left", closed="left") OHLC dropna; E.indicators (ATR14/ADX14, computed for parity
    with engine_v3, not used by any F5 rule); warmup 200 M15 bars;
  * session key k = (t + 1h).date for every bar (engine_v3 m1_day / skey / m15_day); daily = engine_v2.daily_frame(m1)
    (session-day OHLC labelled by the date the session ends; sma200 = rolling 200 session-day closes; atr14 = EWM
    alpha 1/14 adjust False of the session-day true range); pdy = the daily row before k; D1ATR = pdy.atr14;
  * decisions only at the close of a closed M15 bar i (after bar i's M1 bars were simulated); the order acts on bar i+1's
    M1 bars; the session-start order (ASIA_LONG_2300) is placed at the new-session detection (k != day["key"]) before
    the session day's first M1 bar is simulated, exactly as engine_v3's F4 DC arms its stops;
  * fill_entry: market order long = bid open + spread + slippage, short = bid open - slippage, on the first simulated M1
    bar; gap rule (fill at/beyond its own stop or target -> SKIP_gap_fill_past_stop / _target; moot here because the stop
    is defined from the fill); same-minute stop: long bid low <= stop -> (bid low - slip if bid low < stop else stop -
    slip); short ask high >= stop -> stop + slip; reason stop_same_minute;
  * open position, per M1 bar, in order: (1) session_gap_exit when the bar's session key differs from the position's
    (long bid open - slip, short ask open + slip); (2) time_exit (F5: session-minute test, see below) at the same prices;
    (3) stop: long bid low <= stop -> min(stop, bid open) - slip, short ask high >= stop -> max(stop, ask open) + slip;
    target (none in F5, code path kept): long bid high > target, short ask low < target; stop first when both print in
    the same minute (ambiguous flag); (4) max_hold_minutes (None in F5; --max-hold override for the account-feasibility
    check): bar_time - entry_time >= max_hold - 1 min -> closed at that bar's close (+1 min timestamp) at bid close - slip
    (long) / bid close + spread + slip (short), reason max_hold;
  * pending orders: CANCEL_session_ended when the session key changes; CANCEL_no_entry_bar replaces the minute-of-day
    cutoff (see below); no level is rounded; planned_risk = |level - stop| with level = fill for market orders;
    R = pnl_per_oz / planned_risk, pnl_per_oz = sign x (exit - fill) - commission; end_of_data close of an open
    position at the last bar (flagged, counted; cannot happen for F5 because the data ends on a Friday evening).

F5-specific rules (PREREGISTRATION_v4 §2 F5):
  SESSION MINUTE smin(t) = (60*hour + minute + 60) mod 1440 (23:00 -> 0, 23:30 -> 30, 06:50 -> 470). EVERY time test of
  this family is on smin because the hold crosses midnight: engine_v3's `mod >= texit_min` time exit and the
  minute-of-day cancel are NOT used (they would close a 23:00 position in its fill minute).
  DAILY INPUTS (previous session day only): i = dpos[k]; pdy = daily.iloc[i-1]; D1ATR = pdy.atr14;
  SMA = daily.close.rolling(sma_len).mean() at row i-1 (sma_len 200 == pdy.sma200); mom_N = close[i-1] - close[i-1-N].
  SKIPS: pdy missing or D1ATR NaN -> SKIP_d1atr_undefined; sma200_long: SMA NaN -> SKIP_bias_undefined, pdy.close <= SMA
  -> SKIP_bias_short_side; mom rules: row i-1-N missing -> SKIP_mom_undefined, mom == 0 -> SKIP_mom_zero; mom_long:
  mom <= 0 -> SKIP_mom_not_positive.
  DIRECTION: long | sma200_long | mom_sign (long if mom > 0, short if mom < 0) | mom_long.
  ENTRY: entry_smin = 0 (ASIA_LONG_2300): market order placed at the new-session detection using pdy only; fills at the
  open of the session day's FIRST M1 bar; if that bar has smin > entry_tolerance_min (5) -> CANCEL_no_entry_bar.
  entry_smin = 30 (other variants): decision at the close of the M15 bar whose open smin is 15 (the 23:15 bar); the
  market order fills at the open of the first M1 bar with smin >= 30; if that bar has smin > 35 -> CANCEL_no_entry_bar;
  no 23:15 M15 bar in session day k -> SKIP_decision_bar_missing. General rule (entry_smin perturbation 24-36 only):
  decision at the close of the latest M15 bar whose close smin <= entry_smin (open smin = 15*(entry_smin//15) - 15);
  fill at the first M1 bar with smin >= entry_smin; cancel if that bar's smin > entry_smin + tolerance.
  STOP: fill -/+ stop_d1atr x D1ATR, never moved. EXIT: time_exit at the first M1 bar with smin >= exit_smin (470) at
  bid open - slip (long) / ask open + slip (short); session_gap_exit unchanged. No target, no max_hold, no trailing, no
  partial, no re-entry, no news gate.
  BOOKKEEPING: signal_time = signal_bar_open = open time of the session day's first M15 bar (t15[i] at the detection)
  for ASIA_LONG_2300 and the decision (23:15) bar's open time for the others; period by signal_bar_open; extra columns
  hold_minutes, signal_date, session_day, entry_smin, flag_hold_lt_3min (account rule: profit of trades held < 3 min is
  deducted).

Judgement calls (literal readings, stated here and in the run report):
  * The 21 one-hour Sunday "stub" session days (22:00-22:59 bars on DST-mismatch weeks, own session key) and the 61 days
    whose feed starts at 00:00/01:00 are real session keys: they produce CANCEL_no_entry_bar (ASIA_LONG_2300) or
    SKIP_decision_bar_missing (2330 variants) rows; no special handling.
  * A pending market order waits (does nothing) on M1 bars with smin < entry_smin (only relevant for the entry_smin
    perturbation), fills on the first bar with smin >= entry_smin and is cancelled when that bar's smin exceeds
    entry_smin + tolerance.
  * If a position is still open at a new-session detection (feed gap from before 06:50 to the next session day, e.g.
    2021-05-31 and 2026-09-25), session_gap_exit closes it on the new day's first M1 bar AND the ASIA_LONG_2300 market
    order placed at that detection fills on the same bar (the spec's "session day's FIRST M1 bar"). engine_v3's
    `if pos ... elif pending` structure would have deferred that fill to the next minute; the first run did so for one
    trade (2026-09-28) and the independent audit caught it, so the gap-exit branch falls through to the pending block.
    Counted in counters["session_gap_exit"] (2 occurrences in the data for the long-only variants).
  * --perturb and --cost-stress run in memory and write only perturb.json / cost_stress.json next to the base outputs;
    the base trades.csv is never overwritten by them. --max-hold N writes to results/V4_<ID>_h<N>/ (or --out-dir).

Usage:
  python3 engine_v4_asia_hold.py --variant ASIA_LONG_2330
  python3 engine_v4_asia_hold.py --all [--jobs 2]            (at most 2 processes)
  python3 engine_v4_asia_hold.py --perturb ASIA_LONG_2330    -> results/V4_ASIA_LONG_2330/perturb.json
  python3 engine_v4_asia_hold.py --cost-stress ASIA_LONG_2330 -> results/V4_ASIA_LONG_2330/cost_stress.json
  python3 engine_v4_asia_hold.py --variant ASIA_LONG_2330 --max-hold 15 [--out-dir DIR]
Outputs: ../results/V4_<variant>/trades.csv, skips.csv, config.json (engine_v3's columns and counters + hold_minutes, signal_date).
"""
import argparse, json, pathlib, datetime as dt, time, sys
import numpy as np, pandas as pd
import engine as E
import engine_v2 as V2

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
FAMILY = "ASIA_HOLD"
PREFIX = "V4_"
ONE_MIN = np.timedelta64(1, "m")
PERIODS = {"development": ("2021-01-04", "2024-07-01"), "validation": ("2024-07-01", "2025-09-01"), "final_test": ("2025-09-01", "2026-11-01")}

V4_CONFIG = dict(E.BASE_CONFIG)
for _k in ("adx_threshold", "adx_rising_lookback", "adx_cancel_below", "entry_offset", "stop_buffer_min", "stop_buffer_atr",
           "deep_break_atr", "target_lookback", "min_rr", "rearm", "expiry_bars", "signal_start", "signal_end", "pending_cutoff",
           "max_trades_per_day", "news_filter", "news_window_min", "time_exit"):
    V4_CONFIG.pop(_k, None)   # v1 pullback parameters and the minute-of-day time exit are not used by F5
V4_CONFIG.update(dict(
    version="v4.0-asia_hold", family=FAMILY, variant=None,
    entry_smin=30,              # 0 = session's first bar (structural, ASIA_LONG_2300); 30 = 23:30 [numeric, perturb 24-36]
    entry_tolerance_min=5,      # fixed feed-gap guard: cancel if the entry bar opens more than 5 min after entry_smin
    exit_smin=470,              # 06:50 [numeric, perturb 376-564]
    stop_d1atr=1.0,             # disaster stop distance in previous-session-day ATR14 [numeric, perturb 0.8-1.2]
    target=None, max_hold_minutes=None,
    direction_rule="long",      # long | sma200_long | mom_sign | mom_long (structural per variant)
    sma_len=200,                # [numeric, perturb 160-240; sma200_long only]
    mom_lookback_days=20,       # [integer numeric; perturb 16-24 (N=20) / 4-6 (N=5); mom rules only]
    max_orders_per_session_day=1, news_gate=None,
))

# ---- PRE-REGISTERED VARIANT LIST (PREREGISTRATION_v4.md §2 F5; frozen 2026-11-12 before the first run) ----
VARIANTS = {
    "ASIA_LONG_2300":    dict(entry_smin=0,  direction_rule="long"),
    "ASIA_LONG_2330":    dict(entry_smin=30, direction_rule="long"),
    "ASIA_SMA200L_2330": dict(entry_smin=30, direction_rule="sma200_long", sma_len=200),
    "ASIA_MOM20_2330":   dict(entry_smin=30, direction_rule="mom_sign", mom_lookback_days=20),
    "ASIA_MOM20L_2330":  dict(entry_smin=30, direction_rule="mom_long", mom_lookback_days=20),
    "ASIA_MOM5_2330":    dict(entry_smin=30, direction_rule="mom_sign", mom_lookback_days=5),
}
# numeric parameters perturbed +-20 % one at a time (pre-registered; robustness only, never used to pick parameters)
PERTURB = {
    "ASIA_LONG_2300":    ["exit_smin", "stop_d1atr"],
    "ASIA_LONG_2330":    ["entry_smin", "exit_smin", "stop_d1atr"],
    "ASIA_SMA200L_2330": ["entry_smin", "exit_smin", "stop_d1atr", "sma_len"],
    "ASIA_MOM20_2330":   ["entry_smin", "exit_smin", "stop_d1atr", "mom_lookback_days"],
    "ASIA_MOM20L_2330":  ["entry_smin", "exit_smin", "stop_d1atr", "mom_lookback_days"],
    "ASIA_MOM5_2330":    ["entry_smin", "exit_smin", "stop_d1atr", "mom_lookback_days"],
}
INTEGER_PARAMS = {"entry_smin", "exit_smin", "sma_len", "mom_lookback_days"}
COST_STRESS = dict(spread=0.50, slippage=0.15)   # as V1_cost_stress; pre-registered for EVERY F5 variant


def make_cfg(name, **overrides):
    cfg = dict(V4_CONFIG); cfg.update(VARIANTS[name]); cfg["variant"] = name; cfg.update(overrides)
    return cfg


def smin_to_hhmm(s):
    m = (int(s) - 60) % 1440
    return f"{m // 60:02d}:{m % 60:02d}"


def run(cfg: dict, m1: pd.DataFrame, out_dir=None):
    """Run one configuration. Writes trades.csv / skips.csv / config.json into out_dir unless out_dir is None."""
    t0 = time.time()
    m15 = m1.resample("15min", label="left", closed="left").agg(open=("open", "first"), high=("high", "max"),
                                                                 low=("low", "min"), close=("close", "last")).dropna()
    ind = E.indicators(m15, cfg)
    atr, adx = ind.atr.values, ind.adx.values
    t15 = ind.index
    mod15 = (t15.hour * 60 + t15.minute).values
    smin15 = (mod15 + 60) % 1440
    skey = (t15 + pd.Timedelta(hours=1)).date
    daily = V2.daily_frame(m1)
    sma_len, N = int(cfg["sma_len"]), int(cfg["mom_lookback_days"])
    daily["sma_n"] = daily.close.rolling(sma_len).mean()        # == daily.sma200 when sma_len == 200
    dkeys = list(daily.index); dclose, dsma, datr = daily.close.values, daily.sma_n.values, daily.atr14.values
    dpos = {k: i for i, k in enumerate(dkeys)}
    spread, slip, comm = cfg["spread"], cfg["slippage"], cfg["commission_rt"]
    entry_smin, tol, exit_smin = int(cfg["entry_smin"]), int(cfg["entry_tolerance_min"]), int(cfg["exit_smin"])
    stop_mult, rule = float(cfg["stop_d1atr"]), cfg["direction_rule"]
    at_open = entry_smin == 0
    dec_open_smin = None if at_open else 15 * (entry_smin // 15) - 15   # open smin of the latest M15 bar whose close smin <= entry_smin
    max_hold = cfg["max_hold_minutes"]
    hold_td = np.timedelta64(int(max_hold) - 1, "m") if max_hold else None
    m1_t = m1.index.values; m1_o, m1_h, m1_l, m1_c = (m1[k].values for k in ("open", "high", "low", "close"))
    m1_mod = (m1.index.hour * 60 + m1.index.minute).values
    m1_smin = (m1_mod + 60) % 1440
    m1_day = (m1.index.values + np.timedelta64(1, "h")).astype("datetime64[D]")
    m15_day = (t15.values + np.timedelta64(1, "h")).astype("datetime64[D]")
    bar_start = np.searchsorted(m1_t, t15.values, side="left")
    bar_end = np.searchsorted(m1_t, (t15 + pd.Timedelta(minutes=15)).values, side="left")
    fixed_side = "long" if rule in ("long", "sma200_long", "mom_long") else "both"

    trades, skips = [], []
    pending = None; pos = None
    day = dict(key=None, entries=0, decided=False)
    counters = dict(ambiguous_stop_target=0, both_sides_same_minute=0, same_minute_stop=0, gap_fill_skipped=0,
                    cancel_no_entry_bar=0, cancel_session_ended=0, session_gap_exit=0, decision_bar_missing=0, end_of_data=0)

    def log_skip(t, side, reason, **kw): skips.append(dict(signal_time=t, side=side, reason=reason, **kw))

    def open_pos(side, j, fill, level, stop, target, meta):
        risk = abs(level - stop)
        return dict(variant=cfg["variant"], family=FAMILY, side=side, signal_time=meta["signal_time"], signal_bar_open=meta["signal_bar_open"],
                    entry_time=m1_t[j], entry_price=fill, level=level, initial_stop=stop, stop=stop, target=target, planned_risk=risk,
                    ambiguous=False, day=m1_day[j], **{k: v for k, v in meta.items() if k not in ("signal_time", "signal_bar_open")})

    def close_pos(p, t, px, reason):
        sign = 1.0 if p["side"] == "long" else -1.0
        pnl = sign * (px - p["entry_price"]) - comm
        rec = dict(p); rec.update(exit_time=t, exit_price=px, exit_reason=reason, pnl_per_oz=pnl, realised_R=pnl / p["planned_risk"],
                                  final_stop=p["stop"])
        for k in ("stop", "day"): rec.pop(k, None)
        trades.append(rec)

    def fill_entry(side, j, level_or_none, stop, target, meta, stop_dist=None):
        """engine_v3.fill_entry: buy/sell stop (level given) or market order (level None) on M1 bar j; same-minute stop check.
        stop_dist (F5): the stop is defined from the fill, stop = fill -/+ stop_dist, so the gap rule is moot."""
        nonlocal pos
        bo, bh, bl = m1_o[j], m1_h[j], m1_l[j]; ao, ah = bo + spread, bh + spread
        fill = ((max(level_or_none, ao) if level_or_none is not None else ao) + slip) if side == "long" else ((min(level_or_none, bo) if level_or_none is not None else bo) - slip)
        if stop_dist is not None: stop = fill - stop_dist if side == "long" else fill + stop_dist
        past_stop = (fill <= stop) if side == "long" else (fill >= stop)
        past_tgt = target is not None and ((fill >= target) if side == "long" else (fill <= target))
        if past_stop or past_tgt:   # the first print after a gap is already beyond the planned stop or target: the order is not taken
            counters["gap_fill_skipped"] += 1
            log_skip(meta["signal_time"], side, "SKIP_gap_fill_past_stop" if past_stop else "SKIP_gap_fill_past_target", fill=fill, stop=stop, target=target); return
        level = level_or_none if level_or_none is not None else fill
        if side == "long":
            pos = open_pos("long", j, fill, level, stop, target, meta); day["entries"] += 1
            if bl <= stop:
                counters["same_minute_stop"] += 1
                close_pos(pos, m1_t[j], (min(stop, bl) - slip if bl < stop else stop - slip), "stop_same_minute"); pos = None
        else:
            pos = open_pos("short", j, fill, level, stop, target, meta); day["entries"] += 1
            if ah >= stop:
                counters["same_minute_stop"] += 1
                close_pos(pos, m1_t[j], stop + slip, "stop_same_minute"); pos = None

    def decide(k, when):
        """Previous-session-day rule for session day k. Returns (side, meta) or None after logging the skip."""
        i = dpos.get(k)
        if i is None or i == 0 or np.isnan(datr[i - 1]) or not datr[i - 1] > 0:
            log_skip(when, fixed_side, "SKIP_d1atr_undefined"); return None
        d1atr, pclose = float(datr[i - 1]), float(dclose[i - 1])
        meta = dict(signal_time=when, signal_bar_open=when, session_day=k, pdy_key=dkeys[i - 1], d1atr=d1atr, pdy_close=pclose,
                    direction_rule=rule, sma=np.nan, mom=np.nan)
        if rule == "long":
            side = "long"
        elif rule == "sma200_long":
            sma = dsma[i - 1]
            if np.isnan(sma): log_skip(when, "long", "SKIP_bias_undefined"); return None
            if pclose <= sma: log_skip(when, "long", "SKIP_bias_short_side", pdy_close=pclose, sma=sma); return None
            side = "long"; meta["sma"] = float(sma)
        elif rule in ("mom_sign", "mom_long"):
            if i - 1 - N < 0: log_skip(when, fixed_side, "SKIP_mom_undefined"); return None
            mom = pclose - float(dclose[i - 1 - N])
            if mom == 0: log_skip(when, fixed_side, "SKIP_mom_zero", mom=mom); return None
            if rule == "mom_long" and mom <= 0: log_skip(when, "long", "SKIP_mom_not_positive", mom=mom); return None
            side = "long" if mom > 0 else "short"; meta["mom"] = mom
        else:
            raise ValueError(f"unknown direction_rule {rule}")
        return side, meta

    for i in range(cfg["warmup_bars"], len(ind)):
        k = skey[i]
        if k != day["key"]:
            # ---- new session day (23:00 on the dataset clock): reset per-day state. ASIA_LONG_2300 places its market order here,
            # before the day's first M1 bar is simulated (as engine_v3's F4 DC arms), using previous-session-day values only.
            day.update(key=k, entries=0, decided=False)
            if at_open:
                day["decided"] = True
                dec = decide(k, t15[i])
                if dec is not None:
                    pending = dict(kind="market", side=dec[0], not_before_smin=0, day=m15_day[i], meta=dec[1])
        # ---- 1) simulate the M1 bars of bar i against the standing order / open position
        if pending is not None or pos is not None:
            for j in range(bar_start[i], bar_end[i]):
                bo, bh, bl, bc, sm = m1_o[j], m1_h[j], m1_l[j], m1_c[j], m1_smin[j]
                ao, ah, al = bo + spread, bh + spread, bl + spread
                if pos is not None:
                    side = pos["side"]
                    if m1_day[j] != pos["day"]:
                        # (1) session_gap_exit. No `continue`: this bar is the new session day's first M1 bar, on which the
                        # ASIA_LONG_2300 market order placed at the detection must fill (F5: "the session day's FIRST M1 bar"),
                        # so the pending block below is reached on this same bar once the position is closed.
                        counters["session_gap_exit"] += 1
                        close_pos(pos, m1_t[j], bo - slip if side == "long" else ao + slip, "session_gap_exit"); pos = None
                    else:
                        if sm >= exit_smin:   # (2) F5 time exit on the SESSION minute (never minute-of-day: the hold crosses midnight)
                            close_pos(pos, m1_t[j], bo - slip if side == "long" else ao + slip, "time_exit"); pos = None; continue
                        if side == "long":   # (3) stop (and target: none in F5, code path kept)
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
                        if hold_td is not None and m1_t[j] - pos["entry_time"] >= hold_td:   # (4) max_hold (only where set)
                            px = bc - slip if side == "long" else bc + spread + slip
                            close_pos(pos, m1_t[j] + ONE_MIN, px, "max_hold"); pos = None; continue
                        continue
                if pending is not None and pos is None:
                    if m1_day[j] != pending["day"]:
                        counters["cancel_session_ended"] += 1
                        log_skip(pending["meta"]["signal_time"], pending["side"], "CANCEL_session_ended"); pending = None; continue
                    if sm < pending["not_before_smin"]: continue      # the order waits for its entry minute (entry_smin perturbation only)
                    if sm > pending["not_before_smin"] + tol:          # the entry bar is missing (feed gap / late reopen): no trade that day
                        counters["cancel_no_entry_bar"] += 1
                        log_skip(pending["meta"]["signal_time"], pending["side"], "CANCEL_no_entry_bar", first_bar=m1_t[j], first_bar_smin=int(sm)); pending = None; continue
                    p = pending; pending = None
                    meta = dict(p["meta"]); meta["entry_smin"] = int(sm)
                    fill_entry(p["side"], j, None, None, None, meta, stop_dist=stop_mult * meta["d1atr"])
                    continue
        # ---- 2) decision at the close of bar i (bar i is closed; bar i+1 has not started): 2330-type variants only
        if at_open or day["decided"]: continue
        if np.isnan(atr[i]) or np.isnan(adx[i]): continue   # engine_v3 warm-up guard (no effect after 200 bars; kept for parity)
        if smin15[i] == dec_open_smin:
            day["decided"] = True
            if pos is not None or pending is not None:
                log_skip(t15[i], fixed_side, "SKIP_position_open"); continue
            dec = decide(k, t15[i])
            if dec is not None:
                pending = dict(kind="market", side=dec[0], not_before_smin=entry_smin, day=m15_day[i], meta=dec[1])
        elif smin15[i] > dec_open_smin:
            day["decided"] = True; counters["decision_bar_missing"] += 1
            log_skip(t15[i], fixed_side, "SKIP_decision_bar_missing", first_bar_smin=int(smin15[i]))
    # end of data: an open position is closed at the last bar's close (flagged) so that it is counted
    if pos is not None:
        j = len(m1_t) - 1; counters["end_of_data"] += 1
        close_pos(pos, m1_t[j], m1_c[j] - slip if pos["side"] == "long" else m1_c[j] + spread + slip, "end_of_data"); pos = None
    tr = pd.DataFrame(trades)
    if len(tr):
        tr["hold_minutes"] = (pd.to_datetime(tr.exit_time) - pd.to_datetime(tr.entry_time)).dt.total_seconds() / 60
        tr["signal_date"] = pd.to_datetime(tr.signal_bar_open).dt.date
        tr["flag_hold_lt_3min"] = tr.hold_minutes < 3
    sk = pd.DataFrame(skips)
    meta = dict(config=cfg, n_trades=int(len(tr)), n_skips=int(len(sk)), counters=counters,
                skip_reasons=(sk.reason.value_counts().to_dict() if len(sk) else {}),
                exit_reasons=(tr.exit_reason.value_counts().to_dict() if len(tr) else {}),
                n_flag_hold_lt_3min=int(tr.flag_hold_lt_3min.sum()) if len(tr) else 0,
                m15_bars=int(len(ind)), m1_bars=int(len(m1)), session_days=int(len(daily)),
                data_start=str(m1.index[0]), data_end=str(m1.index[-1]), periods=PERIODS,
                run_seconds=round(time.time() - t0, 1), run_time_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    if out_dir is not None:
        out_dir = pathlib.Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
        tr.to_csv(out_dir / "trades.csv", index=False)
        sk.to_csv(out_dir / "skips.csv", index=False)
        (out_dir / "config.json").write_text(json.dumps(meta, indent=2, default=str))
    return tr, sk, meta


# ---------------------------------------------------------------- statistics helpers (analyze.metrics on period subsets)
def with_periods(tr: pd.DataFrame) -> pd.DataFrame:
    """Normalise time columns (tz-aware UTC) and assign the pre-registered period by signal_bar_open."""
    t = tr.copy()
    for c in ("signal_time", "signal_bar_open", "entry_time", "exit_time"):
        s = pd.to_datetime(t[c], utc=True) if c in ("signal_time", "signal_bar_open") else pd.to_datetime(t[c])
        if s.dt.tz is None: s = s.dt.tz_localize("UTC")
        t[c] = s
    t["period"] = "none"
    for name, (a, b) in PERIODS.items():
        m = (t.signal_bar_open >= pd.Timestamp(a, tz="UTC")) & (t.signal_bar_open < pd.Timestamp(b, tz="UTC")); t.loc[m, "period"] = name
    return t


def period_stats(tr: pd.DataFrame):
    import analyze as A
    t = with_periods(tr) if len(tr) else tr
    out = {}
    for name, (a, b) in PERIODS.items():
        sub = t[t.period == name] if len(t) else t
        m = A.metrics(sub, a, b) if len(sub) else dict(n=0)
        out[name] = dict(n=m.get("n", 0), mean_R=m.get("mean_R"), profit_factor=m.get("profit_factor"), max_drawdown_R=m.get("max_drawdown_R"),
                         total_R=m.get("total_R"), win_rate=m.get("win_rate"))
    oos = t[t.period.isin(["validation", "final_test"])] if len(t) else t
    m = A.metrics(oos, PERIODS["validation"][0], PERIODS["final_test"][1]) if len(oos) else dict(n=0)
    out["validation+final_test"] = dict(n=m.get("n", 0), mean_R=m.get("mean_R"), profit_factor=m.get("profit_factor"), max_drawdown_R=m.get("max_drawdown_R"),
                                        total_R=m.get("total_R"), boot_ci90=m.get("boot_ci90"), mean_R_ex_top5=m.get("mean_R_ex_top5"))
    return out


def _json_safe(x):
    if isinstance(x, float) and (np.isinf(x) or np.isnan(x)): return str(x)
    return x


def perturb(name, m1, out_dir):
    """+-20 % one-at-a-time perturbation of every numeric parameter (integers rounded; skipped if unchanged). In memory; writes perturb.json only."""
    base = make_cfg(name); rows = []
    for p in PERTURB[name]:
        for mult in (0.8, 1.2):
            v0 = base[p]; v = v0 * mult
            if p in INTEGER_PARAMS:
                v = int(round(v))
                if v == v0: continue
            cfg = dict(base); cfg[p] = v
            tr, sk, meta = run(cfg, m1, None)
            st = period_stats(tr); oos = st["validation+final_test"]
            rows.append(dict(param=p, mult=mult, value=v, base_value=v0, n_oos=oos["n"], meanR_oos=_json_safe(oos["mean_R"]),
                             pf_oos=_json_safe(oos["profit_factor"]), dd_oos=oos["max_drawdown_R"], n_dev=st["development"]["n"],
                             meanR_dev=_json_safe(st["development"]["mean_R"]), pf_dev=_json_safe(st["development"]["profit_factor"]),
                             n_total=int(len(tr))))
            print(f"{name} perturb {p}={v} (x{mult}): n_oos={oos['n']} meanR_oos={oos['mean_R']} pf_oos={oos['profit_factor']} dd_oos={oos['max_drawdown_R']}", flush=True)
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    (pathlib.Path(out_dir) / "perturb.json").write_text(json.dumps(rows, indent=2, default=str))
    return rows


def cost_stress(name, m1, out_dir):
    """Pre-registered cost-stress rerun (spread 0.50 / slippage 0.15, as V1_cost_stress). In memory; writes cost_stress.json only."""
    cfg = make_cfg(name, **COST_STRESS)
    tr, sk, meta = run(cfg, m1, None)
    st = period_stats(tr)
    res = dict(variant=name, costs=COST_STRESS, n_trades=int(len(tr)), counters=meta["counters"], periods=st)
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    (pathlib.Path(out_dir) / "cost_stress.json").write_text(json.dumps(res, indent=2, default=str))
    oos = st["validation+final_test"]
    print(f"{name} cost-stress: n={len(tr)} dev meanR={st['development']['mean_R']} val meanR={st['validation']['mean_R']} test meanR={st['final_test']['mean_R']} "
          f"oos meanR={oos['mean_R']} pf={oos['profit_factor']} ci90={oos['boot_ci90']}", flush=True)
    return res


_M1 = None
_MAX_HOLD = None
def _worker(name):
    cfg = make_cfg(name, max_hold_minutes=_MAX_HOLD) if _MAX_HOLD else make_cfg(name)
    out = RESULTS / (PREFIX + name + (f"_h{int(_MAX_HOLD)}" if _MAX_HOLD else ""))
    tr, sk, meta = run(cfg, _M1, out)
    extra = f" meanR={tr.realised_R.mean():+.3f} totalR={tr.realised_R.sum():+.1f}" if len(tr) else ""
    return f"{name}: trades={len(tr)} skips={len(sk)} counters={meta['counters']} secs={meta['run_seconds']}{extra} -> {out}"


def main():
    global _M1, _MAX_HOLD
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--variant", help="run one variant (ID without the V4_ prefix)")
    ap.add_argument("--all", action="store_true", help="run all F5 variants (multiprocessing, at most 2 processes)")
    ap.add_argument("--perturb", help="+-20%% one-at-a-time perturbation of the variant's numeric parameters -> perturb.json")
    ap.add_argument("--cost-stress", dest="cost_stress", help="spread 0.50 / slippage 0.15 rerun of the variant -> cost_stress.json")
    ap.add_argument("--cost-stress-all", dest="cost_stress_all", action="store_true", help="cost-stress rerun of every variant")
    ap.add_argument("--max-hold", dest="max_hold", type=int, default=None, help="optional max_hold_minutes override (account-feasibility check); output dir gets suffix _h<N>")
    ap.add_argument("--out-dir", dest="out_dir", default=None, help="override the output directory (single --variant runs only)")
    ap.add_argument("--jobs", type=int, default=2); ap.add_argument("--data", default=str(E.DATA)); ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list: print("\n".join(f"{PREFIX}{v}: {VARIANTS[v]}  perturb={PERTURB[v]}" for v in VARIANTS)); return
    _M1 = pd.read_parquet(a.data); _MAX_HOLD = a.max_hold
    t0 = time.time()
    if a.perturb:
        perturb(a.perturb, _M1, RESULTS / (PREFIX + a.perturb))
    elif a.cost_stress or a.cost_stress_all:
        for n in (list(VARIANTS) if a.cost_stress_all else [a.cost_stress]): cost_stress(n, _M1, RESULTS / (PREFIX + n))
    elif a.all:
        jobs = max(1, min(2, a.jobs))   # at most 2 processes
        import multiprocessing as mp
        with mp.get_context("fork").Pool(jobs) as pool:
            for line in pool.imap_unordered(_worker, list(VARIANTS)): print(line, flush=True)
    else:
        name = a.variant or "ASIA_LONG_2330"
        if a.out_dir:
            cfg = make_cfg(name, max_hold_minutes=a.max_hold) if a.max_hold else make_cfg(name)
            tr, sk, meta = run(cfg, _M1, pathlib.Path(a.out_dir))
            print(f"{name}: trades={len(tr)} skips={len(sk)} counters={meta['counters']} secs={meta['run_seconds']} -> {a.out_dir}")
        else:
            print(_worker(name), flush=True)
    print(f"total wall time {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
