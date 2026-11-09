#!/usr/bin/env python3
"""Gold-specific facts computed from the research dataset (HistData M1 bid, UTC) for the v2.0 framework.
Writes ../results/DATA_FACTS.md. Descriptive only: nothing here is a strategy test.
"""
import pathlib, numpy as np, pandas as pd
HERE = pathlib.Path(__file__).resolve().parent
m1 = pd.read_parquet(HERE.parent / "data" / "xauusd_m1_utc.parquet")
L = ["# DATA FACTS — XAUUSD from HistData M1 bid, 2021-01 → 2026-10 (UTC)", "", "Descriptive statistics to size stops, pick windows and set expectations. Not a strategy test. Bid prices; constant-spread caveats apply.", ""]

def wilder_atr(df, n=14):
    pc = df.close.shift(1); tr = pd.concat([df.high-df.low, (df.high-pc).abs(), (df.low-pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1/n, adjust=False).mean()

# daily bars: session day = 23:00 UTC to 22:00 UTC next day -> shift by +1h so a "day" starts at 00:00 after shifting
d = m1.copy(); d.index = d.index + pd.Timedelta(hours=1)
daily = d.resample("1D").agg(open=("open","first"), high=("high","max"), low=("low","min"), close=("close","last")).dropna()
daily = daily[daily.index.dayofweek < 5]
daily["range"] = daily.high - daily.low; daily["atr14"] = wilder_atr(daily); daily["ret"] = daily.close.pct_change()
L += ["## 1. Daily volatility by year (session day 23:00→22:00 UTC)", "", "| year | days | median daily range (USD) | median range (% of price) | median ATR(14) (USD) | median close | annualised vol of daily returns |", "|---|---|---|---|---|---|---|"]
for y, g in daily.groupby(daily.index.year):
    L.append(f"| {y} | {len(g)} | {g.range.median():.1f} | {(g.range/g.close).median()*100:.2f}% | {g.atr14.median():.1f} | {g.close.median():.0f} | {g.ret.std()*np.sqrt(252)*100:.1f}% |")

# M15 ATR by year and by session
m15 = m1.resample("15min").agg(open=("open","first"), high=("high","max"), low=("low","min"), close=("close","last")).dropna()
m15["atr14"] = wilder_atr(m15); m15["rng"] = m15.high - m15.low
hour = m15.index.hour
sess = np.where((hour >= 23) | (hour < 7), "Asia 23-07", np.where(hour < 12, "London 07-12", np.where(hour < 16, "NY-am 12-16", "NY-pm 16-22")))
m15["session"] = sess
L += ["", "## 2. M15 bar range by year and session (median, USD)", "", "| year | Asia 23-07 | London 07-12 | NY-am 12-16 | NY-pm 16-22 | all |", "|---|---|---|---|---|---|"]
for y, g in m15.groupby(m15.index.year):
    row = [f"{g[g.session==s].rng.median():.2f}" for s in ["Asia 23-07", "London 07-12", "NY-am 12-16", "NY-pm 16-22"]]
    L.append(f"| {y} | " + " | ".join(row) + f" | {g.rng.median():.2f} |")
L += ["", "Median M15 ATR(14) over the whole sample: " + f"{m15.atr14.median():.2f} USD; 2025-2026 only: {m15.loc['2025':].atr14.median():.2f} USD.", ""]

# hourly volatility profile
L += ["## 3. Volatility profile by UTC hour (median M15 range, USD, 2024-07 → 2026-10)", "", "| UTC hour | median M15 range | relative to day median |", "|---|---|---|"]
rec = m15.loc["2024-07":]; med_all = rec.rng.median()
for h, g in rec.groupby(rec.index.hour):
    L.append(f"| {h:02d} | {g.rng.median():.2f} | {g.rng.median()/med_all:.2f}x |")

# session returns (open-to-close of each session, bps) with t-stats, per year
def session_bounds(day):
    pass
L += ["", "## 4. Session returns (sum of M1 log returns inside the window, basis points per session, mean ± t-stat)", "", "| year | Asia 23-07 | London 07-12 | NY-am 12-16 | NY-pm 16-22 |", "|---|---|---|---|---|"]
lr = np.log(m1.close).diff().dropna().to_frame("r")
h1 = lr.index.hour
lr["session"] = np.where((h1 >= 23) | (h1 < 7), "Asia 23-07", np.where(h1 < 12, "London 07-12", np.where(h1 < 16, "NY-am 12-16", "NY-pm 16-22")))
lr["day"] = (lr.index + pd.Timedelta(hours=1)).date
ss = lr.groupby(["day", "session"]).r.sum().unstack()
for y, g in ss.groupby(pd.to_datetime(ss.index).year):
    cells = []
    for s in ["Asia 23-07", "London 07-12", "NY-am 12-16", "NY-pm 16-22"]:
        x = g[s].dropna() * 1e4; t = x.mean() / (x.std() / np.sqrt(len(x))) if len(x) > 2 else np.nan
        cells.append(f"{x.mean():+.1f} (t {t:+.1f})")
    L.append(f"| {y} | " + " | ".join(cells) + " |")
tot = []
for s in ["Asia 23-07", "London 07-12", "NY-am 12-16", "NY-pm 16-22"]:
    x = ss[s].dropna() * 1e4; t = x.mean() / (x.std() / np.sqrt(len(x))); tot.append(f"{x.mean():+.1f} (t {t:+.1f})")
L.append("| all | " + " | ".join(tot) + " |")
L += ["", "Reading: a |t| below about 2 means the session drift is indistinguishable from zero in this sample. Session seasonality found in older studies should not be assumed to persist.", ""]

# 200-day SMA regime and 12-1 momentum on daily closes
daily["sma200"] = daily.close.rolling(200).mean(); daily["above"] = daily.close > daily.sma200
daily["fwd1"] = daily.close.pct_change().shift(-1)
daily["mom12_1"] = daily.close.shift(21) / daily.close.shift(252) - 1
L += ["## 5. Daily regime filters (descriptive, next-day return conditional on the filter)", "", "| filter | days | share of days | mean next-day return (bps) | t-stat | ann. vol next day |", "|---|---|---|---|---|---|"]
for name, mask in [("close > SMA200", daily.above & daily.sma200.notna()), ("close < SMA200", ~daily.above & daily.sma200.notna()),
                   ("12-1 month momentum > 0", daily.mom12_1 > 0), ("12-1 month momentum < 0", daily.mom12_1 < 0)]:
    x = daily.loc[mask, "fwd1"].dropna() * 1e4
    L.append(f"| {name} | {len(x)} | {len(x)/daily.sma200.notna().sum()*100:.0f}% | {x.mean():+.1f} | {x.mean()/(x.std()/np.sqrt(len(x))):+.1f} | {x.std()*np.sqrt(252)/100:.1f}% |")
L += ["", "2021-2026 was dominated by a long uptrend (gold roughly doubled), so 'above SMA200' days are the majority and any long-biased filter looks good in-sample. Treat as context, not evidence.", ""]

# weekend gaps and daily-break gaps
fri_close = daily.close[daily.index.dayofweek == 4]; mon_open = daily.open[daily.index.dayofweek == 0]
gaps = (mon_open.values[:len(fri_close)] - fri_close.values[:len(mon_open)]) if False else None
wk = pd.DataFrame({"fri_close": fri_close.reset_index(drop=True)})
mo = mon_open.reset_index(drop=True)
n = min(len(wk), len(mo)); g = (mo.iloc[:n].values - wk.fri_close.iloc[:n].values)
L += ["## 6. Weekend gaps (Monday session open minus Friday session close, USD)", "", f"- weeks: {n}; median |gap| {np.median(np.abs(g)):.1f}; 90th percentile |gap| {np.percentile(np.abs(g), 90):.1f}; max |gap| {np.max(np.abs(g)):.1f}", f"- share of weeks with |gap| > 10 USD: {np.mean(np.abs(g) > 10)*100:.0f}%; > 20 USD: {np.mean(np.abs(g) > 20)*100:.0f}%", ""]
# daily break gap: 23:00 open vs 21:5x close
d2 = m1.copy(); idx = d2.index
last_pre = d2[(idx.hour == 21)].groupby(idx[idx.hour == 21].date).close.last()
first_post = d2[(idx.hour == 23)].groupby(idx[idx.hour == 23].date).open.first()
j = last_pre.index.intersection(first_post.index); bg = (first_post.loc[j].values - last_pre.loc[j].values)
L += ["## 7. Daily-break gaps (23:00 UTC reopen minus last 21:xx UTC close, same date, USD)", "", f"- days: {len(j)}; median |gap| {np.median(np.abs(bg)):.2f}; 90th percentile {np.percentile(np.abs(bg), 90):.2f}; max {np.max(np.abs(bg)):.1f}", ""]
# trend share: daily ADX
def adx(df, n=14):
    up = df.high.diff(); dn = -df.low.diff()
    pdm = np.where((up > dn) & (up > 0), up, 0.0); mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    atr = wilder_atr(df, n); pdi = 100 * pd.Series(pdm, index=df.index).ewm(alpha=1/n, adjust=False).mean() / atr
    mdi = 100 * pd.Series(mdm, index=df.index).ewm(alpha=1/n, adjust=False).mean() / atr
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi); return dx.ewm(alpha=1/n, adjust=False).mean()
daily["adx"] = adx(daily)
L += ["## 8. Trend regimes", "", f"- Share of days with daily ADX(14) > 25: {np.mean(daily.adx.dropna() > 25)*100:.0f}%; > 30: {np.mean(daily.adx.dropna() > 30)*100:.0f}%.", f"- Share of M15 bars with ADX(14) > 30 (from VALIDATION_MECHANICS): 29.3%.", ""]
(HERE.parent / "results" / "DATA_FACTS.md").write_text("\n".join(L))
print("\n".join(L))
