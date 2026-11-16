"""Adversarial statistics on the H4 filter (solo run after the agent version was cut off by the usage limit).
All tests use the HL_C_W01 trade list and classify each trade by a state at its own order step."""
import sys
sys.path.insert(0, "/home/user/tradingview-mcp/gold-research/backtest")
import numpy as np, pandas as pd
import engine as E, htf_refs as HR
R = E.DATA.parent.parent / "results"
m1 = pd.read_parquet(E.DATA)
tmin = m1.index.values.astype("datetime64[m]").astype(np.int64); C = m1["close"].values.astype(float)
slot = (tmin + 120) // 240
cl, gidx = HR._bars(tmin, C, slot); e = HR._ema(cl, 50); e4 = np.r_[np.full(4, np.nan), e[:-4]]
up_bar = (cl > e) & (e > e4); dn_bar = (cl < e) & (e < e4)
def load(n):
    t = pd.read_csv(R / n / "trades.csv")
    for c in ["signal_bar_open", "signal_time", "entry_time", "exit_time"]: t[c] = pd.to_datetime(t[c], utc=True, format="mixed")
    return t
w = load("V5_HL_C_W01"); h = load("V5_HL_C_W01_RH4")
# order step of the fill = close of the M15 bar signal_bar_open; last minute of that bar = signal_bar_open + 14 min
last_min = (w.signal_bar_open.values.astype("datetime64[m]").astype(np.int64) + 14)
pos = np.searchsorted(tmin, last_min, side="right") - 1                 # last existing M1 bar at or before that minute
g = gidx[pos]                                                            # H4 bar containing it
def state(lag_bars=0, warm=200):
    p = g - 1 - lag_bars; ok = p >= warm; q = np.maximum(p, 0)
    return np.where(ok, up_bar[q], False), np.where(ok, dn_bar[q], False)
long_ = (w.side == "long").values; r = w.realised_R.values
dev = (w.signal_bar_open < "2024-07-01").values; oos = ~dev
day = (w.signal_bar_open + pd.Timedelta(hours=1)).dt.date.values
def kept_mask(lag=0):
    u, d = state(lag); return (long_ & u) | (~long_ & d)
def line(lab, k):
    out = f"{lab:44s}"
    for nm, m in (("six years", np.ones(len(r), bool)), ("development", dev), ("held-out", oos)):
        a, b = r[m & k], r[m & ~k]
        se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)) if len(a) > 1 and len(b) > 1 else np.nan
        out += f" | {nm}: kept n={len(a):4d} {a.mean():+.3f}  removed n={len(b):4d} {b.mean():+.3f}  diff {a.mean() - b.mean():+.3f} (t {(a.mean() - b.mean()) / se:+.1f})"
    print(out)
k0 = kept_mask(0)
print("check: kept by the real state", int(k0.sum()), "(independent audit: 916)")
line("REAL 4-hour state", k0)
print("\n-- placebo 1: the same state, but stale (lagged by whole trading days = 6 four-hour bars each)")
for lagd in (1, 2, 5, 10, 20, 40, 60):
    line(f"state lagged {lagd:2d} trading days", kept_mask(6 * lagd))
print("\n-- placebo 2: side only")
line("longs only", long_); line("shorts only", ~long_)
print("\n-- placebo 3: previous session day's direction (close vs close of the day before)")
sday = (tmin + 60) // 1440; dcl, dg = HR._bars(tmin, C, sday)
dprev_up = np.r_[False, False, dcl[1:-1] > dcl[:-2]]; dprev_dn = np.r_[False, False, dcl[1:-1] < dcl[:-2]]      # state of day d = day d-1 vs d-2
dd = dg[pos]
line("previous day up -> longs, down -> shorts", (long_ & dprev_up[dd]) | (~long_ & dprev_dn[dd]))
print("\n-- placebo 4: random subsets of the same size (20,000 draws), rank of the real kept-set mean")
rng = np.random.default_rng(11)
for nm, m in (("six years", np.ones(len(r), bool)), ("development", dev), ("held-out", oos)):
    rr = r[m]; nk = int(k0[m].sum()); real = rr[k0[m]].mean()
    sims = np.array([rr[rng.permutation(len(rr))[:nk]].mean() for _ in range(20000)])
    print(f"   {nm:12s} real kept mean {real:+.3f}; random subsets: mean {sims.mean():+.3f}, 95th pct {np.quantile(sims, 0.95):+.3f}, 99th {np.quantile(sims, 0.99):+.3f}; share of random subsets >= real: {100 * (sims >= real).mean():.2f} %")
print("\n-- placebo 5: circular shift of the kept/removed labels along the trade sequence (keeps the clustering in time), 5,000 shifts")
for nm, m in (("six years", np.ones(len(r), bool)), ("development", dev), ("held-out", oos)):
    rr = r[m]; kk = k0[m]; real = rr[kk].mean() - rr[~kk].mean()
    sh = rng.integers(20, len(rr) - 20, 5000)
    sims = np.array([rr[np.roll(kk, s)].mean() - rr[~np.roll(kk, s)].mean() for s in sh])
    print(f"   {nm:12s} real difference {real:+.3f}; shifted labels: mean {sims.mean():+.3f}, 95th pct {np.quantile(sims, 0.95):+.3f}; share >= real: {100 * (sims >= real).mean():.2f} %")
print("\n-- bootstrap by session day (blocks of 5 consecutive days), 90 % interval of kept minus removed")
days_u = np.array(sorted(set(day))); didx = pd.Series(np.arange(len(days_u)), index=days_u).reindex(day).values
for nm, m in (("six years", np.ones(len(r), bool)), ("development", dev), ("held-out", oos)):
    ds = np.unique(didx[m]); nb = len(ds) // 5; out = []
    by = {d: np.flatnonzero(m & (didx == d)) for d in ds}
    for _ in range(3000):
        st = rng.integers(0, len(ds) - 5, nb); ii = np.concatenate([by[ds[s + j]] for s in st for j in range(5)])
        a, b = r[ii][k0[ii]], r[ii][~k0[ii]]
        out.append(a.mean() - b.mean())
    print(f"   {nm:12s} [{np.quantile(out, 0.05):+.3f}, {np.quantile(out, 0.95):+.3f}], share of resamples <= 0: {100 * (np.array(out) <= 0).mean():.1f} %")
print("\n-- by entry hour (London) and with a wider spread in the Asian hours (R falls by extra spread / planned risk)")
for nm_, t in (("HL_C_W01", w), ("HL_C_W01_RH4", h)):
    eh = t.entry_time.dt.hour.values; asia = (eh >= 1) & (eh < 7); o = (t.signal_bar_open >= "2024-07-01").values
    rr, pr = t.realised_R.values, t.planned_risk.values
    print(f"   {nm_:13s} held-out: entries 01-07h: n={int((asia & o).sum())} ({100 * (asia & o).sum() / o.sum():.0f} %) mean {rr[asia & o].mean():+.3f} R, sum {rr[asia & o].sum():+.1f} R | entries 07-16h: n={int((~asia & o).sum())} mean {rr[~asia & o].mean():+.3f} R, sum {rr[~asia & o].sum():+.1f} R"
          f" | all held-out mean with Asian spread 0.60: {(rr - np.where(asia, 0.35 / pr, 0))[o].mean():+.3f}, 0.80: {(rr - np.where(asia, 0.55 / pr, 0))[o].mean():+.3f}; development 01-07h mean {rr[asia & ~o].mean():+.3f} (n={int((asia & ~o).sum())}), 07-16h {rr[~asia & ~o].mean():+.3f}; dev mean with Asian spread 0.60: {(rr - np.where(asia, 0.35 / pr, 0))[~o].mean():+.3f}")
