"""Would the 50k account survive HL_C_W01_RH4?  (solo run; the agent version was cut off by the usage limit)
Firm: daily loss 3 % of the day's starting equity (floating included), trailing floor 6 % below peak equity.
Guard in the Pine script: no new trades once the day's loss reaches 2 % or equity is within 500 USD of the floor.
One position at a time, so the worst intraday equity of a trade = equity before it - size x worst adverse move."""
import sys
sys.path.insert(0, "/home/user/tradingview-mcp/gold-research/backtest")
import numpy as np, pandas as pd
import engine as E
R = E.DATA.parent.parent / "results"
m1 = pd.read_parquet(E.DATA)
tmin = m1.index.values.astype("datetime64[m]").astype(np.int64); H = m1["high"].values; L = m1["low"].values
def load(n):
    t = pd.read_csv(R / n / "trades.csv")
    for c in ["signal_bar_open", "entry_time", "exit_time"]: t[c] = pd.to_datetime(t[c], utc=True, format="mixed")
    t = t.sort_values("entry_time").reset_index(drop=True)
    a = np.searchsorted(tmin, t.entry_time.values.astype("datetime64[m]").astype(np.int64)); b = np.searchsorted(tmin, t.exit_time.values.astype("datetime64[m]").astype(np.int64))
    mae = np.empty(len(t)); mfe = np.empty(len(t))
    for i in range(len(t)):
        lo = L[a[i]:b[i] + 1].min(); hi = H[a[i]:b[i] + 1].max(); ep = t.entry_price[i]
        if t.side[i] == "long": mae[i] = max(0.0, ep - lo); mfe[i] = max(0.0, hi - ep)
        else: mae[i] = max(0.0, hi + 0.25 - ep); mfe[i] = max(0.0, ep - (lo + 0.25))
    t["mae"] = mae; t["mfe"] = mfe; t["date"] = t.entry_time.dt.date
    return t
def simulate(t, f, start=50000.0, guard=True):
    eq = start; peak = start; floor = start * 0.94
    day = None; day0 = eq; day_halt = False; dead = None; breach = None; halted_days = set(); skipped = 0
    worst_day_pct = 0.0; min_room = eq - floor; maxdd = 0.0; hi_water = eq; big = 0.0; n = 0; fl700 = 0
    for r in t.itertuples():
        if r.date != day: day = r.date; day0 = eq; day_halt = False
        if breach is not None: break
        if guard and (dead is not None or day_halt): skipped += 1; continue
        if guard and eq - floor <= 500: dead = r.date; skipped += 1; continue
        qty = np.floor(eq * f / r.planned_risk)
        qty = min(qty, 200.0, np.floor(eq * 0.5 / (r.entry_price * 0.05)))
        if qty < 1: skipped += 1; continue
        n += 1
        low_eq = eq - qty * r.mae; high_eq = eq + qty * r.mfe
        if qty * r.mae >= 700: fl700 += 1
        if high_eq > peak: peak = high_eq; floor = max(floor, peak * 0.94)      # floating peaks raise the floor (strict reading)
        day_loss_pct = (day0 - low_eq) / day0 * 100; worst_day_pct = max(worst_day_pct, day_loss_pct)
        min_room = min(min_room, low_eq - floor)
        if low_eq <= floor: breach = (r.date, "trailing floor"); break
        if day_loss_pct >= 3.0: breach = (r.date, "daily 3 %"); break
        pnl = qty * r.pnl_per_oz; eq += pnl; big = min(big, pnl)
        hi_water = max(hi_water, eq); maxdd = min(maxdd, eq - hi_water)
        if guard and (day0 - eq) / day0 * 100 >= 2.0: day_halt = True; halted_days.add(r.date)
    return dict(end=eq, pnl=eq - start, maxdd=maxdd, worst_day_pct=worst_day_pct, min_room=min_room, breach=breach, guard_stop=dead, halted_days=len(halted_days), trades=n, skipped=skipped, worst_trade=big, fl700=fl700)
for name in ("V5_HL_C_W01_RH4", "V5_HL_C_W01"):
    t = load(name)
    print(f"\n===== {name}: {len(t)} trades; largest single loss {t.realised_R.min():+.2f} R; trades worse than -1.2 R: {(t.realised_R < -1.2).sum()}; median planned risk 2021 {t.planned_risk[t.entry_time.dt.year == 2021].median():.1f} USD, 2026 {t.planned_risk[t.entry_time.dt.year == 2026].median():.1f} USD")
    for f in (0.0025, 0.0020, 0.0015, 0.0010):
        s = simulate(t, f)
        print(f"  risk {100 * f:.2f} %  whole path 2021-2026 with guard: end {s['end']:8.0f} USD, max DD {s['maxdd']:7.0f} USD, worst day {s['worst_day_pct']:.2f} %, least room above the floor {s['min_room']:6.0f} USD, firm breach {s['breach']}, guard stopped for good {s['guard_stop']}, 2 %-halt days {s['halted_days']}, trades {s['trades']}, floating loss >= 700 USD: {s['fl700']}, worst trade {s['worst_trade']:.0f} USD")
        line = "               fresh 50k on 1 Jan:"
        for y in range(2021, 2027):
            ty = t[t.entry_time.dt.year == y]
            s = simulate(ty, f)
            tag = "BREACH " + str(s["breach"][0]) if s["breach"] else ("guard stop " + str(s["guard_stop"]) if s["guard_stop"] else "ok")
            line += f"  {y}: {s['pnl']:+6.0f} (DD {s['maxdd']:6.0f}, room {s['min_room']:5.0f}, {tag})"
        print(line)
        # every possible start month: does the account get stopped within 12 months?
        starts = pd.date_range("2021-03-01", "2025-11-01", freq="MS", tz="UTC"); stopped = []; pn = []
        for st in starts:
            ty = t[(t.entry_time >= st) & (t.entry_time < st + pd.DateOffset(months=12))]
            s = simulate(ty, f); stopped.append(bool(s["breach"] or s["guard_stop"])); pn.append(s["pnl"])
        st_dev = [x for x, d in zip(stopped, starts) if d < pd.Timestamp("2023-07-01", tz="UTC")]; st_new = [x for x, d in zip(stopped, starts) if d >= pd.Timestamp("2024-07-01", tz="UTC")]
        print(f"               12-month runs from every month start ({len(starts)}): stopped by the firm or the guard in {sum(stopped)} ({100 * np.mean(stopped):.0f} %); starts before mid-2023: {sum(st_dev)}/{len(st_dev)}; starts from mid-2024: {sum(st_new)}/{len(st_new)}; median 12-month P&L {np.median(pn):+.0f} USD, worst {np.min(pn):+.0f}, best {np.max(pn):+.0f}")
# block bootstrap: probability of losing 6 % from a peak within a year
rng = np.random.default_rng(5)
t = load("V5_HL_C_W01_RH4"); dev = t[t.signal_bar_open < "2024-07-01"].realised_R.values; oos = t[t.signal_bar_open >= "2024-07-01"].realised_R.values
print("\nblock bootstrap (blocks of 20 trades, 185 trades = one year at 0.74 a day, 5,000 paths): chance of a 6 % fall from a peak within the year / chance of being within 500 USD of the floor (the guard's stop) / median and 5th-percentile yearly P&L in USD")
for lab, rr in (("development-like market (2021 to mid-2024)", dev), ("held-out-like market (mid-2024 to 2026)", oos)):
    for f in (0.0025, 0.0020, 0.0015, 0.0010):
        hit = 0; near = 0; pnl = []
        for _ in range(5000):
            seq = np.concatenate([rr[s:s + 20] for s in rng.integers(0, len(rr) - 20, 10)])[:185]
            eq = 50000 * np.cumprod(1 + f * seq); pk = np.maximum.accumulate(np.r_[50000, eq])[1:]
            hit += bool((eq <= 0.94 * pk).any()); near += bool((eq - 0.94 * pk <= 500).any()); pnl.append(eq[-1] - 50000)
        print(f"   {lab:44s} risk {100 * f:.2f} %: {100 * hit / 5000:5.1f} % / {100 * near / 5000:5.1f} % / {np.median(pnl):+7.0f} / {np.quantile(pnl, 0.05):+7.0f}")
