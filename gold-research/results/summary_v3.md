# Backtest results — v3 alternative strategy families (pre-registered variants)

R = planned risk (entry level to initial stop; for market orders, fill to initial stop). Realised R includes spread 0.25, slippage 0.05 per fill, commission 0. Periods by signal time: development 2021-01-04→2024-07-01 (41.9 months), validation 2024-07-01→2025-09-01 (14.0 months), final test 2025-09-01→2026-11-01 (14.0 months).

Reference v2.2 (V2_K_confirm): validation 17 trades, +0.978 R/trade, +16.6 R, PF 3.01; final test 26 trades, +0.191 R, +5.0 R, PF 1.49; max DD −7.1 R.

## Overview (per variant: n / mean R / PF / max DD per period; verdict against the pre-registered rule)

| variant | family | development n / mean R / PF / max DD | validation n / mean R / PF / max DD | final test n / mean R / PF / max DD | OOS trades/month | passes rule? | conditions failed |
|---|---|---|---|---|---|---|---|
| V3_ORB_L10 | ORB | 540 / +0.002 / 1.00 / -31.8 | 177 / -0.002 / 1.00 / -13.1 | 153 / -0.026 / 0.95 / -17.0 | 11.8 | no | meanR_pos_both, pf_gt_1_10_both, maxDD_le_10R_all_periods, beats_v22_meanR_both, beats_v22_totalR_both |
| V3_ORB_L15 | ORB | 540 / -0.039 / 0.94 / -49.5 | 177 / +0.005 / 1.01 / -14.8 | 153 / -0.009 / 0.98 / -18.3 | 11.8 | no | meanR_pos_both, pf_gt_1_10_both, maxDD_le_10R_all_periods, beats_v22_meanR_both, beats_v22_totalR_both |
| V3_ORB_NY10 | ORB | 666 / -0.009 / 0.98 / -31.2 | 206 / +0.054 / 1.13 / -7.5 | 171 / +0.014 / 1.03 / -18.4 | 13.5 | no | pf_gt_1_10_both, maxDD_le_10R_all_periods, beats_v22_meanR_both, beats_v22_totalR_both |
| V3_ORB_NY15 | ORB | 668 / +0.018 / 1.04 / -27.3 | 206 / +0.100 / 1.22 / -7.5 | 171 / +0.040 / 1.08 / -24.5 | 13.5 | no | pf_gt_1_10_both, maxDD_le_10R_all_periods, beats_v22_meanR_both |
| V3_VB_03 | VB | 805 / -0.067 / 0.88 / -79.9 | 269 / -0.074 / 0.86 / -35.8 | 243 / -0.044 / 0.91 / -21.0 | 18.3 | no | meanR_pos_both, pf_gt_1_10_both, maxDD_le_10R_all_periods, beats_v22_meanR_both, beats_v22_totalR_both |
| V3_VB_05 | VB | 495 / -0.037 / 0.90 / -29.8 | 162 / +0.002 / 1.01 / -8.8 | 120 / +0.145 / 1.53 / -6.0 | 10.1 | no | pf_gt_1_10_both, maxDD_le_10R_all_periods, beats_v22_meanR_both, beats_v22_totalR_both |
| V3_VB_03_bias | VB | 369 / -0.133 / 0.77 / -55.2 | 156 / +0.052 / 1.11 / -13.7 | 139 / -0.071 / 0.86 / -21.1 | 10.5 | no | meanR_pos_both, pf_gt_1_10_both, maxDD_le_10R_all_periods, beats_v22_meanR_both, beats_v22_totalR_both |
| V3_VB_05_bias | VB | 188 / +0.003 / 1.01 / -12.2 | 88 / +0.130 / 1.51 / -6.5 | 62 / +0.137 / 1.52 / -3.7 | 5.4 | no | maxDD_le_10R_all_periods, beats_v22_meanR_both, beats_v22_totalR_both |
| V3_VW_2s | VW | 818 / -0.177 / 0.74 / -155.0 | 256 / -0.155 / 0.77 / -47.6 | 217 / -0.106 / 0.84 / -31.6 | 16.9 | no | meanR_pos_both, pf_gt_1_10_both, maxDD_le_10R_all_periods, beats_v22_meanR_both, beats_v22_totalR_both |
| V3_VW_25s | VW | 614 / -0.156 / 0.78 / -110.5 | 190 / -0.153 / 0.78 / -42.4 | 159 / -0.096 / 0.86 / -23.8 | 12.5 | no | meanR_pos_both, pf_gt_1_10_both, maxDD_le_10R_all_periods, beats_v22_meanR_both, beats_v22_totalR_both |
| V3_VW_2s_adx15 | VW | 288 / -0.237 / 0.65 / -72.7 | 80 / -0.278 / 0.61 / -23.0 | 85 / -0.097 / 0.85 / -13.1 | 5.9 | no | meanR_pos_both, pf_gt_1_10_both, maxDD_le_10R_all_periods, beats_v22_meanR_both, beats_v22_totalR_both |
| V3_DC_20_10 | DC | 52 / +0.157 / 1.46 / -3.8 | 16 / +0.703 / 3.01 / -3.2 | 13 / +0.713 / 3.05 / -2.2 | 1.0 | no | n_val_ge60, n_test_ge60, beats_v22_meanR_both, beats_v22_totalR_both |
| V3_DC_55_20 | DC | 25 / +0.439 / 3.03 / -2.8 | 8 / +1.660 / 11.25 / -0.8 | 9 / +0.655 / 4.12 / -1.0 | 0.6 | no | n_val_ge60, n_test_ge60, beats_v22_totalR_both |
| V3_ORB_L10_h15 | ORB | 540 / -0.048 / 0.69 / -29.9 | 177 / -0.039 / 0.70 / -8.4 | 153 / +0.003 / 1.02 / -6.9 | 11.8 | no | meanR_pos_both, pf_gt_1_10_both, maxDD_le_10R_all_periods, beats_v22_meanR_both, beats_v22_totalR_both |
| V3_VB_03_h15 | VB | 805 / -0.053 / 0.69 / -45.8 | 269 / -0.043 / 0.72 / -16.5 | 243 / -0.056 / 0.66 / -14.7 | 18.3 | no | meanR_pos_both, pf_gt_1_10_both, maxDD_le_10R_all_periods, beats_v22_meanR_both, beats_v22_totalR_both |
| V3_VW_2s_h15 | VW | 904 / -0.152 / 0.54 / -139.5 | 283 / -0.101 / 0.66 / -30.5 | 252 / -0.004 / 0.99 / -13.0 | 19.1 | no | meanR_pos_both, pf_gt_1_10_both, maxDD_le_10R_all_periods, beats_v22_meanR_both, beats_v22_totalR_both |

## Verdict per family

| family | variants | any passes the rule? | positive OOS (mean R > 0 and PF > 1.10 in both held-out periods) | notes |
|---|---|---|---|---|
| ORB | 5 | no | none |  |
| VB | 5 | no | V3_VB_05_bias |  |
| VW | 4 | no | none |  |
| DC | 2 | no | V3_DC_20_10, V3_DC_55_20 | overnight holding; not account-compatible as is |

## 15-minute maximum hold vs unconstrained twin (validation + final test)

| twin | unconstrained n / mean R / PF / total R / max DD | h15 n / mean R / PF / total R / max DD | h15 exits |
|---|---|---|---|
| V3_ORB_L10 → V3_ORB_L10_h15 | 330 / -0.013 / 0.97 / -4.3 / -17.0 | 330 / -0.020 / 0.84 / -6.6 / -8.4 | {'max_hold': 324, 'target': 4, 'stop': 2} |
| V3_VB_03 → V3_VB_03_h15 | 512 / -0.060 / 0.89 / -30.6 / -38.4 | 512 / -0.049 / 0.69 / -25.2 / -26.1 | {'max_hold': 493, 'stop_same_minute': 10, 'target': 7, 'stop': 2} |
| V3_VW_2s → V3_VW_2s_h15 | 473 / -0.133 / 0.81 / -62.8 / -71.3 | 535 / -0.055 / 0.80 / -29.5 / -42.7 | {'max_hold': 450, 'stop': 74, 'target': 10, 'stop_same_minute': 1} |

## V3_ORB_L10 (ORB; `{"family": "ORB"}`)

| period | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 540 | 12.9 | +0.002 | [-0.069, +0.075] | 51.9% | 1.00 | +1.2 | -31.8 | 8 | 169 |
| validation 2024-07-01→2025-09-01 | 177 | 12.6 | -0.002 | [-0.122, +0.119] | 50.3% | 1.00 | -0.3 | -13.1 | 7 | 172 |
| final_test 2025-09-01→2026-11-01 | 153 | 10.9 | -0.026 | [-0.159, +0.106] | 49.0% | 0.95 | -4.0 | -17.0 | 8 | 189 |
| validation+final_test | 330 | 11.8 | -0.013 | [-0.103, +0.077] | 49.7% | 0.97 | -4.3 | -17.0 | 8 | 180 |
| all (reference) | 870 | 12.4 | -0.004 | [-0.058, +0.053] | 51.0% | 0.99 | -3.1 | -31.8 | 8 | 172 |

Exit reasons (all periods): target 431, stop 412, time_exit 18, session_gap_exit 9

By side (validation + final test):

| side | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 178 | 6.4 | +0.062 | [-0.060, +0.184] | 53.9% | 1.14 | +11.1 | -15.0 | 5 | 186 |
| short | 152 | 5.4 | -0.102 | [-0.236, +0.026] | 44.7% | 0.81 | -15.4 | -23.1 | 8 | 161 |

## V3_ORB_L15 (ORB; `{"family": "ORB", "orb_target_mult": 1.5}`)

| period | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 540 | 12.9 | -0.039 | [-0.123, +0.048] | 40.9% | 0.94 | -21.2 | -49.5 | 11 | 242 |
| validation 2024-07-01→2025-09-01 | 177 | 12.6 | +0.005 | [-0.142, +0.154] | 41.2% | 1.01 | +0.9 | -14.8 | 10 | 246 |
| final_test 2025-09-01→2026-11-01 | 153 | 10.9 | -0.009 | [-0.165, +0.151] | 41.2% | 0.98 | -1.4 | -18.3 | 11 | 257 |
| validation+final_test | 330 | 11.8 | -0.001 | [-0.110, +0.109] | 41.2% | 1.00 | -0.5 | -21.8 | 11 | 252 |
| all (reference) | 870 | 12.4 | -0.025 | [-0.092, +0.042] | 41.0% | 0.96 | -21.6 | -49.5 | 11 | 246 |

Exit reasons (all periods): stop 493, target 328, time_exit 39, session_gap_exit 10

By side (validation + final test):

| side | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 178 | 6.4 | +0.068 | [-0.076, +0.211] | 44.9% | 1.13 | +12.1 | -13.1 | 7 | 285 |
| short | 152 | 5.4 | -0.082 | [-0.242, +0.076] | 36.8% | 0.87 | -12.5 | -28.8 | 11 | 224 |

## V3_ORB_NY10 (ORB; `{"family": "ORB", "orb_range_start": "13:30", "orb_range_end": "14:00", "orb_cancel": "16:00"}`)

| period | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 666 | 15.9 | -0.009 | [-0.067, +0.049] | 50.5% | 0.98 | -5.7 | -31.2 | 7 | 64 |
| validation 2024-07-01→2025-09-01 | 206 | 14.7 | +0.054 | [-0.048, +0.160] | 52.4% | 1.13 | +11.0 | -7.5 | 5 | 75 |
| final_test 2025-09-01→2026-11-01 | 171 | 12.2 | +0.014 | [-0.107, +0.133] | 50.9% | 1.03 | +2.4 | -18.4 | 7 | 55 |
| validation+final_test | 377 | 13.5 | +0.036 | [-0.042, +0.115] | 51.7% | 1.08 | +13.4 | -18.4 | 7 | 63 |
| all (reference) | 1043 | 14.9 | +0.007 | [-0.039, +0.053] | 50.9% | 1.02 | +7.7 | -31.2 | 7 | 64 |

Exit reasons (all periods): target 428, stop 391, time_exit 220, session_gap_exit 4

By side (validation + final test):

| side | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 214 | 7.6 | +0.060 | [-0.045, +0.165] | 54.2% | 1.14 | +12.9 | -14.1 | 8 | 76 |
| short | 163 | 5.8 | +0.003 | [-0.117, +0.125] | 48.5% | 1.01 | +0.5 | -9.7 | 8 | 52 |

## V3_ORB_NY15 (ORB; `{"family": "ORB", "orb_range_start": "13:30", "orb_range_end": "14:00", "orb_cancel": "16:00", "orb_target_mult": 1.5}`)

| period | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 668 | 16.0 | +0.018 | [-0.048, +0.084] | 45.2% | 1.04 | +11.8 | -27.3 | 12 | 95 |
| validation 2024-07-01→2025-09-01 | 206 | 14.7 | +0.100 | [-0.022, +0.224] | 47.6% | 1.22 | +20.6 | -7.5 | 6 | 115 |
| final_test 2025-09-01→2026-11-01 | 171 | 12.2 | +0.040 | [-0.094, +0.179] | 46.2% | 1.08 | +6.8 | -24.5 | 11 | 83 |
| validation+final_test | 377 | 13.5 | +0.073 | [-0.018, +0.164] | 46.9% | 1.15 | +27.5 | -24.5 | 11 | 101 |
| all (reference) | 1045 | 15.0 | +0.038 | [-0.014, +0.091] | 45.8% | 1.08 | +39.3 | -27.3 | 12 | 97 |

Exit reasons (all periods): stop 422, time_exit 323, target 295, session_gap_exit 5

By side (validation + final test):

| side | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 214 | 7.6 | +0.063 | [-0.055, +0.181] | 49.1% | 1.14 | +13.4 | -17.4 | 8 | 111 |
| short | 163 | 5.8 | +0.086 | [-0.061, +0.232] | 44.2% | 1.18 | +14.0 | -11.0 | 11 | 82 |

## V3_VB_03 (VB; `{"family": "VB", "vb_k": 0.3}`)

| period | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 805 | 19.2 | -0.067 | [-0.132, -0.002] | 41.0% | 0.88 | -53.9 | -79.9 | 9 | 218 |
| validation 2024-07-01→2025-09-01 | 269 | 19.2 | -0.074 | [-0.181, +0.036] | 40.1% | 0.86 | -19.9 | -35.8 | 8 | 251 |
| final_test 2025-09-01→2026-11-01 | 243 | 17.4 | -0.044 | [-0.156, +0.068] | 43.2% | 0.91 | -10.6 | -21.0 | 13 | 266 |
| validation+final_test | 512 | 18.3 | -0.060 | [-0.136, +0.017] | 41.6% | 0.89 | -30.6 | -38.4 | 13 | 261 |
| all (reference) | 1317 | 18.8 | -0.064 | [-0.113, -0.015] | 41.2% | 0.88 | -84.4 | -107.5 | 13 | 235 |

Exit reasons (all periods): stop 622, target 352, time_exit 307, stop_same_minute 20, session_gap_exit 16

By side (validation + final test):

| side | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 271 | 9.7 | -0.014 | [-0.119, +0.091] | 44.6% | 0.97 | -3.7 | -18.9 | 7 | 302 |
| short | 241 | 8.6 | -0.111 | [-0.225, +0.003] | 38.2% | 0.80 | -26.8 | -40.6 | 10 | 217 |

## V3_VB_05 (VB; `{"family": "VB", "vb_k": 0.5}`)

| period | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 495 | 11.8 | -0.037 | [-0.101, +0.026] | 46.9% | 0.90 | -18.2 | -29.8 | 10 | 352 |
| validation 2024-07-01→2025-09-01 | 162 | 11.5 | +0.002 | [-0.100, +0.106] | 46.9% | 1.01 | +0.4 | -8.8 | 5 | 363 |
| final_test 2025-09-01→2026-11-01 | 120 | 8.6 | +0.145 | [+0.017, +0.272] | 51.7% | 1.53 | +17.4 | -6.0 | 4 | 372 |
| validation+final_test | 282 | 10.1 | +0.063 | [-0.018, +0.146] | 48.9% | 1.21 | +17.8 | -8.8 | 5 | 368 |
| all (reference) | 777 | 11.1 | -0.001 | [-0.050, +0.049] | 47.6% | 1.00 | -0.4 | -30.6 | 10 | 359 |

Exit reasons (all periods): time_exit 477, stop 188, target 101, stop_same_minute 6, session_gap_exit 5

By side (validation + final test):

| side | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 143 | 5.1 | +0.102 | [-0.004, +0.208] | 51.7% | 1.38 | +14.5 | -6.5 | 7 | 372 |
| short | 139 | 5.0 | +0.024 | [-0.096, +0.145] | 46.0% | 1.07 | +3.3 | -13.4 | 10 | 359 |

## V3_VB_03_bias (VB; `{"family": "VB", "vb_k": 0.3, "vb_bias": "sma200"}`)

| period | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 369 | 8.8 | -0.133 | [-0.227, -0.039] | 40.4% | 0.77 | -48.9 | -55.2 | 8 | 197 |
| validation 2024-07-01→2025-09-01 | 156 | 11.1 | +0.052 | [-0.086, +0.195] | 47.4% | 1.11 | +8.1 | -13.7 | 6 | 302 |
| final_test 2025-09-01→2026-11-01 | 139 | 9.9 | -0.071 | [-0.215, +0.074] | 41.0% | 0.86 | -9.9 | -21.1 | 7 | 291 |
| validation+final_test | 295 | 10.5 | -0.006 | [-0.107, +0.095] | 44.4% | 0.99 | -1.8 | -21.1 | 7 | 294 |
| all (reference) | 664 | 9.5 | -0.076 | [-0.144, -0.008] | 42.2% | 0.86 | -50.7 | -64.1 | 8 | 244 |

Exit reasons (all periods): stop 302, time_exit 177, target 164, stop_same_minute 14, session_gap_exit 7

By side (validation + final test):

| side | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 255 | 9.1 | -0.037 | [-0.148, +0.074] | 43.1% | 0.93 | -9.4 | -21.6 | 7 | 294 |
| short | 40 | 1.4 | +0.191 | [-0.066, +0.450] | 52.5% | 1.54 | +7.6 | -5.8 | 7 | 294 |

## V3_VB_05_bias (VB; `{"family": "VB", "vb_k": 0.5, "vb_bias": "sma200"}`)

| period | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 188 | 4.5 | +0.003 | [-0.100, +0.107] | 48.4% | 1.01 | +0.5 | -12.2 | 9 | 350 |
| validation 2024-07-01→2025-09-01 | 88 | 6.3 | +0.130 | [-0.006, +0.267] | 53.4% | 1.51 | +11.4 | -6.5 | 5 | 370 |
| final_test 2025-09-01→2026-11-01 | 62 | 4.4 | +0.137 | [-0.024, +0.300] | 53.2% | 1.52 | +8.5 | -3.7 | 6 | 370 |
| validation+final_test | 150 | 5.4 | +0.133 | [+0.030, +0.238] | 53.3% | 1.52 | +19.9 | -6.5 | 6 | 370 |
| all (reference) | 338 | 4.8 | +0.060 | [-0.013, +0.133] | 50.6% | 1.19 | +20.4 | -12.2 | 9 | 360 |

Exit reasons (all periods): time_exit 220, stop 72, target 39, stop_same_minute 4, session_gap_exit 3

By side (validation + final test):

| side | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 127 | 4.5 | +0.119 | [+0.004, +0.232] | 52.8% | 1.44 | +15.1 | -6.5 | 6 | 369 |
| short | 23 | 0.8 | +0.209 | [-0.016, +0.445] | 56.5% | 2.20 | +4.8 | -1.3 | 3 | 405 |

## V3_VW_2s (VW; `{"family": "VW", "vw_sigma": 2.0, "vw_adx_max": 20.0}`)

| period | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 818 | 19.5 | -0.177 | [-0.247, -0.106] | 34.2% | 0.74 | -144.7 | -155.0 | 11 | 43 |
| validation 2024-07-01→2025-09-01 | 256 | 18.2 | -0.155 | [-0.286, -0.021] | 32.0% | 0.77 | -39.7 | -47.6 | 12 | 45 |
| final_test 2025-09-01→2026-11-01 | 217 | 15.5 | -0.106 | [-0.255, +0.045] | 32.3% | 0.84 | -23.0 | -31.6 | 13 | 53 |
| validation+final_test | 473 | 16.9 | -0.133 | [-0.232, -0.033] | 32.1% | 0.81 | -62.8 | -71.3 | 13 | 48 |
| all (reference) | 1291 | 18.5 | -0.161 | [-0.219, -0.102] | 33.5% | 0.76 | -207.5 | -225.2 | 13 | 45 |

Exit reasons (all periods): stop 843, target 418, time_exit 21, stop_same_minute 9

By side (validation + final test):

| side | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 193 | 6.9 | -0.185 | [-0.328, -0.040] | 32.6% | 0.73 | -35.6 | -40.5 | 15 | 50 |
| short | 280 | 10.0 | -0.097 | [-0.231, +0.039] | 31.8% | 0.86 | -27.1 | -43.3 | 11 | 47 |

## V3_VW_25s (VW; `{"family": "VW", "vw_sigma": 2.5, "vw_adx_max": 20.0}`)

| period | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 614 | 14.7 | -0.156 | [-0.246, -0.067] | 32.7% | 0.78 | -95.8 | -110.5 | 13 | 50 |
| validation 2024-07-01→2025-09-01 | 190 | 13.5 | -0.153 | [-0.311, +0.007] | 31.1% | 0.78 | -29.1 | -42.4 | 19 | 48 |
| final_test 2025-09-01→2026-11-01 | 159 | 11.4 | -0.096 | [-0.273, +0.084] | 32.7% | 0.86 | -15.2 | -23.8 | 12 | 56 |
| validation+final_test | 349 | 12.5 | -0.127 | [-0.244, -0.010] | 31.8% | 0.81 | -44.4 | -54.7 | 19 | 50 |
| all (reference) | 963 | 13.8 | -0.146 | [-0.215, -0.074] | 32.4% | 0.79 | -140.2 | -161.3 | 19 | 50 |

Exit reasons (all periods): stop 636, target 286, time_exit 33, stop_same_minute 8

By side (validation + final test):

| side | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 149 | 5.3 | -0.184 | [-0.346, -0.017] | 32.2% | 0.73 | -27.5 | -30.5 | 12 | 52 |
| short | 200 | 7.1 | -0.084 | [-0.248, +0.084] | 31.5% | 0.88 | -16.9 | -33.3 | 12 | 50 |

## V3_VW_2s_adx15 (VW; `{"family": "VW", "vw_sigma": 2.0, "vw_adx_max": 15.0}`)

| period | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 288 | 6.9 | -0.237 | [-0.350, -0.123] | 34.4% | 0.65 | -68.3 | -72.7 | 9 | 36 |
| validation 2024-07-01→2025-09-01 | 80 | 5.7 | -0.278 | [-0.489, -0.057] | 30.0% | 0.61 | -22.3 | -23.0 | 10 | 39 |
| final_test 2025-09-01→2026-11-01 | 85 | 6.1 | -0.097 | [-0.324, +0.141] | 34.1% | 0.85 | -8.3 | -13.1 | 9 | 60 |
| validation+final_test | 165 | 5.9 | -0.185 | [-0.343, -0.021] | 32.1% | 0.73 | -30.5 | -32.7 | 10 | 43 |
| all (reference) | 453 | 6.5 | -0.218 | [-0.311, -0.125] | 33.6% | 0.68 | -98.8 | -106.4 | 10 | 40 |

Exit reasons (all periods): stop 296, target 148, stop_same_minute 5, time_exit 4

By side (validation + final test):

| side | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 53 | 1.9 | -0.288 | [-0.542, -0.015] | 30.2% | 0.59 | -15.3 | -17.6 | 7 | 43 |
| short | 112 | 4.0 | -0.136 | [-0.333, +0.069] | 33.0% | 0.80 | -15.3 | -22.0 | 8 | 44 |

## V3_DC_20_10 (DC; `{"family": "DC", "dc_entry_n": 20, "dc_exit_n": 10}`)

| period | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 52 | 1.2 | +0.157 | [-0.081, +0.407] | 38.5% | 1.46 | +8.1 | -3.8 | 5 | 15108 |
| validation 2024-07-01→2025-09-01 | 16 | 1.1 | +0.703 | [-0.049, +1.573] | 50.0% | 3.01 | +11.2 | -3.2 | 5 | 16683 |
| final_test 2025-09-01→2026-11-01 | 13 | 0.9 | +0.713 | [-0.005, +1.514] | 53.8% | 3.05 | +9.3 | -2.2 | 3 | 13441 |
| validation+final_test | 29 | 1.0 | +0.707 | [+0.161, +1.297] | 51.7% | 3.03 | +20.5 | -3.2 | 5 | 15356 |
| all (reference) | 81 | 1.2 | +0.354 | [+0.099, +0.627] | 43.2% | 2.03 | +28.7 | -3.8 | 5 | 15356 |

Exit reasons (all periods): trail_stop 80, end_of_data 1

By side (validation + final test):

| side | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 18 | 0.6 | +1.127 | [+0.356, +1.991] | 61.1% | 4.73 | +20.3 | -1.6 | 2 | 18562 |
| short | 11 | 0.4 | +0.020 | [-0.476, +0.572] | 36.4% | 1.05 | +0.2 | -2.8 | 4 | 10219 |

## V3_DC_55_20 (DC; `{"family": "DC", "dc_entry_n": 55, "dc_exit_n": 20}`)

| period | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 25 | 0.6 | +0.439 | [+0.099, +0.783] | 52.0% | 3.03 | +11.0 | -2.8 | 6 | 16330 |
| validation 2024-07-01→2025-09-01 | 8 | 0.6 | +1.660 | [+nan, +nan] | 75.0% | 11.25 | +13.3 | -0.8 | 1 | 25854 |
| final_test 2025-09-01→2026-11-01 | 9 | 0.6 | +0.655 | [+nan, +nan] | 44.4% | 4.12 | +5.9 | -1.0 | 4 | 10822 |
| validation+final_test | 17 | 0.6 | +1.128 | [+0.403, +1.937] | 58.8% | 7.03 | +19.2 | -1.0 | 4 | 12282 |
| all (reference) | 42 | 0.6 | +0.718 | [+0.352, +1.128] | 54.8% | 4.51 | +30.1 | -2.8 | 6 | 13979 |

Exit reasons (all periods): trail_stop 41, end_of_data 1

By side (validation + final test):

| side | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 13 | 0.5 | +1.437 | [+0.534, +2.444] | 69.2% | 8.90 | +18.7 | -1.0 | 1 | 17527 |
| short | 4 | 0.1 | +0.124 | [+nan, +nan] | 25.0% | 1.61 | +0.5 | -0.8 | 3 | 9593 |

## V3_ORB_L10_h15 (ORB; `{"family": "ORB", "max_hold_minutes": 15}`)

| period | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 540 | 12.9 | -0.048 | [-0.072, -0.024] | 43.7% | 0.69 | -26.0 | -29.9 | 20 | 15 |
| validation 2024-07-01→2025-09-01 | 177 | 12.6 | -0.039 | [-0.075, -0.004] | 48.0% | 0.70 | -7.0 | -8.4 | 6 | 15 |
| final_test 2025-09-01→2026-11-01 | 153 | 10.9 | +0.003 | [-0.039, +0.043] | 48.4% | 1.02 | +0.4 | -6.9 | 8 | 15 |
| validation+final_test | 330 | 11.8 | -0.020 | [-0.046, +0.007] | 48.2% | 0.84 | -6.6 | -8.4 | 8 | 15 |
| all (reference) | 870 | 12.4 | -0.037 | [-0.055, -0.019] | 45.4% | 0.74 | -32.5 | -35.7 | 20 | 15 |

Exit reasons (all periods): max_hold 848, target 12, stop 10

By side (validation + final test):

| side | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 178 | 6.4 | -0.002 | [-0.036, +0.030] | 49.4% | 0.98 | -0.4 | -4.5 | 8 | 15 |
| short | 152 | 5.4 | -0.040 | [-0.084, +0.004] | 46.7% | 0.71 | -6.1 | -6.3 | 6 | 15 |

## V3_VB_03_h15 (VB; `{"family": "VB", "vb_k": 0.3, "max_hold_minutes": 15}`)

| period | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 805 | 19.2 | -0.053 | [-0.078, -0.029] | 39.0% | 0.69 | -42.9 | -45.8 | 10 | 15 |
| validation 2024-07-01→2025-09-01 | 269 | 19.2 | -0.043 | [-0.080, -0.005] | 43.5% | 0.72 | -11.5 | -16.5 | 9 | 15 |
| final_test 2025-09-01→2026-11-01 | 243 | 17.4 | -0.056 | [-0.096, -0.016] | 38.3% | 0.66 | -13.7 | -14.7 | 13 | 15 |
| validation+final_test | 512 | 18.3 | -0.049 | [-0.077, -0.022] | 41.0% | 0.69 | -25.2 | -26.1 | 13 | 15 |
| all (reference) | 1317 | 18.8 | -0.052 | [-0.070, -0.033] | 39.8% | 0.69 | -68.1 | -70.8 | 13 | 15 |

Exit reasons (all periods): max_hold 1261, stop_same_minute 20, target 19, stop 17

By side (validation + final test):

| side | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 271 | 9.7 | -0.019 | [-0.054, +0.015] | 44.6% | 0.85 | -5.3 | -7.8 | 10 | 15 |
| short | 241 | 8.6 | -0.083 | [-0.126, -0.039] | 36.9% | 0.58 | -20.0 | -21.0 | 11 | 15 |

## V3_VW_2s_h15 (VW; `{"family": "VW", "vw_sigma": 2.0, "vw_adx_max": 20.0, "max_hold_minutes": 15}`)

| period | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| development 2021-01-04→2024-07-01 | 904 | 21.6 | -0.152 | [-0.186, -0.119] | 41.8% | 0.54 | -137.3 | -139.5 | 9 | 15 |
| validation 2024-07-01→2025-09-01 | 283 | 20.2 | -0.101 | [-0.161, -0.039] | 42.4% | 0.66 | -28.6 | -30.5 | 9 | 15 |
| final_test 2025-09-01→2026-11-01 | 252 | 18.0 | -0.004 | [-0.070, +0.064] | 49.6% | 0.99 | -0.9 | -13.0 | 7 | 15 |
| validation+final_test | 535 | 19.1 | -0.055 | [-0.100, -0.009] | 45.8% | 0.80 | -29.5 | -42.7 | 9 | 15 |
| all (reference) | 1439 | 20.6 | -0.116 | [-0.143, -0.089] | 43.3% | 0.62 | -166.8 | -181.0 | 9 | 15 |

Exit reasons (all periods): max_hold 1162, stop 235, target 34, stop_same_minute 8

By side (validation + final test):

| side | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|
| long | 209 | 7.5 | -0.044 | [-0.117, +0.028] | 47.8% | 0.84 | -9.2 | -13.9 | 9 | 15 |
| short | 326 | 11.6 | -0.062 | [-0.119, -0.006] | 44.5% | 0.77 | -20.3 | -30.8 | 8 | 15 |
