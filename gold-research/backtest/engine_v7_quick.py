#!/usr/bin/env python3
"""engine_v7_quick.py — "quick in, quick out" in the direction of the move (XAUUSD M1 data).

Specification: results/PREREGISTRATION_v7_quick.md (frozen 2026-11-13 before this file existed). Tenth look at the data.
Signals are computed for every minute with numpy from information available at that minute's close; one flat loop over
the M1 bars then handles entries and exits with the conventions of every earlier engine (BID bars, ask = bid + spread,
slippage per fill, commission 0, same-minute stop check on the fill minute, 20:50 flat, session-gap exit).

Usage: python3 engine_v7_quick.py [ID ...] [--stress]    (--stress = spread 0.50, slippage 0.10 -> results/V7_<ID>_stress/)
"""
import sys, json, math, pathlib, time
import numpy as np, pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
import engine_v6_mtf as V6

HERE = pathlib.Path(__file__).resolve().parent
RES = HERE.parent / "results"; DATA = V6.DATA

BASE = dict(spread=0.25, slippage=0.05, stop_atr=1.0, cap_entries=6, win_start=7 * 60, win_end=16 * 60, flat_at=20 * 60 + 50,
            warmup_m15=200, max_fill_delay=2, burst_w=5, burst_k=2.0, hold=5, signal="burst", fade=False, need_trend=False)
VARIANTS = {   # frozen in results/PREREGISTRATION_v7_quick.md
    "QS_BURST5_H5":     dict(signal="burst", burst_w=5, burst_k=2.0, hold=5),
    "QS_BURST5_H15":    dict(signal="burst", burst_w=5, burst_k=2.0, hold=15),
    "QS_BURST5_H5_T":   dict(signal="burst", burst_w=5, burst_k=2.0, hold=5, need_trend=True),
    "QS_BURST15_H15":   dict(signal="burst", burst_w=15, burst_k=2.0, hold=15),
    "QS_TREND_BRK_H5":  dict(signal="trend_break", hold=5),
    "QS_TREND_BRK_H15": dict(signal="trend_break", hold=15),
    "QS_TREND_PB_H15":  dict(signal="trend_pullback", hold=15),
    "QS_FADE5_H5":      dict(signal="burst", burst_w=5, burst_k=2.0, hold=5, fade=True),
}


def signals(cfg, D):
    """Per-minute arrays: +1 long signal / -1 short signal / 0 at the close of each M1 bar, and the stop distance."""
    tmin, H, L, C = D["tmin"], D["H"], D["L"], D["C"]; n = len(tmin)
    L15 = D["ltf15"]; g15 = np.asarray(L15["gidx"]); atr15 = np.asarray(L15["atr"])
    prev = g15 - 1; okp = prev >= cfg["warmup_m15"]
    atr_prev = np.where(okp, atr15[np.maximum(prev, 0)], np.nan)                       # ATR14(M15) of the last CLOSED M15 bar
    b_cl, ema50 = D["b_cl"], D["ema50"]
    e4 = np.r_[np.full(4, np.nan), ema50[:-4]]
    up_bar = (b_cl > ema50) & (ema50 > e4); dn_bar = (b_cl < ema50) & (ema50 < e4)
    trend_up = np.where(okp, up_bar[np.maximum(prev, 0)], False); trend_dn = np.where(okp, dn_bar[np.maximum(prev, 0)], False)
    cmod = (tmin + 1) % 1440
    in_win = (cmod >= cfg["win_start"]) & (cmod < cfg["win_end"]) & ~np.isnan(atr_prev)
    up = np.zeros(n, dtype=bool); dn = np.zeros(n, dtype=bool)
    if cfg["signal"] == "burst":
        W, k = int(cfg["burst_w"]), float(cfg["burst_k"])
        r = np.full(n, np.nan); contig = np.zeros(n, dtype=bool)
        contig[W:] = (tmin[W:] - tmin[:-W]) == W
        r[W:] = C[W:] - C[:-W]
        z = r / (atr_prev * math.sqrt(W / 15.0))
        up = contig & (z >= k); dn = contig & (z <= -k)
        if cfg["need_trend"]: up &= trend_up; dn &= trend_dn
    elif cfg["signal"] == "trend_break":
        hh = np.full(n, np.nan); ll = np.full(n, np.nan); contig = np.zeros(n, dtype=bool)
        hh[5:] = sliding_window_view(H, 5).max(axis=1)[:-1]                             # highest high of the previous 5 M1 bars
        ll[5:] = sliding_window_view(L, 5).min(axis=1)[:-1]
        contig[5:] = (tmin[5:] - tmin[:-5]) == 5
        up = contig & trend_up & (C > hh); dn = contig & trend_dn & (C < ll)
    elif cfg["signal"] == "trend_pullback":
        L5 = D["ltf"][5]; g5 = np.asarray(L5["gidx"]); end5 = np.asarray(L5["is_end"])
        lo5, hi5, cl5 = (np.asarray(L5[kk]) for kk in ("lo", "hi", "cl"))
        ema20 = np.empty(len(cl5)); ema20[0] = cl5[0]; a = 2.0 / 21.0
        for q in range(1, len(cl5)): ema20[q] = ema20[q - 1] + a * (cl5[q] - ema20[q - 1])
        ql = (lo5 <= ema20) & (cl5 > ema20); qs = (hi5 >= ema20) & (cl5 < ema20)        # trades through its EMA20, closes back
        ql_new = ql & ~np.r_[False, ql[:-1]]; qs_new = qs & ~np.r_[False, qs[:-1]]
        up = end5 & ql_new[g5] & trend_up; dn = end5 & qs_new[g5] & trend_dn
    # a signal must be new: true now, false on the previous M1 bar (the pullback signal is already per M5 bar)
    if cfg["signal"] != "trend_pullback":
        up = up & ~np.r_[False, up[:-1]]; dn = dn & ~np.r_[False, dn[:-1]]
    sig = np.where(up & in_win, 1, np.where(dn & in_win, -1, 0))
    if cfg["fade"]: sig = -sig
    return sig.tolist(), (cfg["stop_atr"] * atr_prev).tolist()


def run(vid, D, over=None):
    cfg = dict(BASE); cfg.update(VARIANTS[vid]); cfg.update(over or {})
    SPREAD, SLIP, FLAT, CAP, HOLD = cfg["spread"], cfg["slippage"], cfg["flat_at"], cfg["cap_entries"], int(cfg["hold"])
    sig, dist = signals(cfg, D)
    tmin, O, H, L, C = (D[k].tolist() for k in ("tmin", "O", "H", "L", "C")); sday = D["sday"].tolist()
    position = None; pend = None; trades = []; entries = 0; cur_day = None
    counters = dict(signals=0, taken=0, skipped_busy_or_cap=0, late=0, same_minute_stop=0)
    for n in range(len(tmin)):
        day = sday[n]
        if day != cur_day: cur_day = day; entries = 0
        o, h, l = O[n], H[n], L[n]; t = tmin[n]; mod = t % 1440
        just_opened = False
        if pend is not None:
            pe = pend; pend = None
            if day != pe["day"] or t - pe["close_min"] > cfg["max_fill_delay"] or mod >= FLAT: counters["late"] += 1
            else:
                is_long = pe["side"] == 1
                fill = (o + SPREAD + SLIP) if is_long else (o - SLIP)
                stop = fill - pe["dist"] if is_long else fill + pe["dist"]
                entries += 1; counters["taken"] += 1
                P = dict(side="long" if is_long else "short", entry_min=t, entry_price=fill, initial_stop=stop, planned_risk=pe["dist"], day=day,
                         sig_close_min=pe["close_min"], entry_no=entries)
                if is_long and l <= stop:
                    counters["same_minute_stop"] += 1
                    P.update(exit_min=t, exit_price=(l - SLIP if l < stop else stop - SLIP), exit_reason="stop_same_minute"); trades.append(P)
                elif (not is_long) and h + SPREAD >= stop:
                    counters["same_minute_stop"] += 1
                    P.update(exit_min=t, exit_price=stop + SLIP, exit_reason="stop_same_minute"); trades.append(P)
                else: position = P; just_opened = True
        if position is not None and not just_opened:
            P = position; is_long = P["side"] == "long"; px = None
            if day != P["day"]: px, why = (o - SLIP if is_long else o + SPREAD + SLIP), "session_gap_exit"
            elif mod >= FLAT: px, why = (o - SLIP if is_long else o + SPREAD + SLIP), "time_exit_2050"
            elif t - P["entry_min"] >= HOLD: px, why = (o - SLIP if is_long else o + SPREAD + SLIP), "hold_exit"
            elif is_long and l <= P["initial_stop"]: px, why = min(P["initial_stop"], o) - SLIP, "stop"
            elif (not is_long) and h + SPREAD >= P["initial_stop"]: px, why = max(P["initial_stop"], o + SPREAD) + SLIP, "stop"
            if px is not None:
                P.update(exit_min=t, exit_price=px, exit_reason=why); trades.append(P); position = None
        s = sig[n]
        if s != 0:
            counters["signals"] += 1
            if position is None and pend is None and entries < CAP: pend = dict(side=s, dist=dist[n], day=day, close_min=t + 1)
            else: counters["skipped_busy_or_cap"] += 1
    out = pd.DataFrame(trades)
    if len(out):
        sign = np.where(out.side == "long", 1.0, -1.0)
        out["pnl_per_oz"] = sign * (out.exit_price - out.entry_price); out["realised_R"] = out.pnl_per_oz / out.planned_risk
        for c_new, c_old in (("entry_time", "entry_min"), ("exit_time", "exit_min"), ("signal_time", "sig_close_min")):
            out[c_new] = pd.to_datetime(out[c_old].values.astype("int64") * 60, unit="s", utc=True)
        out["signal_bar_open"] = out["signal_time"] - pd.Timedelta(minutes=1)
        out["hold_minutes"] = (out.exit_min - out.entry_min).astype(float)
        out.insert(0, "variant", "V7_" + vid)
    return out, counters, cfg


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]; stress = "--stress" in sys.argv
    m1 = pd.read_parquet(DATA); D = V6.prepare(m1)
    D["ltf15"] = V6.ltf_arrays(D["tmin"], D["H"], D["L"], D["C"], 15)
    over = dict(spread=0.50, slippage=0.10) if stress else None
    for vid in (args or list(VARIANTS)):
        t0 = time.time(); tr, counters, cfg = run(vid, D, over)
        out = RES / ("V7_" + vid + ("_stress" if stress else "")); out.mkdir(parents=True, exist_ok=True)
        tr.to_csv(out / "trades.csv", index=False)
        (out / "config.json").write_text(json.dumps(dict(config=cfg, n_trades=int(len(tr)), counters=counters, data_start=str(m1.index[0]), data_end=str(m1.index[-1])), indent=2))
        print(f"V7_{vid}{'_stress' if stress else ''}: trades={len(tr)} counters={counters} ({time.time() - t0:.0f} s)", flush=True)

if __name__ == "__main__":
    main()
