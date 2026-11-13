#!/usr/bin/env python3
"""engine_v4_pdlvl_fade.py — F8 PDLVL_FADE: previous-day high/low or floor-trader pivot fade with resting OCO LIMIT
orders, tight 0.10 x D1ATR stop, 1.5 R target. The only passive-order family in the project.
Specification: results/PREREGISTRATION_v4.md §0 (shared conventions) and §2 F8, frozen 2026-11-12 before any v4 run.
Nothing here may be re-tuned after a result has been seen.

Mechanics are engine_v3.py's, copied where they apply (fill_entry, the M1 loop, open_pos/close_pos, counters, output):
  * BID M1 bars, ask = bid + spread (0.25), slippage 0.05 per fill, commission 0 (E.BASE_CONFIG);
  * M15 = m1.resample("15min", label="left", closed="left") OHLC dropna; E.indicators (ATR14 = Wilder RMA of the true
    range; not used by this family's rules, computed for uniformity); warmup 200 M15 bars; session-day key of a bar =
    (t + 1h).date (m1_day / m15_day / skey); daily = engine_v2.daily_frame(m1); pdy = prev_day(k) (previous session-day
    row); D1ATR = pdy.atr14 — previous-session-day values only, no look-ahead;
  * decisions only at the close of a closed M15 bar i, after bar i's M1 bars have been simulated; an order placed at that
    close acts on the M1 bars of bar i+1 onward;
  * gap rule: a fill at/beyond the order's own stop or target is not taken (SKIP_gap_fill_past_stop / _target);
  * same-minute stop: long, fill bar's bid low <= stop -> closed at (bid low - slip if bid low < stop else stop - slip);
    short, ask high >= stop -> stop + slip; reason stop_same_minute;
  * open position, per M1 bar, in this order: session_gap_exit when the bar's session key differs from the position's
    (long bid open - slip / short ask open + slip); time_exit at the first bar with minute-of-day >= 20:50 (same prices);
    stop (long bid low <= stop -> min(stop, bid open) - slip; short ask high >= stop -> max(stop, ask open) + slip);
    target on a strict trade-through (long bid high > target; short ask low < target) filled at the target; stop first
    when both print in one minute (ambiguous flag, counter); then max_hold (only when set, engine_v3 definition:
    bar_time - entry_time >= max_hold - 1 min -> closed at that bar's close, timestamp + 1 min, at bid close - slip
    (long) / bid close + spread + slip (short));
  * pending orders: CANCEL_unfilled_at_cutoff at the first M1 bar with minute-of-day >= 16:00, CANCEL_session_ended when
    the session key changes; no rounding of any level;
  * planned_risk = |level - stop| with the LIMIT LEVEL as `level` (engine_v3 open_pos; §0 "the limit level for F8")
    = stop_d1atr x D1ATR; pnl_per_oz = sign x (exit - fill) - commission; realised_R = pnl_per_oz / planned_risk.
    The fill-based risk |entry_price - initial_stop| is recorded as `risk_from_fill` for reference.
    signal_time = 07:00 (the placement = close of the 06:45 bar), signal_bar_open = the 06:45 bar's open.

F8 rules (frozen; §2 F8 of the preregistration):
  pdy = prev_day(k): H = pdy.high, L = pdy.low, C = pdy.close, D1ATR = pdy.atr14.
  1) level set: PDL_FADE_PDHL {PDH = H, PDL = L}; PDL_FADE_PIV {S1, PP, R1}, PP = (H + L + C) / 3, R1 = 2 PP - L,
     S1 = 2 PP - H.
  2) placement decision at the close of the M15 bar with open time 06:45 of session day k (close 07:00); c = that bar's
     close. No 06:45 bar on day k -> SKIP_placement_bar_missing; pdy missing or D1ATR NaN -> SKIP_d1atr_undefined.
     Candidates above c: level - c >= min_dist_d1atr x D1ATR; below c: c - level >= min_dist_d1atr x D1ATR. Sell limit at
     U = the NEAREST qualifying level above c; buy limit at D = the NEAREST qualifying level below c; one side only if
     only one qualifies; none -> SKIP_no_level. The two orders are OCO.
  3) orders are active from the first M1 bar at/after 07:00 (the M1 bars of the M15 bar after the 06:45 bar) until the
     first M1 bar with minute-of-day >= 16:00 (CANCEL_unfilled_at_cutoff) or the session change (CANCEL_session_ended).
     On M1 bars OPENING in [13:25, 13:35] inclusive no entry fill is evaluated (orders stay alive; a level crossed during
     the blackout fills on the next qualifying bar under the normal rule, subject to the gap rule).
  4) limit fill rule (pending kind "limit", new): buy limit D fills on the first active M1 bar with ask low (= bid low
     + 0.25) <= D - through, at min(D, ask open) + 0.05; sell limit U fills on the first active M1 bar with bid high >=
     U + through, at max(U, bid open) - 0.05; through = 0.10 USD (a touch is not a fill). Both sides in one minute: the
     level nearer the bar's open fills — if (ask open - D) <= (U - bid open) the buy fills, else the sell.
  5) stop and target fixed at placement: long stop = D - stop_d1atr x D1ATR, long target = D + target_mult x stop_d1atr
     x D1ATR; short stop = U + stop_d1atr x D1ATR, short target = U - target_mult x stop_d1atr x D1ATR.
  6) gap rule as above; a gap-skipped fill ends the day (both orders cancelled).
  7) one trade per session day: the first fill cancels the other order; no re-placement after a stop-out.
  8) same-minute stop, stop-first ambiguity, strict trade-through target, 20:50 time_exit, session_gap_exit; no
     max_hold (unless the --max-hold feasibility override is used), partial, trailing or news calendar; trades with
     hold_minutes < 3 flagged (column hold_lt3; account rule).

Judgement calls (literal readings of the frozen text; see the notes in the result):
  * The 13:25-13:35 blackout suppresses ENTRY fills only; an open position's stop/target/time exits are evaluated
    normally in those minutes (the rule text is about "orders ... no fill is evaluated (orders stay alive ...)").
  * SKIP_placement_bar_missing is logged at the new-session detection for a session day without a 06:45 M15 bar
    (nominal signal_time = 07:00 of that day); a day whose 06:45 bar exists but whose feed ends before the next bar has
    its orders cancelled with CANCEL_session_ended by the loop.
  * The pending record is cancelled at 16:00 / at the session change with side "both", "long" or "short" according to
    which orders were still alive; the OCO partner cancelled by a fill is not logged as a skip (engine_v3 ORB/VB
    convention); the partner's level is recorded on the trade (oco_other_level / oco_other_name).
  * prev_day(k) is the daily row before k exactly as engine_v2.daily_frame orders them, including the 21 Sunday
    22:00-23:00 stub rows on US/EU DST-mismatch weeks (§0: accepted quirk shared by every engine, no special rule).

Variants (frozen): PDL_FADE_PDHL (level_set PDHL) and PDL_FADE_PIV (level_set PIV); both stop_d1atr=0.10,
target_mult=1.5, min_dist_d1atr=0.05, through=0.10, placement 06:45 close, cancel 16:00, blackout 13:25-13:35,
time_exit 20:50, one trade per session day, OCO, max_hold None.
Perturbation (robustness report only, never selection): stop_d1atr, target_mult, min_dist_d1atr, through at 0.8x and
1.2x, one at a time (no integer parameters in this family), pooled validation + final-test trades.

Usage:
  python3 engine_v4_pdlvl_fade.py --variant PDL_FADE_PDHL      # -> results/V4_PDL_FADE_PDHL/{trades,skips}.csv, config.json
  python3 engine_v4_pdlvl_fade.py --all                        # both variants, at most 2 processes
  python3 engine_v4_pdlvl_fade.py --perturb PDL_FADE_PDHL      # -> results/V4_PDL_FADE_PDHL/perturb.json (trades.csv untouched)
  python3 engine_v4_pdlvl_fade.py --variant PDL_FADE_PDHL --max-hold 15   # feasibility check -> results/V4_PDL_FADE_PDHL_h15/
"""
import argparse, json, pathlib, datetime as dt, time, math
import numpy as np, pandas as pd
import engine as E
import engine_v2 as V2

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
FAMILY = "PDLVL_FADE"

V4_CONFIG = dict(E.BASE_CONFIG)
for _k in ("adx_threshold", "adx_rising_lookback", "adx_cancel_below", "entry_offset", "stop_buffer_min", "stop_buffer_atr",
           "deep_break_atr", "target_lookback", "min_rr", "rearm", "expiry_bars", "signal_start", "signal_end", "pending_cutoff",
           "max_trades_per_day", "news_filter", "news_window_min"):
    V4_CONFIG.pop(_k, None)   # v1 pullback parameters are not used by this family
V4_CONFIG.update(dict(
    version="v4.0-pdlvl_fade", family=FAMILY,
    level_set="PDHL",              # "PDHL" = {PDH, PDL} | "PIV" = {S1, PP, R1}                       [structural per variant]
    stop_d1atr=0.10,               # stop distance beyond the level, in previous-session-day atr14 units [numeric]
    target_mult=1.5,               # target = target_mult x stop distance on the other side of the level [numeric]
    min_dist_d1atr=0.05,           # minimum distance of a level from the 06:45 close, in D1ATR units   [numeric]
    through=0.10,                  # USD trade-through required for a limit fill                        [numeric]
    placement_bar_open="06:45",    # decision at this M15 bar's close (07:00)                           [fixed]
    cancel_time="16:00",           # unfilled orders cancelled at the first M1 bar at/after this time   [fixed]
    blackout_start="13:25", blackout_end="13:35",   # M1 bars opening in this window (inclusive): no entry fill [fixed]
    time_exit="20:50", max_hold_minutes=None, warmup_bars=200, one_trade_per_day=True,
))

# ---- PRE-REGISTERED VARIANT LIST (PREREGISTRATION_v4.md §2 F8, frozen 2026-11-12) ----
VARIANTS = {
    "PDL_FADE_PDHL": dict(level_set="PDHL"),
    "PDL_FADE_PIV":  dict(level_set="PIV"),
}
NUMERIC_PARAMS = ("stop_d1atr", "target_mult", "min_dist_d1atr", "through")
INTEGER_PARAMS = ()
PERTURB_MULTS = (0.8, 1.2)
PERIODS = {"development": ("2021-01-04", "2024-07-01"), "validation": ("2024-07-01", "2025-09-01"),
           "final_test": ("2025-09-01", "2026-11-01")}   # by signal_bar_open; same as analyze.PERIODS

hhmm = E.hhmm
ONE_MIN = np.timedelta64(1, "m")


def level_set(name: str, H: float, L: float, C: float):
    """The faded levels of a variant from the previous session day's high / low / close (rule 1)."""
    if name == "PDHL":
        return {"PDH": H, "PDL": L}
    if name == "PIV":
        PP = (H + L + C) / 3.0
        return {"S1": 2.0 * PP - H, "PP": PP, "R1": 2.0 * PP - L}
    raise ValueError(f"unknown level_set {name!r}")


def run(cfg: dict, m1: pd.DataFrame, out_dir):
    """Run one configuration. out_dir None -> nothing is written (used by --perturb)."""
    t0 = time.time()
    if out_dir is not None: out_dir.mkdir(parents=True, exist_ok=True)
    fam = cfg["family"]
    m15 = m1.resample("15min", label="left", closed="left").agg(open=("open", "first"), high=("high", "max"),
                                                                 low=("low", "min"), close=("close", "last")).dropna()
    ind = E.indicators(m15, cfg)
    cl, atr = ind.close.values, ind.atr.values
    t15 = ind.index
    mod15 = (t15.hour * 60 + t15.minute).values
    skey = (t15 + pd.Timedelta(hours=1)).date
    daily = V2.daily_frame(m1)
    dpos = {k: i for i, k in enumerate(daily.index)}
    spread, slip, comm = cfg["spread"], cfg["slippage"], cfg["commission_rt"]
    texit_min = hhmm(cfg["time_exit"]); cancel_min = hhmm(cfg["cancel_time"]); place_mod = hhmm(cfg["placement_bar_open"])
    blk_lo, blk_hi = hhmm(cfg["blackout_start"]), hhmm(cfg["blackout_end"])
    max_hold = cfg["max_hold_minutes"]
    hold_td = np.timedelta64(int(max_hold) - 1, "m") if max_hold else None
    s_k, tgt_m, min_dist, through = float(cfg["stop_d1atr"]), float(cfg["target_mult"]), float(cfg["min_dist_d1atr"]), float(cfg["through"])
    lset = cfg["level_set"]
    m1_t = m1.index.values; m1_o, m1_h, m1_l, m1_c = (m1[k].values for k in ("open", "high", "low", "close"))
    m1_mod = (m1.index.hour * 60 + m1.index.minute).values
    # session-day number of each M1 / M15 bar (23:00 start). Intraday positions and orders may not outlive their session
    # day: on days where the feed ends before 20:50 they are closed / cancelled at the first bar of the next session day.
    m1_day = (m1.index.values + np.timedelta64(1, "h")).astype("datetime64[D]")
    m15_day = (t15.values + np.timedelta64(1, "h")).astype("datetime64[D]")
    bar_start = np.searchsorted(m1_t, t15.values, side="left")
    bar_end = np.searchsorted(m1_t, (t15 + pd.Timedelta(minutes=15)).values, side="left")
    w0 = cfg["warmup_bars"]
    days_with_placement_bar = set(skey[w0:][mod15[w0:] == place_mod])   # session days (from the warmup on) that have a 06:45 bar

    def prev_day(k):
        i = dpos.get(k)
        return None if i is None or i == 0 else daily.iloc[i - 1]

    trades, skips = [], []
    pending = None; pos = None
    day = dict(key=None, entries=0, done=False, pdy=None)
    counters = dict(ambiguous_stop_target=0, both_sides_same_minute=0, same_minute_stop=0, gap_fill_skipped=0,
                    session_days=0, placements=0, placements_both=0, placements_buy_only=0, placements_sell_only=0,
                    fills_long=0, fills_short=0, blackout_bars_not_evaluated=0, cancelled_unfilled_at_cutoff=0,
                    cancelled_session_ended=0, placement_bar_missing=0, no_level=0)

    def log_skip(t, side, reason, **kw): skips.append(dict(signal_time=t, side=side, reason=reason, **kw))

    def open_pos(side, t, fill, level, stop, target, meta):
        risk = abs(level - stop)
        return dict(variant=cfg["variant"], family=fam, side=side, signal_time=meta["signal_time"], signal_bar_open=meta["signal_bar_open"],
                    entry_time=t, entry_price=fill, level=level, initial_stop=stop, stop=stop, target=target, planned_risk=risk,
                    risk_from_fill=abs(fill - stop),
                    hh=fill, ll=fill, ambiguous=False, day=m1_day[np.searchsorted(m1_t, t)], **{k: v for k, v in meta.items() if k not in ("signal_time", "signal_bar_open")})

    def close_pos(p, t, px, reason):
        sign = 1.0 if p["side"] == "long" else -1.0
        pnl = sign * (px - p["entry_price"]) - comm
        rec = dict(p); rec.update(exit_time=t, exit_price=px, exit_reason=reason, pnl_per_oz=pnl, realised_R=pnl / p["planned_risk"],
                                  final_stop=p["stop"])
        for k in ("hh", "ll", "stop", "day"): rec.pop(k, None)
        trades.append(rec)

    def fill_entry(side, j, kind, level_or_none, stop, target, meta):
        """engine_v3.fill_entry extended with the limit kind. Fill price: stop order -> long max(level, ask open) + slip /
        short min(level, bid open) - slip; market -> ask open + slip / bid open - slip; LIMIT (F8 rule 4) -> long
        min(level, ask open) + slip / short max(level, bid open) - slip. Then the gap rule and the same-minute stop
        check exactly as engine_v3. A filled or gap-skipped order consumes the session day (rules 6 and 7)."""
        nonlocal pos
        bo, bh, bl = m1_o[j], m1_h[j], m1_l[j]; ao, ah = bo + spread, bh + spread
        if kind == "limit":
            fill = (min(level_or_none, ao) + slip) if side == "long" else (max(level_or_none, bo) - slip)
        elif kind == "stop":
            fill = (max(level_or_none, ao) + slip) if side == "long" else (min(level_or_none, bo) - slip)
        else:   # market
            fill = (ao + slip) if side == "long" else (bo - slip)
        past_stop = (fill <= stop) if side == "long" else (fill >= stop)
        past_tgt = target is not None and ((fill >= target) if side == "long" else (fill <= target))
        if past_stop or past_tgt:   # the first print after a gap is already beyond the planned stop or target: the order is not taken
            counters["gap_fill_skipped"] += 1
            log_skip(meta["signal_time"], side, "SKIP_gap_fill_past_stop" if past_stop else "SKIP_gap_fill_past_target", fill=fill, stop=stop, target=target,
                     level=level_or_none, fill_time=m1_t[j]); return
        level = level_or_none if level_or_none is not None else fill
        if side == "long":
            pos = open_pos("long", m1_t[j], fill, level, stop, target, meta); day["entries"] += 1; counters["fills_long"] += 1
            if bl <= stop:
                counters["same_minute_stop"] += 1
                close_pos(pos, m1_t[j], (min(stop, bl) - slip if bl < stop else stop - slip), "stop_same_minute"); pos = None
        else:
            pos = open_pos("short", m1_t[j], fill, level, stop, target, meta); day["entries"] += 1; counters["fills_short"] += 1
            if ah >= stop:
                counters["same_minute_stop"] += 1
                close_pos(pos, m1_t[j], stop + slip, "stop_same_minute"); pos = None

    def pending_sides(p):
        return "both" if (p["buy"] is not None and p["sell"] is not None) else ("long" if p["buy"] is not None else "short")

    for i in range(w0, len(ind)):
        k = skey[i]
        if k != day["key"]:
            # ---- new session day (23:00): reset per-day state; daily quantities are previous-session-day values
            day.update(key=k, entries=0, done=False, pdy=prev_day(k)); counters["session_days"] += 1
            if k not in days_with_placement_bar:   # rule 2: no 06:45 bar on this session day
                counters["placement_bar_missing"] += 1; day["done"] = True
                log_skip(pd.Timestamp(k, tz="UTC") + pd.Timedelta(hours=7), "both", "SKIP_placement_bar_missing")
        # ---- 1) simulate the M1 bars of bar i against the standing orders / open position (engine_v3 loop)
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
                        counters["cancelled_unfilled_at_cutoff"] += 1
                        log_skip(pending["meta"]["signal_time"], pending_sides(pending), "CANCEL_unfilled_at_cutoff", buy=pending["buy"], sell=pending["sell"], cancel_time=m1_t[j]); pending = None; continue
                    if pending.get("day") is not None and m1_day[j] != pending["day"]:
                        counters["cancelled_session_ended"] += 1
                        log_skip(pending["meta"]["signal_time"], pending_sides(pending), "CANCEL_session_ended", buy=pending["buy"], sell=pending["sell"], cancel_time=m1_t[j]); pending = None; continue
                    if blk_lo <= mod <= blk_hi:   # rule 3: no entry fill is evaluated on bars opening in the blackout; orders stay alive
                        counters["blackout_bars_not_evaluated"] += 1; continue
                    # rule 4: limit fills require a trade-through of the level (ask low for the buy, bid high for the sell)
                    hit_buy = pending["buy"] is not None and al <= pending["buy"] - through
                    hit_sell = pending["sell"] is not None and bh >= pending["sell"] + through
                    if hit_buy and hit_sell:
                        counters["both_sides_same_minute"] += 1
                        if (ao - pending["buy"]) <= (pending["sell"] - bo): hit_sell = False   # the level nearer the open fills first
                        else: hit_buy = False
                    if hit_buy:
                        p = pending; pending = None; day["done"] = True
                        meta = dict(p["meta"]); meta.update(level_name=p["buy_name"], dist_d1atr=(meta["c0645"] - p["buy"]) / meta["d1atr"],
                                                          oco_other_level=p["sell"], oco_other_name=p["sell_name"], fill_kind="limit")
                        fill_entry("long", j, "limit", p["buy"], p["stop_long"], p["target_long"], meta)
                        continue
                    if hit_sell:
                        p = pending; pending = None; day["done"] = True
                        meta = dict(p["meta"]); meta.update(level_name=p["sell_name"], dist_d1atr=(p["sell"] - meta["c0645"]) / meta["d1atr"],
                                                          oco_other_level=p["buy"], oco_other_name=p["buy_name"], fill_kind="limit")
                        fill_entry("short", j, "limit", p["sell"], p["stop_short"], p["target_short"], meta)
                        continue
        # ---- 2) decision at the close of bar i (bar i is closed; bar i+1 has not started): placement at the 06:45 bar's close
        if mod15[i] != place_mod: continue
        if day["done"] or pos is not None or pending is not None: continue
        day["done"] = True   # one placement per session day (rule 7: no re-placement)
        pdy = day["pdy"]
        close_ts = t15[i] + pd.Timedelta(minutes=15)
        if pdy is None or np.isnan(pdy.atr14):
            log_skip(close_ts, "both", "SKIP_d1atr_undefined"); continue
        H, L, C, A = float(pdy.high), float(pdy.low), float(pdy.close), float(pdy.atr14)
        levels = level_set(lset, H, L, C)
        c = float(cl[i])
        above = sorted((lv - c, name, lv) for name, lv in levels.items() if lv - c >= min_dist * A)
        below = sorted((c - lv, name, lv) for name, lv in levels.items() if c - lv >= min_dist * A)
        if not above and not below:
            counters["no_level"] += 1
            log_skip(close_ts, "both", "SKIP_no_level", c0645=c, d1atr=A, **levels); continue
        U_name, U = (above[0][1], above[0][2]) if above else (None, None)
        D_name, D = (below[0][1], below[0][2]) if below else (None, None)
        counters["placements"] += 1
        counters["placements_both" if (U is not None and D is not None) else ("placements_buy_only" if D is not None else "placements_sell_only")] += 1
        pending = dict(kind="limit", buy=D, sell=U, buy_name=D_name, sell_name=U_name, cancel_min=cancel_min, day=m15_day[i],
                       stop_long=(D - s_k * A) if D is not None else None, target_long=(D + tgt_m * s_k * A) if D is not None else None,
                       stop_short=(U + s_k * A) if U is not None else None, target_short=(U - tgt_m * s_k * A) if U is not None else None,
                       meta=dict(signal_time=close_ts, signal_bar_open=t15[i], d1atr=A, c0645=c, pdh=H, pdl=L, pdc=C, atr_m15=float(atr[i]),
                                 buy_level=D, sell_level=U, **{f"lvl_{n}": v for n, v in levels.items()}))
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
                n_session_days=n_session_days, n_session_days_evaluated=counters["session_days"],
                trades_per_session_day=(len(tr) / n_session_days if n_session_days else None),
                exit_reasons=(tr.exit_reason.value_counts().to_dict() if len(tr) else {}),
                skip_reasons=(sk.reason.value_counts().to_dict() if len(sk) else {}),
                n_hold_lt3=(int(tr.hold_lt3.sum()) if len(tr) else 0),
                periods=PERIODS,
                data_start=str(m1.index[0]), data_end=str(m1.index[-1]), run_seconds=round(time.time() - t0, 1),
                run_time_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    if out_dir is not None:
        tr.to_csv(out_dir / "trades.csv", index=False)
        sk.to_csv(out_dir / "skips.csv", index=False)
        (out_dir / "config.json").write_text(json.dumps(meta, indent=2, default=str))
    return tr, sk, meta


def make_cfg(name: str, max_hold=None):
    """Config and output directory name for a frozen variant id ('PDL_FADE_PDHL' or 'V4_PDL_FADE_PDHL'); --max-hold N
    writes to a separate '<dir>_h<N>' directory so that the registered run is never overwritten."""
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
    base trades.csv is not touched (perturbation runs write nothing but perturb.json)."""
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
        with mp.get_context("fork").Pool(min(jobs, 2)) as pool:   # at most 2 processes
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
    ap.add_argument("--variant", help="variant id, e.g. PDL_FADE_PDHL"); ap.add_argument("--all", action="store_true")
    ap.add_argument("--perturb", help="variant id: +-20%% one-at-a-time perturbation -> results/V4_<ID>/perturb.json")
    ap.add_argument("--max-hold", type=int, default=None, help="override max_hold_minutes (feasibility check); writes to results/V4_<ID>_h<N>/")
    ap.add_argument("--jobs", type=int, default=2); ap.add_argument("--data", default=str(E.DATA)); ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list: print("\n".join(f"{v}: {VARIANTS[v]}" for v in VARIANTS)); return
    _M1 = pd.read_parquet(a.data)
    t0 = time.time()
    if a.perturb:
        perturb(a.perturb, jobs=min(a.jobs, 2)); print(f"total wall time {time.time() - t0:.0f} s"); return
    names = list(VARIANTS) if a.all else [a.variant or "PDL_FADE_PDHL"]
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
