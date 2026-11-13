#!/usr/bin/env python3
"""engine_v5_hl.py — "mark the highs and lows, trade the break" (HL) on XAUUSD M1, six pre-registered readings.

Specification: results/PREREGISTRATION_v5_hl.md (frozen 2026-11-13 before this file existed). Seventh look at the same
data. Nothing here may be re-tuned after a result has been seen; a null or negative result is valid.

Mechanics copied from engine_v3.py (same expressions, same order per M1 bar): BID M1 bars, ask = bid + spread (0.25),
slippage 0.05 per fill, commission 0 (engine.BASE_CONFIG); M15 = resample(label=left, closed=left) OHLC dropna;
engine.indicators for ATR14 (Wilder); session day (t + 1 h).date and engine_v2.daily_frame, previous-session-day values
for D1ATR / SMA200 / previous-day high-low; decisions only at the close of a closed M15 bar after its M1 bars were
simulated; stop orders fill on the M1 bars of the next M15 bar onward (buy: ask high >= level at max(level, ask open) +
slip; sell: bid low <= level at min(level, bid open) - slip; both in one minute -> the level nearer the open); gap rule
(a fill at/beyond the order's own stop or target is not taken); stop_same_minute; per-minute order for an open
position: session_gap_exit, 20:50 time_exit, stop / target with stop first, max_hold (None here), trail update.

HL rules (frozen; see the pre-registration for the full text and decisions D1-D16):
  LEVELS   swing readings: last CONFIRMED M15 swing high / low, pivot N (high[j] >= the N highs before and the N highs
           after; marked at the close of bar j+N). Previous-day readings: previous session day's high / low, marked at
           the session-day start. A new level of a kind replaces the old one and is live.
  LIFE     a level is LIVE until price first trades at/beyond its trigger (high + offset: bid high >= trigger, or its
           buy stop is triggered by ask high >= trigger; low - offset: bid low <= trigger), checked on every M1 bar in
           every state; then CONSUMED for good (no order ever again on it).
  ORDERS   at every M15 close with close time in [07:00, 16:00): flat and entries today < cap -> buy stop at the live
           high's trigger and/or sell stop at the live low's trigger, OCO; cancelled at 16:00.
  STOP     opposite marked level (live or consumed), distance from the trigger clamped to [floor x ATR14(M15), cap x
           D1ATR]; computed when the order is first placed for the current pair of marked levels, recomputed only when
           either marked level is replaced.
  EXIT     RR: target = trigger +/- target_mult x distance. TRAIL: no target, Chandelier trail_mult x ATR14(M15) of the
           last closed bar from the running extreme since the fill, ratchet only, never beyond the minute's extreme.
           Everything flat at 20:50.

Usage:
  python3 engine_v5_hl.py --variant HL_SW5_RR      # -> results/V5_HL_SW5_RR/{trades,skips,levels}.csv, config.json
  python3 engine_v5_hl.py --all                    # all six readings, at most 2 processes
  python3 engine_v5_hl.py --perturb HL_SW5_RR      # -> results/V5_HL_SW5_RR/perturb.json (trades.csv untouched)
  python3 engine_v5_hl.py --list
The engine prints trade counts and mechanical counters only — no performance figure — so that the hand-checks
(verify_v5_*.py) can be done before any statistic is read (analyze_v5.py).
"""
import argparse, json, pathlib, datetime as dt, time
import numpy as np, pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
import engine as E
import engine_v2 as V2
import htf_refs as HR

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
PREFIX = "V5_"

V5_CONFIG = dict(E.BASE_CONFIG)          # costs: spread 0.25, slippage 0.05, commission 0; adx/ema/atr lengths for E.indicators
V5_CONFIG.update(dict(
    version="v5.0-hl",
    family=None,
    time_exit="20:50",
    max_hold_minutes=None,               # engine_v3 semantics; None in all six readings
    warmup_bars=200,
    hl_level_mode="swing",               # "swing" (M15 pivots) | "prevday" (previous session day's high / low)
    hl_pivot_n=5,                        # [numeric, integer] bars on each side of a swing
    hl_offset=0.10,                      # [numeric] trigger = marked high + offset / marked low - offset
    hl_stop_cap_d1atr=0.6,               # [numeric] stop distance cap, x previous-session-day D1ATR
    hl_stop_floor_atr=0.3,               # [numeric] stop distance floor, x ATR14(M15) of the bar at whose close the order is computed
    hl_exit_mode="rr",                   # "rr" (fixed target) | "trail" (Chandelier, no target)
    hl_target_mult=1.5,                  # [numeric] RR readings
    hl_trail_mult=3.0,                   # [numeric] TRAIL readings
    hl_max_entries=3,                    # [numeric, integer] entries per session day
    hl_order_start="07:00", hl_order_end="16:00",   # order step at M15 closes with close time in [start, end); cancel at end
    hl_bias=None,                        # None | "sma200" (previous session-day close vs its 200-day SMA)
    # ---- v5b improvement filters (results/PREREGISTRATION_v5b_hl_improve.md); all off in the six frozen readings
    hl_min_stop_d1atr=None,              # MS: no order for a side whose stop distance < k x D1ATR
    hl_trend=None,                       # T: "ema50" -> buy side only above EMA50(M15) at the order-step close, sell side only below
    hl_ref=None,                         # v8: None | "h1" | "h4" -> buy side only while that timeframe's EMA-trend state (htf_refs.py) is up, sell side only while down
    hl_adx_max=None,                     # Q: no orders at an order step whose bar has ADX14(M15) above this
    hl_min_age_min=None,                 # A: a side needs a level at least this many minutes old
    hl_block_hours=None,                 # H: list of [start, end) "HH:MM" pairs; no order rests in them
))
for _k in ("adx_threshold", "adx_rising_lookback", "adx_cancel_below", "entry_offset", "stop_buffer_min", "stop_buffer_atr",
           "deep_break_atr", "target_lookback", "min_rr", "rearm", "expiry_bars", "signal_start", "signal_end", "pending_cutoff",
           "max_trades_per_day", "news_filter", "news_window_min"):
    V5_CONFIG.pop(_k, None)   # v1 pullback parameters are not used here (same list as engine_v3)

# ---- PRE-REGISTERED READINGS (frozen 2026-11-13 before the first run; results/PREREGISTRATION_v5_hl.md) ----
VARIANTS = {
    "HL_SW5_RR":      dict(family="HL_SW", hl_level_mode="swing", hl_pivot_n=5, hl_exit_mode="rr", hl_max_entries=3),
    "HL_SW5_TRAIL":   dict(family="HL_SW", hl_level_mode="swing", hl_pivot_n=5, hl_exit_mode="trail", hl_max_entries=3),
    "HL_SW10_RR":     dict(family="HL_SW", hl_level_mode="swing", hl_pivot_n=10, hl_exit_mode="rr", hl_max_entries=3),
    "HL_PD_RR":       dict(family="HL_PD", hl_level_mode="prevday", hl_exit_mode="rr", hl_max_entries=1),
    "HL_PD_TRAIL":    dict(family="HL_PD", hl_level_mode="prevday", hl_exit_mode="trail", hl_max_entries=1),
    "HL_SW5_RR_BIAS": dict(family="HL_SW", hl_level_mode="swing", hl_pivot_n=5, hl_exit_mode="rr", hl_max_entries=3, hl_bias="sma200"),
}
# ---- v5b improvement variants (frozen 2026-11-13 04:45 UTC in results/PREREGISTRATION_v5b_hl_improve.md, before any was run)
_B = dict(family="HL_IMP", hl_level_mode="swing", hl_pivot_n=5, hl_exit_mode="rr", hl_max_entries=3, hl_min_stop_d1atr=0.10)
IMPROVE = {
    "HL_IMP_MS":       dict(_B),
    "HL_IMP_MS_T":     dict(_B, hl_trend="ema50"),
    "HL_IMP_MS_T_Q":   dict(_B, hl_trend="ema50", hl_adx_max=25.0),
    "HL_IMP_MS_T_A":   dict(_B, hl_trend="ema50", hl_min_age_min=60),
    "HL_IMP_MS_T_H":   dict(_B, hl_trend="ema50", hl_block_hours=[["07:00", "08:00"], ["13:00", "14:00"]]),
    "HL_IMP_MS_T_Q_A": dict(_B, hl_trend="ema50", hl_adx_max=25.0, hl_min_age_min=60),
    "HL_IMP_MS_EOD":   dict(_B, hl_exit_mode="eod"),
    "HL_IMP10_MS_T":   dict(_B, hl_pivot_n=10, hl_trend="ema50"),
}
VARIANTS.update(IMPROVE)
# ---- v5c: order hours and target on the improved base (frozen 2026-11-13 in the v5c addendum of PREREGISTRATION_v5b_hl_improve.md)
_C = dict(_B, family="HL_C", hl_pivot_n=10, hl_trend="ema50")
V5C = {
    "HL_C_W19":     dict(_C, hl_order_end="19:00"),
    "HL_C_W01":     dict(_C, hl_order_start="01:00"),
    "HL_C_W0119":   dict(_C, hl_order_start="01:00", hl_order_end="19:00"),
    "HL_C_T20":     dict(_C, hl_target_mult=2.0),
    "HL_C_T30":     dict(_C, hl_target_mult=3.0),
    "HL_C_EOD":     dict(_C, hl_exit_mode="eod"),
    "HL_C_W19_T20": dict(_C, hl_order_end="19:00", hl_target_mult=2.0),
    "HL_C_E5":      dict(_C, hl_order_end="19:00", hl_max_entries=5),
}
VARIANTS.update(V5C)
# ---- v7b: smaller profit targets on HL_C_W01 (frozen 2026-11-13 in the v7b addendum of PREREGISTRATION_v7_quick.md)
_W01 = dict(_C, hl_order_start="01:00")
V7B = {
    "HL_C_W01_T05":  dict(_W01, hl_target_mult=0.5),
    "HL_C_W01_T075": dict(_W01, hl_target_mult=0.75),
    "HL_C_W01_T10":  dict(_W01, hl_target_mult=1.0),
}
VARIANTS.update(V7B)
# ---- v8 family B: a bigger-timeframe direction reference on top of HL_C_W01 (frozen 2026-11-13 in PREREGISTRATION_v8_htf.md)
V8B = {
    "HL_C_W01_RH1": dict(_W01, hl_ref="h1"),
    "HL_C_W01_RH4": dict(_W01, hl_ref="h4"),
    "HL_C_W01_RD1": dict(_W01, hl_bias="sma200"),
    "HL_C_RH4ONLY": dict(_W01, hl_trend=None, hl_ref="h4"),
}
VARIANTS.update(V8B)
OOS = ("2024-07-01", "2026-11-01")       # pooled validation + final test, by signal_bar_open (perturbation report)

hhmm = E.hhmm
ONE_MIN = np.timedelta64(1, "m")
FIFTEEN = pd.Timedelta(minutes=15)


def pivot_flags(hi: np.ndarray, lo: np.ndarray, n: int):
    """Swing flags on consecutive M15 rows. is_ph[j] iff bar j has n bars on each side, hi[j] >= max(hi[j-n .. j-1]) and
    hi[j] >= max(hi[j+1 .. j+n]); is_pl[j] is the mirror with <= / min. The flag of bar j uses bars up to j+n, so it may
    only be USED from the close of bar j+n (the caller reads is_ph[i - n] at the close of bar i)."""
    m = len(hi); is_ph = np.zeros(m, dtype=bool); is_pl = np.zeros(m, dtype=bool)
    if m < 2 * n + 1: return is_ph, is_pl
    wmax = sliding_window_view(hi, n).max(axis=1)   # wmax[q] = max(hi[q .. q+n-1])
    wmin = sliding_window_view(lo, n).min(axis=1)
    j = np.arange(n, m - n)
    is_ph[j] = (hi[j] >= wmax[j - n]) & (hi[j] >= wmax[j + 1])
    is_pl[j] = (lo[j] <= wmin[j - n]) & (lo[j] <= wmin[j + 1])
    return is_ph, is_pl


def run(cfg: dict, m1: pd.DataFrame, out_dir):
    """Run one configuration. out_dir None -> nothing is written (used by --perturb)."""
    t0 = time.time()
    if out_dir is not None: out_dir.mkdir(parents=True, exist_ok=True)
    fam = cfg["family"]
    swing = cfg["hl_level_mode"] == "swing"; trail = cfg["hl_exit_mode"] == "trail"
    no_target = cfg["hl_exit_mode"] in ("trail", "eod")
    m15 = m1.resample("15min", label="left", closed="left").agg(open=("open", "first"), high=("high", "max"),
                                                                 low=("low", "min"), close=("close", "last")).dropna()
    ind = E.indicators(m15, cfg)
    hi, lo, atr = ind.high.values, ind.low.values, ind.atr.values
    cl15, adx15 = ind.close.values, ind.adx.values
    ema50 = ind.close.ewm(span=50, adjust=False).mean().values
    f_minstop, f_trend, f_adxmax, f_age = cfg.get("hl_min_stop_d1atr"), cfg.get("hl_trend"), cfg.get("hl_adx_max"), cfg.get("hl_min_age_min")
    f_block = [(E.hhmm(a), E.hhmm(b)) for a, b in (cfg.get("hl_block_hours") or [])]
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
    m1_day = (m1.index.values + np.timedelta64(1, "h")).astype("datetime64[D]")     # session day of each M1 bar (23:00 start)
    m15_day = (t15.values + np.timedelta64(1, "h")).astype("datetime64[D]")
    bar_start = np.searchsorted(m1_t, t15.values, side="left")
    bar_end = np.searchsorted(m1_t, (t15 + FIFTEEN).values, side="left")
    off = float(cfg["hl_offset"]); N = int(cfg["hl_pivot_n"])
    cap_k, floor_k = float(cfg["hl_stop_cap_d1atr"]), float(cfg["hl_stop_floor_atr"])
    tmult, trail_mult = float(cfg["hl_target_mult"]), float(cfg["hl_trail_mult"])
    max_entries = int(cfg["hl_max_entries"]); warm = int(cfg["warmup_bars"]); bias_mode = cfg["hl_bias"]
    ord_s, ord_e = hhmm(cfg["hl_order_start"]), hhmm(cfg["hl_order_end"])
    is_ph, is_pl = pivot_flags(hi, lo, N) if swing else (None, None)
    f_ref = cfg.get("hl_ref")
    if f_ref:
        # state of the reference at the last M1 bar of each M15 bar (last closed reference bar before the one containing it)
        tmin_all = m1.index.values.astype("datetime64[m]").astype(np.int64)
        slot = tmin_all // 60 if f_ref == "h1" else (tmin_all + 120) // 240
        assert f_ref in ("h1", "h4"), f_ref
        ref_up_m1, ref_dn_m1 = HR.ema_state(tmin_all, m1_c.astype(float), slot)
        ref_up15, ref_dn15 = ref_up_m1[bar_end - 1], ref_dn_m1[bar_end - 1]

    def prev_day(k):
        i = dpos.get(k)
        return None if i is None or i == 0 else daily.iloc[i - 1]

    trades, skips, levels = [], [], []
    pending = None; pos = None
    day = dict(key=None, entries=0, pdy=None)
    lvl = {"high": None, "low": None}     # the current marked level of each kind (live or consumed)
    calc = {}                             # side -> order parameters for the current pair of marked levels (D8)
    waited = set()
    counters = dict(ambiguous_stop_target=0, both_sides_same_minute=0, same_minute_stop=0, gap_fill_skipped=0,
                    levels_created_high=0, levels_created_low=0, high_consumed_bid=0, high_consumed_fill=0, low_consumed_bid=0,
                    low_consumed_fill=0, order_closes=0, order_closes_two_sided=0, order_params_computed=0,
                    stop_clamp_floor=0, stop_clamp_cap=0, stop_clamp_none=0)

    def log_skip(t, side, reason, **kw): skips.append(dict(signal_time=t, side=side, reason=reason, **kw))

    def wait(close_ts, reason):
        """No order at this close: count every close, log the first one per session day and reason."""
        counters["closes_" + reason] = counters.get("closes_" + reason, 0) + 1
        key = (day["key"], reason)
        if key not in waited:
            waited.add(key); log_skip(close_ts, "both", reason)

    def new_level(kind, price, created, source):
        """A newly created level replaces the old one of its kind, is live, and invalidates the cached order parameters."""
        old = lvl[kind]
        if old is not None: old["replaced_time"] = created
        rec = dict(kind=kind, price=price, trigger=(price + off) if kind == "high" else (price - off), created=created, source=source,
                   live=True, consumed_time=None, consumed_how=None, replaced_time=None, traded=False)
        lvl[kind] = rec; levels.append(rec); calc.clear()
        counters["levels_created_" + kind] += 1

    def consume(kind, t, how):
        rec = lvl[kind]; rec["live"] = False; rec["consumed_time"] = t; rec["consumed_how"] = how
        counters[f"{kind}_consumed_{how}"] += 1

    def consume_by_order(kind, t):
        """The resting order of this level was triggered in minute t (filled or refused by the gap rule)."""
        rec = lvl[kind]
        if rec["live"]: consume(kind, t, "fill")
        else:   # already consumed by the bid test at the top of this same minute: record the order as the cause
            assert rec["consumed_time"] == t and rec["consumed_how"] == "bid", "a resting order outlived its level"
            rec["consumed_how"] = "fill"; counters[f"{kind}_consumed_bid"] -= 1; counters[f"{kind}_consumed_fill"] += 1

    def open_pos(side, j, fill, level, stop, target, meta):
        risk = abs(level - stop)
        return dict(variant=cfg["variant"], family=fam, side=side, signal_time=meta["signal_time"], signal_bar_open=meta["signal_bar_open"],
                    entry_time=m1_t[j], entry_price=fill, level=level, initial_stop=stop, stop=stop, target=target, planned_risk=risk,
                    hh=fill, ll=fill, ambiguous=False, day=m1_day[j], **{k: v for k, v in meta.items() if k not in ("signal_time", "signal_bar_open")})

    def close_pos(p, t, px, reason):
        sign = 1.0 if p["side"] == "long" else -1.0
        pnl = sign * (px - p["entry_price"]) - comm
        rec = dict(p); rec.update(exit_time=t, exit_price=px, exit_reason=reason, pnl_per_oz=pnl, realised_R=pnl / p["planned_risk"],
                                  final_stop=p["stop"])
        for k in ("hh", "ll", "stop", "day"): rec.pop(k, None)
        trades.append(rec)

    def fill_entry(side, j, level, stop, target, meta):
        """Fill a buy/sell stop on M1 bar j (engine_v3.fill_entry for stop orders): gap rule, then same-minute stop check."""
        nonlocal pos
        bo, bh, bl = m1_o[j], m1_h[j], m1_l[j]; ao, ah = bo + spread, bh + spread
        fill = (max(level, ao) + slip) if side == "long" else (min(level, bo) - slip)
        past_stop = (fill <= stop) if side == "long" else (fill >= stop)
        past_tgt = target is not None and ((fill >= target) if side == "long" else (fill <= target))
        if past_stop or past_tgt:   # the first print after a gap is already beyond the planned stop or target: the order is not taken
            counters["gap_fill_skipped"] += 1
            log_skip(meta["signal_time"], side, "SKIP_gap_fill_past_stop" if past_stop else "SKIP_gap_fill_past_target", fill=fill, stop=stop,
                     target=target, minute=m1_t[j]); return
        lvl["high" if side == "long" else "low"]["traded"] = True
        meta["entry_no"] = day["entries"] + 1
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

    def order_params(side, i, close_ts, pdy):
        """Stop / target of one side for the current pair of marked levels, computed at the close of bar i (D8, D9)."""
        H, L = lvl["high"], lvl["low"]
        floor = floor_k * atr[i]; cap = cap_k * pdy.atr14
        if side == "long": trig = H["trigger"]; raw = trig - L["price"]
        else: trig = L["trigger"]; raw = H["price"] - trig
        dist = min(max(raw, floor), cap)
        clamp = "cap" if dist < raw else ("floor" if dist > raw else "none")
        counters["order_params_computed"] += 1; counters["stop_clamp_" + clamp] += 1
        if side == "long": stop = trig - dist; target = None if no_target else trig + tmult * dist
        else: stop = trig + dist; target = None if no_target else trig - tmult * dist
        return dict(trigger=trig, stop=stop, target=target, dist=dist, raw_dist=raw, stop_clamp=clamp, atr_m15=atr[i], d1atr=pdy.atr14,
                    calc_time=close_ts)

    def build_orders(i, close_ts):
        """The resting OCO set after the close of bar i (flat, inside the order window), or None."""
        H, L = lvl["high"], lvl["low"]
        if day["entries"] >= max_entries: wait(close_ts, "WAIT_daily_cap"); return None
        if H is None or L is None: wait(close_ts, "WAIT_no_opposite_level"); return None
        if i < warm or np.isnan(atr[i]): wait(close_ts, "WAIT_warmup"); return None
        pdy = day["pdy"]
        if pdy is None or np.isnan(pdy.atr14): wait(close_ts, "WAIT_d1atr_undefined"); return None
        allow_long = allow_short = True; bias = "none"
        if bias_mode == "sma200":
            if np.isnan(pdy.sma200): wait(close_ts, "WAIT_bias_undefined"); return None
            allow_long, allow_short = bool(pdy.close > pdy.sma200), bool(pdy.close < pdy.sma200)
            bias = "long" if allow_long else ("short" if allow_short else "flat")
        want_buy, want_sell = H["live"] and allow_long, L["live"] and allow_short
        if not (want_buy or want_sell):
            wait(close_ts, "WAIT_no_live_level" if not (H["live"] or L["live"]) else "WAIT_live_level_against_bias"); return None
        # ---- v5b improvement filters (all off in the six frozen readings)
        if f_adxmax is not None and not np.isnan(adx15[i]) and adx15[i] > f_adxmax: wait(close_ts, "WAIT_adx_above_max"); return None
        if f_block and any(a <= (mod15[i] + 15) % 1440 < b for a, b in f_block): wait(close_ts, "WAIT_blocked_hour"); return None
        if f_trend == "ema50":
            want_buy, want_sell = want_buy and cl15[i] > ema50[i], want_sell and cl15[i] < ema50[i]
        if f_ref:
            want_buy, want_sell = want_buy and bool(ref_up15[i]), want_sell and bool(ref_dn15[i])
        if f_age is not None:
            age = pd.Timedelta(minutes=int(f_age))
            want_buy = want_buy and (close_ts - pd.Timestamp(H["created"])) >= age
            want_sell = want_sell and (close_ts - pd.Timestamp(L["created"])) >= age
        if not (want_buy or want_sell): wait(close_ts, "WAIT_filtered"); return None
        for side, want in (("long", want_buy), ("short", want_sell)):
            if want and side not in calc: calc[side] = order_params(side, i, close_ts, pdy)
        if f_minstop is not None:
            if want_buy and calc["long"]["dist"] < f_minstop * pdy.atr14: want_buy = False
            if want_sell and calc["short"]["dist"] < f_minstop * pdy.atr14: want_sell = False
            if not (want_buy or want_sell): wait(close_ts, "WAIT_stop_too_small"); return None
        counters["order_closes"] += 1; counters["order_closes_two_sided"] += int(want_buy and want_sell)
        common = dict(signal_time=close_ts, signal_bar_open=t15[i], level_high=H["price"], level_low=L["price"],
                      level_high_created=H["created"], level_low_created=L["created"], level_high_live=H["live"], level_low_live=L["live"],
                      bias=bias)
        cl_, cs_ = calc.get("long"), calc.get("short")
        return dict(kind="stop", cancel_min=ord_e, day=m15_day[i], meta=common,
                    buy=cl_["trigger"] if want_buy else None, sell=cs_["trigger"] if want_sell else None,
                    stop_long=cl_["stop"] if want_buy else None, stop_short=cs_["stop"] if want_sell else None,
                    target_long=cl_["target"] if want_buy else None, target_short=cs_["target"] if want_sell else None,
                    meta_long={k: v for k, v in cl_.items() if k not in ("trigger", "stop", "target")} if want_buy else None,
                    meta_short={k: v for k, v in cs_.items() if k not in ("trigger", "stop", "target")} if want_sell else None)

    for i in range(len(ind)):
        k = skey[i]
        if k != day["key"]:
            # ---- new session day (23:00 UTC): reset per-day state; daily quantities are previous-day values
            day.update(key=k, entries=0, pdy=prev_day(k))
            if not swing:   # previous-day readings: the pair of levels is created here, before the day's first M1 bar is simulated
                pdy = day["pdy"]
                if pdy is not None:
                    new_level("high", float(pdy.high), t15[i], str(pdy.name)); new_level("low", float(pdy.low), t15[i], str(pdy.name))
                else:
                    lvl["high"] = lvl["low"] = None; calc.clear()
        H, L = lvl["high"], lvl["low"]
        # ---- 1) simulate the M1 bars of bar i against standing orders / open position; level consumption on every minute
        if pending is not None or pos is not None:
            for j in range(bar_start[i], bar_end[i]):
                bo, bh, bl, bc, mod = m1_o[j], m1_h[j], m1_l[j], m1_c[j], m1_mod[j]
                ao, ah, al = bo + spread, bh + spread, bl + spread
                if H is not None and H["live"] and bh >= H["trigger"]: consume("high", m1_t[j], "bid")
                if L is not None and L["live"] and bl <= L["trigger"]: consume("low", m1_t[j], "bid")
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
                    if trail:   # Chandelier on the running extreme since the fill, ATR14 of the last CLOSED M15 bar, ratchet only,
                        pos["hh"] = max(pos["hh"], bh); pos["ll"] = min(pos["ll"], bl)   # never beyond this minute's extreme
                        if side == "long":
                            new = pos["hh"] - trail_mult * atr[i - 1]
                            if new > pos["stop"] and new < bl: pos["stop"] = new
                        else:
                            new = pos["ll"] + trail_mult * atr[i - 1]
                            if new < pos["stop"] and new > ah: pos["stop"] = new
                elif pending is not None:
                    if mod >= pending["cancel_min"]:
                        log_skip(pending["meta"]["signal_time"], "both", "CANCEL_unfilled_at_cutoff"); pending = None; continue
                    if m1_day[j] != pending["day"]:
                        log_skip(pending["meta"]["signal_time"], "both", "CANCEL_session_ended"); pending = None; continue
                    hit_buy = pending["buy"] is not None and ah >= pending["buy"]
                    hit_sell = pending["sell"] is not None and bl <= pending["sell"]
                    if hit_buy and hit_sell:
                        counters["both_sides_same_minute"] += 1
                        if (pending["buy"] - ao) <= (bo - pending["sell"]): hit_sell = False   # the edge nearer the open is reached first
                        else: hit_buy = False
                    if hit_buy:
                        p = pending; pending = None   # OCO: the sell stop is cancelled with it
                        consume_by_order("high", m1_t[j])
                        fill_entry("long", j, p["buy"], p["stop_long"], p["target_long"], dict(p["meta"], **p["meta_long"]))
                        continue
                    if hit_sell:
                        p = pending; pending = None
                        consume_by_order("low", m1_t[j])
                        fill_entry("short", j, p["sell"], p["stop_short"], p["target_short"], dict(p["meta"], **p["meta_short"]))
                        continue
        else:   # nothing rests and nothing is open: the M15 bar's extremes (= the extremes of its M1 bars) decide consumption
            if H is not None and H["live"] and hi[i] >= H["trigger"]:
                s = bar_start[i]; consume("high", m1_t[s + int(np.argmax(m1_h[s:bar_end[i]] >= H["trigger"]))], "bid")
            if L is not None and L["live"] and lo[i] <= L["trigger"]:
                s = bar_start[i]; consume("low", m1_t[s + int(np.argmax(m1_l[s:bar_end[i]] <= L["trigger"]))], "bid")
        # ---- 2) level creation at the close of bar i (bar i is closed; bar i+1 has not started)
        close_ts = t15[i] + FIFTEEN
        if swing and i >= N:   # the pivot at bar i-N needs the N bars after it: confirmed only now (no look-ahead)
            j0 = i - N
            if is_ph[j0]: new_level("high", float(hi[j0]), close_ts, str(t15[j0]))
            if is_pl[j0]: new_level("low", float(lo[j0]), close_ts, str(t15[j0]))
        # ---- 3) order step: closes with close time in [07:00, 16:00), flat; the OCO set is rebuilt from the levels live now
        if pos is not None: continue
        if not (ord_s <= mod15[i] + 15 < ord_e): continue   # an order still resting after the last step is cancelled by the M1 loop at 16:00
        pending = build_orders(i, close_ts)
    # end of data: nothing should be open (20:50 exit); kept from engine_v3 so that an open position would be counted
    if pos is not None:
        j = len(m1_t) - 1
        close_pos(pos, m1_t[j], m1_c[j] - slip if pos["side"] == "long" else m1_c[j] + spread + slip, "end_of_data"); pos = None
    tr = pd.DataFrame(trades)
    if len(tr):
        tr["hold_minutes"] = (pd.to_datetime(tr.exit_time) - pd.to_datetime(tr.entry_time)).dt.total_seconds() / 60
        tr["signal_date"] = pd.to_datetime(tr.signal_bar_open).dt.date
    sk = pd.DataFrame(skips)
    meta = dict(config=cfg, n_trades=int(len(tr)), n_skips=len(skips), counters=counters, n_levels=len(levels), m15_bars=int(len(ind)),
                m1_bars=int(len(m1)), data_start=str(m1.index[0]), data_end=str(m1.index[-1]), run_seconds=round(time.time() - t0, 1),
                run_time_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    if out_dir is not None:
        tr.to_csv(out_dir / "trades.csv", index=False)
        sk.to_csv(out_dir / "skips.csv", index=False)
        lv = pd.DataFrame(levels)
        if len(lv):
            for c in ("created", "consumed_time", "replaced_time"): lv[c] = pd.to_datetime(lv[c], utc=True)
        lv.to_csv(out_dir / "levels.csv", index=False)
        (out_dir / "config.json").write_text(json.dumps(meta, indent=2, default=str))
    return tr, sk, meta


def make_cfg(name: str):
    vid = name[len(PREFIX):] if name.startswith(PREFIX) else name
    if vid not in VARIANTS: raise SystemExit(f"unknown variant {name}; known: {', '.join(VARIANTS)}")
    cfg = dict(V5_CONFIG); cfg.update(VARIANTS[vid]); cfg["variant"] = PREFIX + vid
    return cfg, vid


_M1 = None
def _worker(name):
    cfg, vid = make_cfg(name)
    tr, sk, meta = run(cfg, _M1, RESULTS / (PREFIX + vid))
    return f"{PREFIX + vid}: trades={len(tr)} skips={len(sk)} levels={meta['n_levels']} counters={meta['counters']} secs={meta['run_seconds']}"


def perturb_grid(cfg: dict):
    """(param, mult, value) for the +-20 % one-at-a-time perturbation; only parameters this reading uses (D14)."""
    params = (["hl_pivot_n"] if cfg["hl_level_mode"] == "swing" else []) + ["hl_offset", "hl_stop_cap_d1atr", "hl_stop_floor_atr"]
    params += ["hl_target_mult" if cfg["hl_exit_mode"] == "rr" else "hl_trail_mult", "hl_max_entries"]
    grid, skipped = [], []
    for p in params:
        base = cfg[p]
        for mult in (0.8, 1.2):
            v = int(round(base * mult)) if isinstance(base, int) else base * mult
            if v == base: skipped.append((p, mult, v)); continue
            grid.append((p, mult, v))
    return grid, skipped


def _perturb_worker(args):
    name, param, mult, value = args
    cfg, vid = make_cfg(name); cfg[param] = value; cfg["variant"] = f"{PREFIX}{vid}_perturb_{param}_{mult}"
    tr, _, meta = run(cfg, _M1, None)
    row = dict(param=param, mult=mult, value=value, n_oos=0, meanR_oos=None, pf_oos=None)
    if len(tr):
        sbo = pd.to_datetime(tr.signal_bar_open, utc=True)
        r = tr.realised_R[(sbo >= pd.Timestamp(OOS[0], tz="UTC")) & (sbo < pd.Timestamp(OOS[1], tz="UTC"))].values
        if len(r):
            wins, losses = r[r > 0].sum(), r[r <= 0].sum()
            row.update(n_oos=int(len(r)), meanR_oos=float(r.mean()), pf_oos=float(wins / abs(losses)) if losses != 0 else None)
    return row


def perturb(name: str, jobs: int = 2):
    """+-20 % one-at-a-time perturbation of the numeric parameters; pooled validation + final-test statistics only; the base
    trades.csv is not touched (perturbation runs write nothing but perturb.json)."""
    cfg, vid = make_cfg(name)
    grid, skipped = perturb_grid(cfg)
    for p, mult, v in skipped: print(f"perturb {p} x{mult}: unchanged ({v}), skipped")
    args = [(name, p, mult, v) for p, mult, v in grid]
    rows = []
    if jobs > 1 and len(args) > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(min(jobs, 2)) as pool:
            for r in pool.imap(_perturb_worker, args): rows.append(r); print(r, flush=True)
    else:
        for a in args: r = _perturb_worker(a); rows.append(r); print(r, flush=True)
    out = RESULTS / (PREFIX + vid); out.mkdir(parents=True, exist_ok=True)
    (out / "perturb.json").write_text(json.dumps(rows, indent=2, default=str))
    print(f"wrote {out / 'perturb.json'} ({len(rows)} rows)")


def main():
    global _M1
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--variant", help="reading id, e.g. HL_SW5_RR"); ap.add_argument("--all", action="store_true")
    ap.add_argument("--perturb", help="reading id: +-20%% one-at-a-time perturbation -> results/V5_<ID>/perturb.json")
    ap.add_argument("--jobs", type=int, default=2, help="processes for --all / --perturb (capped at 2; the machine is shared)")
    ap.add_argument("--data", default=str(E.DATA)); ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list: print("\n".join(f"{v}: {VARIANTS[v]}" for v in VARIANTS)); return
    jobs = max(1, min(a.jobs, 2))
    _M1 = pd.read_parquet(a.data)
    t0 = time.time()
    if a.perturb:
        perturb(a.perturb, jobs=jobs); print(f"total wall time {time.time() - t0:.0f} s"); return
    names = list(VARIANTS) if a.all else [a.variant or "HL_SW5_RR"]
    if jobs > 1 and len(names) > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(jobs) as pool:
            for line in pool.imap_unordered(_worker, names): print(line, flush=True)
    else:
        for n in names: print(_worker(n), flush=True)
    print(f"total wall time {time.time() - t0:.0f} s")

if __name__ == "__main__":
    main()
