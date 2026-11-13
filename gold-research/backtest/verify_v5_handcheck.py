#!/usr/bin/env python3
"""verify_v5_handcheck.py — hand-check of individual HL trades against the raw M1 bars.

For each requested reading two trades are drawn with a fixed seed (one long, one short, different exit reasons where
possible; never chosen by outcome size) and re-derived from the raw data with plain pandas / loops:
  1. the marked high and low (pivot bars and their neighbours, or the previous session day's extremes) and that no
     newer level of the same kind was confirmed before the order step;
  2. liveness of the traded level (raw M1 extremes from its creation to the entry minute) and the recorded live flag
     of the opposite level;
  3. stop distance (raw, floor, cap), stop and target from ATR14(M15) at the computation close and the previous
     session day's D1ATR;
  4. the fill minute, side and price (bars around the entry printed; no earlier minute could have filled the order);
  5. the exit minute, price and reason (bars around the exit printed; RR: first stop/target print; TRAIL: the stop path
     is rebuilt minute by minute), and R.
Nothing is imported from the engines. Prints PASS/FAIL per item; no aggregate performance figure.

Usage: python3 verify_v5_handcheck.py [ID ...] [--rows i,j]     (default: all six readings, seeded picks)
"""
import sys, pathlib, math
import numpy as np, pandas as pd
import verify_v5_replay as RP     # prepare(): own M15 / ATR / session-day arrays (independent of the engines)

HERE = pathlib.Path(__file__).resolve().parent
RES = HERE.parent / "results"
SEED = 20261113
S, SL = RP.SPREAD, RP.SLIP
pd.set_option("display.width", 220); pd.set_option("display.max_columns", 30)


def minute(ts): return int(pd.Timestamp(ts).tz_convert("UTC").value // 60_000_000_000) if pd.Timestamp(ts).tzinfo else int(pd.Timestamp(ts).value // 60_000_000_000)

def show(m1, lo_t, hi_t, mark=None):
    w = m1.loc[lo_t:hi_t].copy(); w["ask_high"] = w.high + S; w["ask_low"] = w.low + S; w["ask_open"] = w.open + S
    w.index = [f"{t:%Y-%m-%d %H:%M}" + ("  <==" if mark is not None and t == mark else "") for t in w.index]
    print(w.round(3).to_string())

def verdict(name, ok, detail=""):
    print(f"   [{'PASS' if ok else 'FAIL'}] {name}{(' — ' + detail) if detail else ''}")
    return bool(ok)


def check_trade(vid, tr, row, m1, D, prev_exit):
    spec = RP.READINGS[vid]; swing = spec["levels"] == "swing"; trail = spec["exit"] == "trail"; N = spec["n"]
    t = tr.iloc[row]; ok = True; is_long = t.side == "long"
    b_open = D["b_open_min"]; b_hi, b_lo, atr = D["b_hi"], D["b_lo"], D["atr"]; tmin = D["tmin"]
    print("=" * 150)
    print(f"{vid}  trade row {row}: {t.side.upper()}  signal_time {t.signal_time}  entry {t.entry_time} @ {t.entry_price:.3f}  level(trigger) {t.level:.3f}  "
          f"stop {t.initial_stop:.3f}  target {t.target if not pd.isna(t.target) else 'none'}\n"
          f"   exit {t.exit_time} @ {t.exit_price:.3f} ({t.exit_reason})  planned_risk {t.planned_risk:.3f}  realised_R {t.realised_R:+.4f}  "
          f"marked high {t.level_high:.3f} (created {t.level_high_created}, live at placement {t.level_high_live})  "
          f"marked low {t.level_low:.3f} (created {t.level_low_created}, live {t.level_low_live})  entry_no {t.entry_no}")
    sig_close = minute(t.signal_time); sig_bar = int(np.searchsorted(b_open, sig_close - 15)); assert b_open[sig_bar] == sig_close - 15
    # ---------------- 1. marked levels
    print("-- 1. marked levels")
    for kind, price, created in (("high", t.level_high, t.level_high_created), ("low", t.level_low, t.level_low_created)):
        cmin = minute(created)
        if swing:
            ci = int(np.searchsorted(b_open, cmin - 15)); assert b_open[ci] == cmin - 15, "confirmation bar not found"
            j = ci - N; arr = b_hi if kind == "high" else b_lo
            win = pd.DataFrame({"bar_open": pd.to_datetime(b_open[j - N:ci + 1] * 60, unit="s"), "high": b_hi[j - N:ci + 1], "low": b_lo[j - N:ci + 1]})
            win["role"] = ["before"] * N + ["PIVOT"] + ["after"] * N
            print(f"   swing {kind}: pivot bar {pd.to_datetime(b_open[j] * 60, unit='s')}, confirmed at the close of {pd.to_datetime(b_open[ci] * 60, unit='s')} (= {pd.to_datetime(cmin * 60, unit='s')})")
            print("   " + win.round(3).to_string().replace("\n", "\n   "))
            if kind == "high": piv = arr[j] >= arr[j - N:j].max() and arr[j] >= arr[j + 1:j + N + 1].max()
            else: piv = arr[j] <= arr[j - N:j].min() and arr[j] <= arr[j + 1:j + N + 1].min()
            ok &= verdict(f"bar is a swing {kind} with N={N} and its price equals the marked {kind}", piv and abs(arr[j] - price) < 1e-9, f"{arr[j]:.3f} vs {price:.3f}")
            # no newer pivot of this kind confirmed in (ci, sig_bar]
            newer = []
            for q in range(ci + 1, sig_bar + 1):
                jj = q - N
                if kind == "high" and arr[jj] >= arr[jj - N:jj].max() and arr[jj] >= arr[jj + 1:jj + N + 1].max(): newer.append(q)
                if kind == "low" and arr[jj] <= arr[jj - N:jj].min() and arr[jj] <= arr[jj + 1:jj + N + 1].min(): newer.append(q)
            ok &= verdict(f"no newer swing {kind} confirmed between its creation and the order step ({sig_bar - ci} M15 closes scanned)", not newer, str(newer))
            ok &= verdict("confirmation is causal (created at or before the order step)", cmin <= sig_close)
        else:
            sd = (sig_close - 15 + 60) // 1440                                  # session day of the signal bar
            pm = (D["sday"] == sd - 1)
            if not pm.any():   # previous session day is not the previous calendar day (Monday, holiday): take the last earlier session day
                prev_ids = np.unique(D["sday"][D["sday"] < sd]); pm = (D["sday"] == prev_ids[-1])
            seg = m1.iloc[np.flatnonzero(pm)]
            val = seg.high.max() if kind == "high" else seg.low.min()
            print(f"   previous session day = M1 bars {seg.index[0]} .. {seg.index[-1]} ({len(seg)} bars): {kind} = {val:.3f}")
            ok &= verdict(f"previous session day's {kind} equals the marked {kind}", abs(val - price) < 1e-9, f"{val:.3f} vs {price:.3f}")
            first_today = m1.index[np.flatnonzero(D["sday"] == sd)[0]]
            ok &= verdict("level created at the first bar of the session day", pd.Timestamp(created) == first_today, f"{created} vs {first_today}")
    # ---------------- 2. liveness
    print("-- 2. liveness (raw M1 bid extremes from creation to the entry minute)")
    emin = minute(pd.Timestamp(t.entry_time, tz="UTC") if pd.Timestamp(t.entry_time).tzinfo is None else t.entry_time)
    e_idx = int(np.searchsorted(tmin, emin)); assert tmin[e_idx] == emin
    for kind, price, created, live_flag in (("high", t.level_high, t.level_high_created, t.level_high_live), ("low", t.level_low, t.level_low_created, t.level_low_live)):
        c_idx = int(np.searchsorted(tmin, minute(created)))
        s_idx = int(np.searchsorted(tmin, sig_close))   # first minute after the order step
        if kind == "high":
            trig = price + RP.OFFSET; ext_to_sig = D["H"][c_idx:s_idx].max() if s_idx > c_idx else -np.inf; ext_to_entry = D["H"][c_idx:e_idx].max() if e_idx > c_idx else -np.inf
            live_at_sig = ext_to_sig < trig; untouched = ext_to_entry < trig
            print(f"   high: trigger {trig:.3f}; max bid high creation->order step {ext_to_sig:.3f}; creation->entry minute (excl.) {ext_to_entry:.3f}")
        else:
            trig = price - RP.OFFSET; ext_to_sig = D["L"][c_idx:s_idx].min() if s_idx > c_idx else np.inf; ext_to_entry = D["L"][c_idx:e_idx].min() if e_idx > c_idx else np.inf
            live_at_sig = ext_to_sig > trig; untouched = ext_to_entry > trig
            print(f"   low: trigger {trig:.3f}; min bid low creation->order step {ext_to_sig:.3f}; creation->entry minute (excl.) {ext_to_entry:.3f}")
        traded = (kind == "high") == is_long
        if traded: ok &= verdict(f"traded {kind} never printed at/through its trigger on the bid before the entry minute", untouched and bool(live_flag))
        else:
            # the opposite level may also have been consumed earlier by its own order's ask-side trigger; the bid test is a lower bound
            ok &= verdict(f"opposite {kind}: recorded live flag ({bool(live_flag)}) is consistent with the bid scan (live by bid: {bool(live_at_sig)})",
                          (bool(live_flag) == bool(live_at_sig)) or (kind == "high" and not live_flag and live_at_sig),
                          "a high can also be consumed by its own buy stop's ask-side trigger" if (kind == "high" and not live_flag and live_at_sig) else "")
    # ---------------- 3. stop / target
    print("-- 3. stop distance, stop, target")
    cmin = minute(t.calc_time); cb = int(np.searchsorted(b_open, cmin - 15)); assert b_open[cb] == cmin - 15
    a = atr[cb]; sd = (cmin - 15 + 60) // 1440; di = D["d_index"][int(sd)]; d1 = D["d_atr"][di - 1]
    trig = t.level_high + RP.OFFSET if is_long else t.level_low - RP.OFFSET
    raw = trig - t.level_low if is_long else t.level_high - trig
    floor, cap = RP.FLOOR_K * a, RP.CAP_K * d1; dist = min(max(raw, floor), cap)
    stop = trig - dist if is_long else trig + dist
    tgt = None if trail else (trig + RP.TARGET_K * dist if is_long else trig - RP.TARGET_K * dist)
    print(f"   computed at {t.calc_time}: ATR14(M15) of the bar just closed = {a:.4f} (engine {t.atr_m15:.4f}); previous session day D1ATR = {d1:.4f} (engine {t.d1atr:.4f})")
    print(f"   trigger {trig:.3f}; raw distance to the opposite level {raw:.3f}; floor 0.3 x ATR = {floor:.3f}; cap 0.6 x D1ATR = {cap:.3f} -> distance {dist:.3f} "
          f"({'cap' if dist < raw else 'floor' if dist > raw else 'unclamped'}; engine {t.stop_clamp})")
    ok &= verdict("trigger = marked level +/- 0.10", abs(trig - t.level) < 1e-9, f"{trig:.3f} vs {t.level:.3f}")
    ok &= verdict("stop", abs(stop - t.initial_stop) < 1e-9, f"{stop:.3f} vs {t.initial_stop:.3f}")
    ok &= verdict("target", (tgt is None and pd.isna(t.target)) or (tgt is not None and abs(tgt - t.target) < 1e-9), f"{tgt} vs {t.target}")
    ok &= verdict("planned risk = |trigger - stop|", abs(dist - t.planned_risk) < 1e-9, f"{dist:.3f} vs {t.planned_risk:.3f}")
    # the cache: parameters may only be older than the order step if neither level changed in between (checked in 1.)
    ok &= verdict("parameters computed after both levels existed and not after the order step", cmin <= sig_close and cmin >= max(minute(t.level_high_created), minute(t.level_low_created)))
    # ---------------- 4. entry
    print("-- 4. entry (raw M1 bars, BID; ask = bid + 0.25)")
    et = m1.index[e_idx]
    show(m1, et - pd.Timedelta(minutes=4), et + pd.Timedelta(minutes=2), mark=et)
    o, h, l = D["O"][e_idx], D["H"][e_idx], D["L"][e_idx]
    if is_long: trig_ok = h + S >= trig; fill = max(trig, o + S) + SL
    else: trig_ok = l <= trig; fill = min(trig, o) - SL
    ok &= verdict("entry minute triggers the stop order (long: ask high >= trigger; short: bid low <= trigger)", trig_ok)
    ok &= verdict("fill price (long: max(trigger, ask open) + 0.05; short: min(trigger, bid open) - 0.05)", abs(fill - t.entry_price) < 1e-9, f"{fill:.3f} vs {t.entry_price:.3f}")
    mod_e = emin % 1440
    ok &= verdict("entry minute inside the order window [07:00, 16:00) and after the order step", RP.WIN_START <= mod_e < RP.WIN_END and emin >= sig_close and emin < sig_close + 15)
    # earliest minute at which the order could have rested: the first order step after (a) both levels exist, (b) 07:00 of the entry day, (c) the previous trade's exit
    day0 = (emin // 1440) * 1440
    rest_from = max(minute(t.level_high_created), minute(t.level_low_created), day0 + RP.WIN_START)
    if prev_exit is not None: rest_from = max(rest_from, ((minute(prev_exit) // 15) + 1) * 15)
    r_idx = int(np.searchsorted(tmin, rest_from))
    if is_long: early = np.flatnonzero(D["H"][r_idx:e_idx] + S >= trig)
    else: early = np.flatnonzero(D["L"][r_idx:e_idx] <= trig)
    ok &= verdict(f"no earlier minute since the order could first rest ({pd.to_datetime(rest_from * 60, unit='s')}, {e_idx - r_idx} minutes) would have triggered it", len(early) == 0,
                  "" if len(early) == 0 else f"first at {m1.index[r_idx + early[0]]}")
    # ---------------- 5. exit
    print("-- 5. exit")
    xmin = minute(pd.Timestamp(t.exit_time, tz="UTC") if pd.Timestamp(t.exit_time).tzinfo is None else t.exit_time)
    x_idx = int(np.searchsorted(tmin, xmin)); xt = m1.index[x_idx]
    show(m1, xt - pd.Timedelta(minutes=3), xt + pd.Timedelta(minutes=1), mark=xt)
    stop_now = stop; ext = fill; res = None; changes = []
    if (is_long and l <= stop) or ((not is_long) and h + S >= stop):
        res = (e_idx, (l - SL if l < stop else stop - SL) if is_long else stop + SL, "stop_same_minute")
    q = e_idx + 1
    while res is None and q < len(tmin):
        o2, h2, l2 = D["O"][q], D["H"][q], D["L"][q]; mod = tmin[q] % 1440
        if D["sday"][q] != D["sday"][e_idx]: res = (q, o2 - SL if is_long else o2 + S + SL, "session_gap_exit"); break
        if mod >= RP.FLAT_AT: res = (q, o2 - SL if is_long else o2 + S + SL, "time_exit"); break
        if is_long:
            if l2 <= stop_now: res = (q, min(stop_now, o2) - SL, "stop" if stop_now == stop else "trail_stop"); break
            if tgt is not None and h2 > tgt: res = (q, tgt, "target"); break
        else:
            if h2 + S >= stop_now: res = (q, max(stop_now, o2 + S) + SL, "stop" if stop_now == stop else "trail_stop"); break
            if tgt is not None and l2 + S < tgt: res = (q, tgt, "target"); break
        if trail:
            bq = int(np.searchsorted(b_open, (tmin[q] // 15) * 15)); a_prev = atr[bq - 1]
            if is_long:
                ext = max(ext, h2); cand = ext - RP.TRAIL_K * a_prev
                if cand > stop_now and cand < l2: stop_now = cand; changes.append((m1.index[q], ext, a_prev, cand))
            else:
                ext = min(ext, l2); cand = ext + RP.TRAIL_K * a_prev
                if cand < stop_now and cand > h2 + S: stop_now = cand; changes.append((m1.index[q], ext, a_prev, cand))
        q += 1
    if trail:
        print(f"   trail: {len(changes)} ratchets; last three (minute, running extreme, ATR14 of last closed M15 bar, new stop):")
        for cg in changes[-3:]: print(f"      {cg[0]:%Y-%m-%d %H:%M}  extreme {cg[1]:.3f}  ATR {cg[2]:.4f}  stop -> {cg[3]:.3f}")
        ok &= verdict("final stop", abs(stop_now - t.final_stop) < 1e-9, f"{stop_now:.3f} vs {t.final_stop:.3f}")
    ok &= verdict("exit minute", res is not None and tmin[res[0]] == xmin, f"{m1.index[res[0]] if res else None} vs {t.exit_time}")
    ok &= verdict("exit price", res is not None and abs(res[1] - t.exit_price) < 1e-9, f"{res[1]:.3f} vs {t.exit_price:.3f}" if res else "")
    ok &= verdict("exit reason", res is not None and res[2] == t.exit_reason, f"{res[2] if res else None} vs {t.exit_reason}")
    R = (1 if is_long else -1) * (t.exit_price - t.entry_price) / dist
    print(f"   R = {'+' if is_long else '-'}({t.exit_price:.3f} - {t.entry_price:.3f}) / {dist:.3f} = {R:+.4f}")
    ok &= verdict("realised R", abs(R - t.realised_R) < 1e-9, f"{R:+.4f} vs {t.realised_R:+.4f}")
    print(f"   ==> trade {vid} row {row}: {'ALL CHECKS PASS' if ok else 'CHECK FAILED'}")
    return ok


def pick(tr, rng):
    """One long and one short, drawn uniformly at random (fixed seed); the short is drawn among exit reasons different from the long's if any exist."""
    longs = np.flatnonzero((tr.side == "long").values); a = int(rng.choice(longs))
    shorts = np.flatnonzero(((tr.side == "short") & (tr.exit_reason != tr.exit_reason.iloc[a])).values)
    if len(shorts) == 0: shorts = np.flatnonzero((tr.side == "short").values)
    return [a, int(rng.choice(shorts))]


def main():
    args = sys.argv[1:]; rows = None
    if "--rows" in args:
        k = args.index("--rows"); rows = [int(x) for x in args[k + 1].split(",")]; args = args[:k] + args[k + 2:]
    ids = args or list(RP.READINGS)
    m1 = pd.read_parquet(RP.DATA); D = RP.prepare(m1)
    rng = np.random.default_rng(SEED); all_ok = True; summary = []
    for vid in ids:
        tr = pd.read_csv(RES / f"V5_{vid}" / "trades.csv")
        chosen = rows if rows is not None else pick(tr, rng)
        for r in chosen:
            ok = check_trade(vid, tr, r, m1, D, tr.exit_time.iloc[r - 1] if r > 0 else None)
            all_ok &= ok; t = tr.iloc[r]
            summary.append(f"{vid} row {r}: {t.side} {t.entry_time} @ {t.entry_price:.3f} -> {t.exit_reason} {t.exit_time} @ {t.exit_price:.3f}, R {t.realised_R:+.3f}: {'PASS' if ok else 'FAIL'}")
    print("=" * 150); print("\n".join(summary)); print("HAND-CHECK:", "PASS" if all_ok else "FAIL")
    if not all_ok: raise SystemExit(1)

if __name__ == "__main__":
    main()
