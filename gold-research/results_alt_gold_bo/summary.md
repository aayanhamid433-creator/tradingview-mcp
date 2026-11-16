# ALT candidate results — Gold Breakout 15M (WillyAlgoTrader) re-implemented on HistData M1 2021–2026 (clock-corrected: index converted from New York local stamps to true UTC)

R = planned risk = 1% of the breakout level (SL 1% of entry). Costs per variant. Periods identical to GOLD_PLAYBOOK v1.0 §13. NOT a pre-registered test of our own: this candidate was selected after seeing the author's published result, so treat every number as descriptive.

## G0_author_like

`{"clock": "fixed_gmt3", "sl_mode": "pct", "spread": 0.0, "slippage": 0.0, "commission_frac_rt": 8e-05, "both_sides_rule": "nearer_open"}`; minutes crossing both boundaries: 1

| window | dates | trades | total R | mean R | 90% bootstrap CI | win rate | profit factor | max DD (R) | longest losing streak | compounded at 1% risk |
|---|---|---|---|---|---|---|---|---|---|---|
| development | 2021-01-04 → 2024-07-01 | 891 | +28.8 | +0.032 | [-0.005, +0.071] | 48.3% | 1.13 | -9.8 | 9 | +30.6% |
| validation | 2024-07-01 → 2025-09-01 | 298 | +24.9 | +0.084 | [+0.018, +0.149] | 54.4% | 1.35 | -7.4 | 8 | +27.4% |
| final_test | 2025-09-01 → 2026-11-01 | 288 | +40.3 | +0.140 | [+0.042, +0.236] | 54.9% | 1.44 | -13.2 | 11 | +47.5% |
| screenshot_window_2026-08-02_to_2026-10-30 | 2026-08-02 → 2026-10-31 | 63 | +13.5 | +0.214 | [+0.023, +0.420] | 61.9% | 1.82 | -3.6 | 5 | +14.1% |
| all_2021-2026 | 2021-01-04 → 2026-11-01 | 1477 | +94.1 | +0.064 | [+0.031, +0.096] | 50.8% | 1.24 | -13.2 | 11 | +145.4% |

## G1_base_costs

`{"clock": "fixed_gmt3", "sl_mode": "pct", "spread": 0.25, "slippage": 0.05, "commission_frac_rt": 0.0, "both_sides_rule": "nearer_open"}`; minutes crossing both boundaries: 1

| window | dates | trades | total R | mean R | 90% bootstrap CI | win rate | profit factor | max DD (R) | longest losing streak | compounded at 1% risk |
|---|---|---|---|---|---|---|---|---|---|---|
| development | 2021-01-04 → 2024-07-01 | 893 | +12.4 | +0.014 | [-0.025, +0.052] | 47.0% | 1.05 | -18.5 | 9 | +10.9% |
| validation | 2024-07-01 → 2025-09-01 | 298 | +23.1 | +0.077 | [+0.011, +0.143] | 54.0% | 1.32 | -7.3 | 8 | +25.0% |
| final_test | 2025-09-01 → 2026-11-01 | 288 | +39.3 | +0.136 | [+0.042, +0.234] | 54.5% | 1.43 | -13.1 | 11 | +46.0% |
| screenshot_window_2026-08-02_to_2026-10-30 | 2026-08-02 → 2026-10-31 | 63 | +13.7 | +0.218 | [+0.022, +0.418] | 61.9% | 1.84 | -3.5 | 5 | +14.4% |
| all_2021-2026 | 2021-01-04 → 2026-11-01 | 1479 | +74.8 | +0.051 | [+0.017, +0.083] | 49.9% | 1.19 | -18.5 | 11 | +102.3% |

### G1 breakdowns

**By year**

| year | trades | total R | mean R | 90% bootstrap CI | win rate | profit factor | max DD (R) | longest losing streak | compounded at 1% risk |
|---|---|---|---|---|---|---|---|---|---|
| 2021 | 254 | +14.3 | +0.056 | [-0.015, +0.128] | 45.7% | 1.24 | -6.3 | 7 | +14.7% |
| 2022 | 256 | -4.1 | -0.016 | [-0.089, +0.059] | 48.0% | 0.94 | -16.5 | 6 | -4.7% |
| 2023 | 256 | -2.0 | -0.008 | [-0.075, +0.061] | 45.3% | 0.97 | -11.3 | 9 | -2.5% |
| 2024 | 258 | +13.3 | +0.052 | [-0.020, +0.122] | 53.9% | 1.20 | -5.9 | 8 | +13.5% |
| 2025 | 253 | +16.4 | +0.065 | [-0.017, +0.148] | 50.2% | 1.24 | -13.1 | 11 | +16.8% |
| 2026 | 202 | +36.9 | +0.183 | [+0.066, +0.301] | 57.9% | 1.58 | -7.0 | 5 | +43.1% |

**By side (all years)**

| side | trades | total R | mean R | 90% bootstrap CI | win rate | profit factor | max DD (R) | longest losing streak | compounded at 1% risk |
|---|---|---|---|---|---|---|---|---|---|
| long | 796 | +43.8 | +0.055 | [+0.014, +0.096] | 50.6% | 1.22 | -14.3 | 12 | +51.8% |
| short | 683 | +31.0 | +0.045 | [-0.007, +0.099] | 49.0% | 1.16 | -12.5 | 9 | +33.3% |

**By exit reason (all years)**

| exit | trades | total R | mean R | 90% bootstrap CI | win rate | profit factor | max DD (R) | longest losing streak | compounded at 1% risk |
|---|---|---|---|---|---|---|---|---|---|
| stop | 218 | -219.6 | -1.007 | [-1.016, -1.002] | 0.0% | 0.00 | -218.6 | 218 | -89.0% |
| time_exit | 1261 | +294.4 | +0.233 | [+0.202, +0.265] | 58.5% | 2.66 | -4.4 | 9 | +1739.8% |

**Top-5 dependence (2024-07 → 2026-10):** total +62.4 R, best 5 trades +18.9 R, mean R excluding best 5 +0.075

## G2_cost_stress

`{"clock": "fixed_gmt3", "sl_mode": "pct", "spread": 0.5, "slippage": 0.15, "commission_frac_rt": 0.0, "both_sides_rule": "nearer_open"}`; minutes crossing both boundaries: 1

| window | dates | trades | total R | mean R | 90% bootstrap CI | win rate | profit factor | max DD (R) | longest losing streak | compounded at 1% risk |
|---|---|---|---|---|---|---|---|---|---|---|
| development | 2021-01-04 → 2024-07-01 | 893 | -6.7 | -0.007 | [-0.045, +0.031] | 46.1% | 0.97 | -30.2 | 14 | -8.4% |
| validation | 2024-07-01 → 2025-09-01 | 298 | +19.5 | +0.066 | [+0.000, +0.130] | 54.0% | 1.26 | -8.4 | 8 | +20.7% |
| final_test | 2025-09-01 → 2026-11-01 | 288 | +38.1 | +0.132 | [+0.036, +0.232] | 54.2% | 1.42 | -13.3 | 11 | +44.2% |
| screenshot_window_2026-08-02_to_2026-10-30 | 2026-08-02 → 2026-10-31 | 63 | +13.3 | +0.211 | [+0.016, +0.407] | 60.3% | 1.80 | -3.6 | 5 | +13.9% |
| all_2021-2026 | 2021-01-04 → 2026-11-01 | 1479 | +51.0 | +0.034 | [+0.001, +0.067] | 49.3% | 1.12 | -30.2 | 14 | +59.4% |

## G3_ny7_clock

`{"clock": "ny_plus_7", "sl_mode": "pct", "spread": 0.25, "slippage": 0.05, "commission_frac_rt": 0.0, "both_sides_rule": "nearer_open"}`; minutes crossing both boundaries: 1

| window | dates | trades | total R | mean R | 90% bootstrap CI | win rate | profit factor | max DD (R) | longest losing streak | compounded at 1% risk |
|---|---|---|---|---|---|---|---|---|---|---|
| development | 2021-01-04 → 2024-07-01 | 893 | +20.6 | +0.023 | [-0.015, +0.062] | 48.3% | 1.09 | -16.5 | 9 | +20.2% |
| validation | 2024-07-01 → 2025-09-01 | 298 | +20.9 | +0.070 | [+0.004, +0.136] | 53.7% | 1.29 | -7.3 | 8 | +22.3% |
| final_test | 2025-09-01 → 2026-11-01 | 288 | +44.5 | +0.154 | [+0.056, +0.257] | 55.2% | 1.49 | -12.2 | 10 | +53.5% |
| screenshot_window_2026-08-02_to_2026-10-30 | 2026-08-02 → 2026-10-31 | 63 | +13.7 | +0.218 | [+0.024, +0.416] | 61.9% | 1.84 | -3.5 | 5 | +14.4% |
| all_2021-2026 | 2021-01-04 → 2026-11-01 | 1479 | +85.9 | +0.058 | [+0.025, +0.091] | 50.7% | 1.22 | -16.5 | 10 | +125.6% |

## G4_sl_range_boundary

`{"clock": "fixed_gmt3", "sl_mode": "range", "spread": 0.25, "slippage": 0.05, "commission_frac_rt": 0.0, "both_sides_rule": "nearer_open"}`; minutes crossing both boundaries: 1

| window | dates | trades | total R | mean R | 90% bootstrap CI | win rate | profit factor | max DD (R) | longest losing streak | compounded at 1% risk |
|---|---|---|---|---|---|---|---|---|---|---|
| development | 2021-01-04 → 2024-07-01 | 894 | -0.3 | -0.000 | [-0.082, +0.083] | 36.4% | 1.00 | -47.0 | 17 | -9.8% |
| validation | 2024-07-01 → 2025-09-01 | 298 | +29.2 | +0.098 | [-0.020, +0.217] | 47.0% | 1.23 | -10.8 | 10 | +30.9% |
| final_test | 2025-09-01 → 2026-11-01 | 288 | +35.2 | +0.122 | [+0.027, +0.220] | 54.5% | 1.38 | -16.4 | 11 | +40.1% |
| screenshot_window_2026-08-02_to_2026-10-30 | 2026-08-02 → 2026-10-31 | 63 | +11.9 | +0.188 | [-0.016, +0.403] | 58.7% | 1.64 | -5.4 | 5 | +12.2% |
| all_2021-2026 | 2021-01-04 → 2026-11-01 | 1480 | +64.1 | +0.043 | [-0.015, +0.102] | 42.0% | 1.09 | -47.0 | 17 | +65.5% |

## G5_both_sides_adverse

`{"clock": "fixed_gmt3", "sl_mode": "pct", "spread": 0.25, "slippage": 0.05, "commission_frac_rt": 0.0, "both_sides_rule": "adverse"}`; minutes crossing both boundaries: 1

| window | dates | trades | total R | mean R | 90% bootstrap CI | win rate | profit factor | max DD (R) | longest losing streak | compounded at 1% risk |
|---|---|---|---|---|---|---|---|---|---|---|
| development | 2021-01-04 → 2024-07-01 | 893 | +12.6 | +0.014 | [-0.024, +0.052] | 47.0% | 1.05 | -18.5 | 9 | +11.0% |
| validation | 2024-07-01 → 2025-09-01 | 298 | +23.1 | +0.077 | [+0.011, +0.145] | 54.0% | 1.32 | -7.3 | 8 | +25.0% |
| final_test | 2025-09-01 → 2026-11-01 | 288 | +39.3 | +0.136 | [+0.039, +0.234] | 54.5% | 1.43 | -13.1 | 11 | +46.0% |
| screenshot_window_2026-08-02_to_2026-10-30 | 2026-08-02 → 2026-10-31 | 63 | +13.7 | +0.218 | [+0.026, +0.422] | 61.9% | 1.84 | -3.5 | 5 | +14.4% |
| all_2021-2026 | 2021-01-04 → 2026-11-01 | 1479 | +75.0 | +0.051 | [+0.018, +0.083] | 49.9% | 1.19 | -18.5 | 11 | +102.7% |
