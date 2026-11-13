# VALIDATION REPORT v7 — "quick in, quick out" in the direction of the move, 2026-11-13

Status: **REJECTED. All thirteen variants (eight on one-minute bars, five on five-minute bars) lose in every period, before and after the cost stress.** Written by the main
session; adversarial agent verification is queued (usage limit).

## 1. Request and rules

Aayan, 2026-11-13: "directional buy if the direction is going one way like up i quickly entry and quickly exit ... quick
in and quick out". Frozen before any code in results/PREREGISTRATION_v7_quick.md: signals on M1 closes between 07:00 and
16:00 London time, market entry on the next minute, stop 1 x ATR14(M15), exit after 5 or 15 minutes, at most six trades a
day. Engine backtest/engine_v7_quick.py (mechanical assertions and a hand check passed). 1 R = the stop distance.

## 2. Does a fast move keep going? (development period only, before any strategy was run)

Burst = the last W minutes moved at least k x (ATR14(M15) x sqrt(W / 15)). Gross USD per ounce in the direction of the
burst, entry next minute, BEFORE the 0.35 USD round-trip cost:

| burst | signals | mean burst | after 1 min | 3 min | 5 min | 15 min |
|---|---|---|---|---|---|---|
| 3 minutes, k 2 | 7,506 | 2.89 USD | -0.048 (t -4.4) | -0.077 (t -4.4) | -0.092 (t -4.3) | -0.073 |
| 5 minutes, k 2 | 5,212 | 3.74 USD | -0.023 | -0.059 (t -2.8) | -0.085 (t -3.2) | -0.055 |
| 15 minutes, k 2 | 2,139 | 6.74 USD | +0.004 | +0.006 | -0.038 | +0.009 |

After a fast move gold gives a few cents back on average. It does not continue. Splitting by the 15-minute trend, by the
Asian hours or by the US data window changes nothing. The largest effect anywhere is a quarter of the round-trip cost.

## 3. The eight variants

| variant | trades per day | development mean R / PF | validation | final test | held-out mean R [90 % CI] | held-out, costs doubled | net USD per ounce per trade, by year |
|---|---|---|---|---|---|---|---|
| QS_BURST5_H5 (follow a 5-minute burst, hold 5 min) | 4.2 | -0.231 / 0.46 | -0.124 / 0.63 | -0.084 / 0.74 | -0.104 [-0.128, -0.081] | -0.183 | -0.37 to -0.63 |
| QS_BURST5_H15 (hold 15 min) | 3.8 | -0.201 / 0.63 | -0.096 / 0.80 | -0.070 / 0.84 | -0.084 [-0.120, -0.046] | -0.171 | |
| QS_BURST5_H5_T (only with the M15 trend) | 2.2 | -0.227 / 0.48 | -0.112 / 0.67 | -0.078 / 0.76 | -0.096 [-0.131, -0.060] | -0.170 | -0.38 to -0.55 |
| QS_BURST15_H15 (15-minute burst) | 2.1 | -0.151 / 0.72 | -0.122 / 0.76 | -0.155 / 0.70 | -0.137 [-0.189, -0.084] | -0.221 | |
| QS_TREND_BRK_H5 (trend + 1-minute breakout, 5 min) | 5.9 | -0.216 / 0.34 | -0.106 / 0.54 | -0.048 / 0.72 | -0.078 [-0.089, -0.066] | -0.156 | |
| QS_TREND_BRK_H15 (15 min) | 5.9 | -0.206 / 0.52 | -0.102 / 0.70 | -0.061 / 0.78 | -0.082 [-0.100, -0.063] | -0.158 | -0.29 to -0.72 |
| QS_TREND_PB_H15 (trend + 5-minute pullback, 15 min) | 5.7 | -0.187 / 0.54 | -0.106 / 0.67 | -0.030 / 0.89 | -0.068 [-0.087, -0.050] | -0.145 | -0.14 to -0.40 |
| QS_FADE5_H5 (the opposite: fade the burst) | 4.1 | -0.148 / 0.60 | -0.075 / 0.76 | -0.016 / 0.94 | -0.047 [-0.071, -0.023] | -0.121 | -0.34 to +0.02 |

Development drawdowns are 400 to 1,160 R. Before costs, following a burst loses a little in every year (gross -0.01 to
-0.09 R); the trend variants are about zero before costs; fading earns +0.01 to +0.07 R before costs. The cost is 0.04 R
(2026) to 0.21 R (2023) per trade, so every variant loses the spread on every trade. At 0.25 % risk QS_BURST5_H5 would
have lost about 9 R, roughly 1,100 USD, in an average month of the held-out period.

## 3b. The same rules on 5-minute bars (v7c addendum, frozen before running)

The Pine script (§7) also runs on a 5-minute chart, where a signal is checked every five minutes. That is a different
list of trades (18 to 45 % of the signals are shared with the one-minute forms), so it was tested instead of assumed.

| variant | trades per day | development mean R / PF | validation | final test | held-out mean R [90 % CI] | held-out, costs doubled |
|---|---|---|---|---|---|---|
| QS5_TREND_BRK_H5 (trend + close beyond the previous 5-minute bar, hold 5 min) | 5.9 | -0.212 / 0.32 | -0.115 / 0.49 | -0.057 / 0.67 | -0.086 [-0.097, -0.075] | -0.164 |
| QS5_TREND_BRK_H15 (hold 15 min) | 5.9 | -0.211 / 0.50 | -0.109 / 0.67 | -0.057 / 0.79 | -0.083 [-0.101, -0.066] | -0.159 |
| QS5_BURST5_H5 (fast 5-minute bar, hold 5 min) | 1.9 | -0.209 / 0.52 | -0.119 / 0.66 | -0.082 / 0.74 | -0.100 [-0.138, -0.064] | -0.172 |
| QS5_BURST5_H15 (hold 15 min) | 1.8 | -0.167 / 0.70 | -0.087 / 0.82 | -0.120 / 0.75 | -0.104 [-0.159, -0.047] | -0.173 |
| QS5_TREND_PB_H5 (trend + pullback, hold 5 min) | 5.8 | -0.191 / 0.34 | -0.115 / 0.47 | -0.039 / 0.76 | -0.077 [-0.088, -0.066] | -0.153 |

All five lose in every period. By calendar year the trend variants make between -0.04 and +0.02 R before costs and lose
0.3 to 0.5 USD per ounce per trade after costs, in every year from 2021 to 2026: there is nothing in the signal, and the
spread is paid each time. The stop (1 x ATR14 of the 15-minute chart) grew from about 1.7 USD in 2021 to about 8.4 USD
in 2026, so the cost in R fell from 0.21 to 0.04 per trade, and the result is still negative.

## 4. Quick exits on the improved breakout (exploratory, same engine as HL_C_W01)

| forced exit after | held-out trades | mean R | PF | total R | development mean R |
|---|---|---|---|---|---|
| none (20:50 only) | 666 | +0.141 | 1.37 | +94.1 | +0.006 |
| 15 minutes | 1,060 | +0.001 | 1.01 | +1.0 | -0.034 |
| 30 minutes | 1,059 | +0.001 | 1.01 | +1.5 | -0.037 |
| 60 minutes | 1,052 | +0.002 | 1.01 | +2.5 | -0.044 |
| 2 hours | 1,035 | +0.036 | 1.18 | +37.4 | -0.017 |
| 4 hours | 962 | +0.062 | 1.25 | +59.5 | -0.019 |

With costs doubled the 15- and 60-minute versions are negative (-0.015 and -0.017 R). In the uncapped version the 348
held-out trades that lasted more than eight hours made +83.3 R of the +94.1 R; the 32 trades that ended within an hour
lost 14.7 R. The breakout earns by being held through the day.

## 4b. Taking profit sooner on the improved breakout (v7b addendum, frozen before running)

Same breakout as HL_C_W01, only the profit target changes. Held-out period (2024-07 to 2026-10) unless stated.

| target | trades | win rate | mean R [90 % CI] | PF validation / final test | total R | median time in a trade | trades over within 1 hour | development mean R / drawdown | held-out mean R, costs doubled |
|---|---|---|---|---|---|---|---|---|---|
| 1.5 R (HL_C_W01) | 666 | 50 % | +0.141 [+0.076, +0.206] | 1.35 / 1.39 | +94.1 | 8.2 hours | 5 % | +0.006 / -26.7 R | +0.123 |
| 1.0 R | 697 | 54 % | +0.104 [+0.051, +0.159] | 1.28 / 1.31 | +72.6 | 6.7 hours | 10 % | +0.001 / -28.0 R | +0.084 |
| 0.75 R | 730 | 58 % | +0.066 [+0.019, +0.113] | 1.15 / 1.26 | +48.5 | 5.5 hours | 14 % | -0.019 / -33.3 R | +0.051 |
| 0.5 R | 777 | 65 % | +0.031 [-0.007, +0.068] | 1.09 / 1.13 | +23.8 | 3.6 hours | 22 % | -0.026 / -42.6 R | +0.011 |

Each step down in the target raises the win rate and lowers the profit. At 0.5 R the held-out result is no longer
distinguishable from zero and the development period loses; the typical trade still lasts three and a half hours,
because the stop sits at the opposite swing level and losing trades take a median of six hours to resolve. In the 1.5 R
version 252 of the 666 held-out trades (38 %) end at the 20:50 flat, 179 at the target and 219 at the stop: the rule is,
in effect, "enter on the break and hold for the rest of the day". No smaller target passes the strict rule (development
mean R is zero or negative for all of them, as for HL_C_W01 itself). The 1.5 R target stays.

## 5. Verdict and what it means

Rejected. On this data there is no version of "enter fast in the direction of the move and leave within minutes" that
makes money on gold: fast moves do not continue over the next minutes, and each round trip costs 0.35 USD in the research
model and 0.55 to 0.65 USD at the spread FOREX.com showed off-peak on 2026-11-12/13. The earlier checks agree: v2.2 with a
15-minute cap kept a fifth of its edge (results/HOLD_CAP_v22.md); 5-minute and 1-minute entries on M15 levels lose
(VALIDATION_REPORT_v5.md §11); the 15-minute twins of round 3 and FIXT_US_15M lose.

## 7. The Pine script (pine/gold_quick.pine, built 2026-11-13 because Aayan asked for it)

Purpose: let him see the idea on his own chart. It is not a recommendation. The banner on the chart states the tested
result for the selected setting ("SIX-YEAR TEST OF THIS SETTING: LOSES 0.08 R PER TRADE ..."), the default risk is
0.10 %, and the header says demo and Strategy Tester only. It runs on a 1-minute or a 5-minute chart, with the three
signal types of this report, exits after 5 / 10 / 15 / 30 minutes, the news blackout and the account guard.

Check of the port (backtest/verify_v7_pine_port.py): the script's signal expressions, rewritten operation by operation
with pandas on chart bars built from the M1 data, give exactly the engine's signals and stop distances over the six
years: 59,940 (trend breakout, 1-minute), 9,959 / 4,744 / 5,304 (fast move, with trend, 15-minute window), 15,591
(pullback, 5-minute), and for the 5-minute forms 23,092 / 3,827. Not checked: the Pine code has not been compiled here
(no TradingView in this environment), and order handling was reviewed by reading only.

Known differences from the engine: costs are a 0.20 USD commission per ounce per fill (0.40 per round trip) instead of
spread 0.25 plus slippage 0.05 per fill; a short's stop is checked on the chart's bid high without the spread; stops are
checked on the chart's bars instead of one-minute bars when the chart is 5-minute; the news blackout and the account
guard remove a few trades; the rule that an entry must open within two minutes of the signal is not coded.

## 6. Caveats and files

Looks ten to eighteen at the same data; bid-only data with a constant modelled spread; one-minute bars (no tick data, so the order of
prices inside a minute is unknown; stops are checked conservatively); no news gate.
Files: backtest/engine_v7_quick.py, backtest/verify_v7_pine_port.py, pine/gold_quick.pine, results/PREREGISTRATION_v7_quick.md
(with the v7b and v7c addenda), results/V7_QS5_*/, results/V7_QS_*/ (and
*_stress/), results/V5_HL_C_W01_T05, _T075, _T10 (and *_stress/), results/V5_HL_C_W01_stress, results/summary_v7.md.
