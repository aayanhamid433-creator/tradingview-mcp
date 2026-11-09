# DATA FACTS — XAUUSD from HistData M1 bid, 2021-01 → 2026-10 (UTC)

Descriptive statistics to size stops, pick windows and set expectations. Not a strategy test. Bid prices; constant-spread caveats apply.

## 1. Daily volatility by year (session day 23:00→22:00 UTC)

| year | days | median daily range (USD) | median range (% of price) | median ATR(14) (USD) | median close | annualised vol of daily returns |
|---|---|---|---|---|---|---|
| 2021 | 258 | 21.1 | 1.18% | 23.5 | 1793 | 13.1% |
| 2022 | 258 | 23.1 | 1.28% | 24.8 | 1804 | 14.9% |
| 2023 | 257 | 20.6 | 1.05% | 23.6 | 1943 | 13.1% |
| 2024 | 259 | 30.7 | 1.23% | 33.3 | 2382 | 15.1% |
| 2025 | 258 | 51.3 | 1.49% | 52.3 | 3345 | 19.1% |
| 2026 | 215 | 99.4 | 2.19% | 107.0 | 4478 | 28.9% |

## 2. M15 bar range by year and session (median, USD)

| year | Asia 23-07 | London 07-12 | NY-am 12-16 | NY-pm 16-22 | all |
|---|---|---|---|---|---|
| 2021 | 1.36 | 1.90 | 3.26 | 1.48 | 1.73 |
| 2022 | 1.42 | 2.12 | 3.34 | 1.80 | 1.89 |
| 2023 | 1.30 | 1.77 | 2.90 | 1.56 | 1.63 |
| 2024 | 1.87 | 2.51 | 3.98 | 2.30 | 2.40 |
| 2025 | 4.10 | 4.43 | 6.35 | 3.78 | 4.45 |
| 2026 | 8.06 | 7.67 | 11.62 | 7.50 | 8.29 |

Median M15 ATR(14) over the whole sample: 2.75 USD; 2025-2026 only: 7.05 USD.

## 3. Volatility profile by UTC hour (median M15 range, USD, 2024-07 → 2026-10)

| UTC hour | median M15 range | relative to day median |
|---|---|---|
| 00 | 3.92 | 0.77x |
| 01 | 5.90 | 1.17x |
| 02 | 6.53 | 1.29x |
| 03 | 5.08 | 1.00x |
| 04 | 4.04 | 0.80x |
| 05 | 3.83 | 0.76x |
| 06 | 5.09 | 1.00x |
| 07 | 5.30 | 1.05x |
| 08 | 5.47 | 1.08x |
| 09 | 4.88 | 0.96x |
| 10 | 4.61 | 0.91x |
| 11 | 4.34 | 0.86x |
| 12 | 4.93 | 0.97x |
| 13 | 7.39 | 1.46x |
| 14 | 8.87 | 1.75x |
| 15 | 8.24 | 1.63x |
| 16 | 6.27 | 1.24x |
| 17 | 4.98 | 0.99x |
| 18 | 4.50 | 0.89x |
| 19 | 4.01 | 0.79x |
| 20 | 4.03 | 0.80x |
| 21 | 2.95 | 0.58x |
| 22 | 4.84 | 0.96x |
| 23 | 3.86 | 0.76x |

## 4. Session returns (sum of M1 log returns inside the window, basis points per session, mean ± t-stat)

| year | Asia 23-07 | London 07-12 | NY-am 12-16 | NY-pm 16-22 |
|---|---|---|---|---|
| 2021 | +6.4 (t +3.3) | -3.9 (t -1.9) | -2.4 (t -0.7) | -1.8 (t -0.8) |
| 2022 | +0.1 (t +0.0) | -1.2 (t -0.5) | +2.2 (t +0.6) | -1.2 (t -0.5) |
| 2023 | +5.6 (t +3.1) | +0.6 (t +0.4) | -1.7 (t -0.5) | +0.3 (t +0.1) |
| 2024 | +5.6 (t +2.3) | +4.0 (t +1.8) | -2.9 (t -0.8) | +2.5 (t +0.9) |
| 2025 | +10.5 (t +2.8) | +2.5 (t +0.8) | +2.6 (t +0.6) | +3.6 (t +1.3) |
| 2026 | +2.5 (t +0.3) | +1.5 (t +0.3) | -3.4 (t -0.5) | -5.5 (t -1.0) |
| all | +5.2 (t +3.3) | +0.6 (t +0.5) | -0.9 (t -0.5) | -0.2 (t -0.2) |

Reading: a |t| below about 2 means the session drift is indistinguishable from zero in this sample. Session seasonality found in older studies should not be assumed to persist.

## 5. Daily regime filters (descriptive, next-day return conditional on the filter)

| filter | days | share of days | mean next-day return (bps) | t-stat | ann. vol next day |
|---|---|---|---|---|---|
| close > SMA200 | 1005 | 77% | +7.9 | +2.1 | 18.5% |
| close < SMA200 | 300 | 23% | +3.0 | +0.5 | 18.1% |
| 12-1 month momentum > 0 | 1060 | 81% | +5.8 | +1.5 | 19.2% |
| 12-1 month momentum < 0 | 192 | 15% | +12.5 | +1.8 | 14.9% |

2021-2026 was dominated by a long uptrend (gold roughly doubled), so 'above SMA200' days are the majority and any long-biased filter looks good in-sample. Treat as context, not evidence.

## 6. Weekend gaps (Monday session open minus the preceding Friday session close, USD, date-aligned)

- weeks: 292; median |gap| 1.5; 90th percentile |gap| 15.7; max |gap| 111.9
- share of weeks with |gap| > 5 USD: 22%; > 10 USD: 14%; > 20 USD: 7%
- 2025-2026 only: median |gap| 4.4, 90th percentile 36.3

## 7. Daily-break gaps (23:00 UTC reopen minus last 21:xx UTC close, same date, USD)

- days: 1026; median |gap| 0.49; 90th percentile 1.84; max 30.8

## 8. Trend regimes

- Share of days with daily ADX(14) > 25: 53%; > 30: 35%.
- Share of M15 bars with ADX(14) > 30 (from VALIDATION_MECHANICS): 29.3%.
