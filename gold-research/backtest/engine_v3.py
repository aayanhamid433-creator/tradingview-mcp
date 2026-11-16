#!/usr/bin/env python3
"""engine_v3.py — pre-registered ALTERNATIVE strategy families on XAUUSD M1 (sixth look at the same data).

Question: does any family other than the EMA20 pullback (v1/v2) produce a positive, cost-adjusted, out-of-sample
edge with more trades per month, on the same data, costs, session day and time exit?

Shared with engine.py / engine_v2.py: BASE_CONFIG costs (spread 0.25, slippage 0.05, commission 0), M15 decisions on
closed bars, M1 fill simulation (prices are BID; ask = bid + spread), stop-first ambiguity, stop_same_minute handling,
20:50 UTC time exit, session day 23:00 -> 23:00 UTC (engine_v2.daily_frame), previous-day values for all daily
quantities, ATR of the last CLOSED bar / previous session day for any trailing. No partial exits in v3: every family
has its own full exit as specified below. No news gate.

Families (all variants pre-registered here BEFORE any run; nothing may be added after seeing results):
  F1 ORB  opening-range breakout. Range = M15 bars of [range_start, range_end). Buy stop range_high + 0.10 / sell stop
          range_low - 0.10 placed at the close of the range, OCO, cancelled at orb_cancel if unfilled. Stop = opposite
          edge, distance capped at 0.6 x D1ATR(prev day); day skipped if range < 0.15 x D1ATR. Target = m x range.
          One trade per session day.
  F2 VB   volatility breakout (Larry Williams). At the first M1 bar at/after 07:00 UTC: buy stop open + k x D1ATR,
          sell stop open - k x D1ATR (OCO, cancel 16:00). Stop = the 07:00 open (distance k x D1ATR), target 1.5 x that
          distance. One trade per day. "_bias" variants: long only above / short only below the daily SMA200
          (previous session-day close vs SMA200, exactly as engine_v2 computes it).
  F3 VW   session "VWAP" mean reversion. VWAP from the 23:00 UTC session start on M1 closes with volume proxy 1
          (the data has NO volume: this is a time-weighted average price, TWAP). Band = +/- s x running population std of
          (close - vwap) within the session, minimum 1 USD. Signal = M15 close beyond a band AND ADX14(M15) < adx_max,
          window 07:00-15:45 UTC; market order on the next M1 bar towards VWAP; stop = 1 x ATR14(M15) beyond the
          signal bar's extreme; target = VWAP at signal time; max 2 trades per session day.
  F4 DC   daily Donchian trend following, HELD OVERNIGHT (breaks the account's flat-by-night habit; flagged).
          Previous-session-day basis: buy stop at the N-day high, sell stop at the N-day low (OCO, standing all day,
          re-placed at every session start while flat). Exit stop = the closer of the M-day low/high and a 2 x D1ATR
          Chandelier trail from the running extreme, ratchet only, updated at each session start and on M1. No time
          exit. One position at a time; at most one entry per session day.
  max_hold_minutes (coordinator addition, pre-registered before the first run): when set, a position that has hit
          neither stop nor target is closed at the close of the M1 bar that closes max_hold_minutes after the open of
          the fill minute, at bid close - slippage (long) or bid close + spread + slippage (short), commission as usual.

Usage: python3 engine_v3.py --all [--jobs 4] | --variant V3_ORB_L10
Outputs: ../results/<variant>/trades.csv, skips.csv, config.json
"""
import argparse, json, pathlib, datetime as dt, time, sys
import numpy as np, pandas as pd
import engine as E
import engine_v2 as V2

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"

V3_CONFIG = dict(E.BASE_CONFIG)
V3_CONFIG.update(dict(
    version="v3.0-families",
    family=None,
    time_exit="20:50",
    max_hold_minutes=None,
    warmup_bars=200,
    # F1 ORB
    orb_range_start="07:00", orb_range_end="08:00", orb_cancel="11:00", orb_offset=0.10,
    orb_stop_cap_d1atr=0.6, orb_min_range_d1atr=0.15, orb_target_mult=1.0,
    # F2 VB
    vb_open="07:00", vb_cancel="16:00", vb_k=0.3, vb_target_mult=1.5, vb_bias=None,
    # F3 VW
    vw_sigma=2.0, vw_adx_max=20.0, vw_min_band=1.0, vw_stop_atr=1.0, vw_start="07:00", vw_end="15:45", vw_max_trades=2,
    # F4 DC
    dc_entry_n=20, dc_exit_n=10, dc_trail_atr=2.0,
))
for _k in ("adx_threshold", "adx_rising_lookback", "adx_cancel_below", "entry_offset", "stop_buffer_min", "stop_buffer_atr",
           "deep_break_atr", "target_lookback", "min_rr", "rearm", "expiry_bars", "signal_start", "signal_end", "pending_cutoff",
           "max_trades_per_day", "news_filter", "news_window_min"):
    V3_CONFIG.pop(_k, None)   # v1 pullback parameters are not used by any v3 family

# ---- PRE-REGISTERED VARIANT LIST (frozen 2026-11-12 before the first run) ----
VARIANTS = {
    # F1 opening-range breakout
    "V3_ORB_L10":  dict(family="ORB"),
    "V3_ORB_L15":  dict(family="ORB", orb_target_mult=1.5),
    "V3_ORB_NY10": dict(family="ORB", orb_range_start="13:30", orb_range_end="14:00", orb_cancel="16:00"),
    "V3_ORB_NY15": dict(family="ORB", orb_range_start="13:30", orb_range_end="14:00", orb_cancel="16:00", orb_target_mult=1.5),
    # F2 volatility breakout
    "V3_VB_03":      dict(family="VB", vb_k=0.3),
    "V3_VB_05":      dict(family="VB", vb_k=0.5),
    "V3_VB_03_bias": dict(family="VB", vb_k=0.3, vb_bias="sma200"),
    "V3_VB_05_bias": dict(family="VB", vb_k=0.5, vb_bias="sma200"),
    # F3 session-VWAP (TWAP) mean reversion
    "V3_VW_2s":       dict(family="VW", vw_sigma=2.0, vw_adx_max=20.0),
    "V3_VW_25s":      dict(family="VW", vw_sigma=2.5, vw_adx_max=20.0),
    "V3_VW_2s_adx15": dict(family="VW", vw_sigma=2.0, vw_adx_max=15.0),
    # F4 daily Donchian (overnight)
    "V3_DC_20_10": dict(family="DC", dc_entry_n=20, dc_exit_n=10),
    "V3_DC_55_20": dict(family="DC", dc_entry_n=55, dc_exit_n=20),
    # 15-minute maximum hold, one per intraday family, applied to the first variant of each family (coordinator, 2026-11-12,
    # added to the pre-registration before any variant was run)
    "V3_ORB_L10_h15": dict(family="ORB", max_hold_minutes=15),
    "V3_VB_03_h15":   dict(family="VB", vb_k=0.3, max_hold_minutes=15),
    "V3_VW_2s_h15":   dict(family="VW", vw_sigma=2.0, vw_adx_max=20.0, max_hold_minutes=15),
}
FAMILY_OF = {v: VARIANTS[v]["family"] for v in VARIANTS}

hhmm = E.hhmm
ONE_MIN = np.timedelta64(1, "m")


def session_twap(m1: pd.DataFrame):
    """Running TWAP (volume proxy = 1) and running population std of (close - twap) within each 23:00 UTC session day."""
    key = (m1.index + pd.Timedelta(hours=1)).date
    df = pd.DataFrame({"k": key, "c": m1.close.values})
    g = df.groupby("k", sort=False)
    n = g.cumcount().values + 1
    twap = g.c.cumsum().values / n
    dev = df.c.values - twap
    df["d"] = dev; df["d2"] = dev * dev
    g = df.groupby("k", sort=False)
    s1 = g.d.cumsum().values; s2 = g.d2.cumsum().values
    var = s2 / n - (s1 / n) ** 2
    sd = np.sqrt(np.maximum(var, 0.0))
    return twap, sd


def run(cfg: dict, m1: pd.DataFrame, out_dir: pathlib.Path):
    t0 = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)
    fam = cfg["family"]
    m15 = m1.resample("15min", label="left", closed="left").agg(open=("open", "first"), high=("high", "max"),
                                                                 low=("low", "min"), close=("close", "last")).dropna()
    ind = E.indicators(m15, cfg)
    hi, lo, cl, atr, adx = ind.high.values, ind.low.values, ind.close.values, ind.atr.values, ind.adx.values
    t15 = ind.index
    mod15 = (t15.hour * 60 + t15.minute).values
    skey = (t15 + pd.Timedelta(hours=1)).date
    daily = V2.daily_frame(m1)
    daily["hh_entry"] = daily.high.rolling(cfg["dc_entry_n"]).max().shift(1)
    daily["ll_entry"] = daily.low.rolling(cfg["dc_entry_n"]).min().shift(1)
    daily["hh_exit"] = daily.high.rolling(cfg["dc_exit_n"]).max().shift(1)
    daily["ll_exit"] = daily.low.rolling(cfg["dc_exit_n"]).min().shift(1)
    dpos = {k: i for i, k in enumerate(daily.index)}
    spread, slip, comm = cfg["spread"], cfg["slippage"], cfg["commission_rt"]
    texit_min = None if fam == "DC" else hhmm(cfg["time_exit"])
    max_hold = cfg["max_hold_minutes"]
    hold_td = np.timedelta64(int(max_hold) - 1, "m") if max_hold else None
    m1_t = m1.index.values; m1_o, m1_h, m1_l, m1_c = (m1[k].values for k in ("open", "high", "low", "close"))
    m1_mod = (m1.index.hour * 60 + m1.index.minute).values
    # session-day number of each M1 / M15 bar (23:00 UTC start). Intraday positions and orders may not outlive their session
    # day: on days where the feed ends before 20:50 (early closes, feed gaps) they are closed / cancelled at the first bar
    # of the next session day instead of leaking into it (engine_v2 has this leak; v3 does not).
    m1_day = (m1.index.values + np.timedelta64(1, "h")).astype("datetime64[D]")
    m15_day = (t15.values + np.timedelta64(1, "h")).astype("datetime64[D]")
    bar_start = np.searchsorted(m1_t, t15.values, side="left")
    bar_end = np.searchsorted(m1_t, (t15 + pd.Timedelta(minutes=15)).values, side="left")
    twap = sd = None
    if fam == "VW": twap, sd = session_twap(m1)
    # family time parameters
    orb_s, orb_e, orb_cancel = hhmm(cfg["orb_range_start"]), hhmm(cfg["orb_range_end"]), hhmm(cfg["orb_cancel"])
    orb_nbars = (orb_e - orb_s) // 15
    vb_open, vb_cancel = hhmm(cfg["vb_open"]), hhmm(cfg["vb_cancel"])
    vw_s, vw_e = hhmm(cfg["vw_start"]), hhmm(cfg["vw_end"])

    def prev_day(k):
        i = dpos.get(k)
        return None if i is None or i == 0 else daily.iloc[i - 1]

    trades, skips = [], []
    pending = None; pos = None
    day = dict(key=None, entries=0, done=False, pdy=None, armed_time=None)
    counters = dict(ambiguous_stop_target=0, both_sides_same_minute=0, same_minute_stop=0, gap_fill_skipped=0)

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
        """Fill a buy/sell stop (level given) or a market order (level None) on M1 bar j; same-minute stop check as engine_v2."""
        nonlocal pos
        bo, bh, bl = m1_o[j], m1_h[j], m1_l[j]; ao, ah = bo + spread, bh + spread
        fill = ((max(level_or_none, ao) if level_or_none is not None else ao) + slip) if side == "long" else ((min(level_or_none, bo) if level_or_none is not None else bo) - slip)
        past_stop = (fill <= stop) if side == "long" else (fill >= stop)
        past_tgt = target is not None and ((fill >= target) if side == "long" else (fill <= target))
        if past_stop or past_tgt:   # the first print after a gap is already beyond the planned stop or target: the order is not taken
            counters["gap_fill_skipped"] += 1
            log_skip(meta["signal_time"], side, "SKIP_gap_fill_past_stop" if past_stop else "SKIP_gap_fill_past_target", fill=fill, stop=stop, target=target); return
        if side == "long":
            level = level_or_none if level_or_none is not None else fill
            pos = open_pos("long", m1_t[j], fill, level, stop, target, meta); day["entries"] += 1
            if bl <= stop:
                counters["same_minute_stop"] += 1
                close_pos(pos, m1_t[j], (min(stop, bl) - slip if bl < stop else stop - slip), "stop_same_minute"); pos = None
        else:
            level = level_or_none if level_or_none is not None else fill
            pos = open_pos("short", m1_t[j], fill, level, stop, target, meta); day["entries"] += 1
            if ah >= stop:
                counters["same_minute_stop"] += 1
                close_pos(pos, m1_t[j], stop + slip, "stop_same_minute"); pos = None

    def dc_arm(k, when):
        """Place Donchian entry stops for session day k from previous-day values (only while flat)."""
        row = daily.iloc[dpos[k]] if k in dpos else None
        if row is None or np.isnan(row.hh_entry) or np.isnan(row.ll_entry) or np.isnan(row.ll_exit): return None
        pdy = prev_day(k)
        if pdy is None or np.isnan(pdy.atr14): return None
        return dict(kind="stop", buy=row.hh_entry, sell=row.ll_entry, cancel_min=None,
                    stop_long=max(row.ll_exit, row.hh_entry - cfg["dc_trail_atr"] * pdy.atr14),
                    stop_short=min(row.hh_exit, row.ll_entry + cfg["dc_trail_atr"] * pdy.atr14),
                    target_long=None, target_short=None,
                    meta=dict(signal_time=when, signal_bar_open=when, d1atr=pdy.atr14, dc_exit_long=row.ll_exit, dc_exit_short=row.hh_exit))

    for i in range(cfg["warmup_bars"], len(ind)):
        k = skey[i]
        if k != day["key"]:
            # ---- new session day (23:00 UTC): reset per-day state; daily quantities are previous-day values
            day.update(key=k, entries=0, done=False, pdy=prev_day(k), armed_time=t15[i])
            if fam == "DC":
                pdy = day["pdy"]; row = daily.iloc[dpos[k]] if k in dpos else None
                if pos is not None and row is not None and pdy is not None and not np.isnan(pdy.atr14):
                    pos["d1atr"] = pdy.atr14   # trail distance for today uses yesterday's D1 ATR
                    if pos["side"] == "long" and not np.isnan(row.ll_exit):
                        pos["stop"] = max(pos["stop"], row.ll_exit, pos["hh"] - cfg["dc_trail_atr"] * pdy.atr14)
                    elif pos["side"] == "short" and not np.isnan(row.hh_exit):
                        pos["stop"] = min(pos["stop"], row.hh_exit, pos["ll"] + cfg["dc_trail_atr"] * pdy.atr14)
                if pos is None: pending = dc_arm(k, t15[i])
        # ---- 1) simulate the M1 bars of bar i against standing orders / open position
        if pending is not None or pos is not None:
            for j in range(bar_start[i], bar_end[i]):
                bo, bh, bl, bc, mod = m1_o[j], m1_h[j], m1_l[j], m1_c[j], m1_mod[j]
                ao, ah, al = bo + spread, bh + spread, bl + spread
                if pos is not None:
                    side = pos["side"]
                    if texit_min is not None and m1_day[j] != pos["day"]:
                        close_pos(pos, m1_t[j], bo - slip if side == "long" else ao + slip, "session_gap_exit"); pos = None; continue
                    if texit_min is not None and mod >= texit_min:
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
                    if fam == "DC":   # Chandelier trail on running extreme, ratchet only, never beyond this minute's extreme
                        pos["hh"] = max(pos["hh"], bh); pos["ll"] = min(pos["ll"], bl)
                        if side == "long":
                            new = pos["hh"] - cfg["dc_trail_atr"] * pos["d1atr"]
                            if new > pos["stop"] and new < bl: pos["stop"] = new
                        else:
                            new = pos["ll"] + cfg["dc_trail_atr"] * pos["d1atr"]
                            if new < pos["stop"] and new > ah: pos["stop"] = new
                elif pending is not None:
                    if pending["cancel_min"] is not None and mod >= pending["cancel_min"]:
                        log_skip(pending["meta"]["signal_time"], "both", "CANCEL_unfilled_at_cutoff"); pending = None; continue
                    if pending.get("day") is not None and m1_day[j] != pending["day"]:
                        log_skip(pending["meta"]["signal_time"], "both", "CANCEL_session_ended"); pending = None; continue
                    if pending["kind"] == "arm_at_open":   # F2: set levels from this minute's open (the 07:00 open print)
                        d = pending["k"] * pending["meta"]["d1atr"]
                        pending.update(kind="stop", buy=(bo + d) if pending["allow_long"] else None, sell=(bo - d) if pending["allow_short"] else None,
                                       stop_long=bo, stop_short=bo, target_long=bo + d + cfg["vb_target_mult"] * d,
                                       target_short=bo - d - cfg["vb_target_mult"] * d)
                        pending["meta"].update(session_open=bo, open_time=m1_t[j])
                    if pending["kind"] == "market":
                        side = pending["side"]; meta = pending["meta"]
                        pending = None
                        stop, target = meta.pop("stop"), meta.pop("target")
                        fill_entry(side, j, None, stop, target, meta)
                        continue
                    hit_buy = pending["buy"] is not None and ah >= pending["buy"]
                    hit_sell = pending["sell"] is not None and bl <= pending["sell"]
                    if hit_buy and hit_sell:
                        counters["both_sides_same_minute"] += 1
                        if (pending["buy"] - ao) <= (bo - pending["sell"]): hit_sell = False   # the edge nearer the open is reached first
                        else: hit_buy = False
                    if hit_buy:
                        p = pending; pending = None; day["done"] = True
                        fill_entry("long", j, p["buy"], p["stop_long"], p["target_long"], dict(p["meta"]))
                        continue
                    if hit_sell:
                        p = pending; pending = None; day["done"] = True
                        fill_entry("short", j, p["sell"], p["stop_short"], p["target_short"], dict(p["meta"]))
                        continue
        # ---- 2) decisions at the close of bar i (bar i is closed; bar i+1 has not started)
        if np.isnan(atr[i]) or np.isnan(adx[i]): continue
        mod_i = mod15[i]
        pdy = day["pdy"]
        d1atr = pdy.atr14 if pdy is not None and not np.isnan(pdy.atr14) else np.nan
        close_ts = t15[i] + pd.Timedelta(minutes=15)
        if fam == "ORB":
            if day["done"] or pos is not None or pending is not None or mod_i != orb_e - 15: continue
            day["done"] = True   # one attempt per session day
            idx = list(range(i - orb_nbars + 1, i + 1))
            if idx[0] < 0 or any(skey[q] != k or mod15[q] != orb_s + 15 * n for n, q in enumerate(idx)):
                log_skip(close_ts, "both", "SKIP_range_bars_missing"); continue
            if np.isnan(d1atr): log_skip(close_ts, "both", "SKIP_d1atr_undefined"); continue
            rh, rl = hi[idx].max(), lo[idx].min(); rng = rh - rl
            if rng < cfg["orb_min_range_d1atr"] * d1atr:
                log_skip(close_ts, "both", "SKIP_range_too_small", range=rng, d1atr=d1atr); continue
            buy, sell = rh + cfg["orb_offset"], rl - cfg["orb_offset"]
            cap = cfg["orb_stop_cap_d1atr"] * d1atr
            pending = dict(kind="stop", buy=buy, sell=sell, cancel_min=orb_cancel, day=m15_day[i],
                           stop_long=max(rl, buy - cap), stop_short=min(rh, sell + cap),
                           target_long=buy + cfg["orb_target_mult"] * rng, target_short=sell - cfg["orb_target_mult"] * rng,
                           meta=dict(signal_time=close_ts, signal_bar_open=t15[i], range_high=rh, range_low=rl, range=rng, d1atr=d1atr,
                                     stop_capped=(rng + cfg["orb_offset"]) > cap))
        elif fam == "VB":
            if day["done"] or pos is not None or pending is not None or mod_i != vb_open - 15: continue
            day["done"] = True
            if np.isnan(d1atr): log_skip(close_ts, "both", "SKIP_d1atr_undefined"); continue
            allow_long = allow_short = True; bias = "none"
            if cfg["vb_bias"] == "sma200":
                if pdy is None or np.isnan(pdy.sma200): log_skip(close_ts, "both", "SKIP_bias_undefined"); continue
                bias = "long" if pdy.close > pdy.sma200 else "short"
                allow_long, allow_short = bias == "long", bias == "short"
            pending = dict(kind="arm_at_open", k=cfg["vb_k"], allow_long=allow_long, allow_short=allow_short, cancel_min=vb_cancel, day=m15_day[i],
                           meta=dict(signal_time=close_ts, signal_bar_open=t15[i], d1atr=d1atr, k=cfg["vb_k"], bias=bias))
        elif fam == "VW":
            if pos is not None or pending is not None or not (vw_s <= mod_i <= vw_e) or day["entries"] >= cfg["vw_max_trades"]: continue
            if adx[i] >= cfg["vw_adx_max"]: continue
            jlast = bar_end[i] - 1
            v, s = twap[jlast], max(sd[jlast], cfg["vw_min_band"])
            upper, lower = v + cfg["vw_sigma"] * s, v - cfg["vw_sigma"] * s
            if cl[i] > upper: side, stop = "short", hi[i] + cfg["vw_stop_atr"] * atr[i]
            elif cl[i] < lower: side, stop = "long", lo[i] - cfg["vw_stop_atr"] * atr[i]
            else: continue
            pending = dict(kind="market", side=side, cancel_min=None, day=m15_day[i],
                           meta=dict(signal_time=close_ts, signal_bar_open=t15[i], stop=stop, target=v, vwap=v, band_sd=s, adx=adx[i],
                                     atr=atr[i], signal_close=cl[i]))
        # DC: nothing at M15 closes; orders are (re)placed at the session start only
    # end of data: an open DC position is closed at the last bar's close (flagged) so that it is counted
    if pos is not None:
        j = len(m1_t) - 1
        close_pos(pos, m1_t[j], m1_c[j] - slip if pos["side"] == "long" else m1_c[j] + spread + slip, "end_of_data"); pos = None
    tr = pd.DataFrame(trades)
    if len(tr):
        tr["hold_minutes"] = (pd.to_datetime(tr.exit_time) - pd.to_datetime(tr.entry_time)).dt.total_seconds() / 60
        tr["signal_date"] = pd.to_datetime(tr.signal_bar_open).dt.date
    tr.to_csv(out_dir / "trades.csv", index=False)
    pd.DataFrame(skips).to_csv(out_dir / "skips.csv", index=False)
    meta = dict(config=cfg, n_trades=int(len(tr)), n_skips=len(skips), counters=counters, m15_bars=int(len(ind)), m1_bars=int(len(m1)),
                data_start=str(m1.index[0]), data_end=str(m1.index[-1]), run_seconds=round(time.time() - t0, 1),
                run_time_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    (out_dir / "config.json").write_text(json.dumps(meta, indent=2, default=str))
    return tr, pd.DataFrame(skips), meta


_M1 = None
def _worker(name):
    cfg = dict(V3_CONFIG); cfg.update(VARIANTS[name]); cfg["variant"] = name
    tr, sk, meta = run(cfg, _M1, RESULTS / name)
    extra = f" meanR={tr.realised_R.mean():+.3f} totalR={tr.realised_R.sum():+.1f}" if len(tr) else ""
    return f"{name}: trades={len(tr)} skips={len(sk)} counters={meta['counters']} secs={meta['run_seconds']}{extra}"


def main():
    global _M1
    ap = argparse.ArgumentParser(); ap.add_argument("--variant"); ap.add_argument("--all", action="store_true")
    ap.add_argument("--jobs", type=int, default=1); ap.add_argument("--data", default=str(E.DATA)); ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list: print("\n".join(f"{v}: {VARIANTS[v]}" for v in VARIANTS)); return
    _M1 = pd.read_parquet(a.data)
    names = list(VARIANTS) if a.all else [a.variant or "V3_ORB_L10"]
    t0 = time.time()
    if a.jobs > 1 and len(names) > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(a.jobs) as pool:
            for line in pool.imap_unordered(_worker, names): print(line, flush=True)
    else:
        for n in names: print(_worker(n), flush=True)
    print(f"total wall time {time.time() - t0:.0f} s")

if __name__ == "__main__":
    main()
