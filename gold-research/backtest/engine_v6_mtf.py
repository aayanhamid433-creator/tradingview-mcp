#!/usr/bin/env python3
"""engine_v6_mtf.py — levels on the 15-minute chart, entries on the 5-minute or 1-minute chart (XAUUSD M1 data).

Specification: results/PREREGISTRATION_v6_mtf.md (frozen 2026-11-13 before this file existed). Ninth look at the same data.

One flat loop over the M1 bars, with its own M15 / session-day aggregation (the structure of verify_v5_replay.py, which
reproduces engine_v5_hl.py trade for trade). Conventions shared with every earlier engine: BID M1 bars, ask = bid +
spread, slippage per fill, commission 0; a marked level is known only from the close of the M15 bar that confirms it;
previous-session-day D1ATR; stop first when stop and target print in the same minute; target needs trade-through;
same-minute stop check on the fill minute; 20:50 time exit; session-gap exit; fills at or beyond their own stop refused.

Usage: python3 engine_v6_mtf.py [ID ...] [--stress]   (default: all variants; --stress = spread 0.50, slippage 0.10,
       written to results/V6_<ID>_stress/)
"""
import sys, json, math, pathlib, time
import numpy as np, pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

HERE = pathlib.Path(__file__).resolve().parent
RES = HERE.parent / "results"; DATA = HERE.parent / "data" / "xauusd_m1_utc.parquet"

BASE = dict(spread=0.25, slippage=0.05, offset=0.10, cap_k=0.6, floor_k=1.0, target_mult=2.0, pivot_n=10, ltf=5, trend=True,
            cap_entries=3, win_start=7 * 60, win_end=16 * 60, flat_at=20 * 60 + 50, warmup=200, max_fill_delay=5)
VARIANTS = {   # frozen in results/PREREGISTRATION_v6_mtf.md
    "MTF10_M5":         dict(pivot_n=10, ltf=5),
    "MTF10_M1":         dict(pivot_n=10, ltf=1),
    "MTF5_M5":          dict(pivot_n=5, ltf=5),
    "MTF5_M1":          dict(pivot_n=5, ltf=1),
    "MTF10_M5_T15":     dict(pivot_n=10, ltf=5, target_mult=1.5),
    "MTF10_M5_T30":     dict(pivot_n=10, ltf=5, target_mult=3.0),
    "MTF10_M5_NOTREND": dict(pivot_n=10, ltf=5, trend=False),
}


def ltf_arrays(tmin, H, L, C, k):
    """Bars of k minutes built from the M1 bars that exist: per-bar high / low / close / ATR14 and, per M1 index, whether
    it is the last M1 bar of its k-minute bar. ATR is Wilder smoothing (alpha 1/14) of the true range, seeded with the
    first true range; it uses bars up to and including the bar it is read for."""
    slot = tmin // k
    gs = np.flatnonzero(np.r_[True, slot[1:] != slot[:-1]]); ge = np.r_[gs[1:], len(slot)]
    hi = np.maximum.reduceat(H, gs); lo = np.minimum.reduceat(L, gs); cl = C[ge - 1]
    pc = np.r_[cl[0], cl[:-1]]
    tr = np.maximum(hi - lo, np.maximum(np.abs(hi - pc), np.abs(lo - pc)))
    atr = pd.Series(tr).ewm(alpha=1 / 14.0, adjust=False).mean().to_numpy(copy=True)
    atr[:14] = np.nan
    is_end = np.zeros(len(slot), dtype=bool); is_end[ge - 1] = True
    gidx = np.cumsum(np.r_[True, slot[1:] != slot[:-1]]) - 1
    return dict(is_end=is_end.tolist(), gidx=gidx.tolist(), hi=hi.tolist(), lo=lo.tolist(), cl=cl.tolist(), atr=atr.tolist(),
                open_min=(slot[gs] * k).tolist(), close_min=((slot[gs] + 1) * k).tolist())


def prepare(m1: pd.DataFrame):
    tmin = m1.index.values.astype("datetime64[m]").astype(np.int64)          # minutes since epoch (dataset clock = London time)
    O, H, L, C = (m1[c].values.astype(float) for c in ("open", "high", "low", "close"))
    assert (np.diff(tmin) > 0).all()
    slot = tmin // 15
    bs = np.flatnonzero(np.r_[True, slot[1:] != slot[:-1]]); be = np.r_[bs[1:], len(slot)]
    b_hi = np.maximum.reduceat(H, bs); b_lo = np.minimum.reduceat(L, bs); b_cl = C[be - 1]
    ema50 = np.empty(len(b_cl)); ema50[0] = b_cl[0]; a = 2.0 / 51.0
    for q in range(1, len(b_cl)): ema50[q] = ema50[q - 1] + a * (b_cl[q] - ema50[q - 1])
    sday = (tmin + 60) // 1440                                                # session day 23:00 -> 23:00
    ds = np.flatnonzero(np.r_[True, sday[1:] != sday[:-1]]); de = np.r_[ds[1:], len(sday)]
    d_hi = np.maximum.reduceat(H, ds); d_lo = np.minimum.reduceat(L, ds); d_cl = C[de - 1]; d_id = sday[ds]
    d_tr = d_hi - d_lo
    d_tr[1:] = np.maximum(d_tr[1:], np.maximum(np.abs(d_hi[1:] - d_cl[:-1]), np.abs(d_lo[1:] - d_cl[:-1])))
    d_atr = np.empty(len(d_tr)); d_atr[0] = d_tr[0]
    for q in range(1, len(d_tr)): d_atr[q] = d_atr[q - 1] + (d_tr[q] - d_atr[q - 1]) / 14.0
    return dict(tmin=tmin, O=O, H=H, L=L, C=C, be=be, b_hi=b_hi, b_lo=b_lo, b_cl=b_cl, ema50=ema50, sday=sday, d_atr=d_atr,
                d_index={int(k): i for i, k in enumerate(d_id)}, ltf={1: ltf_arrays(tmin, H, L, C, 1), 5: ltf_arrays(tmin, H, L, C, 5)})


def pivots(hi, lo, n):
    """{index of the confirming M15 bar: price}. Bar j is a swing high iff hi[j] >= max of the n bars before and of the n
    bars after; it is confirmed by the close of bar j + n."""
    m = len(hi); conf_hi, conf_lo = {}, {}
    if m < 2 * n + 1: return conf_hi, conf_lo
    wmax = sliding_window_view(hi, n).max(axis=1); wmin = sliding_window_view(lo, n).min(axis=1)
    j = np.arange(n, m - n)
    ph = (hi[j] >= wmax[j - n]) & (hi[j] >= wmax[j + 1]); pl = (lo[j] <= wmin[j - n]) & (lo[j] <= wmin[j + 1])
    for q in j[ph]: conf_hi[int(q) + n] = float(hi[q])
    for q in j[pl]: conf_lo[int(q) + n] = float(lo[q])
    return conf_hi, conf_lo


def run(vid: str, D: dict, over=None):
    cfg = dict(BASE); cfg.update(VARIANTS[vid]); cfg.update(over or {})
    SPREAD, SLIP, OFF = cfg["spread"], cfg["slippage"], cfg["offset"]
    WS, WE, FLAT, CAP = cfg["win_start"], cfg["win_end"], cfg["flat_at"], cfg["cap_entries"]
    tmult, trend_on = cfg["target_mult"], cfg["trend"]
    tmin, O, H, L, C = (D[k].tolist() for k in ("tmin", "O", "H", "L", "C"))
    b_end = D["be"].tolist(); b_cl = D["b_cl"].tolist(); ema50 = D["ema50"].tolist(); sday = D["sday"].tolist()
    d_atr = D["d_atr"].tolist(); d_index = D["d_index"]
    LT = D["ltf"][cfg["ltf"]]
    is_end, gidx, l_hi, l_lo, l_cl, l_atr, l_open, l_close = (LT[k] for k in ("is_end", "gidx", "hi", "lo", "cl", "atr", "open_min", "close_min"))
    conf_hi, conf_lo = pivots(D["b_hi"], D["b_lo"], cfg["pivot_n"])
    high = low = None; position = None; pend = None; trades = []
    counters = dict(signals=0, signals_blocked=0, refused_gap=0, late_or_closed=0, same_minute_stop=0, levels_high=0, levels_low=0, floor_used=0, cap_used=0)
    entries = 0; cur_day = None; prev = None; b = 0; nb = len(b_end)
    for n in range(len(tmin)):
        if b < nb and n == b_end[b]:
            # M15 bar b has just closed: levels confirmed by it become live now
            if b in conf_hi: high = dict(price=conf_hi[b], trig=conf_hi[b] + OFF, live=True); counters["levels_high"] += 1
            if b in conf_lo: low = dict(price=conf_lo[b], trig=conf_lo[b] - OFF, live=True); counters["levels_low"] += 1
            b += 1
        day = sday[n]
        if day != cur_day:
            cur_day = day; entries = 0; di = d_index[day]; prev = di - 1 if di > 0 else None
        o, h, l, c = O[n], H[n], L[n], C[n]; t = tmin[n]; mod = t % 1440
        just_opened = False
        # ---- 1) market entry scheduled by the signal bar that closed just before this minute
        if pend is not None:
            pe = pend; pend = None
            if position is None:
                if day != pe["day"] or t - pe["close_min"] > cfg["max_fill_delay"] or mod >= FLAT: counters["late_or_closed"] += 1
                else:
                    is_long = pe["side"] == "long"
                    fill = (o + SPREAD + SLIP) if is_long else (o - SLIP)
                    stop = pe["stop"]
                    if (is_long and fill <= stop) or ((not is_long) and fill >= stop): counters["refused_gap"] += 1
                    else:
                        risk = abs(fill - stop); entries += 1
                        P = dict(side=pe["side"], entry_min=t, entry_price=fill, initial_stop=stop, planned_risk=risk,
                                 target=(fill + tmult * risk) if is_long else (fill - tmult * risk), day=day, sig_open_min=pe["open_min"],
                                 sig_close_min=pe["close_min"], sig_close=pe["close"], level=pe["level"], dist=pe["dist"], clamp=pe["clamp"],
                                 ltf_atr=pe["ltf_atr"], d1atr=pe["d1atr"], entry_no=entries)
                        if is_long and l <= stop:
                            counters["same_minute_stop"] += 1
                            P.update(exit_min=t, exit_price=(l - SLIP if l < stop else stop - SLIP), exit_reason="stop_same_minute"); trades.append(P)
                        elif (not is_long) and h + SPREAD >= stop:
                            counters["same_minute_stop"] += 1
                            P.update(exit_min=t, exit_price=stop + SLIP, exit_reason="stop_same_minute"); trades.append(P)
                        else: position = P; just_opened = True
        # ---- 2) open position (from the minute after the fill)
        if position is not None and not just_opened:
            P = position; is_long = P["side"] == "long"; px = None
            if day != P["day"]: px, why = (o - SLIP if is_long else o + SPREAD + SLIP), "session_gap_exit"
            elif mod >= FLAT: px, why = (o - SLIP if is_long else o + SPREAD + SLIP), "time_exit"
            elif is_long:
                if l <= P["initial_stop"]: px, why = min(P["initial_stop"], o) - SLIP, "stop"
                elif h > P["target"]: px, why = P["target"], "target"
            else:
                if h + SPREAD >= P["initial_stop"]: px, why = max(P["initial_stop"], o + SPREAD) + SLIP, "stop"
                elif l + SPREAD < P["target"]: px, why = P["target"], "target"
            if px is not None:
                P.update(exit_min=t, exit_price=px, exit_reason=why); trades.append(P); position = None
        # ---- 3) an entry-timeframe bar closes at the end of this minute: signal and level life
        if is_end[n]:
            g = gidx[n]; cl = l_cl[g]
            hit_h = high is not None and high["live"] and cl >= high["trig"]
            hit_l = low is not None and low["live"] and cl <= low["trig"]
            if hit_h or hit_l:
                cmod = l_close[g] % 1440
                can = (position is None and pend is None and WS <= cmod < WE and entries < CAP and prev is not None
                       and b - 1 >= cfg["warmup"] and not math.isnan(l_atr[g]))
                for side, hit in (("long", hit_h), ("short", hit_l)):
                    if not hit: continue
                    lev = high if side == "long" else low
                    lev["live"] = False; counters["signals"] += 1
                    ok_trend = (not trend_on) or (b_cl[b - 1] > ema50[b - 1] if side == "long" else b_cl[b - 1] < ema50[b - 1])
                    if not (can and ok_trend): counters["signals_blocked"] += 1; continue
                    raw = (cl - (l_lo[g] - OFF)) if side == "long" else ((l_hi[g] + OFF) - cl)
                    floor = cfg["floor_k"] * l_atr[g]; capd = cfg["cap_k"] * d_atr[prev]
                    dist = min(max(raw, floor), capd)
                    clamp = "cap" if dist < raw else ("floor" if dist > raw else "none")
                    counters["floor_used"] += clamp == "floor"; counters["cap_used"] += clamp == "cap"
                    pend = dict(side=side, stop=(cl - dist) if side == "long" else (cl + dist), day=day, open_min=l_open[g], close_min=l_close[g],
                                close=cl, level=lev["price"], dist=dist, clamp=clamp, ltf_atr=l_atr[g], d1atr=d_atr[prev])
                    can = False
    out = pd.DataFrame(trades)
    if len(out):
        sign = np.where(out.side == "long", 1.0, -1.0)
        out["pnl_per_oz"] = sign * (out.exit_price - out.entry_price)
        out["realised_R"] = out.pnl_per_oz / out.planned_risk
        for c_new, c_old in (("entry_time", "entry_min"), ("exit_time", "exit_min"), ("signal_bar_open", "sig_open_min"), ("signal_time", "sig_close_min")):
            out[c_new] = pd.to_datetime(out[c_old].values.astype("int64") * 60, unit="s", utc=True)
        out["hold_minutes"] = (out.exit_min - out.entry_min).astype(float)
        out.insert(0, "variant", "V6_" + vid)
    return out, counters, cfg


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]; stress = "--stress" in sys.argv
    ids = args or list(VARIANTS)
    m1 = pd.read_parquet(DATA); D = prepare(m1)
    over = dict(spread=0.50, slippage=0.10) if stress else None
    for vid in ids:
        t0 = time.time(); tr, counters, cfg = run(vid, D, over)
        out = RES / ("V6_" + vid + ("_stress" if stress else "")); out.mkdir(parents=True, exist_ok=True)
        tr.to_csv(out / "trades.csv", index=False)
        (out / "config.json").write_text(json.dumps(dict(config=cfg, n_trades=int(len(tr)), counters={k: int(v) for k, v in counters.items()},
                                                         data_start=str(m1.index[0]), data_end=str(m1.index[-1])), indent=2))
        print(f"V6_{vid}{'_stress' if stress else ''}: trades={len(tr)} counters={ {k: int(v) for k, v in counters.items()} } ({time.time() - t0:.0f} s)", flush=True)

if __name__ == "__main__":
    main()
