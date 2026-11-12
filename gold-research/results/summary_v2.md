# Backtest results — GOLD_PLAYBOOK v2.0 CANDIDATE (pre-registered variants) vs v1.0 baseline

R = initial planned risk. Weighted R = R × size_mult (0.5 when the momentum vote disagrees with the SMA200 trend state). Costs per variant config.

**Coverage note:** the bias layer needs 200 (SMA) / 252 (momentum) session days of warm-up, so biased variants trade from about 2022-01; their development-period rows cover 2022-01 → 2024-06 while V0_base and V2_A cover 2021-01 → 2024-06.
**Pre-registered verdict for V2_0: INCONCLUSIVE** (criteria: GOLD_PLAYBOOK_v2_CANDIDATE.md §11). Conditions: n_val_ge60=no, n_test_ge60=no, meanR_pos_both=yes, pf_gt_1_10_both=yes, ci_excludes_zero=no, ex_top5_pos=no, beats_v1_meanR=yes, beats_v1_pf=yes.

**Contamination disclosure:** the bias layer, min RR 1.5 and the exits were chosen after seeing v1.0's results on this same data; this run can reject layers but cannot support v2.0 (see playbook v2 §11).


## V0_base

| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 254 | -21.1 | -0.083 | -0.083 | [-0.213, +0.048] | 37.8% | 0.87 | -36.5 | 8 | 49 |
| validation 2024-07-01→2025-09-01 | 107 | +22.2 | +0.208 | +0.208 | [+0.001, +0.422] | 48.6% | 1.39 | -11.0 | 6 | 52 |
| final_test 2025-09-01→2026-11-01 | 116 | -5.4 | -0.046 | -0.046 | [-0.253, +0.165] | 36.2% | 0.93 | -22.7 | 8 | 60 |
| validation+final_test | 223 | +16.9 | +0.076 | +0.076 | [-0.070, +0.227] | 42.2% | 1.13 | -22.7 | 8 | 56 |
| all (reference) | 477 | -4.2 | -0.009 | -0.009 | [-0.106, +0.093] | 39.8% | 0.99 | -38.7 | 8 | 52 |

## V2_0

| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 55 | -14.1 | -0.256 | -0.181 | [-0.557, +0.087] | 25.5% | 0.63 | -18.4 | 7 | 59 |
| validation 2024-07-01→2025-09-01 | 23 | +17.3 | +0.752 | +0.752 | [-0.067, +1.689] | 47.8% | 2.40 | -4.4 | 4 | 115 |
| final_test 2025-09-01→2026-11-01 | 38 | +3.4 | +0.089 | +0.176 | [-0.177, +0.359] | 42.1% | 1.22 | -7.2 | 5 | 110 |
| validation+final_test | 61 | +20.7 | +0.339 | +0.393 | [-0.012, +0.731] | 44.3% | 1.74 | -7.2 | 5 | 115 |
| all (reference) | 116 | +6.6 | +0.057 | +0.121 | [-0.190, +0.325] | 35.3% | 1.10 | -21.9 | 7 | 76 |

### V2_0 breakdowns (validation + final test)

**By bias**

| bias | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 39 | +17.4 | +0.445 | +0.445 | [-0.080, +1.054] | 46.2% | 1.81 | -4.4 | 4 | 123 |
| short | 22 | +3.3 | +0.150 | +0.301 | [-0.143, +0.471] | 40.9% | 1.50 | -3.6 | 5 | 69 |

**By size_mult**

| size_mult | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 22 | +3.3 | +0.150 | +0.301 | [-0.143, +0.471] | 40.9% | 1.50 | -3.6 | 5 | 69 |
| 1.0 | 39 | +17.4 | +0.445 | +0.445 | [-0.080, +1.049] | 46.2% | 1.81 | -4.4 | 4 | 123 |

**By session**

| session | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| London | 35 | +2.3 | +0.065 | -0.033 | [-0.378, +0.600] | 31.4% | 1.12 | -9.0 | 8 | 64 |
| NewYork | 26 | +18.4 | +0.708 | +0.967 | [+0.190, +1.324] | 61.5% | 3.13 | -3.1 | 4 | 230 |

**By side**

| side | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 39 | +17.4 | +0.445 | +0.445 | [-0.080, +1.039] | 46.2% | 1.81 | -4.4 | 4 | 123 |
| short | 22 | +3.3 | +0.150 | +0.301 | [-0.142, +0.469] | 40.9% | 1.50 | -3.6 | 5 | 69 |

**By exit_reason**

| exit_reason | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| breakeven_stop | 3 | +2.6 | +0.853 | +0.853 | [+nan, +nan] | 100.0% | inf | 0.0 | 0 | 22 |
| stop | 34 | -28.0 | -0.825 | -1.018 | [-0.897, -0.750] | 0.0% | 0.00 | -27.0 | 34 | 44 |
| time_exit | 12 | +29.0 | +2.413 | +2.924 | [+1.300, +3.697] | 100.0% | inf | 0.0 | 0 | 378 |
| trail_stop | 12 | +17.2 | +1.433 | +1.747 | [+1.143, +1.746] | 100.0% | inf | 0.0 | 0 | 259 |

**By year**

| year | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | 11 | -3.2 | -0.292 | -0.292 | [-0.870, +0.404] | 27.3% | 0.61 | -4.1 | 4 | 45 |
| 2025 | 21 | +23.2 | +1.103 | +1.103 | [+0.278, +2.063] | 61.9% | 3.85 | -2.0 | 2 | 180 |
| 2026 | 29 | +0.7 | +0.025 | +0.139 | [-0.250, +0.321] | 37.9% | 1.06 | -6.7 | 5 | 76 |

**Skipped / cancelled setups (all periods)**

| reason | count |
|---|---|
| WAIT_bias_direction | 1336 |
| WAIT_rr_too_low | 762 |
| WAIT_bias_undefined | 468 |
| CANCEL_deep_break | 32 |
| WAIT_stop_too_wide | 12 |
| CANCEL_cutoff_time | 8 |
| WAIT_daily_or_weekly_stop | 7 |
| CANCEL_rr_too_low_after_rearm | 2 |
| WAIT_news_window | 1 |
| EXPIRED_unfilled | 1 |

## V2_A_nobias

| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 158 | +4.1 | +0.026 | +0.026 | [-0.206, +0.284] | 34.8% | 1.04 | -25.7 | 11 | 73 |
| validation 2024-07-01→2025-09-01 | 59 | +26.1 | +0.442 | +0.442 | [+0.003, +0.921] | 42.4% | 1.76 | -7.9 | 5 | 130 |
| final_test 2025-09-01→2026-11-01 | 99 | +2.1 | +0.022 | +0.022 | [-0.261, +0.334] | 32.3% | 1.03 | -22.2 | 7 | 97 |
| validation+final_test | 158 | +28.2 | +0.179 | +0.179 | [-0.070, +0.439] | 36.1% | 1.28 | -22.2 | 7 | 100 |
| all (reference) | 316 | +32.4 | +0.102 | +0.102 | [-0.069, +0.281] | 35.4% | 1.16 | -31.7 | 14 | 91 |

### V2_A_nobias breakdowns (validation + final test)

**By session**

| session | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| London | 91 | -3.0 | -0.033 | -0.033 | [-0.343, +0.326] | 27.5% | 0.96 | -26.1 | 13 | 89 |
| NewYork | 67 | +31.2 | +0.466 | +0.466 | [+0.100, +0.850] | 47.8% | 1.93 | -6.9 | 5 | 146 |

**By side**

| side | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 47 | +15.8 | +0.336 | +0.336 | [-0.117, +0.838] | 44.7% | 1.59 | -5.2 | 4 | 123 |
| short | 111 | +12.5 | +0.112 | +0.112 | [-0.173, +0.420] | 32.4% | 1.17 | -21.5 | 10 | 97 |

**By exit_reason**

| exit_reason | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| breakeven_stop | 8 | +7.0 | +0.881 | +0.881 | [+nan, +nan] | 100.0% | inf | 0.0 | 0 | 72 |
| stop | 98 | -99.5 | -1.016 | -1.016 | [-1.018, -1.014] | 0.0% | 0.00 | -98.5 | 98 | 54 |
| time_exit | 21 | +44.8 | +2.136 | +2.136 | [+1.338, +3.003] | 85.7% | 40.02 | -0.6 | 1 | 370 |
| trail_stop | 31 | +75.9 | +2.448 | +2.448 | [+1.962, +3.018] | 100.0% | inf | 0.0 | 0 | 281 |

**By year**

| year | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | 21 | +1.0 | +0.048 | +0.048 | [-0.529, +0.687] | 33.3% | 1.07 | -7.9 | 5 | 93 |
| 2025 | 64 | +34.8 | +0.543 | +0.543 | [+0.081, +1.066] | 42.2% | 1.95 | -5.3 | 6 | 142 |
| 2026 | 73 | -7.5 | -0.103 | -0.103 | [-0.378, +0.192] | 31.5% | 0.85 | -22.2 | 7 | 89 |

**Skipped / cancelled setups (all periods)**

| reason | count |
|---|---|
| WAIT_rr_too_low | 1804 |
| CANCEL_deep_break | 134 |
| WAIT_daily_or_weekly_stop | 29 |
| CANCEL_cutoff_time | 26 |
| WAIT_stop_too_wide | 23 |
| CANCEL_rr_too_low_after_rearm | 5 |
| EXPIRED_unfilled | 2 |
| WAIT_news_window | 2 |

## V2_B_sma_only

| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 59 | -10.8 | -0.183 | -0.183 | [-0.585, +0.325] | 25.4% | 0.76 | -19.4 | 7 | 55 |
| validation 2024-07-01→2025-09-01 | 23 | +17.3 | +0.752 | +0.752 | [-0.079, +1.699] | 47.8% | 2.40 | -4.4 | 4 | 115 |
| final_test 2025-09-01→2026-11-01 | 38 | +6.7 | +0.176 | +0.176 | [-0.224, +0.598] | 42.1% | 1.30 | -10.9 | 5 | 110 |
| validation+final_test | 61 | +24.0 | +0.393 | +0.393 | [-0.012, +0.824] | 44.3% | 1.69 | -10.9 | 5 | 115 |
| all (reference) | 120 | +13.2 | +0.110 | +0.110 | [-0.186, +0.433] | 35.0% | 1.17 | -22.9 | 7 | 74 |

## V2_C_trigB_only

| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 189 | -38.6 | -0.204 | -0.247 | [-0.351, -0.058] | 27.0% | 0.68 | -49.9 | 13 | 205 |
| validation 2024-07-01→2025-09-01 | 101 | +1.1 | +0.011 | +0.011 | [-0.251, +0.280] | 31.7% | 1.02 | -23.4 | 8 | 218 |
| final_test 2025-09-01→2026-11-01 | 66 | -4.2 | -0.064 | +0.008 | [-0.304, +0.183] | 33.3% | 0.89 | -14.9 | 7 | 292 |
| validation+final_test | 167 | -3.2 | -0.019 | +0.010 | [-0.205, +0.173] | 32.3% | 0.97 | -25.9 | 8 | 263 |
| all (reference) | 356 | -41.8 | -0.117 | -0.127 | [-0.233, +0.003] | 29.5% | 0.82 | -50.7 | 13 | 221 |

## V2_D_trigAB

| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 225 | -37.2 | -0.165 | -0.173 | [-0.304, -0.020] | 28.4% | 0.74 | -47.3 | 13 | 186 |
| validation 2024-07-01→2025-09-01 | 113 | -2.7 | -0.024 | -0.024 | [-0.282, +0.249] | 30.1% | 0.97 | -31.0 | 14 | 184 |
| final_test 2025-09-01→2026-11-01 | 90 | -7.7 | -0.085 | -0.034 | [-0.281, +0.114] | 32.2% | 0.84 | -19.1 | 6 | 253 |
| validation+final_test | 203 | -10.4 | -0.051 | -0.028 | [-0.221, +0.126] | 31.0% | 0.92 | -32.4 | 14 | 217 |
| all (reference) | 428 | -47.6 | -0.111 | -0.105 | [-0.219, +0.002] | 29.7% | 0.83 | -61.2 | 14 | 198 |

## V2_E_rr1

| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 96 | -22.8 | -0.237 | -0.192 | [-0.454, -0.003] | 30.2% | 0.62 | -27.8 | 6 | 76 |
| validation 2024-07-01→2025-09-01 | 62 | +23.9 | +0.386 | +0.386 | [+0.021, +0.791] | 53.2% | 1.80 | -8.7 | 4 | 95 |
| final_test 2025-09-01→2026-11-01 | 48 | -1.4 | -0.030 | +0.022 | [-0.234, +0.180] | 43.8% | 0.93 | -9.6 | 6 | 81 |
| validation+final_test | 110 | +22.5 | +0.205 | +0.227 | [-0.022, +0.443] | 49.1% | 1.45 | -9.6 | 6 | 90 |
| all (reference) | 206 | -0.3 | -0.001 | +0.032 | [-0.164, +0.174] | 40.3% | 1.00 | -32.9 | 8 | 80 |

## V2_F_v1exits

| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 63 | -24.6 | -0.390 | -0.446 | [-0.607, -0.152] | 22.2% | 0.45 | -26.9 | 8 | 51 |
| validation 2024-07-01→2025-09-01 | 24 | +7.1 | +0.295 | +0.295 | [-0.205, +0.803] | 45.8% | 1.53 | -4.1 | 4 | 48 |
| final_test 2025-09-01→2026-11-01 | 38 | +6.6 | +0.173 | +0.229 | [-0.131, +0.489] | 42.1% | 1.42 | -6.5 | 5 | 63 |
| validation+final_test | 62 | +13.6 | +0.220 | +0.254 | [-0.046, +0.497] | 43.5% | 1.47 | -6.5 | 5 | 58 |
| all (reference) | 125 | -11.0 | -0.088 | -0.099 | [-0.269, +0.094] | 32.8% | 0.85 | -30.0 | 8 | 54 |

## V2_G_nostops

| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 55 | -14.1 | -0.256 | -0.181 | [-0.558, +0.101] | 25.5% | 0.63 | -18.4 | 7 | 59 |
| validation 2024-07-01→2025-09-01 | 23 | +17.3 | +0.752 | +0.752 | [-0.065, +1.688] | 47.8% | 2.40 | -4.4 | 4 | 115 |
| final_test 2025-09-01→2026-11-01 | 38 | +3.4 | +0.089 | +0.176 | [-0.177, +0.361] | 42.1% | 1.22 | -7.2 | 5 | 110 |
| validation+final_test | 61 | +20.7 | +0.339 | +0.393 | [-0.014, +0.730] | 44.3% | 1.74 | -7.2 | 5 | 115 |
| all (reference) | 116 | +6.6 | +0.057 | +0.121 | [-0.187, +0.321] | 35.3% | 1.10 | -21.9 | 7 | 76 |

## V2_H_coststress

| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 59 | -21.5 | -0.364 | -0.310 | [-0.647, -0.039] | 23.7% | 0.52 | -24.3 | 8 | 51 |
| validation 2024-07-01→2025-09-01 | 24 | +14.6 | +0.610 | +0.610 | [-0.187, +1.512] | 45.8% | 2.02 | -6.0 | 4 | 104 |
| final_test 2025-09-01→2026-11-01 | 40 | +0.7 | +0.017 | +0.089 | [-0.240, +0.280] | 40.0% | 1.04 | -7.0 | 5 | 88 |
| validation+final_test | 64 | +15.3 | +0.239 | +0.285 | [-0.102, +0.629] | 42.2% | 1.48 | -7.0 | 5 | 94 |
| all (reference) | 123 | -6.2 | -0.050 | -0.001 | [-0.284, +0.200] | 33.3% | 0.92 | -30.2 | 8 | 64 |

## V2_I_v1window

| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 43 | -5.6 | -0.130 | -0.034 | [-0.508, +0.298] | 27.9% | 0.80 | -12.5 | 7 | 60 |
| validation 2024-07-01→2025-09-01 | 21 | +19.3 | +0.920 | +0.920 | [+0.069, +1.901] | 52.4% | 2.87 | -4.4 | 4 | 162 |
| final_test 2025-09-01→2026-11-01 | 34 | +3.4 | +0.101 | +0.243 | [-0.182, +0.391] | 44.1% | 1.24 | -7.7 | 5 | 111 |
| validation+final_test | 55 | +22.8 | +0.414 | +0.502 | [+0.030, +0.851] | 47.3% | 1.93 | -7.7 | 5 | 123 |
| all (reference) | 98 | +17.2 | +0.175 | +0.267 | [-0.107, +0.479] | 38.8% | 1.32 | -13.8 | 7 | 78 |

## V2_J_ny_only

| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 23 | -11.8 | -0.515 | -0.570 | [-0.801, -0.192] | 21.7% | 0.31 | -11.3 | 7 | 36 |
| validation 2024-07-01→2025-09-01 | 10 | +11.1 | +1.106 | +1.106 | [-0.050, +2.430] | 60.0% | 3.71 | -2.0 | 2 | 211 |
| final_test 2025-09-01→2026-11-01 | 11 | +10.5 | +0.955 | +1.706 | [+0.529, +1.335] | 90.9% | 11.44 | -1.0 | 1 | 320 |
| validation+final_test | 21 | +21.6 | +1.027 | +1.420 | [+0.437, +1.693] | 76.2% | 5.24 | -2.0 | 2 | 307 |
| all (reference) | 44 | +9.7 | +0.221 | +0.380 | [-0.149, +0.634] | 47.7% | 1.44 | -13.3 | 7 | 99 |

## V2_K_confirm

| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 29 | -0.7 | -0.023 | -0.101 | [-0.424, +0.427] | 34.5% | 0.96 | -7.1 | 5 | 79 |
| validation 2024-07-01→2025-09-01 | 17 | +16.6 | +0.978 | +0.978 | [-0.029, +2.147] | 52.9% | 3.01 | -4.1 | 4 | 157 |
| final_test 2025-09-01→2026-11-01 | 26 | +5.0 | +0.191 | +0.453 | [-0.147, +0.537] | 50.0% | 1.49 | -5.2 | 4 | 188 |
| validation+final_test | 43 | +21.6 | +0.502 | +0.661 | [+0.043, +1.028] | 51.2% | 2.17 | -5.2 | 4 | 174 |
| all (reference) | 72 | +20.9 | +0.291 | +0.354 | [-0.031, +0.648] | 44.4% | 1.60 | -7.1 | 5 | 110 |

## V2_L_ny_confirm

| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 14 | -3.9 | -0.277 | -0.388 | [-0.699, +0.184] | 28.6% | 0.57 | -4.8 | 5 | 56 |
| validation 2024-07-01→2025-09-01 | 6 | +8.6 | +1.437 | +1.437 | [+nan, +nan] | 66.7% | 5.23 | -1.0 | 1 | 211 |
| final_test 2025-09-01→2026-11-01 | 9 | +8.9 | +0.985 | +1.838 | [+nan, +nan] | 88.9% | 9.80 | -1.0 | 1 | 320 |
| validation+final_test | 15 | +17.5 | +1.166 | +1.677 | [+0.455, +2.017] | 80.0% | 6.74 | -1.1 | 1 | 307 |
| all (reference) | 29 | +13.6 | +0.469 | +0.680 | [-0.005, +1.008] | 55.2% | 2.14 | -4.8 | 5 | 99 |

## V2_M_daily_bias

| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 536 | -25.2 | -0.047 | -0.056 | [-0.132, +0.043] | 39.6% | 0.91 | -41.1 | 11 | 69 |
| validation 2024-07-01→2025-09-01 | 279 | +9.4 | +0.034 | +0.034 | [-0.109, +0.183] | 41.9% | 1.06 | -21.2 | 10 | 75 |
| final_test 2025-09-01→2026-11-01 | 288 | +21.7 | +0.075 | +0.104 | [-0.044, +0.196] | 43.8% | 1.16 | -18.2 | 8 | 76 |
| validation+final_test | 567 | +31.1 | +0.055 | +0.069 | [-0.037, +0.149] | 42.9% | 1.10 | -21.2 | 10 | 75 |
| all (reference) | 1103 | +5.9 | +0.005 | +0.009 | [-0.057, +0.069] | 41.3% | 1.01 | -42.3 | 11 | 73 |

## V2_N_daily_di_nobias

| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 772 | -37.1 | -0.048 | -0.048 | [-0.130, +0.038] | 39.8% | 0.92 | -45.7 | 13 | 60 |
| validation 2024-07-01→2025-09-01 | 285 | +2.0 | +0.007 | +0.007 | [-0.134, +0.157] | 38.9% | 1.01 | -25.7 | 8 | 66 |
| final_test 2025-09-01→2026-11-01 | 301 | +6.7 | +0.022 | +0.022 | [-0.110, +0.152] | 40.9% | 1.04 | -15.2 | 10 | 68 |
| validation+final_test | 586 | +8.7 | +0.015 | +0.015 | [-0.080, +0.115] | 39.9% | 1.02 | -25.7 | 10 | 68 |
| all (reference) | 1358 | -28.4 | -0.021 | -0.021 | [-0.083, +0.042] | 39.8% | 0.97 | -59.7 | 13 | 63 |

## V2_O_daily_bias_0800

| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 613 | -74.7 | -0.122 | -0.167 | [-0.194, -0.048] | 37.5% | 0.77 | -86.7 | 10 | 99 |
| validation 2024-07-01→2025-09-01 | 295 | +36.9 | +0.125 | +0.125 | [-0.009, +0.264] | 47.1% | 1.23 | -15.8 | 9 | 174 |
| final_test 2025-09-01→2026-11-01 | 286 | -30.5 | -0.106 | -0.070 | [-0.209, -0.003] | 37.4% | 0.80 | -71.0 | 14 | 186 |
| validation+final_test | 581 | +6.4 | +0.011 | +0.029 | [-0.074, +0.101] | 42.3% | 1.02 | -71.0 | 14 | 177 |
| all (reference) | 1194 | -68.3 | -0.057 | -0.071 | [-0.114, +0.000] | 39.9% | 0.89 | -90.7 | 14 | 129 |
