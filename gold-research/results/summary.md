# Backtest results — GOLD_PLAYBOOK v1.0 (all pre-registered variants)

R = planned risk from the entry stop level to the initial stop-loss. Realised R includes spread, slippage and commission per the variant's cost model.
**Pre-registered verdict for V0_base: INCONCLUSIVE** (criteria in GOLD_PLAYBOOK_v1.md §13).


## V0_base

Config differences from base: `{}`; ambiguous stop/target M1 bars: 0

| period | dates | trades | total R | mean R (expectancy) | 90% bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| development | 2021-01-04 → 2024-07-01 | 254 | -21.1 | -0.083 | [-0.213, +0.048] | 37.8% | +1.47 / -1.03 | 0.87 | -36.5 | 8 | 49 |
| validation | 2024-07-01 → 2025-09-01 | 107 | +22.2 | +0.208 | [+0.001, +0.422] | 48.6% | +1.51 / -1.03 | 1.39 | -11.0 | 6 | 52 |
| final_test | 2025-09-01 → 2026-11-01 | 116 | -5.4 | -0.046 | [-0.253, +0.165] | 36.2% | +1.65 / -1.01 | 0.93 | -22.7 | 8 | 60 |
| validation+final_test | 2024-07-01 → 2026-11-01 | 223 | +16.9 | +0.076 | [-0.070, +0.227] | 42.2% | +1.58 / -1.02 | 1.13 | -22.7 | 8 | 56 |
| all (for reference only) | 2021-01-04 → 2026-11-01 | 477 | -4.2 | -0.009 | [-0.106, +0.093] | 39.8% | +1.52 / -1.02 | 0.99 | -38.7 | 8 | 52 |

### V0 breakdowns (validation + final test combined, out-of-sample)

**By session**

| session | trades | total R | mean R (expectancy) | 90% bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| London | 146 | -10.2 | -0.070 | [-0.246, +0.113] | 35.6% | +1.64 / -1.02 | 0.89 | -24.8 | 6 | 64 |
| NewYork | 77 | +27.1 | +0.351 | [+0.107, +0.605] | 54.5% | +1.49 / -1.02 | 1.76 | -7.1 | 6 | 31 |

**By side**

| side | trades | total R | mean R (expectancy) | 90% bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 93 | +11.1 | +0.120 | [-0.092, +0.334] | 47.3% | +1.39 / -1.02 | 1.22 | -10.9 | 7 | 47 |
| short | 130 | +5.7 | +0.044 | [-0.159, +0.250] | 38.5% | +1.74 / -1.01 | 1.07 | -17.7 | 10 | 59 |

**By year**

| year | trades | total R | mean R (expectancy) | 90% bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | 46 | +9.0 | +0.196 | [-0.096, +0.491] | 52.2% | +1.32 / -1.03 | 1.40 | -5.8 | 4 | 48 |
| 2025 | 93 | +11.3 | +0.122 | [-0.108, +0.355] | 43.0% | +1.63 / -1.02 | 1.21 | -9.2 | 6 | 58 |
| 2026 | 84 | -3.5 | -0.041 | [-0.281, +0.220] | 35.7% | +1.70 / -1.01 | 0.94 | -22.7 | 8 | 58 |

**By exit_reason**

| exit_reason | trades | total R | mean R (expectancy) | 90% bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| stop | 129 | -131.2 | -1.017 | [-1.019, -1.015] | 0.0% | +0.00 / -1.02 | 0.00 | -130.1 | 129 | 50 |
| target | 90 | +146.2 | +1.625 | [+1.519, +1.733] | 100.0% | +1.62 / +0.00 | inf | 0.0 | 0 | 60 |
| time_exit | 4 | +1.8 | +0.456 | [+nan, +nan] | 100.0% | +0.46 / +0.00 | inf | 0.0 | 0 | 379 |

**By year (all periods, for reference)**

| year | trades | total R | mean R (expectancy) | 90% bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| 2021 | 68 | +10.4 | +0.152 | [-0.091, +0.409] | 47.1% | +1.44 / -0.99 | 1.29 | -6.1 | 5 | 50 |
| 2022 | 81 | -4.4 | -0.054 | [-0.287, +0.178] | 38.3% | +1.50 / -1.02 | 0.91 | -8.9 | 6 | 47 |
| 2023 | 62 | -9.2 | -0.149 | [-0.423, +0.139] | 35.5% | +1.54 / -1.08 | 0.79 | -11.2 | 6 | 45 |
| 2024 | 89 | -8.8 | -0.099 | [-0.303, +0.113] | 39.3% | +1.32 / -1.02 | 0.84 | -18.9 | 6 | 52 |
| 2025 | 93 | +11.3 | +0.122 | [-0.106, +0.355] | 43.0% | +1.63 / -1.02 | 1.21 | -9.2 | 6 | 58 |
| 2026 | 84 | -3.5 | -0.041 | [-0.283, +0.221] | 35.7% | +1.70 / -1.01 | 0.94 | -22.7 | 8 | 58 |

**Top-5 dependence (validation + final test)**

- Total R: +16.9; R from the 5 best trades: +16.3; mean R excluding the 5 best: +0.002

**Exposure and holding (out-of-sample)**

- Share of session hours with an open position: 3.8%; median hold 56 min; mean hold 87 min

**Skipped / cancelled setups (all periods)**

| reason | count |
|---|---|
| WAIT_rr_too_low | 1177 |
| CANCEL_deep_break | 221 |
| CANCEL_cutoff_time | 30 |
| WAIT_daily_cap | 6 |
| CANCEL_rr_too_low_after_rearm | 4 |
| EXPIRED_unfilled | 4 |
| CANCEL_adx_fell | 3 |

## V1_cost_stress

Config differences from base: `{"spread": 0.5, "slippage": 0.15}`; ambiguous stop/target M1 bars: 0

| period | dates | trades | total R | mean R (expectancy) | 90% bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| development | 2021-01-04 → 2024-07-01 | 264 | -69.1 | -0.262 | [-0.388, -0.135] | 33.7% | +1.41 / -1.11 | 0.64 | -73.2 | 8 | 44 |
| validation | 2024-07-01 → 2025-09-01 | 111 | +8.8 | +0.079 | [-0.126, +0.281] | 45.9% | +1.44 / -1.08 | 1.14 | -19.3 | 8 | 47 |
| final_test | 2025-09-01 → 2026-11-01 | 119 | -13.4 | -0.112 | [-0.309, +0.094] | 34.5% | +1.64 / -1.03 | 0.83 | -25.6 | 8 | 55 |
| validation+final_test | 2024-07-01 → 2026-11-01 | 230 | -4.6 | -0.020 | [-0.164, +0.127] | 40.0% | +1.53 / -1.05 | 0.97 | -26.9 | 8 | 50 |
| all (for reference only) | 2021-01-04 → 2026-11-01 | 494 | -73.6 | -0.149 | [-0.243, -0.051] | 36.6% | +1.47 / -1.09 | 0.78 | -90.2 | 8 | 47 |

## V2_raw_account

Config differences from base: `{"spread": 0.1, "slippage": 0.05, "commission_rt": 0.07}`; ambiguous stop/target M1 bars: 0

| period | dates | trades | total R | mean R (expectancy) | 90% bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| development | 2021-01-04 → 2024-07-01 | 245 | -15.0 | -0.061 | [-0.197, +0.076] | 39.6% | +1.45 / -1.05 | 0.90 | -30.3 | 7 | 50 |
| validation | 2024-07-01 → 2025-09-01 | 105 | +26.5 | +0.252 | [+0.036, +0.467] | 50.5% | +1.52 / -1.04 | 1.49 | -10.4 | 5 | 53 |
| final_test | 2025-09-01 → 2026-11-01 | 115 | -5.1 | -0.045 | [-0.249, +0.167] | 36.5% | +1.65 / -1.02 | 0.93 | -23.0 | 8 | 63 |
| validation+final_test | 2024-07-01 → 2026-11-01 | 220 | +21.3 | +0.097 | [-0.051, +0.251] | 43.2% | +1.58 / -1.03 | 1.17 | -23.0 | 8 | 58 |
| all (for reference only) | 2021-01-04 → 2026-11-01 | 465 | +6.3 | +0.014 | [-0.086, +0.115] | 41.3% | +1.51 / -1.04 | 1.02 | -31.6 | 8 | 54 |

## V3_adx25

Config differences from base: `{"adx_threshold": 25.0, "adx_cancel_below": 20.0}`; ambiguous stop/target M1 bars: 0

| period | dates | trades | total R | mean R (expectancy) | 90% bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| development | 2021-01-04 → 2024-07-01 | 458 | -28.3 | -0.062 | [-0.161, +0.037] | 38.4% | +1.47 / -1.02 | 0.90 | -42.1 | 9 | 52 |
| validation | 2024-07-01 → 2025-09-01 | 191 | -2.8 | -0.014 | [-0.168, +0.143] | 39.3% | +1.54 / -1.02 | 0.98 | -18.1 | 6 | 44 |
| final_test | 2025-09-01 → 2026-11-01 | 202 | -8.4 | -0.041 | [-0.190, +0.116] | 37.1% | +1.60 / -1.01 | 0.93 | -34.4 | 12 | 50 |
| validation+final_test | 2024-07-01 → 2026-11-01 | 393 | -11.1 | -0.028 | [-0.136, +0.083] | 38.2% | +1.57 / -1.02 | 0.95 | -34.4 | 12 | 45 |
| all (for reference only) | 2021-01-04 → 2026-11-01 | 851 | -39.5 | -0.046 | [-0.118, +0.027] | 38.3% | +1.52 / -1.02 | 0.93 | -74.1 | 12 | 49 |

## V4_adx35

Config differences from base: `{"adx_threshold": 35.0, "adx_cancel_below": 30.0}`; ambiguous stop/target M1 bars: 0

| period | dates | trades | total R | mean R (expectancy) | 90% bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| development | 2021-01-04 → 2024-07-01 | 139 | +0.1 | +0.000 | [-0.176, +0.176] | 40.3% | +1.48 / -1.00 | 1.00 | -10.9 | 10 | 54 |
| validation | 2024-07-01 → 2025-09-01 | 63 | +15.7 | +0.250 | [-0.023, +0.526] | 49.2% | +1.56 / -1.02 | 1.48 | -7.2 | 7 | 54 |
| final_test | 2025-09-01 → 2026-11-01 | 65 | -14.8 | -0.228 | [-0.495, +0.062] | 27.7% | +1.81 / -1.01 | 0.69 | -28.0 | 10 | 55 |
| validation+final_test | 2024-07-01 → 2026-11-01 | 128 | +0.9 | +0.007 | [-0.185, +0.201] | 38.3% | +1.65 / -1.02 | 1.01 | -28.3 | 10 | 54 |
| all (for reference only) | 2021-01-04 → 2026-11-01 | 267 | +0.9 | +0.004 | [-0.126, +0.134] | 39.3% | +1.56 / -1.01 | 1.01 | -28.3 | 10 | 54 |

## V5_london_only

Config differences from base: `{"signal_start": "07:00", "signal_end": "11:45", "pending_cutoff": "12:00"}`; ambiguous stop/target M1 bars: 0

| period | dates | trades | total R | mean R (expectancy) | 90% bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| development | 2021-01-04 → 2024-07-01 | 140 | +1.2 | +0.008 | [-0.179, +0.198] | 40.0% | +1.60 / -1.05 | 1.01 | -16.1 | 8 | 56 |
| validation | 2024-07-01 → 2025-09-01 | 67 | +8.4 | +0.125 | [-0.139, +0.390] | 44.8% | +1.55 / -1.03 | 1.22 | -7.6 | 4 | 61 |
| final_test | 2025-09-01 → 2026-11-01 | 69 | -27.5 | -0.398 | [-0.616, -0.169] | 23.2% | +1.63 / -1.01 | 0.49 | -31.6 | 11 | 70 |
| validation+final_test | 2024-07-01 → 2026-11-01 | 136 | -19.1 | -0.140 | [-0.312, +0.041] | 33.8% | +1.58 / -1.02 | 0.79 | -31.6 | 11 | 66 |
| all (for reference only) | 2021-01-04 → 2026-11-01 | 276 | -17.9 | -0.065 | [-0.196, +0.066] | 37.0% | +1.59 / -1.03 | 0.90 | -37.2 | 11 | 61 |

## V6_newyork_only

Config differences from base: `{"signal_start": "12:00", "signal_end": "15:45", "pending_cutoff": "16:00"}`; ambiguous stop/target M1 bars: 0

| period | dates | trades | total R | mean R (expectancy) | 90% bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| development | 2021-01-04 → 2024-07-01 | 112 | -24.6 | -0.220 | [-0.384, -0.044] | 34.8% | +1.23 / -0.99 | 0.66 | -29.6 | 10 | 36 |
| validation | 2024-07-01 → 2025-09-01 | 39 | +17.6 | +0.450 | [+0.101, +0.797] | 59.0% | +1.47 / -1.02 | 2.07 | -6.1 | 6 | 30 |
| final_test | 2025-09-01 → 2026-11-01 | 48 | +25.5 | +0.530 | [+0.157, +0.900] | 56.2% | +1.73 / -1.01 | 2.20 | -5.6 | 3 | 50 |
| validation+final_test | 2024-07-01 → 2026-11-01 | 87 | +43.0 | +0.494 | [+0.248, +0.749] | 57.5% | +1.61 / -1.02 | 2.14 | -6.1 | 6 | 42 |
| all (for reference only) | 2021-01-04 → 2026-11-01 | 199 | +18.4 | +0.093 | [-0.060, +0.246] | 44.7% | +1.44 / -1.00 | 1.17 | -32.3 | 10 | 36 |

## V7_min_rr_1_5

Config differences from base: `{"min_rr": 1.5}`; ambiguous stop/target M1 bars: 0

| period | dates | trades | total R | mean R (expectancy) | 90% bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| development | 2021-01-04 → 2024-07-01 | 158 | -9.3 | -0.059 | [-0.239, +0.128] | 33.5% | +1.86 / -1.03 | 0.91 | -20.7 | 11 | 48 |
| validation | 2024-07-01 → 2025-09-01 | 60 | +16.5 | +0.275 | [-0.049, +0.589] | 43.3% | +1.98 / -1.03 | 1.47 | -7.8 | 7 | 56 |
| final_test | 2025-09-01 → 2026-11-01 | 89 | +0.1 | +0.002 | [-0.257, +0.268] | 33.7% | +1.99 / -1.01 | 1.00 | -17.4 | 6 | 64 |
| validation+final_test | 2024-07-01 → 2026-11-01 | 149 | +16.6 | +0.112 | [-0.090, +0.316] | 37.6% | +1.99 / -1.02 | 1.18 | -17.4 | 7 | 62 |
| all (for reference only) | 2021-01-04 → 2026-11-01 | 307 | +7.3 | +0.024 | [-0.115, +0.163] | 35.5% | +1.93 / -1.02 | 1.04 | -27.4 | 11 | 57 |

## V8_no_rearm

Config differences from base: `{"rearm": false}`; ambiguous stop/target M1 bars: 0

| period | dates | trades | total R | mean R (expectancy) | 90% bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| development | 2021-01-04 → 2024-07-01 | 241 | -18.8 | -0.078 | [-0.207, +0.053] | 39.0% | +1.39 / -1.02 | 0.87 | -29.7 | 6 | 48 |
| validation | 2024-07-01 → 2025-09-01 | 107 | +19.3 | +0.181 | [-0.021, +0.380] | 49.5% | +1.41 / -1.02 | 1.35 | -12.7 | 6 | 46 |
| final_test | 2025-09-01 → 2026-11-01 | 105 | -3.5 | -0.033 | [-0.232, +0.174] | 40.0% | +1.43 / -1.01 | 0.95 | -20.4 | 7 | 64 |
| validation+final_test | 2024-07-01 → 2026-11-01 | 212 | +15.8 | +0.075 | [-0.067, +0.216] | 44.8% | +1.42 / -1.02 | 1.13 | -20.4 | 7 | 54 |
| all (for reference only) | 2021-01-04 → 2026-11-01 | 453 | -2.9 | -0.006 | [-0.104, +0.091] | 41.7% | +1.41 / -1.02 | 0.99 | -31.9 | 7 | 51 |

## V9_target_first

Config differences from base: `{"ambiguity": "target_first"}`; ambiguous stop/target M1 bars: 0

| period | dates | trades | total R | mean R (expectancy) | 90% bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| development | 2021-01-04 → 2024-07-01 | 254 | -21.1 | -0.083 | [-0.214, +0.051] | 37.8% | +1.47 / -1.03 | 0.87 | -36.5 | 8 | 49 |
| validation | 2024-07-01 → 2025-09-01 | 107 | +22.2 | +0.208 | [-0.003, +0.415] | 48.6% | +1.51 / -1.03 | 1.39 | -11.0 | 6 | 52 |
| final_test | 2025-09-01 → 2026-11-01 | 116 | -5.4 | -0.046 | [-0.253, +0.163] | 36.2% | +1.65 / -1.01 | 0.93 | -22.7 | 8 | 60 |
| validation+final_test | 2024-07-01 → 2026-11-01 | 223 | +16.9 | +0.076 | [-0.071, +0.226] | 42.2% | +1.58 / -1.02 | 1.13 | -22.7 | 8 | 56 |
| all (for reference only) | 2021-01-04 → 2026-11-01 | 477 | -4.2 | -0.009 | [-0.108, +0.094] | 39.8% | +1.52 / -1.02 | 0.99 | -38.7 | 8 | 52 |

## V10_news_approx

Config differences from base: `{"news_filter": "approx"}`; ambiguous stop/target M1 bars: 0

| period | dates | trades | total R | mean R (expectancy) | 90% bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| development | 2021-01-04 → 2024-07-01 | 254 | -21.1 | -0.083 | [-0.212, +0.048] | 37.8% | +1.47 / -1.03 | 0.87 | -36.5 | 8 | 48 |
| validation | 2024-07-01 → 2025-09-01 | 107 | +22.2 | +0.208 | [-0.001, +0.417] | 48.6% | +1.51 / -1.03 | 1.39 | -11.0 | 6 | 52 |
| final_test | 2025-09-01 → 2026-11-01 | 116 | -5.4 | -0.046 | [-0.253, +0.163] | 36.2% | +1.65 / -1.01 | 0.93 | -22.7 | 8 | 60 |
| validation+final_test | 2024-07-01 → 2026-11-01 | 223 | +16.9 | +0.076 | [-0.073, +0.222] | 42.2% | +1.58 / -1.02 | 1.13 | -22.7 | 8 | 56 |
| all (for reference only) | 2021-01-04 → 2026-11-01 | 477 | -4.2 | -0.009 | [-0.109, +0.090] | 39.8% | +1.52 / -1.02 | 0.99 | -38.7 | 8 | 51 |
