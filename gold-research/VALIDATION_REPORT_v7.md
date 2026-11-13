# VALIDATION REPORT v7 — "quick in, quick out" in the direction of the move, 2026-11-13

Status: **REJECTED. All eight variants lose in every period, before and after the cost stress.** Written by the main
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

## 5. Verdict and what it means

Rejected. On this data there is no version of "enter fast in the direction of the move and leave within minutes" that
makes money on gold: fast moves do not continue over the next minutes, and each round trip costs 0.35 USD in the research
model and 0.55 to 0.65 USD at the spread FOREX.com showed off-peak on 2026-11-12/13. The earlier checks agree: v2.2 with a
15-minute cap kept a fifth of its edge (results/HOLD_CAP_v22.md); 5-minute and 1-minute entries on M15 levels lose
(VALIDATION_REPORT_v5.md §11); the 15-minute twins of round 3 and FIXT_US_15M lose. No Pine script was built for it.

## 6. Caveats and files

Tenth look at the same data; bid-only data with a constant modelled spread; one-minute bars (no tick data, so the order of
prices inside a minute is unknown; stops are checked conservatively); no news gate.
Files: backtest/engine_v7_quick.py, results/PREREGISTRATION_v7_quick.md, results/V7_QS_*/ (and *_stress/),
results/summary_v7.md.
