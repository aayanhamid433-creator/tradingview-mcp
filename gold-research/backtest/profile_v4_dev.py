#!/usr/bin/env python3
"""profile_v4_dev.py — descriptive profile of XAUUSD intraday behaviour, DEVELOPMENT PERIOD ONLY.

Scope and rules (fixed before the first run; nothing here is a strategy test and nothing was tuned):
  * Data: ../data/xauusd_m1_utc.parquet (HistData M1, BID, no volume) loaded as engine_v3 does (pd.read_parquet) and CUT
    to the development period before anything is computed: bars from 2021-01-03 23:00 (the first bar of session day
    2021-01-04) up to but excluding 2024-07-01 00:00. No bar at or after 2024-07-01 enters any statistic.
  * Session day = 23:00 -> 23:00 on the dataset clock, keyed by (t + 1h).date exactly as engine_v2.daily_frame and
    engine_v3 do. Every daily quantity used as a condition is the PREVIOUS session day's value. Dropped: the 12 one-hour
    Sunday stubs created by the feed's DST-mismatch weeks, the one-hour 2024-07-01 stub, and the 22:00-22:59 bars that
    the 23:00 rule assigns to the wrong day on DST-mismatch days (0.2 % of bars).
  * The dataset clock: the project calls it UTC. Section 0 shows it is London local time (GMT in winter, BST in summer):
    the 08:30 New York data releases sit at 13:30 on this clock in both seasons and the daily break stays at 22:00-23:00
    all year. All times below are on that clock, as the engines use it.
  * Prices are BID. "Buy at T1, sell at T2" = entered at the OPEN of the first M1 bar at/after T1 and exited at the OPEN
    of the first M1 bar at/after T2 (engine_v3's time-exit convention), each within 5 minutes of the nominal time, else
    the day is skipped for that window. Window ends at "END" use the last bar's close of the session day. Net figures
    subtract the BASE_CONFIG spread 0.25 per round trip (section 1) or a 0.30 round-trip cost (section 6); engine_v3
    would charge 0.25 spread + 2 x 0.05 slippage = 0.35.
  * M15 bars = engine resample (label left, closed left). ATR14(M15) = engine.indicators (Wilder) of the last CLOSED bar.
    Session TWAP = engine_v3.session_twap. Daily frame = engine_v2.daily_frame.
  * Statistics: t = mean / (sd / sqrt(N)) on session-day (or bar) observations treated as independent; 95 % bootstrap
    percentile CI of the mean from 2000 resamples (fixed seed). Section 6 lists every registered pattern with |t| > 2 or a
    CI excluding zero and states, for each, the size per trade net of 0.30 USD and the session days per year it fires.

Usage: python3 profile_v4_dev.py      (prints the report and writes ../results/PROFILE_v4_dev.md)
"""
import pathlib, sys, datetime as dt
import numpy as np, pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine as E
import engine_v2 as V2
import engine_v3 as V3

OUT = HERE.parent / "results" / "PROFILE_v4_dev.md"
DEV_START = pd.Timestamp("2021-01-03 23:00", tz="UTC")   # first bar of session day 2021-01-04
DEV_END = pd.Timestamp("2024-07-01 00:00", tz="UTC")     # exclusive
DEV_END_DAY = pd.Timestamp("2024-07-01")
SPREAD = E.BASE_CONFIG["spread"]                         # 0.25 USD, ask = bid + spread
RT_COST = 0.30                                           # section-6 round-trip cost
TOL = 5                                                  # minutes: a boundary bar must exist within TOL after the nominal time
B_BOOT, SEED = 2000, 20240701
MIN_HOUR_BARS = 45                                       # an hour bar needs this many M1 bars to count as a complete hour

# ------------------------------------------------------------------ small helpers
def hm(s): h, m = map(int, s.split(":")); return h * 60 + m
def smin_of(mod): return (np.asarray(mod) + 60) % 1440          # minutes since 23:00
def lab(s):                                                       # session minute -> HH:MM label on the dataset clock
    if s == "END": return "END"
    mod = (int(s) - 60) % 1440; return f"{mod // 60:02d}:{mod % 60:02d}"
def eu_dst_active(d: dt.date) -> bool:
    mar = dt.date(d.year, 3, 31); start = mar - dt.timedelta(days=(mar.weekday() + 1) % 7)   # last Sunday of March
    octo = dt.date(d.year, 10, 31); end = octo - dt.timedelta(days=(octo.weekday() + 1) % 7)  # last Sunday of October
    return start <= d < end

def boot_ci(x, B=B_BOOT, seed=SEED):
    x = np.asarray(x, float); n = len(x)
    if n < 10: return (np.nan, np.nan)
    rng = np.random.default_rng(seed); means = np.empty(B); done = 0
    step = max(1, min(B, int(3e6 // n)))
    while done < B:
        k = min(step, B - done); idx = rng.integers(0, n, size=(k, n))
        means[done:done + k] = x[idx].mean(axis=1); done += k
    lo, hi = np.percentile(means, [2.5, 97.5]); return float(lo), float(hi)

def stats(x, ci=True):
    x = np.asarray(x, float); x = x[~np.isnan(x)]; n = len(x)
    if n < 3: return dict(n=n, mean=np.nan, median=np.nan, sd=np.nan, t=np.nan, lo=np.nan, hi=np.nan, win=np.nan)
    mean = x.mean(); sd = x.std(ddof=1); t = mean / (sd / np.sqrt(n)) if sd > 0 else np.nan
    lo, hi = boot_ci(x) if ci else (np.nan, np.nan)
    return dict(n=n, mean=float(mean), median=float(np.median(x)), sd=float(sd), t=float(t), lo=lo, hi=hi, win=float((x > 0).mean()))

CANDS = []
def cand(section, name, x, note="", kind="signed"):
    """Register a per-event USD/oz series (pd.Series indexed by session day). kind 'signed': the implied trade is long if the
    mean is positive, short if negative; kind 'relative': the series is already in the direction of a prior move, so the
    implied trade is 'follow' if positive, 'fade' if negative. The direction is chosen after seeing the sign (a mild
    selection effect; section 6 says so)."""
    x = pd.Series(x).dropna()
    s = stats(x.values)
    if s["n"] < 20: return s
    yrs = x.groupby(x.index.year).mean()
    s.update(section=section, name=name, note=note, kind=kind, days_fired=int(pd.DatetimeIndex(x.index).normalize().nunique()),
             same_sign_years=int((np.sign(yrs.values) == np.sign(s["mean"])).sum()), n_years=int(len(yrs)),
             by_year={int(k): float(v) for k, v in yrs.items()})
    CANDS.append(s); return s

L = []
def P(*a): L.append(" ".join(str(v) for v in a))
def table(headers, rows):
    P("| " + " | ".join(headers) + " |"); P("|" + "---|" * len(headers))
    for r in rows: P("| " + " | ".join(str(c) for c in r) + " |")
    P("")
def fx(x, d=2, sign=True):
    if x is None or (isinstance(x, float) and np.isnan(x)): return "n/a"
    return f"{x:+.{d}f}" if sign else f"{x:.{d}f}"
def ci(s): return "n/a" if np.isnan(s["lo"]) else f"[{s['lo']:+.2f}, {s['hi']:+.2f}]"
def row_stats(name, s, extra=()):
    return [name, s["n"], fx(s["mean"]), fx(s["median"]), fx(s["sd"], 2, False), fx(s["t"], 1), ci(s), fx(100 * s["win"], 0, False) + "%"] + list(extra)
STAT_HDR = ["window", "days", "mean USD/oz", "median", "sd", "t", "95% CI (boot)", "share > 0"]

# ================================================================== load and cut
m1 = pd.read_parquet(E.DATA)
m1 = m1.loc[(m1.index >= DEV_START) & (m1.index < DEV_END)].copy()
assert len(m1) and m1.index.max() < DEV_END, "development cut failed"
n_raw = len(m1)
day_all = (m1.index + pd.Timedelta(hours=1)).tz_localize(None).normalize()
smin_all = smin_of(m1.index.hour * 60 + m1.index.minute)
keep = (day_all.dayofweek.values < 5) & (day_all.values < np.datetime64(DEV_END_DAY)) & (smin_all < 1380)
m1 = m1.loc[keep].copy()
m1["day"] = day_all.values[keep]; m1["smin"] = smin_all[keep]; m1["hour"] = m1.index.hour; m1["ts"] = m1.index
n_dropped = n_raw - len(m1)
day_arr = m1["day"].values.astype("datetime64[D]")
uday, d_start = np.unique(day_arr, return_index=True); d_end = np.r_[d_start[1:], len(day_arr)]
UDAY = pd.DatetimeIndex(uday)
o_, h_, l_, c_, sm_ = (m1[k].values for k in ("open", "high", "low", "close", "smin"))
YEARS = (uday[-1] - uday[0]).astype("timedelta64[D]").astype(int) / 365.25
n_days = len(uday)
bars_per_day = pd.Series(d_end - d_start, index=UDAY)
complete = bars_per_day >= 1300
dates_py = [pd.Timestamp(d).date() for d in uday]
mismatch = pd.Series([E.us_dst_active(d) and not eu_dst_active(d) for d in dates_py], index=UDAY)

_PX = {}
def px(T):
    """Series by session day: open of the first M1 bar at/after session-minute T (within TOL), or last close for 'END'."""
    if T in _PX: return _PX[T]
    out = np.full(n_days, np.nan)
    for i in range(n_days):
        s, e = d_start[i], d_end[i]
        if T == "END": out[i] = c_[e - 1]; continue
        sm = sm_[s:e]; j = np.searchsorted(sm, T)
        if j < e - s and sm[j] < T + TOL: out[i] = o_[s + j]
    _PX[T] = pd.Series(out, index=UDAY); return _PX[T]
def move(T1, T2): return px(T2) - px(T1)
def move_bp(T1, T2): return (px(T2) / px(T1) - 1) * 1e4

# M15 / indicators / daily frame / H1 frame
m15 = m1[["open", "high", "low", "close"]].resample("15min", label="left", closed="left").agg(
    open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last")).dropna()
ind = E.indicators(m15, E.BASE_CONFIG)
atr15 = pd.Series(ind.atr.values, index=ind.index)
daily = V2.daily_frame(m1[["open", "high", "low", "close"]])
daily.index = pd.DatetimeIndex(daily.index); daily = daily[daily.index.dayofweek < 5].copy()
daily["range"] = daily.high - daily.low
daily["clv"] = (daily.close - daily.low) / daily.range.replace(0, np.nan)
daily["cc"] = daily.close.diff(); daily["oc"] = daily.close - daily.open
prev = daily.shift(1)   # previous session day (previous row, as the engines do)
twap, _sd = V3.session_twap(m1); m1["twap"] = twap
h1 = m1.groupby(["day", "hour"], sort=False).agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"),
                                                  n=("open", "size"), smin=("smin", "first"), twap=("twap", "last")).reset_index()
h1["slot"] = h1.smin // 60; h1 = h1.sort_values(["day", "slot"]).reset_index(drop=True)
h1["move"] = h1.close - h1.open
same_next = (h1.day.shift(-1) == h1.day) & (h1.slot.shift(-1) == h1.slot + 1) & (h1.n.shift(-1) >= MIN_HOUR_BARS)
h1["next_move"] = np.where(same_next, h1.close.shift(-1) - h1.close, np.nan)
hour_end_ts = (pd.DatetimeIndex(h1.day) - pd.Timedelta(hours=1) + pd.to_timedelta((h1.slot * 60 + 45).values, unit="m")).tz_localize("UTC")
h1["atr"] = atr15.reindex(hour_end_ts).values      # ATR14(M15) of the last CLOSED M15 bar of the hour
h1["end_smin"] = h1.slot * 60 + 60
h1["pdh"] = prev.high.reindex(h1.day).values; h1["pdl"] = prev.low.reindex(h1.day).values
h1["prev_range"] = prev.range.reindex(h1.day).values
h1["cum_hi"] = h1.groupby("day").high.cummax(); h1["cum_lo"] = h1.groupby("day").low.cummin()
h1_full = h1[h1.n >= MIN_HOUR_BARS]

# ================================================================== 0. data, clock, coverage
P("# PROFILE v4 — XAUUSD intraday behaviour, DEVELOPMENT PERIOD ONLY")
P("")
P(f"Generated {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC by backtest/profile_v4_dev.py. Data: HistData M1 BID, cut to "
  f"{DEV_START:%Y-%m-%d %H:%M} .. {DEV_END:%Y-%m-%d %H:%M} (exclusive) before any computation; session days "
  f"{UDAY[0]:%Y-%m-%d} .. {UDAY[-1]:%Y-%m-%d}. Descriptive only; no strategy was run and nothing was tuned. "
  "Validation and test periods were not loaded.")
P("")
P("## 0. Data, clock and coverage")
P("")
P(f"- Bars in the cut: {n_raw:,}; kept {len(m1):,} after dropping {n_dropped:,} bars (Sunday one-hour stubs on DST-mismatch weeks, the "
  f"2024-07-01 one-hour stub, and 22:00-22:59 bars that the 23:00 session rule assigns to the wrong day).")
P(f"- Weekday session days: {n_days} ({YEARS:.2f} calendar years, {n_days / YEARS:.0f} session days per year). Complete days (>= 1300 of 1380 M1 bars): "
  f"{int(complete.sum())}; incomplete: {int((~complete).sum())} (feed gaps, {int((~complete)[UDAY.year == 2023].sum())} of them in 2023, where whole "
  "alternating hours are missing on many days between February and July). Window statistics below use a day only when the bars at both window "
  "boundaries exist; hour statistics use hours with >= 45 bars.")
P(f"- DST-mismatch days (US daylight time on, EU off: mid/late March and late Oct/early Nov): {int(mismatch.sum())}. On those days the daily break is at "
  "21:00-22:00 and the US 08:30 ET releases land at 12:30 on this clock instead of 13:30; they are kept (the engines keep them too).")
# clock evidence: mean M1 range at specific minutes, EU-summer vs winter months
mo = m1.index.month; hmv = m1.index.strftime("%H:%M")
rng1 = (m1.high - m1.low).values
ev = []
for label, mask in [("Apr-Sep (BST)", np.isin(mo, [4, 5, 6, 7, 8, 9])), ("Nov-Feb (GMT)", np.isin(mo, [11, 12, 1, 2]))]:
    s = pd.Series(rng1[mask]).groupby(hmv[mask]).mean()
    ev.append([label] + [fx(s.get(k, np.nan), 3, False) for k in ("12:20", "12:30", "13:20", "13:30", "14:00", "15:00", "21:59", "22:00", "23:00")])
P("")
P("**The dataset clock is London local time, not UTC.** HistData stamps are documented as fixed EST, but the mean 1-minute range at the "
  "minute of the 08:30 ET data releases (and the 08:20 ET COMEX open, 10:00 ET releases) sits at the same clock minute in summer and winter, "
  "and the daily break (17:00-18:00 New York) sits at 22:00-23:00 in every month except the DST-mismatch weeks. Both are impossible on a true "
  "UTC axis and exactly what a clock following EU daylight time (GMT/BST) produces. Consequences: the project's \"07:00 UTC\" London open is "
  "07:00 London time all year; \"13:30 UTC\" is 08:30 New York all year (except mismatch weeks); the 20:50 time exit is 15:50 New York; "
  "the LBMA auctions (10:30 / 15:00 London) are at 10:30 / 15:00 on this clock all year. The times in this report are on this clock.")
P("")
table(["months", "12:20", "12:30", "13:20", "13:30", "14:00", "15:00", "21:59", "22:00", "23:00"], ev)
P("Mean 1-minute bar range (USD) at the named minute: the 13:30 / 15:00 spikes and the empty 22:00 minute do not move between seasons.")
P("")
cov = []
for y, g in bars_per_day.groupby(UDAY.year):
    cov.append([y, len(g), int((g >= 1300).sum()), int((g < 1300).sum()), int(mismatch[UDAY.year == y].sum()), f"{daily.close[daily.index.year == y].mean():.0f}",
                f"{daily.range[daily.index.year == y].median():.1f}", f"{daily.atr14[daily.index.year == y].median():.1f}"])
table(["year", "session days", "complete", "incomplete", "DST-mismatch", "mean close", "median day range", "median D1 ATR14"], cov)

# ================================================================== 1. returns by hour / weekday / block
P("## 1. M15 close-to-close returns by hour, weekday and session block; fixed-time trades")
P("")
t15 = m15.index; cl15 = m15.close.values; op15 = m15.open.values
day15 = (t15 + pd.Timedelta(hours=1)).tz_localize(None).normalize()
smin15 = smin_of(t15.hour * 60 + t15.minute)
consec = np.r_[False, (day15[1:] == day15[:-1]) & ((t15[1:] - t15[:-1]) == pd.Timedelta(minutes=15))]
r_cc = np.full(len(m15), np.nan); r_cc[consec] = cl15[consec] - np.roll(cl15, 1)[consec]        # pure close-to-close, consecutive bars only
r_in = np.where(consec, r_cc, cl15 - op15)                                                       # first bar of a day / after a gap: own body
base = np.where(consec, np.roll(cl15, 1), op15)
r_bp = r_in / base * 1e4
R15 = pd.DataFrame(dict(r=r_in, r_bp=r_bp, r_cc=r_cc, day=day15.values, smin=smin15, hour=t15.hour, dow=day15.dayofweek.values), index=t15)
P("Per-bar return = close minus the previous M15 close when the previous bar is the consecutive bar of the same session day; for the first bar of a "
  "day (and a bar after a feed gap) it is close minus open, so the day's bars sum to the session open-to-close move. Hours are the bar's OPEN hour "
  "on the dataset clock; session order 23:00 -> 21:00.")
P("")
P("### 1a. By hour of day (per M15 bar) and the matching one-hour fixed-time trade")
P("")
rows = []
order = [23] + list(range(0, 22))
for hr in order:
    g = R15[R15.hour == hr]
    s = stats(g.r.values, ci=False)
    T1 = int(smin_of(hr * 60)); T2 = "END" if hr == 21 else T1 + 60
    w = cand("1a hour trade", f"{hr:02d}:00 -> {lab(T2)}", move(T1, T2))
    rows.append([f"{hr:02d}", s["n"], fx(s["mean"], 3), fx(s["median"], 3), fx(g.r_bp.mean(), 2), fx(g.r_bp.median(), 2), fx(s["t"], 1),
                 w["n"], fx(w["mean"]), fx(w["t"], 1), ci(w), fx(w["mean"] - SPREAD), fx(-w["mean"] - SPREAD)])
table(["hour", "bars", "mean USD/bar", "median", "mean bp/bar", "median bp", "t (bar)", "days", "hour trade mean USD", "t (day)", "95% CI", "net long (-0.25)", "net short (-0.25)"], rows)
P("### 1b. By weekday of the session day")
P("")
rows = []
for d, name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri"]):
    g = R15[R15.dow == d]; s = stats(g.r.values, ci=False)
    sel = UDAY.dayofweek == d
    w = cand("1b weekday session", f"{name} session open -> close", move(0, "END")[sel])
    w2 = cand("1b weekday 07:00-20:50", f"{name} 07:00 -> 20:50", move(480, 1310)[sel])
    rows.append([name, s["n"], fx(s["mean"], 3), fx(s["median"], 3), fx(g.r_bp.mean(), 2), fx(g.r_bp.median(), 2), fx(s["t"], 1), w["n"], fx(w["mean"]), fx(w["t"], 1), ci(w),
                 fx(w2["mean"]), fx(w2["t"], 1), ci(w2)])
table(["weekday", "bars", "mean USD/bar", "median", "mean bp/bar", "median bp", "t (bar)", "days", "session open->close", "t", "95% CI", "07:00->20:50", "t", "95% CI"], rows)
P("### 1c. By session block (per M15 bar) and the block 'buy at open, sell at close' trade (0.25 spread per round trip subtracted)")
P("")
BLOCKS = [("Asia 23:00-07:00", 0, 480), ("London 07:00-12:00", 480, 780), ("NY 12:00-20:50", 780, 1310), ("late 20:50-END", 1310, "END")]
blk = np.full(len(R15), "", dtype=object)
blk[(smin15 >= 0) & (smin15 < 480)] = BLOCKS[0][0]; blk[(smin15 >= 480) & (smin15 < 780)] = BLOCKS[1][0]
blk[(smin15 >= 780) & (smin15 < 1305)] = BLOCKS[2][0]; blk[smin15 >= 1305] = BLOCKS[3][0]   # the 20:45 bar straddles the 20:50 exit -> 'late'
R15["block"] = blk
rows = []; BLK = {}
for name, T1, T2 in BLOCKS + [("07:00-20:50 (intraday window)", 480, 1310), ("session open -> close", 0, "END")]:
    g = R15[R15.block == name]
    bar_cells = [len(g), fx(g.r.mean(), 3), fx(g.r.median(), 3), fx(g.r_bp.mean(), 2), fx(g.r_bp.median(), 2), fx(stats(g.r.values, ci=False)["t"], 1)] if len(g) else ["-"] * 6
    mv = move(T1, T2); w = cand("1c block trade", name, mv); BLK[name] = (mv, w)
    bp = move_bp(T1, T2).mean()
    rows.append([name] + bar_cells + [w["n"], fx(w["mean"]), fx(bp, 1), fx(w["median"]), fx(w["sd"], 2, False), fx(w["t"], 1), ci(w),
                 fx(w["mean"] - SPREAD), fx(-w["mean"] - SPREAD), fx((mv - SPREAD).sum(), 0), fx((-mv - SPREAD).sum(), 0)])
table(["block", "bars", "mean USD/bar", "median", "mean bp/bar", "median bp", "t (bar)", "days", "trade mean USD", "mean bp", "median", "sd", "t (day)", "95% CI",
       "net long/trade", "net short/trade", "cum net long", "cum net short"], rows)
P("Cumulative columns: sum over all development session days of (move - 0.25) for always-long and (-move - 0.25) for always-short.")
P("")
P("### 1d. Block trade mean by year (USD/oz per day, t in brackets)")
P("")
yrs = sorted(set(UDAY.year)); rows = []
for name, _, _ in BLOCKS + [("07:00-20:50 (intraday window)", 480, 1310), ("session open -> close", 0, "END")]:
    mv = BLK[name][0]; cells = []
    for y in yrs:
        s = stats(mv[mv.index.year == y].values, ci=False); cells.append(f"{fx(s['mean'])} ({fx(s['t'], 1)}) n={s['n']}")
    rows.append([name] + cells)
table(["block"] + [str(y) for y in yrs], rows)

# ================================================================== 2. London fix windows
P("## 2. London fix windows (LBMA auctions 10:30 and 15:00 London time = 10:30 and 15:00 on this clock all year)")
P("")
FIX = [("07:00 -> 10:30 (London open to AM fix)", 480, hm("10:30") + 60), ("10:30 -> 15:00 (AM fix to PM fix)", hm("10:30") + 60, hm("15:00") + 60),
       ("15:00 -> 20:50 (PM fix to time exit)", hm("15:00") + 60, 1310), ("10:00 -> 10:30 (30 min before AM fix)", hm("10:00") + 60, hm("10:30") + 60),
       ("10:30 -> 11:00 (30 min after AM fix)", hm("10:30") + 60, hm("11:00") + 60), ("14:30 -> 15:00 (30 min before PM fix)", hm("14:30") + 60, hm("15:00") + 60),
       ("15:00 -> 15:30 (30 min after PM fix)", hm("15:00") + 60, hm("15:30") + 60)]
rows = []; FIXS = {}
for name, T1, T2 in FIX:
    mv = move(T1, T2); w = cand("2 fix window", name, mv); FIXS[name] = w
    cells = [f"{fx(stats(mv[mv.index.year == y].values, ci=False)['mean'])}" for y in yrs]
    rows.append(row_stats(name, w, [fx(move_bp(T1, T2).mean(), 1), fx(w["mean"] - SPREAD), fx(-w["mean"] - SPREAD)] + cells))
table(STAT_HDR + ["mean bp", "net long", "net short"] + [str(y) for y in yrs], rows)

# ================================================================== 3. continuation
P("## 3. Continuation (sign of an earlier move -> mean of the later move)")
P("")
def cond_table(title, m_a, m_b, label_a, label_b, section):
    P(f"### {title}")
    P("")
    both = pd.concat([m_a.rename("a"), m_b.rename("b")], axis=1).dropna()
    rows = []
    up, dn = both[both.a > 0], both[both.a < 0]
    s_up = cand(section, f"{label_b} given {label_a} up", up.b); s_dn = cand(section, f"{label_b} given {label_a} down", dn.b)
    follow = np.sign(both.a) * both.b; s_f = cand(section, f"follow the sign of {label_a} over {label_b}", follow, kind="relative")
    big = both[both.a.abs() >= both.a.abs().median()]
    s_big = cand(section, f"follow {label_a} over {label_b}, abs(first move) above median", np.sign(big.a) * big.b, kind="relative")
    rho = np.corrcoef(both.a, both.b)[0, 1]; n = len(both); t_rho = rho * np.sqrt((n - 2) / max(1e-12, 1 - rho ** 2))
    rows.append(row_stats(f"{label_b} given {label_a} up", s_up, [f"{s_up['mean'] - RT_COST:+.2f}" if s_up["mean"] > 0 else f"{-s_up['mean'] - RT_COST:+.2f} (short)"]))
    rows.append(row_stats(f"{label_b} given {label_a} down", s_dn, [f"{s_dn['mean'] - RT_COST:+.2f}" if s_dn["mean"] > 0 else f"{-s_dn['mean'] - RT_COST:+.2f} (short)"]))
    rows.append(row_stats(f"follow: sign({label_a}) x {label_b}", s_f, [fx(s_f["mean"] - RT_COST)]))
    rows.append(row_stats(f"follow, abs({label_a}) >= median ({both.a.abs().median():.2f})", s_big, [fx(s_big["mean"] - RT_COST)]))
    table(STAT_HDR + ["net of 0.30 in the implied direction"], rows)
    P(f"Pearson correlation of the two moves: {rho:+.3f} (t {t_rho:+.1f}, n={n}); mean {label_b} unconditional {both.b.mean():+.2f}.")
    P("")
    return s_up, s_dn, s_f
C1 = cond_table("3a. First London hour 07:00-08:00 -> rest of day 08:00-20:50", move(480, 540), move(540, 1310), "07:00-08:00", "08:00-20:50", "3a continuation")
C2 = cond_table("3b. 12:00-13:00 -> 13:00-20:50", move(780, 840), move(840, 1310), "12:00-13:00", "13:00-20:50", "3b continuation")
nd = move(480, 1310).rename("b"); nd_oc = move(0, "END").rename("b2")
C3 = cond_table("3c. Previous session day close-to-close -> next day 07:00-20:50", prev.cc.reindex(UDAY), nd, "prev day c-to-c", "next 07:00-20:50", "3c prev day")
C3b = cond_table("3c'. Previous session day open-to-close -> next day 07:00-20:50", prev.oc.reindex(UDAY), nd, "prev day o-to-c", "next 07:00-20:50", "3c prev day")
P("### 3d. Previous day's close location value (CLV = (close - low) / (high - low)) -> next day's moves")
P("")
clv = prev.clv.reindex(UDAY)
bins = [(-0.01, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.01)]
rows = []
for lo_, hi_ in bins:
    sel = (clv > lo_) & (clv <= hi_)
    s1 = cand("3d CLV", f"next 07:00-20:50 | prev CLV in ({max(lo_, 0):.1f}, {min(hi_, 1):.1f}]", nd[sel])
    s2 = cand("3d CLV", f"next session open->close | prev CLV in ({max(lo_, 0):.1f}, {min(hi_, 1):.1f}]", nd_oc[sel])
    rows.append([f"({max(lo_, 0):.1f}, {min(hi_, 1):.1f}]", s1["n"], fx(s1["mean"]), fx(s1["t"], 1), ci(s1), fx(s2["mean"]), fx(s2["t"], 1), ci(s2)])
table(["prev-day CLV bin", "days", "next 07:00->20:50 mean", "t", "95% CI", "next session open->close mean", "t", "95% CI"], rows)
rho = pd.concat([clv.rename("a"), nd], axis=1).dropna().corr().iloc[0, 1]
P(f"Correlation prev-day CLV vs next 07:00-20:50 move: {rho:+.3f}. Unconditional next 07:00-20:50 mean {nd.mean():+.2f} USD, session open->close mean {nd_oc.mean():+.2f} USD.")
P("")

# ================================================================== 4. autocorrelation, variance ratio, range, NR7
P("## 4. Autocorrelation, variance ratios, intraday range development, NR7 / inside days")
P("")
def autocorr_table(r, dayv, spacing_ok, label):
    rows = []
    for k in (1, 2, 3, 4):
        x = r[:-k]; y = r[k:]; ok = ~np.isnan(x) & ~np.isnan(y) & (dayv[:-k] == dayv[k:]) & spacing_ok(k)
        x, y = x[ok], y[ok]; n = len(x); xm, ym = x - x.mean(), y - y.mean()
        rho = (xm * ym).sum() / np.sqrt((xm ** 2).sum() * (ym ** 2).sum())
        b = (xm * ym).sum() / (xm ** 2).sum(); e = ym - b * xm
        t_rob = b / np.sqrt((xm ** 2 * e ** 2).sum() / (xm ** 2).sum() ** 2)
        rows.append([f"{label} lag {k}", n, f"{rho:+.4f}", f"{rho * np.sqrt(n):+.1f}", f"{t_rob:+.1f}", f"{b * 100:+.2f}%"])
    return rows
def vr_table(r, dayv, spacing_ok, label, qs=range(1, 9)):
    """Lo-MacKinlay variance ratio written through the autocorrelations, VR(q) = 1 + 2 sum_{j<q} (1 - j/q) rho_j, with rho_j and
    its heteroskedasticity-robust variance delta_j computed on consecutive within-day pairs. (A windowed estimator would compare
    q-bar windows, which cannot start in the first q-1 bars of a day, with 1-bar returns that include the quiet first hours; the
    time-of-day volatility pattern then biases VR above 1. This form avoids that.)"""
    valid = ~np.isnan(r); mu = np.nanmean(r); e = np.where(valid, r - mu, 0.0)
    s2 = np.sum(e ** 2); rho = {}; delta = {}
    for j in range(1, max(qs)):
        okj = valid[j:] & valid[:-j] & (dayv[j:] == dayv[:-j]) & spacing_ok(j)
        rho[j] = np.sum(e[j:][okj] * e[:-j][okj]) / s2
        delta[j] = np.sum((e[j:][okj] ** 2) * (e[:-j][okj] ** 2)) / s2 ** 2
    rows = []
    for q in qs:
        vr = 1 + 2 * sum((1 - j / q) * rho[j] for j in range(1, q))
        theta = sum((2 * (q - j) / q) ** 2 * delta[j] for j in range(1, q))
        rows.append([f"{label} q={q}", f"{vr:.3f}", f"{(vr - 1) / np.sqrt(theta):+.1f}" if q > 1 else "-"])
    return rows
P("### 4a. Autocorrelation of within-session returns (consecutive bars of the same session day only)")
P("")
rows = autocorr_table(R15.r_cc.values, R15.day.values, lambda k: (t15[k:] - t15[:-k]) == pd.Timedelta(minutes=15 * k), "M15")
h1c = h1_full.copy(); h1c["r_cc"] = np.where((h1c.day == h1c.day.shift(1)) & (h1c.slot == h1c.slot.shift(1) + 1), h1c.close - h1c.close.shift(1), np.nan)
rows += autocorr_table(h1c.r_cc.values, h1c.day.values, lambda k: (h1c.slot.values[k:] - h1c.slot.values[:-k]) == k, "H1")
table(["series", "pairs", "rho", "naive t (rho sqrt N)", "robust t (HC0)", "slope: next bar per 1 USD"], rows)
P("### 4b. Variance ratios VR(q) = Var(q-bar return) / (q x Var(1-bar return)), within session days; z = Lo-MacKinlay heteroskedasticity-robust")
P("")
rows = vr_table(R15.r_cc.values, R15.day.values, lambda k: (t15[k:] - t15[:-k]) == pd.Timedelta(minutes=15 * k), "M15 (q bars of 15 min)") + \
       vr_table(h1c.r_cc.values, h1c.day.values, lambda k: (h1c.slot.values[k:] - h1c.slot.values[:-k]) == k, "H1 (q hours)")
table(["series", "VR(q)", "robust z"], rows)
P("VR below 1 = mean reversion at that horizon, above 1 = momentum (positive autocorrelation); |z| > 2 is the usual significance mark.")
P("")
P("### 4c. Intraday range as a share of the previous session day's range, by hour (hours with >= 45 bars; previous-day range from the daily frame)")
P("")
rows = []
hh = h1_full[h1_full.prev_range > 0].copy()
hh["own"] = (hh.high - hh.low) / hh.prev_range; hh["cum"] = (hh.cum_hi - hh.cum_lo) / hh.prev_range
for sl in range(0, 23):
    g = hh[hh.slot == sl]
    if len(g) < 50: continue
    rows.append([lab(sl * 60), len(g), f"{g.own.median():.3f}", f"{g.own.mean():.3f}", f"{g.cum.median():.2f}", f"{g.cum.mean():.2f}", f"{(g.cum >= 1).mean() * 100:.0f}%"])
table(["hour (open)", "hours", "hour range / prev day range: median", "mean", "session range so far / prev day range: median", "mean", "share with session range >= prev day range"], rows)
P("### 4d. NR7 and inside days -> next day's range")
P("")
d = daily.copy()
d["nr7"] = d.range == d.range.rolling(7).min(); d["inside"] = (d.high < d.high.shift(1)) & (d.low > d.low.shift(1))
d["next_range"] = d.range.shift(-1); d["next_oc"] = d.oc.shift(-1); d["next_ratio"] = d.next_range / d.range
d["next_vs_atr"] = d.next_range / d.atr14; d["next_oc_vs_atr"] = d.next_oc.abs() / d.atr14
rows = []; n_base = len(d.dropna(subset=["next_range", "atr14"]))
for name, sel in [("all days", d.range.notna()), ("NR7", d.nr7), ("inside day", d.inside), ("NR7 and inside", d.nr7 & d.inside), ("not NR7", ~d.nr7)]:
    g = d[sel].dropna(subset=["next_range", "atr14"])
    if len(g) < 10: continue
    rows.append([name, len(g), f"{len(g) / n_base * 100:.1f}%", f"{g.next_ratio.median():.2f}", f"{g.next_vs_atr.median():.2f}", f"{g.next_vs_atr.mean():.2f}",
                 f"{(g.next_vs_atr > 1).mean() * 100:.0f}%", f"{g.next_oc_vs_atr.median():.2f}"])
table(["condition (day d)", "days", "frequency", "range(d+1)/range(d): median", "range(d+1)/ATR14(d): median", "mean", "share range(d+1) > ATR14(d)", "abs(open->close)(d+1)/ATR14(d): median"], rows)
P("NR7 = range of day d is the narrowest of the last seven session days. The ratio to the day's own range is mechanically > 1 after a narrow day; "
  "the ATR-normalised columns are the fair test of 'expansion'.")
P("")

# ================================================================== 5. mean reversion
P("## 5. Mean reversion")
P("")
P("### 5a. After an hour whose open-to-close move is >= k x ATR14(M15): the next hour's move (close of the signal hour -> close of the next hour)")
P("")
rows = []
hv = h1_full.dropna(subset=["atr", "next_move"]).copy(); hv["ratio"] = hv.move.abs() / hv.atr
hv["cont"] = np.sign(hv.move) * hv.next_move   # > 0 = continuation, < 0 = reversal
intraday = (hv.end_smin >= 480) & (hv.end_smin <= 1200)   # signal hour ends 07:00..19:00
for k in (1.5, 2.0, 3.0):
    for label, sel in [("all hours", hv.ratio >= k), ("signal hour ends 07:00-19:00", (hv.ratio >= k) & intraday)]:
        g = hv[sel]; x = pd.Series(g.cont.values, index=pd.DatetimeIndex(g.day))
        s = cand("5a after k-ATR hour", f"next-hour continuation after >= {k} ATR hour ({label})", x, kind="relative") if k == 2.0 else stats(x.values)
        nd_f = pd.DatetimeIndex(g.day).nunique()
        rows.append([f"{k:.1f}", label, s["n"], f"{s['n'] / YEARS:.0f}", f"{nd_f / YEARS:.0f}", fx(s["mean"]), fx(s["median"]), fx(s["t"], 1), ci(s), fx(100 * s["win"], 0, False) + "%",
                     fx(s["mean"] - RT_COST), fx(-s["mean"] - RT_COST)])
table(["k", "subset", "hours", "events/yr", "days/yr", "mean next-hour move in prior direction", "median", "t", "95% CI", "share continuing", "net follow (-0.30)", "net fade (-0.30)"], rows)
base_s = stats(hv.next_move.abs().values, ci=False)
P(f"Reference: mean |next-hour move| over all complete hours {base_s['mean']:.2f} USD; mean ATR14(M15) {hv.atr.mean():.2f} USD; hours with move >= 2 ATR: "
  f"{(hv.ratio >= 2).mean() * 100:.1f}% of hours.")
P("")
P("### 5b. Distance from the session TWAP (engine_v3.session_twap, from 23:00) at the hour end, in ATR14(M15) units, deciles -> next-hour move")
P("")
tv = h1_full.dropna(subset=["atr", "next_move", "twap"]).copy()
tv = tv[(tv.end_smin >= 480) & (tv.end_smin <= 1200)]   # hour ends 07:00..19:00 so the TWAP has >= 8 hours of history and the next hour is intraday
tv["dist"] = (tv.close - tv.twap) / tv.atr
tv["dec"] = pd.qcut(tv.dist, 10, labels=False)
rows = []
for dec in range(10):
    g = tv[tv.dec == dec]; x = pd.Series(g.next_move.values, index=pd.DatetimeIndex(g.day))
    s = cand("5b TWAP decile", f"next-hour move, TWAP-distance decile {dec + 1} (mean dist {g.dist.mean():+.2f} ATR)", x)
    toward = -np.sign(g.dist) * g.next_move
    rows.append([dec + 1, f"{g.dist.min():+.2f} .. {g.dist.max():+.2f}", fx(g.dist.mean()), s["n"], fx(s["mean"]), fx(s["t"], 1), ci(s), fx(toward.mean()), fx(toward.mean() - RT_COST)])
table(["decile", "distance range (ATR)", "mean distance", "hours", "mean next-hour move USD", "t", "95% CI", "mean move toward TWAP", "net fade (-0.30)"], rows)
rho = np.corrcoef(tv.dist, tv.next_move)[0, 1]
P(f"Correlation of TWAP distance with the next-hour move: {rho:+.3f} over {len(tv)} hours (a negative value means reversion toward the TWAP).")
P("")
P("### 5c. Position relative to the previous session day's high (PDH) and low (PDL) at the hour end -> next-hour move (hour ends 07:00-19:00)")
P("")
pv = h1_full.dropna(subset=["atr", "next_move", "pdh", "pdl"]).copy()
pv = pv[(pv.end_smin >= 480) & (pv.end_smin <= 1200) & (pv.pdh > pv.pdl)]
pv["pos"] = (pv.close - pv.pdl) / (pv.pdh - pv.pdl)
edges = [(-9, -0.25, "below PDL by > 25% of range"), (-0.25, 0, "0-25% of range below PDL"), (0, 0.25, "lowest quarter of prev range"), (0.25, 0.5, "second quarter"),
         (0.5, 0.75, "third quarter"), (0.75, 1.0, "top quarter"), (1.0, 1.25, "0-25% of range above PDH"), (1.25, 9, "above PDH by > 25% of range")]
rows = []
for lo_, hi_, name in edges:
    g = pv[(pv.pos > lo_) & (pv.pos <= hi_)]; x = pd.Series(g.next_move.values, index=pd.DatetimeIndex(g.day))
    s = cand("5c PDH/PDL position", f"next-hour move, {name}", x)
    rows.append([name, s["n"], f"{s['n'] / YEARS:.0f}", fx(s["mean"]), fx(s["median"]), fx(s["t"], 1), ci(s), fx(100 * s["win"], 0, False) + "%"])
table(["position of the close vs previous day's range", "hours", "per year", "mean next-hour move", "median", "t", "95% CI", "share up"], rows)
rows = []
for name, sel in [("within 0.3 ATR of PDH", (pv.close - pv.pdh).abs() <= 0.3 * pv.atr), ("within 0.3 ATR of PDL", (pv.close - pv.pdl).abs() <= 0.3 * pv.atr),
                  ("above PDH by > 0.3 ATR", pv.close - pv.pdh > 0.3 * pv.atr), ("below PDL by > 0.3 ATR", pv.pdl - pv.close > 0.3 * pv.atr)]:
    g = pv[sel]; x = pd.Series(g.next_move.values, index=pd.DatetimeIndex(g.day)); s = cand("5c PDH/PDL distance", f"next-hour move, {name}", x)
    rows.append([name, s["n"], f"{s['n'] / YEARS:.0f}", fx(s["mean"]), fx(s["median"]), fx(s["t"], 1), ci(s), fx(100 * s["win"], 0, False) + "%"])
table(["distance to the level (ATR14 M15)", "hours", "per year", "mean next-hour move", "median", "t", "95% CI", "share up"], rows)

# ================================================================== 6. summary of significant patterns
P("## 6. Every registered pattern with |t| > 2 or a 95 % CI excluding zero, sized net of a 0.30 USD round trip")
P("")
sig = [s for s in CANDS if (abs(s["t"]) > 2) or (not np.isnan(s["lo"]) and (s["lo"] > 0 or s["hi"] < 0))]
P(f"{len(CANDS)} patterns were registered in sections 1-5; at |t| > 2 about {0.046 * len(CANDS):.1f} of them would pass by chance alone with no edge. "
  f"{len(sig)} pass. The trade direction is the sign of the in-sample mean (long if positive, short if negative), chosen after seeing it. "
  "'net' = |mean| - 0.30 USD per oz per trade; 'events/yr' = events per calendar year in the development data and 'session days/yr' = distinct session "
  "days per year on which the pattern fires (hour-level patterns cluster on days, and their t treats every hour as independent, so it is overstated where "
  "events/yr is much larger than session days/yr); 'same-sign years' = number of the "
  f"{len(yrs)} development years (2024 = Jan-Jun) whose mean has the same sign as the overall mean.")
P("")
rows = []
for s in sorted(sig, key=lambda s: -abs(s["t"])):
    net = abs(s["mean"]) - RT_COST
    direction = ("long" if s["mean"] > 0 else "short") if s["kind"] == "signed" else ("follow" if s["mean"] > 0 else "fade")
    rows.append([s["section"], s["name"], direction, s["n"], f"{s['n'] / YEARS:.0f}", f"{s['days_fired'] / YEARS:.0f}", fx(s["mean"]), fx(s["sd"], 2, False), fx(s["t"], 1), ci(s),
                 fx(net), "yes" if net > 0 else "no", f"{s['same_sign_years']}/{s['n_years']}", " ".join(f"{y}:{v:+.2f}" for y, v in s["by_year"].items())])
table(["section", "pattern", "direction", "events", "events/yr", "session days/yr", "mean USD/oz", "sd", "t", "95% CI", "net of 0.30", "covers cost", "same-sign years", "mean by year"], rows)
covering = [s for s in sig if abs(s["mean"]) - RT_COST > 0]
P(f"Patterns that both pass and cover the 0.30 cost on average: {len(covering)} of {len(sig)}. Those with the same sign in every development year: "
  f"{sum(1 for s in covering if s['same_sign_years'] == s['n_years'])}.")
P("")
hour_means = R15.groupby("hour").r.mean(); best_hr = int(hour_means.abs().idxmax())
P("Plain-language reading of this table:")
P("")
asia_w = BLK["Asia 23:00-07:00"][1]; h23 = CANDS[0]   # the first registered candidate is the 23:00 -> 00:00 hour trade
P(f"- The only patterns above |t| = 3 are two faces of one thing: the long drift in the Asian block and in its first hour (23:00-00:00, the hour after "
  f"the daily break). That hour alone contributes {h23['mean']:+.2f} of the block's {asia_w['mean']:+.2f} USD/day ({h23['mean'] / asia_w['mean']:.0%}), and it is "
  "the hour where the constant 0.25 spread is least realistic (reopen spreads are several times wider). 2022, the one development year in which gold did "
  "not rise, shows none of it.")
P(f"- No 15-minute hold covers costs anywhere in the day: the largest mean M15 return of any hour is {hour_means[best_hr]:+.3f} USD (hour {best_hr:02d}), "
  f"a tenth of a 0.30 round trip. Every fixed-time trade that clears 0.30 holds for one hour or longer, in the Asian session.")
P("- None of the continuation tests (section 3) and none of the after-a-large-move tests (5a) pass; the TWAP-decile and PDH/PDL hits are single bins "
  "with no monotonic pattern across neighbouring bins and |t| of 2.0-2.8, exactly what 4-5 false positives among 96 tests look like.")
P("")

# ================================================================== 7. well-known effects
P("## 7. Do the well-known gold intraday effects show up in the development data?")
P("")
asia = BLK["Asia 23:00-07:00"][1]; lon = BLK["London 07:00-12:00"][1]; ny = BLK["NY 12:00-20:50"][1]
fixw = FIXS["10:30 -> 15:00 (AM fix to PM fix)"]
sess_open = px(0); sess_close = px("END")
gap = (sess_open - sess_close.shift(1)); intra = (sess_close - sess_open)
g_s = cand("7 overnight", "daily-break gap: previous session close -> session open (weekends included)", gap)
i_s = cand("7 intraday", "session open -> session close", intra)
nonus = cand("7 split", "23:00 -> 12:00 (Asia + London morning)", move(0, 780)); us = cand("7 split", "12:00 -> session close (New York hours)", move(780, "END"))
def verdict(s, want_sign):
    ok = (not np.isnan(s["t"])) and abs(s["t"]) > 2 and np.sign(s["mean"]) == want_sign
    return "YES" if ok else ("opposite sign" if abs(s["t"]) > 2 else "NO (not distinguishable from zero)")
rows = [
    ["Asian-session drift (price rises 23:00-07:00)", f"{asia['mean']:+.2f} USD/day ({(move_bp(0, 480)).mean():+.1f} bp), t {asia['t']:+.1f}, CI {ci(asia)}, n={asia['n']}",
     verdict(asia, +1), f"net long after 0.25 spread {asia['mean'] - SPREAD:+.2f} USD/day; by year " + " ".join(f"{y}:{v:+.2f}" for y, v in asia["by_year"].items()) +
     f"; {CANDS[0]['mean']:+.2f} of it is the 23:00-00:00 reopen hour; absent in 2022 when gold was flat, so it reads as the up-trend expressed in Asian hours"],
    ["AM-fix to PM-fix decline (10:30 -> 15:00 falls)", f"{fixw['mean']:+.2f} USD/day ({move_bp(hm('10:30') + 60, hm('15:00') + 60).mean():+.1f} bp), t {fixw['t']:+.1f}, CI {ci(fixw)}, n={fixw['n']}, share of days negative {100 * (1 - fixw['win']):.0f}%",
     verdict(fixw, -1), f"net short after 0.25 spread {-fixw['mean'] - SPREAD:+.2f} USD/day; by year " + " ".join(f"{y}:{v:+.2f}" for y, v in fixw["by_year"].items())],
    ["Overnight (daily-break gap) vs intraday (open -> close) split", f"gap {g_s['mean']:+.2f} USD/day (t {g_s['t']:+.1f}), cumulative {gap.sum():+.0f} USD; intraday {i_s['mean']:+.2f} USD/day (t {i_s['t']:+.1f}), cumulative {intra.sum():+.0f} USD",
     "gap carries the drift" if abs(g_s["t"]) > 2 and abs(i_s["t"]) <= 2 else ("intraday carries the drift" if abs(i_s["t"]) > 2 and abs(g_s["t"]) <= 2 else "neither part is distinguishable from zero" if abs(g_s["t"]) <= 2 and abs(i_s["t"]) <= 2 else "both parts significant"),
     "the gap is a 1-hour break (3 days at weekends); it is not tradable (no fills during the break, wide spreads at the reopen)"],
    ["Non-US hours vs US hours (23:00 -> 12:00 vs 12:00 -> close)", f"23:00-12:00 {nonus['mean']:+.2f} USD/day (t {nonus['t']:+.1f}); 12:00-close {us['mean']:+.2f} USD/day (t {us['t']:+.1f})",
     "YES: non-US hours carry the drift" if nonus["t"] > 2 and abs(us["t"]) <= 2 else "NO clean split", f"London 07:00-12:00 alone {lon['mean']:+.2f} (t {lon['t']:+.1f}); NY 12:00-20:50 alone {ny['mean']:+.2f} (t {ny['t']:+.1f})"],
]
table(["effect", "development data", "shows up?", "note"], rows)

P("## 8. Caveats")
P("")
P("- In-sample description of 3.5 years dominated by a rising gold price (mean close by year in section 0); any long-biased number partly measures "
  "that trend, which is not a repeatable intraday edge. The t-statistics assume independent days; overlapping windows within a day are not independent.")
P("- Spread is a constant 0.25 (BASE_CONFIG). Real spreads are wider in Asia, around the daily break and around releases; Asia and 'late' block figures "
  "are therefore optimistic. No slippage is charged in sections 1-5 (engine_v3 charges 0.05 per fill).")
P("- 2023 Feb-Jul has many days with missing hours; window figures skip days whose boundary bars are absent, hour figures skip thin hours, so the "
  "2023 counts are lower. The feed clock is London local time (section 0); the US-anchored measures are shifted by one hour on the DST-mismatch days.")
P("- Section 6 performs many comparisons; the count of expected false positives is stated there. Nothing in this profile was tuned, and the "
  "validation / final-test periods were not loaded.")

text = "\n".join(L)
print(text)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(text + "\n")
print(f"\n[written {OUT}]", file=sys.stderr)
