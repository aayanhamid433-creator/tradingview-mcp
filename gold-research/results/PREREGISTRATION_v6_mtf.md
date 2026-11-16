# PREREGISTRATION v6 — levels on the 15-minute chart, entries on the 5-minute or 1-minute chart
Frozen 2026-11-13 (commit time is the timestamp), BEFORE engine_v6_mtf.py was written or any variant run.

Request (Aayan, 2026-11-13, after the improved breakout HL_IMP10_MS_T): "the trades are lower and the profit isn't that
much; can we mark the highs and the lows on 15m and take trades either 5m or 1m".

## Rules (all variants)

- LEVELS: the last confirmed M15 swing high and swing low, pivot N (a bar whose high is >= the highs of the N bars before
  and the N bars after it; it becomes the marked level at the close of the Nth later M15 bar). A new level of a kind
  replaces the old one and is live. Trigger price: marked high + 0.10, marked low - 0.10.
- ENTRY TIMEFRAME E (5 minutes or 1 minute). SIGNAL: a completed E-bar whose CLOSE (bid) is at or above the buy trigger
  (long) or at or below the sell trigger (short). A wick through the level without a close beyond it is not a signal and
  does not use the level up.
- LIFE: a level is used up by the first E-bar close beyond its trigger, at any time of day, whether or not a trade is
  taken (no chasing of a break that happened outside the window, while a position was open, or after the daily cap).
- A signal becomes a trade only if: the E-bar closes at a time in [07:00, 16:00) on the dataset clock (London time);
  flat; fewer than 3 entries in the session day; and, with the trend filter on, the last closed M15 bar closed above its
  EMA50 for a long (below for a short).
- ENTRY: market order at the open of the next M1 bar (long: bid open + 0.25 spread + 0.05 slippage; short: bid open -
  0.05), only if that bar is in the same session day, opens within 5 minutes of the signal close and before 20:50.
- STOP: for a long, signal close - dist, where dist = (signal close - (signal bar low - 0.10)) but not less than
  1.0 x ATR14 of the E-bars at the signal bar and not more than 0.6 x previous-session-day D1ATR; mirrored for a short.
  A fill at or beyond its own stop is not taken. Planned risk for R = |fill - stop|.
- TARGET: fill +/- target multiple x planned risk. EXIT: stop or target on M1 bars (stop first when both print in one
  minute, target needs trade-through), same-minute stop check on the fill minute, everything flat at 20:50, session-gap
  exit. One position at a time. Costs: spread 0.25, slippage 0.05 per fill, commission 0. Cost stress reported for
  every variant at spread 0.50 / slippage 0.10, because tight stops make costs a large share of the risk.

## Variants

| id | pivot N (M15) | entry timeframe | trend filter | target |
|---|---|---|---|---|
| MTF10_M5 | 10 | M5 | on | 2.0 R |
| MTF10_M1 | 10 | M1 | on | 2.0 R |
| MTF5_M5 | 5 | M5 | on | 2.0 R |
| MTF5_M1 | 5 | M1 | on | 2.0 R |
| MTF10_M5_T15 | 10 | M5 | on | 1.5 R |
| MTF10_M5_T30 | 10 | M5 | on | 3.0 R |
| MTF10_M5_NOTREND | 10 | M5 | off | 2.0 R |

## Expectation, stated before running

The median stop on E-bars will be a few USD, so the 0.35 USD round trip is roughly 0.1 R per trade on M5 and more on M1
(0.2 R or more at the 0.55-0.65 USD spread FOREX.com showed on 2026-11-12/13). The development analysis of the M15
version found that stops tighter than 0.10 x D1ATR lost 0.66 R per trade. The most likely outcome is that lower-timeframe
entries lose after costs, more so on M1 than on M5. A null or negative result is valid and will be reported as such.

## Decision rule

Same strict rule as v5: mean R > 0 in all three periods; pooled held-out 90 % CI excludes zero; PF > 1.10 in both
held-out periods; at least 60 trades in each; max DD <= 10 R in every period; held-out mean R ex-top-5 > 0; and here
also: still PF > 1.10 in both held-out periods under the cost stress. The comparison row is HL_IMP10_MS_T
(held-out 511 trades, +0.121 R, PF 1.34, max DD -10.2 R, 0.84 trades a day).
