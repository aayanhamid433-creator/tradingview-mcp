#!/usr/bin/env python3
"""Mechanics validation for engine.py (validates the SIMULATOR, not profitability).

1. Independent, loop-based Wilder ADX/DI/ATR and recursive EMA vs engine indicators().
2. Arithmetic checks of realised R for long/short with spread, slippage and commission.
3. Independent re-derivation of every V0_base trade from raw M1 data:
   signal-bar conditions, entry level, first-touch fill minute, stop placement, exit minute/reason, P&L sign.
4. Prints three hand-check trades (development period) with surrounding M1 bars.
Writes ../results/VALIDATION_MECHANICS.md
"""
import pathlib, json, numpy as np, pandas as pd
import engine as E

HERE = pathlib.Path(__file__).resolve().parent
RES = HERE.parent / "results"
cfg = dict(E.BASE_CONFIG); cfg.update(E.VARIANTS["V0_base"])
m1 = pd.read_parquet(E.DATA)
m15 = m1.resample("15min", label="left", closed="left").agg(open=("open","first"), high=("high","max"), low=("low","min"), close=("close","last")).dropna()
ind = E.indicators(m15, cfg)
lines = ["# Mechanics validation of the backtest engine (GOLD_PLAYBOOK v1.0)", "", "This validates the simulator's bookkeeping, not profitability.", ""]

# ---- 1. independent indicators
h, l, c = m15.high.values, m15.low.values, m15.close.values
n = cfg["adx_len"]; N = len(c)
tr = np.zeros(N); pdm = np.zeros(N); mdm = np.zeros(N)
for i in range(1, N):
    tr[i] = max(h[i]-l[i], abs(h[i]-c[i-1]), abs(l[i]-c[i-1]))
    up = h[i]-h[i-1]; dn = l[i-1]-l[i]
    pdm[i] = up if (up > dn and up > 0) else 0.0
    mdm[i] = dn if (dn > up and dn > 0) else 0.0
tr[0] = h[0]-l[0]
def rma_loop(x):
    out = np.full(N, np.nan); out[n-1] = x[:n].mean()
    for i in range(n, N): out[i] = (out[i-1]*(n-1) + x[i])/n
    return out
atr = rma_loop(tr); pdi = 100*rma_loop(pdm)/atr; mdi = 100*rma_loop(mdm)/atr
dx = np.where((pdi+mdi) > 0, 100*np.abs(pdi-mdi)/(pdi+mdi), 0.0); dx = np.nan_to_num(dx)
adx = rma_loop(dx); adx[:2*n] = np.nan
ema = np.full(N, np.nan); k = 2/(cfg["ema_len"]+1); ema[0] = c[0]
for i in range(1, N): ema[i] = c[i]*k + ema[i-1]*(1-k)
def maxdiff(a, b):
    m = ~(np.isnan(a) | np.isnan(b)); return float(np.max(np.abs(a[m]-b[m])))
d = dict(ADX=maxdiff(adx, ind.adx.values), plusDI=maxdiff(pdi, ind.pdi.values), minusDI=maxdiff(mdi, ind.mdi.values),
         ATR=maxdiff(atr, ind.atr.values), EMA=maxdiff(ema, ind.ema.values))
lines += ["## 1. Indicator cross-check (independent loop implementation vs engine)", "", "| indicator | max abs difference over all bars |", "|---|---|"]
lines += [f"| {k} | {v:.2e} |" for k, v in d.items()]
assert all(v < 1e-6 for v in d.values()), d
# sanity: ADX range
lines += ["", f"ADX range {np.nanmin(adx):.1f}–{np.nanmax(adx):.1f}; share of M15 bars with ADX>30: {np.nanmean(adx>30)*100:.1f}%", ""]

# ---- 2. arithmetic checks
lines += ["## 2. P&L arithmetic checks", ""]
def realised(side, level, stop, entry, exit, comm):
    risk = abs(level-stop); sign = 1 if side == "long" else -1
    return (sign*(exit-entry) - comm)/risk
cases = [("long", 2000.10, 1995.10, 2000.15, 1995.05, 0.0, (1995.05-2000.15)/5.0),    # stopped long with slippage -> < -1R
         ("long", 2000.10, 1995.10, 2000.15, 2010.00, 0.0, (2010.00-2000.15)/5.0),
         ("short", 1999.90, 2004.90, 1999.85, 2004.95, 0.0, -(2004.95-1999.85)/5.0),
         ("short", 1999.90, 2004.90, 1999.85, 1990.00, 0.07, (1999.85-1990.00-0.07)/5.0)]
lines += ["| side | level | stop | entry fill | exit | commission | expected R | computed R |", "|---|---|---|---|---|---|---|---|"]
for side, lv, st, en, ex, cm, exp in cases:
    got = realised(side, lv, st, en, ex, cm); assert abs(got-exp) < 1e-12
    lines.append(f"| {side} | {lv} | {st} | {en} | {ex} | {cm} | {exp:.4f} | {got:.4f} |")
lines += ["", "A stopped trade with 0.05 slippage realises −1.02 R (loss exceeds the planned 1 R), as intended.", ""]

# ---- 3. independent trade re-derivation
tr_df = pd.read_csv(RES / "V0_base" / "trades.csv", parse_dates=["signal_bar_open", "last_touch_open", "entry_time", "exit_time"])
for col in ["signal_bar_open", "last_touch_open", "entry_time", "exit_time"]:
    if tr_df[col].dt.tz is None: tr_df[col] = tr_df[col].dt.tz_localize("UTC")
spread, slip, comm = cfg["spread"], cfg["slippage"], cfg["commission_rt"]
armed_thr = cfg["adx_threshold"]
problems = []; checks = dict(signal_conditions=0, entry_level=0, entry_minute=0, stop_rule=0, geometry=0, exit_rule=0, exit_price=0, pnl_sign=0)
idx15 = {t: i for i, t in enumerate(m15.index)}
m1h, m1l, m1o = m1.high, m1.low, m1.open
for r in tr_df.itertuples():
    i = idx15[r.signal_bar_open]; j = idx15[r.last_touch_open]
    # signal conditions at first touch bar
    rising = any((adx[k] > armed_thr and adx[k] > adx[k-1]) for k in range(i-cfg["adx_rising_lookback"], i+1))
    cond = adx[i] > armed_thr and rising and l[i] <= ema[i] <= h[i] and ((pdi[i] > mdi[i]) == (r.side == "long"))
    if cond: checks["signal_conditions"] += 1
    else: problems.append((r.Index, "signal_conditions"))
    # entry level from last touch bar
    exp_level = h[j] + cfg["entry_offset"] if r.side == "long" else l[j] - cfg["entry_offset"]
    if abs(exp_level - r.level) < 1e-9: checks["entry_level"] += 1
    else: problems.append((r.Index, "entry_level"))
    # entry minute: first M1 strictly after the last touch bar closed with ask high >= level (long) / bid low <= level (short)
    act = r.last_touch_open + pd.Timedelta(minutes=15)
    seg = m1.loc[act:r.entry_time]
    hits = (seg.high + spread >= r.level) if r.side == "long" else (seg.low <= r.level)
    first_hit = seg.index[hits.values][0] if hits.any() else None
    if first_hit == r.entry_time: checks["entry_minute"] += 1
    else: problems.append((r.Index, "entry_minute", first_hit, r.entry_time))
    # stop rule: beyond the lowest low (highest high) from first touch bar open to entry minute, by >= buffer
    seq = m1.loc[r.signal_bar_open:r.entry_time]
    buffer = max(cfg["stop_buffer_min"], cfg["stop_buffer_atr"] * atr[i])
    exp_stop = seq.low.min() - buffer if r.side == "long" else seq.high.max() + buffer
    if abs(exp_stop - r.stop) < 1e-9: checks["stop_rule"] += 1
    else: problems.append((r.Index, "stop_rule", exp_stop, r.stop))
    # geometry
    geo = (r.stop < r.entry_price < r.target) if r.side == "long" else (r.target < r.entry_price < r.stop)
    if geo: checks["geometry"] += 1
    else: problems.append((r.Index, "geometry"))
    # exit: scan M1 after entry minute
    after = m1.loc[r.entry_time + pd.Timedelta(minutes=1):]
    mod = after.index.hour*60 + after.index.minute
    if r.side == "long":
        stop_hit = after.low <= r.stop; tgt_hit = after.high > r.target
    else:
        stop_hit = after.high + spread >= r.stop; tgt_hit = after.low + spread < r.target
    texit = mod >= E.hhmm(cfg["time_exit"])
    ev = np.where(stop_hit | tgt_hit | texit)[0]
    if r.exit_reason == "stop_same_minute":
        ok = r.exit_time == r.entry_time
    else:
        k0 = ev[0]; t_ex = after.index[k0]
        reason = "time_exit" if texit[k0] else ("stop" if stop_hit.iloc[k0] else "target")
        ok = (t_ex == r.exit_time) and (reason == r.exit_reason)
    if ok: checks["exit_rule"] += 1
    else: problems.append((r.Index, "exit_rule", r.exit_reason, r.exit_time))
    # exit price plausibility
    bar = m1.loc[r.exit_time]
    if r.exit_reason in ("stop", "stop_same_minute"):
        okp = (r.exit_price <= r.stop - slip + 1e-9) if r.side == "long" else (r.exit_price >= r.stop + slip - 1e-9)
    elif r.exit_reason == "target": okp = abs(r.exit_price - r.target) < 1e-9
    else: okp = abs(r.exit_price - ((bar.open - slip) if r.side == "long" else (bar.open + spread + slip))) < 1e-9
    if okp: checks["exit_price"] += 1
    else: problems.append((r.Index, "exit_price"))
    sign_ok = (np.sign(r.realised_R) == np.sign((r.exit_price - r.entry_price) * (1 if r.side == "long" else -1) - comm)) or r.realised_R == 0
    if sign_ok: checks["pnl_sign"] += 1
    else: problems.append((r.Index, "pnl_sign"))
lines += ["## 3. Independent re-derivation of every V0_base trade from raw M1 data", "", f"Trades checked: {len(tr_df)}", "",
          "| check | passed | failed |", "|---|---|---|"]
lines += [f"| {k} | {v} | {len(tr_df)-v} |" for k, v in checks.items()]
if problems:
    lines += ["", "### Discrepancies", ""] + [f"- {p}" for p in problems[:40]]
lines += ["", "Notes: the engine's stop uses the lowest low from the first touch bar through the fill minute (the verifier recomputes it from M1 lows directly);",
          "short-side stop/target tests use ask = bid + spread; exits are re-derived by scanning M1 bars after the entry minute.", ""]

# ---- 4. hand-check printouts (development period only)
dev = tr_df[tr_df.signal_bar_open < pd.Timestamp("2024-07-01", tz="UTC")]
picks = [dev[dev.exit_reason == "target"].iloc[0], dev[dev.exit_reason == "stop"].iloc[0], dev[(dev.side == "short") & (dev.exit_reason == "time_exit")].iloc[0]]
lines += ["## 4. Hand-check examples (development period)", ""]
for r in picks:
    i = idx15[r.signal_bar_open]
    lines += [f"### Trade: {r.side} signalled by M15 bar opening {r.signal_bar_open} (ADX {adx[i]:.1f}, +DI {pdi[i]:.1f}, −DI {mdi[i]:.1f}, EMA20 {ema[i]:.2f}, bar H/L {h[i]:.2f}/{l[i]:.2f})", "",
              f"- Entry stop level {r.level:.2f}; filled {r.entry_time} at {r.entry_price:.2f}; stop {r.stop:.2f}; target {r.target:.2f}; planned risk {r.planned_risk:.2f} USD/oz; exit {r.exit_time} at {r.exit_price:.2f} ({r.exit_reason}); realised {r.realised_R:+.2f} R", "",
              "M1 bars around the entry (bid):", "", "| time (UTC) | open | high | low | close |", "|---|---|---|---|---|"]
    seg = m1.loc[r.entry_time - pd.Timedelta(minutes=2): r.entry_time + pd.Timedelta(minutes=1)]
    lines += [f"| {t:%Y-%m-%d %H:%M} | {b.open:.2f} | {b.high:.2f} | {b.low:.2f} | {b.close:.2f} |" for t, b in seg.iterrows()]
    lines += ["", "M1 bars around the exit (bid):", "", "| time (UTC) | open | high | low | close |", "|---|---|---|---|---|"]
    seg = m1.loc[r.exit_time - pd.Timedelta(minutes=2): r.exit_time + pd.Timedelta(minutes=1)]
    lines += [f"| {t:%Y-%m-%d %H:%M} | {b.open:.2f} | {b.high:.2f} | {b.low:.2f} | {b.close:.2f} |" for t, b in seg.iterrows()]
    lines.append("")
(RES / "VALIDATION_MECHANICS.md").write_text("\n".join(lines))
print("\n".join(lines[:60]))
print("problems:", len(problems))
