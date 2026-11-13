# PREREGISTRATION v7 — "quick in, quick out" in the direction of the move
Frozen 2026-11-13 (commit time is the timestamp), BEFORE engine_v7_quick.py was written or any variant run.

Request (Aayan, 2026-11-13): "i also wanna focus on directional buy if the direction is going one way like up i quickly
entry and quickly exit ... quick in and quick out". Earlier standing wish: a trade should be in and out within 15 minutes.

## What was known when this file was written (development period only, 2021-01 to 2024-06)

Event study on M1 bars, 07:00-16:00 London time. Burst = the move over the last W minutes is at least k x (ATR14(M15) x
sqrt(W / 15)). Entry at the next minute's open in the direction of the burst, exit at the close H minutes later. Gross
USD per ounce BEFORE the 0.35 USD round-trip cost, first signal of each cluster:

| burst | signals | mean burst (USD) | hold 1 min | 3 min | 5 min | 10 min | 15 min | 30 min |
|---|---|---|---|---|---|---|---|---|
| W 3, k 2 | 7,506 | 2.89 | -0.048 (t -4.4) | -0.077 (t -4.4) | -0.092 (t -4.3) | -0.074 | -0.073 | -0.114 |
| W 5, k 1.5 | 10,981 | 2.87 | -0.024 (t -3.3) | -0.051 (t -4.1) | -0.068 (t -4.3) | -0.038 | -0.022 | -0.032 |
| W 5, k 2 | 5,212 | 3.74 | -0.023 | -0.059 (t -2.8) | -0.085 (t -3.2) | -0.052 | -0.055 | -0.041 |
| W 5, k 3 | 1,274 | 5.63 | +0.022 | -0.038 | -0.046 | +0.060 | +0.044 | +0.133 |
| W 15, k 2 | 2,139 | 6.74 | +0.004 | +0.006 | -0.038 | -0.004 | +0.009 | +0.085 |
| W 15, k 3 | 570 | 9.81 | -0.090 | -0.120 | -0.112 | -0.000 | -0.044 | -0.037 |

After a fast move gold does not keep going for the next minutes; on average it gives a few cents back. Splitting by the
M15 trend (EMA50) does not help. Asian hours and the US data window show the same. The M15 return autocorrelation is
-0.013 and variance ratios are below 1 (results/PROFILE_v4_dev.md §4). Nothing in development is larger than a fifth of
the round-trip cost. Expectation: every follow-the-move variant loses about the cost per trade; the fade variant is
listed to show that the small give-back is also far smaller than the cost.

## Rules (all variants)

XAUUSD M1 data, dataset clock (London time). Signals at M1 closes with close time in [07:00, 16:00); market entry at the
next M1 bar's open (long: bid open + 0.25 spread + 0.05 slippage; short: bid open - 0.05), only if it opens within 2
minutes of the signal; one position at a time; at most 6 entries per session day; after an exit the next signal must be
a new one (first minute on which the condition is true after at least one minute on which it was false).
STOP: 1.0 x ATR14(M15) of the last closed M15 bar from the fill; planned risk for R is that distance. No target.
EXIT: stop on M1 bars (same-minute check on the fill minute), or the open of the first M1 bar at or after H minutes from
the fill (long: bid open - 0.05; short: bid open + 0.25 + 0.05), or 20:50, or a session gap. Costs as in every engine;
cost stress at spread 0.50 / slippage 0.10.

Trend state (variants marked T, and the TREND variants): the last closed M15 bar closes above its EMA50 and that EMA50
is above its value four M15 bars earlier (uptrend; mirrored for a downtrend).

| id | signal | direction | hold H |
|---|---|---|---|
| QS_BURST5_H5 | burst W 5, k 2 | with the burst | 5 min |
| QS_BURST5_H15 | burst W 5, k 2 | with the burst | 15 min |
| QS_BURST5_H5_T | burst W 5, k 2, only when it agrees with the trend state | with the burst | 5 min |
| QS_BURST15_H15 | burst W 15, k 2 | with the burst | 15 min |
| QS_TREND_BRK_H5 | trend state and an M1 close beyond the extreme of the previous 5 M1 bars in the trend direction | with the trend | 5 min |
| QS_TREND_BRK_H15 | same | with the trend | 15 min |
| QS_TREND_PB_H15 | trend state and an M5 bar that trades through its EMA20(M5) and closes back on the trend side | with the trend | 15 min |
| QS_FADE5_H5 | burst W 5, k 2 | AGAINST the burst (information only) | 5 min |

## Decision rule

The strict rule of v5 (mean R > 0 in all three periods, held-out CI excludes zero, PF > 1.10 in both held-out periods
at base AND stressed costs, at least 60 trades in each, max DD <= 10 R, ex-top-5 > 0). A null or negative result is
valid and expected.
