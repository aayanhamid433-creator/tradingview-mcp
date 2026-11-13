# DATA AUDIT — XAUUSD 1-minute bars (HistData.com, MT format)

Generated: 2026-11-09 02:16 UTC

## Provenance

| Field | Value |
|---|---|
| Instrument | XAUUSD spot gold vs USD (HistData generic feed; NOT the user's broker feed) |
| Source | https://www.histdata.com/download-free-forex-historical-data/?/metatrader/1-minute-bar-quotes/xauusd |
| Price basis | BID quotes only (per HistData FAQ). No ask, no spread, no volume (column is 0). |
| Native timezone | EST (UTC-5) with no DST; converted to UTC with a fixed +5h. Bar time = bar open. |
| Clock correction (2026-11-13) | The stamps follow New York local time (EST/EDT), not fixed EST, so the +5h index is London local time (UTC in winter, UTC+1 in summer) although it is labelled UTC. See PROJECT_STATE.md working rules. |
| Range (UTC) | 2021-01-03 23:00:00+00:00 to 2026-10-30 20:58:00+00:00 |
| Bars | 2,020,438 |
| Duplicate timestamps removed | 1504 |
| OHLC consistency violations | 0 |
| Resolution | 1 minute (no bar when no tick occurred, so quiet minutes are absent) |
| Cost data | none in source; spread/commission/slippage come from the cost model in the playbook |

## Files

| zip | csv | bars | first (UTC) | last (UTC) |
|---|---|---|---|---|
| HISTDATA_MT_XAUUSD_M1_2021.zip | DAT_MT_XAUUSD_M1_2021.csv | 353,446 | 2021-01-03 23:00:00+00:00 | 2021-12-31 21:58:00+00:00 |
| HISTDATA_MT_XAUUSD_M1_2022.zip | DAT_MT_XAUUSD_M1_2022.csv | 354,628 | 2022-01-02 23:00:00+00:00 | 2022-12-30 21:57:00+00:00 |
| HISTDATA_MT_XAUUSD_M1_2023.zip | DAT_MT_XAUUSD_M1_2023.csv | 308,812 | 2023-01-02 23:00:00+00:00 | 2023-12-29 21:57:00+00:00 |
| HISTDATA_MT_XAUUSD_M1_2024.zip | DAT_MT_XAUUSD_M1_2024.csv | 355,652 | 2024-01-01 23:00:00+00:00 | 2024-12-31 21:57:00+00:00 |
| HISTDATA_MT_XAUUSD_M1_2025.zip | DAT_MT_XAUUSD_M1_2025.csv | 354,011 | 2025-01-01 23:00:00+00:00 | 2025-12-31 21:57:00+00:00 |
| HISTDATA_MT_XAUUSD_M1_202601.zip | DAT_MT_XAUUSD_M1_202601.csv | 28,827 | 2026-01-01 23:00:00+00:00 | 2026-01-30 21:58:00+00:00 |
| HISTDATA_MT_XAUUSD_M1_202602.zip | DAT_MT_XAUUSD_M1_202602.csv | 27,429 | 2026-02-01 23:06:00+00:00 | 2026-02-27 21:58:00+00:00 |
| HISTDATA_MT_XAUUSD_M1_202603.zip | DAT_MT_XAUUSD_M1_202603.csv | 30,595 | 2026-03-01 23:00:00+00:00 | 2026-04-01 04:58:00+00:00 |
| HISTDATA_MT_XAUUSD_M1_202604.zip | DAT_MT_XAUUSD_M1_202604.csv | 28,976 | 2026-04-01 05:00:00+00:00 | 2026-05-01 04:58:00+00:00 |
| HISTDATA_MT_XAUUSD_M1_202605.zip | DAT_MT_XAUUSD_M1_202605.csv | 28,822 | 2026-05-01 05:00:00+00:00 | 2026-06-01 04:58:00+00:00 |
| HISTDATA_MT_XAUUSD_M1_202606.zip | DAT_MT_XAUUSD_M1_202606.csv | 30,144 | 2026-06-01 05:00:00+00:00 | 2026-07-01 04:58:00+00:00 |
| HISTDATA_MT_XAUUSD_M1_202607.zip | DAT_MT_XAUUSD_M1_202607.csv | 31,414 | 2026-07-01 05:00:00+00:00 | 2026-07-31 21:58:00+00:00 |
| HISTDATA_MT_XAUUSD_M1_202608.zip | DAT_MT_XAUUSD_M1_202608.csv | 29,437 | 2026-08-02 23:00:00+00:00 | 2026-09-01 04:58:00+00:00 |
| HISTDATA_MT_XAUUSD_M1_202609.zip | DAT_MT_XAUUSD_M1_202609.csv | 29,321 | 2026-09-01 05:00:00+00:00 | 2026-10-01 04:58:00+00:00 |
| HISTDATA_MT_XAUUSD_M1_202610.zip | DAT_MT_XAUUSD_M1_202610.csv | 30,428 | 2026-10-01 05:00:00+00:00 | 2026-10-30 20:58:00+00:00 |

## Gaps between consecutive bars

| class | count | median minutes | max minutes |
|---|---|---|---|
| daily_break | 1,078 | 61 | 66 |
| long(>60m) | 682 | 61 | 4442 |
| micro(<=5m) | 351 | 2 | 5 |
| short(<=60m) | 12 | 8 | 55 |
| weekend | 296 | 2941 | 4383 |

### Largest non-weekend gaps (>60 min, top 25)

| start (UTC) | end (UTC) | minutes |
|---|---|---|
| 2024-03-28 20:58:00+00:00 | 2024-03-31 23:00:00+00:00 | 4442 |
| 2023-04-06 21:58:00+00:00 | 2023-04-10 00:00:00+00:00 | 4442 |
| 2025-04-17 21:58:00+00:00 | 2025-04-20 23:00:00+00:00 | 4382 |
| 2022-04-14 21:58:00+00:00 | 2022-04-17 23:00:00+00:00 | 4382 |
| 2021-12-23 21:58:00+00:00 | 2021-12-26 23:00:00+00:00 | 4382 |
| 2026-04-02 21:58:00+00:00 | 2026-04-05 23:00:00+00:00 | 4382 |
| 2021-04-01 21:59:00+00:00 | 2021-04-04 23:00:00+00:00 | 4381 |
| 2025-12-24 18:43:00+00:00 | 2025-12-25 23:04:00+00:00 | 1701 |
| 2024-12-24 18:43:00+00:00 | 2024-12-25 23:00:00+00:00 | 1697 |
| 2024-12-31 21:57:00+00:00 | 2025-01-01 23:00:00+00:00 | 1503 |
| 2025-12-31 21:57:00+00:00 | 2026-01-01 23:00:00+00:00 | 1503 |
| 2021-05-31 04:59:00+00:00 | 2021-06-01 01:00:00+00:00 | 1201 |
| 2023-07-12 16:59:00+00:00 | 2023-07-12 23:00:00+00:00 | 361 |
| 2021-11-25 17:58:00+00:00 | 2021-11-25 23:18:00+00:00 | 320 |
| 2023-01-16 17:58:00+00:00 | 2023-01-16 23:00:00+00:00 | 302 |
| 2022-01-17 17:58:00+00:00 | 2022-01-17 23:00:00+00:00 | 302 |
| 2023-03-07 18:59:00+00:00 | 2023-03-08 00:00:00+00:00 | 301 |
| 2021-09-06 17:59:00+00:00 | 2021-09-06 23:00:00+00:00 | 301 |
| 2021-02-15 17:59:00+00:00 | 2021-02-15 23:00:00+00:00 | 301 |
| 2021-01-18 17:59:00+00:00 | 2021-01-18 23:00:00+00:00 | 301 |
| 2021-07-05 17:59:00+00:00 | 2021-07-05 23:00:00+00:00 | 301 |
| 2023-11-23 18:28:00+00:00 | 2023-11-23 23:00:00+00:00 | 272 |
| 2023-06-19 18:59:00+00:00 | 2023-06-19 23:00:00+00:00 | 241 |
| 2023-07-04 18:59:00+00:00 | 2023-07-04 23:00:00+00:00 | 241 |
| 2023-06-28 19:59:00+00:00 | 2023-06-29 00:00:00+00:00 | 241 |

## Weekly session structure (mode of first/last bar time of each week, UTC)

- Most common week open: Mon 00:00
- Most common week close: Sun 23:59

## Implications

- Bid-only data: long entries/exits must add a modelled spread to approximate ask prices; short entries/exits use bid directly.
- No volume: any volume-based rule is untestable with this dataset.
- Missing quiet minutes mean bar-count based windows must be built on wall-clock time, not bar index.
- This is not the user's broker feed; results are preliminary and must be re-run on broker export data.