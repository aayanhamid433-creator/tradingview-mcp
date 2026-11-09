#!/usr/bin/env python3
"""Download XAUUSD 1-minute bars from HistData.com via its public download form.

HistData notes (https://www.histdata.com/f-a-q/):
  * MT (MetaTrader) format: "YYYY.MM.DD,HH:MM,open,high,low,close,volume"
  * Timestamps are Eastern Standard Time (UTC-5) WITHOUT daylight saving adjustment.
  * Prices are BID quotes from HistData's generic feed. No ask / spread. Volume column is 0.
Usage:
  python3 fetch_histdata.py --start 2021-01 --end 2026-10 --out ../data/raw
Yearly consolidated files are used for complete past years, monthly files for the
current year. Files already present are skipped. Requests are spaced 2s apart.
"""
import argparse, re, time, sys, pathlib, datetime as dt
import requests

BASE = "https://www.histdata.com"
UA = "gold-research-downloader/1.0 (python-requests; research use; contact via repo)"

def page_url(year, month=None):
    p = f"{BASE}/download-free-forex-historical-data/?/metatrader/1-minute-bar-quotes/xauusd/{year}"
    return p + (f"/{month}" if month else "")

def fetch(session, year, month, out_dir):
    tag = f"{year}{month:02d}" if month else f"{year}"
    dest = out_dir / f"HISTDATA_MT_XAUUSD_M1_{tag}.zip"
    if dest.exists() and dest.stat().st_size > 1000:
        print("skip", dest.name); return True
    r = session.get(page_url(year, month), timeout=60)
    r.raise_for_status()
    m = re.search(r'name="tk" id="tk" value="([0-9a-f]{32})"', r.text)
    if not m:
        print("no token for", tag, file=sys.stderr); return False
    data = {"tk": m.group(1), "date": str(year), "datemonth": f"{year}{month:02d}" if month else str(year),
            "platform": "MT", "timeframe": "M1", "fxpair": "XAUUSD"}
    time.sleep(2)
    r2 = session.post(f"{BASE}/get.php", data=data, headers={"Referer": page_url(year, month)}, timeout=300)
    if r2.status_code != 200 or not r2.content.startswith(b"PK"):
        print("download failed", tag, r2.status_code, r2.headers.get("content-type"), file=sys.stderr); return False
    dest.write_bytes(r2.content)
    print("saved", dest.name, len(r2.content), "bytes")
    time.sleep(2)
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True); ap.add_argument("--end", required=True)
    ap.add_argument("--out", default="../data/raw")
    a = ap.parse_args()
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    sy, sm = map(int, a.start.split("-")); ey, em = map(int, a.end.split("-"))
    s = requests.Session(); s.headers["User-Agent"] = UA
    this_year = dt.date.today().year
    y = sy
    while y <= ey:
        if y < this_year and y < ey or (y < this_year and y == ey and em == 12):
            ok = fetch(s, y, None, out)
            if not ok:  # fall back to monthly
                for mth in range(1, 13): fetch(s, y, mth, out)
        else:
            lo = sm if y == sy else 1; hi = em if y == ey else 12
            for mth in range(lo, hi + 1): fetch(s, y, mth, out)
        y += 1

if __name__ == "__main__":
    main()
