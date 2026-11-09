#!/usr/bin/env python3
"""Parse HistData MT-format zips into a single UTC 1-minute dataset and write a data audit.

Output:
  ../data/xauusd_m1_utc.parquet   columns: time_utc(index), open, high, low, close   (BID prices)
  ../data/DATA_AUDIT.md            audit of range, gaps, duplicates, weekly structure
Timestamps: HistData MT format is EST (UTC-5) with NO daylight-saving changes, so the
conversion is a constant +5h offset. The bar timestamp marks the bar OPEN time.
"""
import pathlib, zipfile, io, sys
import pandas as pd, numpy as np

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE.parent / "data" / "raw"
OUT = HERE.parent / "data"

def load_zip(p):
    z = zipfile.ZipFile(p)
    name = [n for n in z.namelist() if n.endswith(".csv")][0]
    df = pd.read_csv(io.BytesIO(z.read(name)), header=None,
                     names=["date", "time", "open", "high", "low", "close", "vol"])
    ts = pd.to_datetime(df["date"] + " " + df["time"], format="%Y.%m.%d %H:%M")
    df.index = ts + pd.Timedelta(hours=5)  # EST (UTC-5, fixed) -> UTC
    df.index.name = "time_utc"
    df.index = df.index.tz_localize("UTC")
    return df[["open", "high", "low", "close"]].astype("float64"), name

def main():
    files = sorted(RAW.glob("HISTDATA_MT_XAUUSD_M1_*.zip"))
    parts, names = [], []
    for f in files:
        d, n = load_zip(f); parts.append(d); names.append((f.name, n, len(d), str(d.index[0]), str(d.index[-1])))
        print(f.name, len(d), d.index[0], d.index[-1])
    m1 = pd.concat(parts).sort_index()
    dup = m1.index.duplicated(keep="last").sum()
    m1 = m1[~m1.index.duplicated(keep="last")]
    bad = ((m1.high < m1[["open", "close"]].max(axis=1)) | (m1.low > m1[["open", "close"]].min(axis=1))).sum()
    # gaps: diff between consecutive bars
    diff = m1.index.to_series().diff().dt.total_seconds().div(60).dropna()
    gaps = diff[diff > 1]
    # classify gaps: weekend (Fri ~22:00 UTC -> Sun ~23:00 UTC), daily break (~22:00-23:00 UTC), other
    g = pd.DataFrame({"start": m1.index[1:][diff.values > 1] - pd.to_timedelta(gaps.values, unit="m"), "minutes": gaps.values})
    g["end"] = g["start"] + pd.to_timedelta(g["minutes"], unit="m")
    g["dow"] = g["start"].dt.dayofweek
    def cls(r):
        if r.dow == 4 and r.minutes > 24 * 60: return "weekend"
        if 55 <= r.minutes <= 70 and r.start.hour in (21, 22, 23): return "daily_break"
        if r.minutes <= 5: return "micro(<=5m)"
        if r.minutes <= 60: return "short(<=60m)"
        return "long(>60m)"
    g["class"] = g.apply(cls, axis=1)
    m1.to_parquet(OUT / "xauusd_m1_utc.parquet")
    # weekly open/close structure (mode of first/last bar time by week)
    wk = m1.index.to_series()
    first = wk.groupby(wk.dt.to_period("W")).min(); last = wk.groupby(wk.dt.to_period("W")).max()
    lines = ["# DATA AUDIT — XAUUSD 1-minute bars (HistData.com, MT format)", "",
             f"Generated: {pd.Timestamp.utcnow():%Y-%m-%d %H:%M} UTC", "",
             "## Provenance", "",
             "| Field | Value |", "|---|---|",
             "| Instrument | XAUUSD spot gold vs USD (HistData generic feed; NOT the user's broker feed) |",
             "| Source | https://www.histdata.com/download-free-forex-historical-data/?/metatrader/1-minute-bar-quotes/xauusd |",
             "| Price basis | BID quotes only (per HistData FAQ). No ask, no spread, no volume (column is 0). |",
             "| Native timezone | EST (UTC-5) with no DST; converted to UTC with a fixed +5h. Bar time = bar open. |",
             f"| Range (UTC) | {m1.index[0]} to {m1.index[-1]} |",
             f"| Bars | {len(m1):,} |",
             f"| Duplicate timestamps removed | {dup} |",
             f"| OHLC consistency violations | {bad} |",
             "| Resolution | 1 minute (no bar when no tick occurred, so quiet minutes are absent) |",
             "| Cost data | none in source; spread/commission/slippage come from the cost model in the playbook |", "",
             "## Files", "", "| zip | csv | bars | first (UTC) | last (UTC) |", "|---|---|---|---|---|"]
    lines += [f"| {a} | {b} | {c:,} | {d} | {e} |" for a, b, c, d, e in names]
    lines += ["", "## Gaps between consecutive bars", "", "| class | count | median minutes | max minutes |", "|---|---|---|---|"]
    for k, grp in g.groupby("class"):
        lines.append(f"| {k} | {len(grp):,} | {grp.minutes.median():.0f} | {grp.minutes.max():.0f} |")
    long_gaps = g[(g["class"] == "long(>60m)")].sort_values("minutes", ascending=False).head(25)
    lines += ["", "### Largest non-weekend gaps (>60 min, top 25)", "", "| start (UTC) | end (UTC) | minutes |", "|---|---|---|"]
    lines += [f"| {r.start} | {r.end} | {r.minutes:.0f} |" for r in long_gaps.itertuples()]
    lines += ["", "## Weekly session structure (mode of first/last bar time of each week, UTC)", "",
              f"- Most common week open: {first.dt.strftime('%a %H:%M').mode().iloc[0]}",
              f"- Most common week close: {last.dt.strftime('%a %H:%M').mode().iloc[0]}",
              "", "## Implications", "",
              "- Bid-only data: long entries/exits must add a modelled spread to approximate ask prices; short entries/exits use bid directly.",
              "- No volume: any volume-based rule is untestable with this dataset.",
              "- Missing quiet minutes mean bar-count based windows must be built on wall-clock time, not bar index.",
              "- This is not the user's broker feed; results are preliminary and must be re-run on broker export data."]
    (OUT / "DATA_AUDIT.md").write_text("\n".join(lines))
    print("\n".join(lines[:30]))

if __name__ == "__main__":
    main()
