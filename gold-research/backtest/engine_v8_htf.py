#!/usr/bin/env python3
"""engine_v8_htf.py — bigger timeframe for the direction, 5-minute pullback for the entry (XAUUSD M1 data).

Specification: results/PREREGISTRATION_v8_htf.md (frozen 2026-11-13 before this file existed). Families Q (quick exit)
and N (normal intraday trade). Family B (the M15 breakout with a bigger reference) lives in engine_v5_hl.py (hl_ref).
Conventions of every earlier engine: BID M1 bars, ask = bid + spread, slippage per market / stop fill, commission 0,
targets filled at their price when traded through, stop first when stop and target fall in one minute, same-minute stop
check on the fill minute, 20:50 flat, session-gap exit.

Usage: python3 engine_v8_htf.py [ID ...] [--stress]      (--stress = spread 0.50, slippage 0.10 -> results/V8H_<ID>_stress/)
"""
import sys, json, pathlib, time
import numpy as np, pandas as pd
import engine_v6_mtf as V6, htf_refs as HR

HERE = pathlib.Path(__file__).resolve().parent
RES = HERE.parent / "results"; DATA = V6.DATA

BASE = dict(spread=0.25, slippage=0.05, cap_entries=6, win_start=7 * 60, win_end=16 * 60, flat_at=20 * 60 + 50, warmup_m15=200,
            max_fill_delay=2, pb_len=20, ref="h4", stop_mode="atr15", stop_k=1.0, hold=None, target_r=None)
_N = dict(stop_mode="d1atr", stop_k=0.25, target_r=1.5, cap_entries=3)
VARIANTS = {   # frozen in results/PREREGISTRATION_v8_htf.md
    "Q5_PB_H15_H1":   dict(ref="h1", hold=15),
    "Q5_PB_H15_H4":   dict(ref="h4", hold=15),
    "Q5_PB_H15_D1":   dict(ref="d1", hold=15),
    "N5_PB_M15":      dict(_N, ref="m15"),
    "N5_PB_H1":       dict(_N, ref="h1"),
    "N5_PB_H4":       dict(_N, ref="h4"),
    "N5_PB_D1":       dict(_N, ref="d1"),
    "N5_PB_H4_TIGHT": dict(_N, ref="h4", stop_mode="atr15", stop_k=1.0),
    "N5_PB_H4_EOD":   dict(_N, ref="h4", target_r=None),
}


def prepare(m1):
    D = V6.prepare(m1)
    D["ltf15"] = V6.ltf_arrays(D["tmin"], D["H"], D["L"], D["C"], 15)
    D["refs"] = HR.all_refs(D["tmin"], D["C"])
    # ATR14(M15) of the last closed M15 bar, per M1 index
    g15 = np.asarray(D["ltf15"]["gidx"]); atr15 = np.asarray(D["ltf15"]["atr"]); prev = g15 - 1
    D["atr15_prev"] = np.where(prev >= BASE["warmup_m15"], atr15[np.maximum(prev, 0)], np.nan)
    # D1ATR (Wilder ATR14 of session days) as of the previous completed session day, per M1 index
    sday = D["sday"]; didx = np.array([D["d_index"][int(s)] for s in np.unique(sday)])
    pos = np.searchsorted(np.unique(sday), sday)                       # index of each M1 bar's session day
    d_atr = D["d_atr"].copy(); d_atr[:14] = np.nan                      # not defined before 14 session days exist
    D["d1atr_prev"] = np.where(pos >= 1, d_atr[np.maximum(pos - 1, 0)], np.nan)
    assert (didx == np.arange(len(didx))).all()
    return D


def signals(cfg, D):
    """+1 / -1 / 0 per M1 index (signal at that M1 bar's close) and the stop distance: the 5-minute pullback of v7 in the
    direction of the reference."""
    tmin = D["tmin"]; n = len(tmin)
    L5 = D["ltf"][5]; g5 = np.asarray(L5["gidx"]); end5 = np.asarray(L5["is_end"])
    lo5, hi5, cl5 = (np.asarray(L5[k]) for k in ("lo", "hi", "cl"))
    ema = np.empty(len(cl5)); ema[0] = cl5[0]; a = 2.0 / (cfg["pb_len"] + 1.0)
    for q in range(1, len(cl5)): ema[q] = ema[q - 1] + a * (cl5[q] - ema[q - 1])
    ql = (lo5 <= ema) & (cl5 > ema); qs = (hi5 >= ema) & (cl5 < ema)
    ql_new = ql & ~np.r_[False, ql[:-1]]; qs_new = qs & ~np.r_[False, qs[:-1]]
    ref_up, ref_dn = D["refs"][cfg["ref"]]
    dist = cfg["stop_k"] * (D["atr15_prev"] if cfg["stop_mode"] == "atr15" else D["d1atr_prev"])
    cmod = (tmin + 1) % 1440
    in_win = (cmod >= cfg["win_start"]) & (cmod < cfg["win_end"]) & np.isfinite(dist) & np.isfinite(D["atr15_prev"])
    up = end5 & ql_new[g5] & ref_up; dn = end5 & qs_new[g5] & ref_dn
    sig = np.where(up & in_win, 1, np.where(dn & in_win, -1, 0))
    return sig.tolist(), dist.tolist()


def run(vid, D, over=None):
    cfg = dict(BASE); cfg.update(VARIANTS[vid]); cfg.update(over or {})
    SPREAD, SLIP, FLAT, CAP = cfg["spread"], cfg["slippage"], cfg["flat_at"], cfg["cap_entries"]
    HOLD = int(cfg["hold"]) if cfg["hold"] else None; TR = cfg["target_r"]
    sig, dist = signals(cfg, D)
    tmin, O, H, L, C = (D[k].tolist() for k in ("tmin", "O", "H", "L", "C")); sday = D["sday"].tolist()
    position = None; pend = None; trades = []; entries = 0; cur_day = None
    counters = dict(signals=0, taken=0, skipped_busy_or_cap=0, late=0, same_minute_stop=0, ambiguous_stop_target=0)
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
                target = None if TR is None else (fill + TR * pe["dist"] if is_long else fill - TR * pe["dist"])
                entries += 1; counters["taken"] += 1
                P = dict(side="long" if is_long else "short", entry_min=t, entry_price=fill, initial_stop=stop, target=target,
                         planned_risk=pe["dist"], day=day, sig_close_min=pe["close_min"], entry_no=entries)
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
            elif HOLD is not None and t - P["entry_min"] >= HOLD: px, why = (o - SLIP if is_long else o + SPREAD + SLIP), "hold_exit"
            else:
                if is_long:
                    hit_stop = l <= P["initial_stop"]; hit_tgt = P["target"] is not None and h > P["target"]
                    stop_px = min(P["initial_stop"], o) - SLIP
                else:
                    hit_stop = h + SPREAD >= P["initial_stop"]; hit_tgt = P["target"] is not None and l + SPREAD < P["target"]
                    stop_px = max(P["initial_stop"], o + SPREAD) + SLIP
                if hit_stop and hit_tgt: counters["ambiguous_stop_target"] += 1; hit_tgt = False        # stop first
                if hit_stop: px, why = stop_px, "stop"
                elif hit_tgt: px, why = P["target"], "target"
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
        out["signal_bar_open"] = out["signal_time"] - pd.Timedelta(minutes=5)
        out["hold_minutes"] = (out.exit_min - out.entry_min).astype(float)
        out.insert(0, "variant", "V8H_" + vid)
    return out, counters, cfg


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]; stress = "--stress" in sys.argv
    m1 = pd.read_parquet(DATA); D = prepare(m1)
    over = dict(spread=0.50, slippage=0.10) if stress else None
    for vid in (args or list(VARIANTS)):
        t0 = time.time(); tr, counters, cfg = run(vid, D, over)
        out = RES / ("V8H_" + vid + ("_stress" if stress else "")); out.mkdir(parents=True, exist_ok=True)
        tr.to_csv(out / "trades.csv", index=False)
        (out / "config.json").write_text(json.dumps(dict(config=cfg, n_trades=int(len(tr)), counters=counters, data_start=str(m1.index[0]), data_end=str(m1.index[-1])), indent=2))
        print(f"V8H_{vid}{'_stress' if stress else ''}: trades={len(tr)} counters={counters} ({time.time() - t0:.0f} s)", flush=True)

if __name__ == "__main__":
    main()
