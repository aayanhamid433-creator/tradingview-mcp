#!/usr/bin/env python3
"""verify_v5b_replay.py — independent minute-by-minute replay of the v5b improvement variants (MS = minimum stop, T = EMA50 trend).

Derived from verify_v5_replay.py (which stays the checker of the six frozen readings); the two filters are re-implemented here
from results/PREREGISTRATION_v5b_hl_improve.md with a hand-written EMA, not imported from the engine.

Original header: independent minute-by-minute replay of the six HL readings.

Written from results/PREREGISTRATION_v5_hl.md (rules + decisions D1-D13), NOT from engine_v5_hl.py: one flat loop over
the M1 bars, its own M15 / session-day aggregation, its own Wilder ATR, daily ATR / SMA and brute-force pivots, and the
six readings typed in by hand. Nothing is imported from the engines. The replay's trade list is compared field by field
with results/V5_<ID>/trades.csv. Only mismatches and counts are printed — no performance statistic.

Usage: python3 verify_v5_replay.py [ID ...]      (default: all six)
"""
import sys, pathlib, time, math
import numpy as np, pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
RES = HERE.parent / "results"; DATA = HERE.parent / "data" / "xauusd_m1_utc.parquet"

SPREAD, SLIP = 0.25, 0.05
OFFSET, CAP_K, FLOOR_K, TARGET_K, TRAIL_K = 0.10, 0.6, 0.3, 1.5, 3.0
WIN_START, WIN_END, FLAT_AT = 7 * 60, 16 * 60, 20 * 60 + 50
WARMUP = 200
READINGS = {   # typed from the pre-registration
    "HL_SW5_RR":      dict(levels="swing", n=5,    exit="rr",    cap=3, bias=False),
    "HL_SW5_TRAIL":   dict(levels="swing", n=5,    exit="trail", cap=3, bias=False),
    "HL_SW10_RR":     dict(levels="swing", n=10,   exit="rr",    cap=3, bias=False),
    "HL_PD_RR":       dict(levels="pd",    n=None, exit="rr",    cap=1, bias=False),
    "HL_PD_TRAIL":    dict(levels="pd",    n=None, exit="trail", cap=1, bias=False),
    "HL_SW5_RR_BIAS": dict(levels="swing", n=5,    exit="rr",    cap=3, bias=True),
    # v5b (typed from PREREGISTRATION_v5b_hl_improve.md)
    "HL_IMP_MS":      dict(levels="swing", n=5,    exit="rr",    cap=3, bias=False, minstop=0.10),
    "HL_IMP_MS_T":    dict(levels="swing", n=5,    exit="rr",    cap=3, bias=False, minstop=0.10, trend=True),
    "HL_IMP10_MS_T":  dict(levels="swing", n=10,   exit="rr",    cap=3, bias=False, minstop=0.10, trend=True),
}


def prepare(m1: pd.DataFrame):
    """Minute, M15 and session-day arrays built without resample / the engines' helpers."""
    tmin = m1.index.values.astype("datetime64[m]").astype(np.int64)          # minutes since epoch (dataset clock)
    O, H, L, C = (m1[c].values.astype(float) for c in ("open", "high", "low", "close"))
    assert (np.diff(tmin) > 0).all(), "M1 index not strictly increasing"
    slot = tmin // 15
    bs = np.flatnonzero(np.r_[True, slot[1:] != slot[:-1]]); be = np.r_[bs[1:], len(slot)]
    b_hi = np.maximum.reduceat(H, bs); b_lo = np.minimum.reduceat(L, bs); b_cl = C[be - 1]; b_open_min = slot[bs] * 15
    pc = np.r_[b_cl[0], b_cl[:-1]]
    tr = np.maximum(b_hi - b_lo, np.maximum(np.abs(b_hi - pc), np.abs(b_lo - pc)))
    atr = np.full(len(tr), np.nan); atr[13] = tr[:14].mean()
    for q in range(14, len(tr)): atr[q] = atr[q - 1] + (tr[q] - atr[q - 1]) / 14.0
    sday = (tmin + 60) // 1440                                                # session day: 23:00 -> 23:00
    ds = np.flatnonzero(np.r_[True, sday[1:] != sday[:-1]]); de = np.r_[ds[1:], len(sday)]
    d_hi = np.maximum.reduceat(H, ds); d_lo = np.minimum.reduceat(L, ds); d_cl = C[de - 1]; d_id = sday[ds]
    d_tr = d_hi - d_lo
    d_tr[1:] = np.maximum(d_tr[1:], np.maximum(np.abs(d_hi[1:] - d_cl[:-1]), np.abs(d_lo[1:] - d_cl[:-1])))
    d_atr = np.empty(len(d_tr)); d_atr[0] = d_tr[0]
    for q in range(1, len(d_tr)): d_atr[q] = d_atr[q - 1] + (d_tr[q] - d_atr[q - 1]) / 14.0
    d_sma = np.full(len(d_cl), np.nan); cs = np.cumsum(d_cl)
    d_sma[199:] = (cs[199:] - np.r_[0.0, cs[:-200]]) / 200.0
    ema50 = np.empty(len(b_cl)); ema50[0] = b_cl[0]; alpha = 2.0 / 51.0       # EMA50 of M15 closes, y0 = x0, recursive
    for q in range(1, len(b_cl)): ema50[q] = ema50[q - 1] + alpha * (b_cl[q] - ema50[q - 1])
    return dict(b_cl=b_cl, ema50=ema50, tmin=tmin, O=O, H=H, L=L, C=C, bs=bs, be=be, b_hi=b_hi, b_lo=b_lo, b_open_min=b_open_min, atr=atr, sday=sday,
                d_hi=d_hi, d_lo=d_lo, d_cl=d_cl, d_atr=d_atr, d_sma=d_sma, d_index={int(k): i for i, k in enumerate(d_id)})


def brute_pivots(hi, lo, n):
    """{confirmation bar index: price} for swing highs and swing lows, by direct comparison with the n bars on each side."""
    conf_hi, conf_lo = {}, {}
    hl, ll = hi.tolist(), lo.tolist()
    for j in range(n, len(hl) - n):
        x = hl[j]
        if all(x >= hl[q] for q in range(j - n, j)) and all(x >= hl[q] for q in range(j + 1, j + n + 1)): conf_hi[j + n] = x
        y = ll[j]
        if all(y <= ll[q] for q in range(j - n, j)) and all(y <= ll[q] for q in range(j + 1, j + n + 1)): conf_lo[j + n] = y
    return conf_hi, conf_lo


def replay(vid: str, D: dict):
    spec = READINGS[vid]; swing = spec["levels"] == "swing"; trail = spec["exit"] == "trail"; cap = spec["cap"]; use_bias = spec["bias"]
    tmin, O, H, L, C = (D[k].tolist() for k in ("tmin", "O", "H", "L", "C"))
    b_end = D["be"].tolist(); b_open = D["b_open_min"].tolist(); atr = D["atr"].tolist(); sday = D["sday"].tolist()
    d_hi, d_lo, d_cl, d_atr, d_sma = (D[k].tolist() for k in ("d_hi", "d_lo", "d_cl", "d_atr", "d_sma")); d_index = D["d_index"]
    conf_hi, conf_lo = brute_pivots(D["b_hi"], D["b_lo"], spec["n"]) if swing else ({}, {})
    b_cl = D["b_cl"].tolist(); ema50 = D["ema50"].tolist(); f_trend = spec.get("trend", False); f_ms = spec.get("minstop")
    high = low = None          # marked levels: dict(price, trig, live)
    params = {}                # side -> dict(trig, stop, target, dist, calc_bar)
    orders = None; position = None; trades = []; refused = 0
    entries = 0; cur_day = None; prev = None
    b = 0
    for n in range(len(tmin)):
        if n == b_end[b]:
            # ---------- M15 bar b has just closed
            if swing:
                if b in conf_hi: high = dict(price=conf_hi[b], trig=conf_hi[b] + OFFSET, live=True); params = {}
                if b in conf_lo: low = dict(price=conf_lo[b], trig=conf_lo[b] - OFFSET, live=True); params = {}
            close_mod = b_open[b] % 1440 + 15
            if position is None and WIN_START <= close_mod < WIN_END:
                orders = None
                if (entries < cap and high is not None and low is not None and b >= WARMUP and not math.isnan(atr[b]) and prev is not None):
                    ok_long = ok_short = True
                    if use_bias:
                        s = d_sma[prev]
                        ok_long = (not math.isnan(s)) and d_cl[prev] > s; ok_short = (not math.isnan(s)) and d_cl[prev] < s
                    want_long = high["live"] and ok_long; want_short = low["live"] and ok_short
                    if f_trend:   # T: buy side only above EMA50 at this close, sell side only below
                        want_long = want_long and b_cl[b] > ema50[b]; want_short = want_short and b_cl[b] < ema50[b]
                    if want_long and "long" not in params:
                        raw = high["trig"] - low["price"]; dist = min(max(raw, FLOOR_K * atr[b]), CAP_K * d_atr[prev])
                        params["long"] = dict(trig=high["trig"], stop=high["trig"] - dist, dist=dist, calc_bar=b,
                                              target=None if trail else high["trig"] + TARGET_K * dist)
                    if want_short and "short" not in params:
                        raw = high["price"] - low["trig"]; dist = min(max(raw, FLOOR_K * atr[b]), CAP_K * d_atr[prev])
                        params["short"] = dict(trig=low["trig"], stop=low["trig"] + dist, dist=dist, calc_bar=b,
                                               target=None if trail else low["trig"] - TARGET_K * dist)
                    if f_ms is not None:   # MS: no order for a side whose stop distance is below k x D1ATR
                        if want_long and params["long"]["dist"] < f_ms * d_atr[prev]: want_long = False
                        if want_short and params["short"]["dist"] < f_ms * d_atr[prev]: want_short = False
                    if want_long or want_short:
                        orders = dict(day=cur_day, sig=b, long=params["long"] if want_long else None, short=params["short"] if want_short else None,
                                      lh=high["price"], ll=low["price"])
            b += 1
        day = sday[n]
        if day != cur_day:
            # ---------- new session day
            cur_day = day; entries = 0; di = d_index[day]; prev = di - 1 if di > 0 else None
            if not swing:
                params = {}
                if prev is None: high = low = None
                else:
                    high = dict(price=d_hi[prev], trig=d_hi[prev] + OFFSET, live=True)
                    low = dict(price=d_lo[prev], trig=d_lo[prev] - OFFSET, live=True)
        o, h, l, c = O[n], H[n], L[n], C[n]; mod = tmin[n] % 1440
        if high is not None and high["live"] and h >= high["trig"]: high["live"] = False
        if low is not None and low["live"] and l <= low["trig"]: low["live"] = False
        if position is not None:
            P = position; is_long = P["side"] == "long"; px = None
            if day != P["day"]: px, why = (o - SLIP if is_long else o + SPREAD + SLIP), "session_gap_exit"
            elif mod >= FLAT_AT: px, why = (o - SLIP if is_long else o + SPREAD + SLIP), "time_exit"
            elif is_long:
                if l <= P["stop"]: px, why = min(P["stop"], o) - SLIP, ("stop" if P["stop"] == P["stop0"] else "trail_stop")
                elif P["target"] is not None and h > P["target"]: px, why = P["target"], "target"
            else:
                if h + SPREAD >= P["stop"]: px, why = max(P["stop"], o + SPREAD) + SLIP, ("stop" if P["stop"] == P["stop0"] else "trail_stop")
                elif P["target"] is not None and l + SPREAD < P["target"]: px, why = P["target"], "target"
            if px is not None:
                P.update(exit_min=tmin[n], exit_price=px, exit_reason=why); trades.append(P); position = None
            elif trail:
                a = atr[b - 1]   # the last CLOSED M15 bar while minute n (inside bar b) is running
                if is_long:
                    P["ext"] = max(P["ext"], h); cand = P["ext"] - TRAIL_K * a
                    if cand > P["stop"] and cand < l: P["stop"] = cand
                else:
                    P["ext"] = min(P["ext"], l); cand = P["ext"] + TRAIL_K * a
                    if cand < P["stop"] and cand > h + SPREAD: P["stop"] = cand
        elif orders is not None:
            if mod >= WIN_END or day != orders["day"]: orders = None
            else:
                bo, so = orders["long"], orders["short"]
                tb = bo is not None and h + SPREAD >= bo["trig"]
                ts = so is not None and l <= so["trig"]
                if tb and ts:
                    if bo["trig"] - (o + SPREAD) <= o - so["trig"]: ts = False
                    else: tb = False
                if tb or ts:
                    od = orders; orders = None; q = bo if tb else so
                    if tb: high["live"] = False; fill = max(q["trig"], o + SPREAD) + SLIP
                    else: low["live"] = False; fill = min(q["trig"], o) - SLIP
                    bad = (fill <= q["stop"] or (q["target"] is not None and fill >= q["target"])) if tb else \
                          (fill >= q["stop"] or (q["target"] is not None and fill <= q["target"]))
                    if bad: refused += 1
                    else:
                        entries += 1
                        P = dict(side="long" if tb else "short", entry_min=tmin[n], entry_price=fill, level=q["trig"], stop0=q["stop"], stop=q["stop"],
                                 target=q["target"], day=day, ext=fill, sig_bar_open_min=b_open[od["sig"]], calc_bar_open_min=b_open[q["calc_bar"]],
                                 level_high=od["lh"], level_low=od["ll"], entry_no=entries)
                        if tb and l <= q["stop"]:
                            P.update(exit_min=tmin[n], exit_price=(l - SLIP if l < q["stop"] else q["stop"] - SLIP), exit_reason="stop_same_minute"); trades.append(P)
                        elif (not tb) and h + SPREAD >= q["stop"]:
                            P.update(exit_min=tmin[n], exit_price=q["stop"] + SLIP, exit_reason="stop_same_minute"); trades.append(P)
                        else: position = P
    out = pd.DataFrame(trades)
    if len(out):
        sign = np.where(out.side == "long", 1.0, -1.0)
        out["planned_risk"] = (out.level - out.stop0).abs()
        out["realised_R"] = sign * (out.exit_price - out.entry_price) / out.planned_risk
        for c_new, c_old in (("entry_time", "entry_min"), ("exit_time", "exit_min"), ("signal_bar_open", "sig_bar_open_min"), ("calc_bar_open", "calc_bar_open_min")):
            out[c_new] = pd.to_datetime(out[c_old].values.astype("int64") * 60, unit="s", utc=True)
    return out, refused, position is not None


def compare(vid: str, rep: pd.DataFrame):
    eng = pd.read_csv(RES / f"V5_{vid}" / "trades.csv")
    for c in ("entry_time", "exit_time", "signal_bar_open", "calc_time"): eng[c] = pd.to_datetime(eng[c], utc=True)
    problems = []
    if len(eng) != len(rep): problems.append(f"trade count: engine {len(eng)} vs replay {len(rep)}")
    n = min(len(eng), len(rep)); e, r = eng.iloc[:n].reset_index(drop=True), rep.iloc[:n].reset_index(drop=True)
    def chk(name, a, b, num=True):
        if num:
            a, b = a.astype(float).values, b.astype(float).values
            bad = ~(np.isclose(a, b, rtol=0, atol=1e-9) | (np.isnan(a) & np.isnan(b)))
        else: bad = (a.values != b.values)
        if bad.any(): problems.append(f"{name}: {int(bad.sum())} mismatches, first at row {int(np.flatnonzero(bad)[0])}")
    chk("side", e.side, r.side, num=False); chk("entry_time", e.entry_time, r.entry_time, num=False); chk("exit_time", e.exit_time, r.exit_time, num=False)
    chk("signal_bar_open", e.signal_bar_open, r.signal_bar_open, num=False); chk("exit_reason", e.exit_reason, r.exit_reason, num=False)
    chk("calc_time", e.calc_time, r.calc_bar_open + pd.Timedelta(minutes=15), num=False)
    for ce, cr in (("entry_price", "entry_price"), ("level", "level"), ("initial_stop", "stop0"), ("final_stop", "stop"), ("target", "target"),
                   ("exit_price", "exit_price"), ("planned_risk", "planned_risk"), ("realised_R", "realised_R"), ("level_high", "level_high"),
                   ("level_low", "level_low"), ("entry_no", "entry_no")):
        chk(ce, e[ce], r[cr].astype(float))
    return len(eng), problems


def main():
    ids = sys.argv[1:] or list(READINGS)
    m1 = pd.read_parquet(DATA); D = prepare(m1)
    ok = True
    for vid in ids:
        t0 = time.time(); rep, refused, still_open = replay(vid, D)
        n_eng, problems = compare(vid, rep)
        ok &= not problems
        print(f"V5_{vid}: engine trades {n_eng}, replay trades {len(rep)}, replay gap refusals {refused}, open at end {still_open}, "
              f"{'IDENTICAL' if not problems else 'MISMATCH'} ({time.time() - t0:.0f} s)")
        for p in problems: print("   -", p)
    print("REPLAY CHECK:", "PASS" if ok else "FAIL")
    if not ok: raise SystemExit(1)

if __name__ == "__main__":
    main()
