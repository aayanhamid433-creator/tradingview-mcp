# Mechanics validation — engine_v3.py (all V3_* variants)

Validates the simulator's bookkeeping, not profitability. Prices in the data are BID; ask = bid + 0.25; slippage 0.05 on every stop/market fill.

## 1. Hand-checked trades (M1 bars around entry and exit)

### V3_ORB_L10 trade #0 (row 0)

```
side                                 long
signal_time     2021-01-06 08:00:00+00:00
entry_time      2021-01-06 08:07:00+00:00
entry_price                      1949.459
level                            1949.409
initial_stop                     1943.228
final_stop                       1943.228
target                            1955.49
exit_time       2021-01-06 08:46:00+00:00
exit_price                        1955.49
exit_reason                        target
planned_risk                        6.181
pnl_per_oz                          6.031
realised_R                       0.975732
hold_minutes                         39.0
range_high                       1949.309
range_low                        1943.228
range                               6.081
d1atr                           39.466214
stop_capped                         False

M1 bars around entry:
                               open      high       low     close
time_utc                                                         
2021-01-06 08:04:00+00:00  1947.108  1947.885  1947.075  1947.878
2021-01-06 08:05:00+00:00  1947.885  1948.038  1947.398  1947.918
2021-01-06 08:06:00+00:00  1947.928  1949.108  1947.908  1948.935
2021-01-06 08:07:00+00:00  1948.945  1949.565  1948.645  1948.738
2021-01-06 08:08:00+00:00  1948.828  1949.208  1948.545  1948.555
2021-01-06 08:09:00+00:00  1948.518  1949.158  1948.518  1949.115

M1 bars around exit:
                               open      high       low     close
time_utc                                                         
2021-01-06 08:44:00+00:00  1952.589  1954.298  1952.558  1954.095
2021-01-06 08:45:00+00:00  1954.045  1954.355  1953.805  1954.165
2021-01-06 08:46:00+00:00  1954.165  1956.575  1954.155  1955.828
2021-01-06 08:47:00+00:00  1955.845  1956.028  1955.185  1955.299
2021-01-06 08:48:00+00:00  1955.298  1955.518  1954.595  1954.735
```

Check: pnl = +1 × (1955.490 − 1949.459) − 0.0 = 6.031; R = 6.031 / 6.181 = +0.976 (recorded +0.976)

### V3_ORB_L10 trade #409 (min R)

```
side                                 long
signal_time     2023-07-10 08:00:00+00:00
entry_time      2023-07-10 08:05:00+00:00
entry_price                      1924.545
level                            1924.495
initial_stop                     1919.295
final_stop                       1919.295
target                           1929.595
exit_time       2023-07-10 14:00:00+00:00
exit_price                       1913.825
exit_reason                          stop
planned_risk                          5.2
pnl_per_oz                         -10.72
realised_R                      -2.061538
hold_minutes                        355.0
range_high                       1924.395
range_low                        1919.295
range                                 5.1
d1atr                           20.581755
stop_capped                         False

M1 bars around entry:
                               open      high       low     close
time_utc                                                         
2023-07-10 08:02:00+00:00  1922.908  1923.375  1922.874  1923.375
2023-07-10 08:03:00+00:00  1923.405  1923.585  1923.185  1923.435
2023-07-10 08:04:00+00:00  1923.435  1923.665  1923.395  1923.398
2023-07-10 08:05:00+00:00  1923.395  1924.294  1923.305  1924.244
2023-07-10 08:06:00+00:00  1924.234  1924.345  1923.915  1924.145
2023-07-10 08:07:00+00:00  1924.175  1924.345  1924.105  1924.285

M1 bars around exit:
                               open      high       low     close
time_utc                                                         
2023-07-10 12:58:00+00:00  1924.625  1924.625  1924.405  1924.545
2023-07-10 12:59:00+00:00  1924.535  1924.628  1924.488  1924.568
2023-07-10 14:00:00+00:00  1913.875  1915.805  1913.875  1915.125
2023-07-10 14:01:00+00:00  1915.115  1915.305  1914.195  1914.235
2023-07-10 14:02:00+00:00  1914.245  1914.435  1913.915  1914.045
```

Check: pnl = +1 × (1913.825 − 1924.545) − 0.0 = -10.720; R = -10.720 / 5.200 = -2.062 (recorded -2.062)

### V3_VB_03 trade #2 (row 2)

```
side                                short
signal_time     2021-01-08 07:00:00+00:00
entry_time      2021-01-08 08:00:00+00:00
entry_price                   1895.429711
level                         1895.479711
initial_stop                     1907.298
final_stop                       1907.298
target                        1877.752277
exit_time       2021-01-08 13:39:00+00:00
exit_price                    1877.752277
exit_reason                        target
planned_risk                    11.818289
pnl_per_oz                      17.677434
realised_R                       1.495769
hold_minutes                        339.0
d1atr                           39.394297
k                                     0.3
session_open                     1907.298
bias                                 none

M1 bars around entry:
                               open      high       low     close
time_utc                                                         
2021-01-08 07:57:00+00:00  1906.128  1906.178  1904.568  1905.158
2021-01-08 07:58:00+00:00  1905.158  1905.518  1904.758  1905.008
2021-01-08 07:59:00+00:00  1904.928  1905.098  1904.318  1904.745
2021-01-08 08:00:00+00:00  1904.725  1904.725  1876.835  1887.958
2021-01-08 08:01:00+00:00  1887.995  1893.048  1884.676  1890.118
2021-01-08 08:02:00+00:00  1890.068  1897.808  1889.968  1894.358

M1 bars around exit:
                               open      high       low     close
time_utc                                                         
2021-01-08 13:37:00+00:00  1882.418  1882.518  1878.978  1880.188
2021-01-08 13:38:00+00:00  1880.198  1881.688  1880.080  1880.385
2021-01-08 13:39:00+00:00  1880.547  1880.808  1876.188  1876.968
2021-01-08 13:40:00+00:00  1876.968  1878.948  1876.915  1878.765
2021-01-08 13:41:00+00:00  1878.755  1881.838  1878.398  1879.708
```

Check: pnl = -1 × (1877.752 − 1895.430) − 0.0 = 17.677; R = 17.677 / 11.818 = +1.496 (recorded +1.496)

### V3_VB_03 trade #557 (min R)

```
side                                short
signal_time     2023-06-15 07:00:00+00:00
entry_time      2023-06-15 08:02:00+00:00
entry_price                    1930.39952
level                          1930.44952
initial_stop                     1937.598
final_stop                       1937.598
target                          1919.7268
exit_time       2023-06-15 15:00:00+00:00
exit_price                       1952.988
exit_reason                          stop
planned_risk                      7.14848
pnl_per_oz                      -22.58848
realised_R                        -3.1599
hold_minutes                        418.0
d1atr                           23.828267
k                                     0.3
session_open                     1937.598
bias                                 none

M1 bars around entry:
                               open      high       low     close
time_utc                                                         
2023-06-15 07:59:00+00:00  1932.425  1932.555  1932.215  1932.515
2023-06-15 08:00:00+00:00  1932.535  1932.865  1931.425  1931.425
2023-06-15 08:01:00+00:00  1931.395  1931.475  1930.535  1931.225
2023-06-15 08:02:00+00:00  1931.155  1931.345  1929.675  1929.715
2023-06-15 08:03:00+00:00  1929.765  1930.105  1929.355  1929.865
2023-06-15 08:04:00+00:00  1929.865  1930.455  1929.625  1930.365

M1 bars around exit:
                               open      high       low     close
time_utc                                                         
2023-06-15 13:58:00+00:00  1931.395  1932.195  1931.395  1931.645
2023-06-15 13:59:00+00:00  1931.665  1933.405  1931.665  1933.405
2023-06-15 15:00:00+00:00  1952.688  1952.958  1951.234  1952.775
2023-06-15 15:01:00+00:00  1952.805  1953.165  1952.235  1952.775
2023-06-15 15:02:00+00:00  1952.775  1953.525  1952.345  1952.598
```

Check: pnl = -1 × (1952.988 − 1930.400) − 0.0 = -22.588; R = -22.588 / 7.148 = -3.160 (recorded -3.160)

### V3_VW_2s trade #1 (row 1)

```
side                                 long
signal_time     2021-01-13 09:15:00+00:00
entry_time      2021-01-13 09:15:00+00:00
entry_price                      1850.108
level                            1850.108
initial_stop                  1846.819925
final_stop                    1846.819925
target                         1858.58787
exit_time       2021-01-13 13:41:00+00:00
exit_price                     1858.58787
exit_reason                        target
planned_risk                     3.288075
pnl_per_oz                        8.47987
realised_R                       2.578977
hold_minutes                        266.0
vwap                           1858.58787
band_sd                           1.85618
adx                             16.232935
atr                              2.708075

M1 bars around entry:
                               open      high       low     close
time_utc                                                         
2021-01-13 09:12:00+00:00  1854.735  1854.845  1850.078  1852.538
2021-01-13 09:13:00+00:00  1852.525  1852.688  1851.118  1851.168
2021-01-13 09:14:00+00:00  1851.218  1852.027  1849.528  1849.908
2021-01-13 09:15:00+00:00  1849.808  1851.432  1849.268  1851.105
2021-01-13 09:16:00+00:00  1851.135  1851.368  1849.328  1849.995
2021-01-13 09:17:00+00:00  1850.005  1851.518  1849.678  1851.415

M1 bars around exit:
                               open      high       low     close
time_utc                                                         
2021-01-13 13:39:00+00:00  1857.175  1857.917  1857.015  1857.458
2021-01-13 13:40:00+00:00  1857.458  1857.978  1857.395  1857.866
2021-01-13 13:41:00+00:00  1857.903  1859.043  1857.777  1858.892
2021-01-13 13:42:00+00:00  1858.885  1859.022  1858.305  1858.335
2021-01-13 13:43:00+00:00  1858.335  1859.008  1858.335  1858.958
```

Check: pnl = +1 × (1858.588 − 1850.108) − 0.0 = 8.480; R = 8.480 / 3.288 = +2.579 (recorded +2.579)

### V3_VW_2s trade #724 (min R)

```
side                                 long
signal_time     2024-02-02 13:30:00+00:00
entry_time      2024-02-02 13:30:00+00:00
entry_price                      2052.595
level                            2052.595
initial_stop                  2049.785657
final_stop                    2049.785657
target                        2054.822417
exit_time       2024-02-02 13:30:00+00:00
exit_price                       2041.125
exit_reason              stop_same_minute
planned_risk                     2.809343
pnl_per_oz                         -11.47
realised_R                      -4.082804
hold_minutes                          0.0
vwap                          2054.822417
band_sd                               1.0
adx                               11.5604
atr                              1.782343

M1 bars around entry:
                               open      high       low     close
time_utc                                                         
2024-02-02 13:27:00+00:00  2053.555  2053.725  2053.075  2053.095
2024-02-02 13:28:00+00:00  2053.025  2053.245  2052.705  2052.885
2024-02-02 13:29:00+00:00  2052.875  2053.078  2051.568  2052.315
2024-02-02 13:30:00+00:00  2052.295  2052.435  2041.175  2041.405
2024-02-02 13:31:00+00:00  2041.385  2045.895  2040.345  2045.175
2024-02-02 13:32:00+00:00  2045.175  2045.175  2043.145  2044.055

M1 bars around exit:
                               open      high       low     close
time_utc                                                         
2024-02-02 13:28:00+00:00  2053.025  2053.245  2052.705  2052.885
2024-02-02 13:29:00+00:00  2052.875  2053.078  2051.568  2052.315
2024-02-02 13:30:00+00:00  2052.295  2052.435  2041.175  2041.405
2024-02-02 13:31:00+00:00  2041.385  2045.895  2040.345  2045.175
2024-02-02 13:32:00+00:00  2045.175  2045.175  2043.145  2044.055
```

Check: pnl = +1 × (2041.125 − 2052.595) − 0.0 = -11.470; R = -11.470 / 2.809 = -4.083 (recorded -4.083)

### V3_DC_20_10 trade #3 (row 3)

```
side                                  long
signal_time      2021-04-07 23:00:00+00:00
entry_time       2021-04-08 14:32:00+00:00
entry_price                       1755.458
level                             1755.408
initial_stop                    1709.26928
final_stop                     1874.114312
exit_time        2021-06-03 14:32:00+00:00
exit_price                     1874.064312
exit_reason                     trail_stop
planned_risk                      46.13872
pnl_per_oz                      118.606312
realised_R                        2.570646
hold_minutes                       80640.0
d1atr                            21.185344
dc_exit_long                      1677.788
dc_exit_short                     1745.388

M1 bars around entry:
                               open      high       low     close
time_utc                                                         
2021-04-08 14:29:00+00:00  1752.575  1752.635  1752.115  1752.498
2021-04-08 14:30:00+00:00  1752.518  1753.118  1752.105  1753.005
2021-04-08 14:31:00+00:00  1753.005  1754.148  1752.915  1754.094
2021-04-08 14:32:00+00:00  1754.088  1755.168  1753.665  1754.258
2021-04-08 14:33:00+00:00  1754.248  1754.338  1753.348  1753.638
2021-04-08 14:34:00+00:00  1753.678  1753.728  1752.718  1752.728

M1 bars around exit:
                               open      high       low     close
time_utc                                                         
2021-06-03 14:30:00+00:00  1877.805  1877.805  1875.728  1877.198
2021-06-03 14:31:00+00:00  1877.198  1877.198  1875.518  1875.748
2021-06-03 14:32:00+00:00  1875.778  1875.778  1873.838  1874.858
2021-06-03 14:33:00+00:00  1874.878  1875.658  1873.058  1874.768
2021-06-03 14:34:00+00:00  1874.758  1874.758  1873.338  1874.405
```

Check: pnl = +1 × (1874.064 − 1755.458) − 0.0 = 118.606; R = 118.606 / 46.139 = +2.571 (recorded +2.571)

### V3_DC_20_10 trade #67 (max R)

```
side                                  long
signal_time      2025-08-27 23:00:00+00:00
entry_time       2025-08-28 13:11:00+00:00
entry_price                       3408.725
level                             3408.675
initial_stop                   3331.767571
final_stop                     3948.136468
exit_time        2025-10-09 18:16:00+00:00
exit_price                     3948.086468
exit_reason                     trail_stop
planned_risk                     76.907429
pnl_per_oz                      539.361468
realised_R                        7.013126
hold_minutes                       60785.0
d1atr                            56.971425
dc_exit_long                      3311.255
dc_exit_short                     3398.569

M1 bars around entry:
                               open      high       low     close
time_utc                                                         
2025-08-28 13:08:00+00:00  3407.365  3408.045  3407.135  3407.585
2025-08-28 13:09:00+00:00  3407.615  3408.335  3407.285  3407.865
2025-08-28 13:10:00+00:00  3407.835  3408.405  3407.195  3408.285
2025-08-28 13:11:00+00:00  3408.335  3408.515  3407.665  3408.205
2025-08-28 13:12:00+00:00  3408.245  3408.455  3406.095  3406.585
2025-08-28 13:13:00+00:00  3406.575  3406.745  3406.015  3406.345

M1 bars around exit:
                               open      high       low     close
time_utc                                                         
2025-10-09 18:14:00+00:00  3955.565  3956.515  3950.698  3951.755
2025-10-09 18:15:00+00:00  3951.775  3954.465  3951.698  3953.515
2025-10-09 18:16:00+00:00  3953.195  3953.365  3943.788  3945.675
2025-10-09 18:17:00+00:00  3945.695  3955.395  3945.615  3955.395
2025-10-09 18:18:00+00:00  3955.345  3961.595  3955.345  3961.595
```

Check: pnl = +1 × (3948.086 − 3408.725) − 0.0 = 539.361; R = 539.361 / 76.907 = +7.013 (recorded +7.013)

### V3_VW_2s_h15 trade #0 (row 0)

```
side                                short
signal_time     2021-01-06 08:45:00+00:00
entry_time      2021-01-06 08:45:00+00:00
entry_price                      1953.995
level                            1953.995
initial_stop                  1957.406532
final_stop                    1957.406532
target                        1947.444585
exit_time       2021-01-06 09:00:00+00:00
exit_price                       1953.075
exit_reason                      max_hold
planned_risk                     3.411532
pnl_per_oz                           0.92
realised_R                       0.269674
hold_minutes                         15.0
vwap                          1947.444585
band_sd                          2.464676
adx                             15.542074
atr                              3.108532

M1 bars around entry:
                               open      high       low     close
time_utc                                                         
2021-01-06 08:42:00+00:00  1953.145  1953.405  1952.398  1952.915
2021-01-06 08:43:00+00:00  1952.988  1952.988  1952.575  1952.695
2021-01-06 08:44:00+00:00  1952.589  1954.298  1952.558  1954.095
2021-01-06 08:45:00+00:00  1954.045  1954.355  1953.805  1954.165
2021-01-06 08:46:00+00:00  1954.165  1956.575  1954.155  1955.828
2021-01-06 08:47:00+00:00  1955.845  1956.028  1955.185  1955.299

M1 bars around exit:
                               open      high       low     close
time_utc                                                         
2021-01-06 08:57:00+00:00  1953.548  1954.025  1953.255  1953.645
2021-01-06 08:58:00+00:00  1953.605  1953.655  1952.979  1953.079
2021-01-06 08:59:00+00:00  1953.079  1953.378  1952.715  1952.775
2021-01-06 09:00:00+00:00  1952.795  1953.479  1952.785  1953.048
2021-01-06 09:01:00+00:00  1953.048  1953.609  1952.648  1953.439
```

Check: pnl = -1 × (1953.075 − 1953.995) − 0.0 = 0.920; R = 0.920 / 3.412 = +0.270 (recorded +0.270)

## 2. Automated per-trade checks

### V3_ORB_L10 — 870 trades, 0 failed checks

| check | passed | failed |
|---|---|---|
| entries_per_session_day_within_cap | 1 | 0 |
| realised_R_arithmetic | 870 | 0 |
| planned_risk_eq_level_minus_stop | 870 | 0 |
| geometry_stop_target_vs_entry | 870 | 0 |
| entry_after_signal | 870 | 0 |
| exit_same_session_day | 870 | 0 |
| stop_entry_reachable_and_fill_rule | 870 | 0 |
| orb_range_from_m1 | 870 | 0 |
| orb_level_is_edge_plus_offset | 870 | 0 |
| orb_range_ge_min | 870 | 0 |
| orb_stop_opposite_edge_capped | 870 | 0 |
| orb_target_mult_x_range | 870 | 0 |
| orb_entry_in_window | 870 | 0 |
| orb_d1atr_is_previous_day | 870 | 0 |
| target_exit_traded_through | 431 | 0 |
| target_exit_price_eq_target | 431 | 0 |
| stop_exit_reachable | 412 | 0 |
| stop_exit_price_le_stop_minus_slip | 215 | 0 |
| stop_exit_price_ge_stop_plus_slip | 197 | 0 |
| time_exit_at_or_after_2050 | 18 | 0 |
| time_exit_price_rule | 18 | 0 |
| session_gap_exit_is_first_bar_of_next_session | 9 | 0 |

### V3_ORB_L15 — 870 trades, 0 failed checks

| check | passed | failed |
|---|---|---|
| entries_per_session_day_within_cap | 1 | 0 |
| realised_R_arithmetic | 870 | 0 |
| planned_risk_eq_level_minus_stop | 870 | 0 |
| geometry_stop_target_vs_entry | 870 | 0 |
| entry_after_signal | 870 | 0 |
| exit_same_session_day | 870 | 0 |
| stop_entry_reachable_and_fill_rule | 870 | 0 |
| orb_range_from_m1 | 870 | 0 |
| orb_level_is_edge_plus_offset | 870 | 0 |
| orb_range_ge_min | 870 | 0 |
| orb_stop_opposite_edge_capped | 870 | 0 |
| orb_target_mult_x_range | 870 | 0 |
| orb_entry_in_window | 870 | 0 |
| orb_d1atr_is_previous_day | 870 | 0 |
| target_exit_traded_through | 328 | 0 |
| target_exit_price_eq_target | 328 | 0 |
| time_exit_at_or_after_2050 | 39 | 0 |
| time_exit_price_rule | 39 | 0 |
| stop_exit_reachable | 493 | 0 |
| stop_exit_price_le_stop_minus_slip | 260 | 0 |
| stop_exit_price_ge_stop_plus_slip | 233 | 0 |
| session_gap_exit_is_first_bar_of_next_session | 10 | 0 |

### V3_ORB_NY10 — 1043 trades, 0 failed checks

| check | passed | failed |
|---|---|---|
| entries_per_session_day_within_cap | 1 | 0 |
| realised_R_arithmetic | 1043 | 0 |
| planned_risk_eq_level_minus_stop | 1043 | 0 |
| geometry_stop_target_vs_entry | 1043 | 0 |
| entry_after_signal | 1043 | 0 |
| exit_same_session_day | 1043 | 0 |
| stop_entry_reachable_and_fill_rule | 1043 | 0 |
| orb_range_from_m1 | 1043 | 0 |
| orb_level_is_edge_plus_offset | 1043 | 0 |
| orb_range_ge_min | 1043 | 0 |
| orb_stop_opposite_edge_capped | 1043 | 0 |
| orb_target_mult_x_range | 1043 | 0 |
| orb_entry_in_window | 1043 | 0 |
| orb_d1atr_is_previous_day | 1043 | 0 |
| target_exit_traded_through | 428 | 0 |
| target_exit_price_eq_target | 428 | 0 |
| stop_exit_reachable | 391 | 0 |
| stop_exit_price_le_stop_minus_slip | 205 | 0 |
| stop_exit_price_ge_stop_plus_slip | 186 | 0 |
| time_exit_at_or_after_2050 | 220 | 0 |
| time_exit_price_rule | 220 | 0 |
| session_gap_exit_is_first_bar_of_next_session | 4 | 0 |

### V3_ORB_NY15 — 1045 trades, 0 failed checks

| check | passed | failed |
|---|---|---|
| entries_per_session_day_within_cap | 1 | 0 |
| realised_R_arithmetic | 1045 | 0 |
| planned_risk_eq_level_minus_stop | 1045 | 0 |
| geometry_stop_target_vs_entry | 1045 | 0 |
| entry_after_signal | 1045 | 0 |
| exit_same_session_day | 1045 | 0 |
| stop_entry_reachable_and_fill_rule | 1045 | 0 |
| orb_range_from_m1 | 1045 | 0 |
| orb_level_is_edge_plus_offset | 1045 | 0 |
| orb_range_ge_min | 1045 | 0 |
| orb_stop_opposite_edge_capped | 1045 | 0 |
| orb_target_mult_x_range | 1045 | 0 |
| orb_entry_in_window | 1045 | 0 |
| orb_d1atr_is_previous_day | 1045 | 0 |
| target_exit_traded_through | 295 | 0 |
| target_exit_price_eq_target | 295 | 0 |
| stop_exit_reachable | 422 | 0 |
| stop_exit_price_le_stop_minus_slip | 222 | 0 |
| stop_exit_price_ge_stop_plus_slip | 200 | 0 |
| time_exit_at_or_after_2050 | 323 | 0 |
| time_exit_price_rule | 323 | 0 |
| session_gap_exit_is_first_bar_of_next_session | 5 | 0 |

### V3_VB_03 — 1317 trades, 0 failed checks

| check | passed | failed |
|---|---|---|
| entries_per_session_day_within_cap | 1 | 0 |
| realised_R_arithmetic | 1317 | 0 |
| planned_risk_eq_level_minus_stop | 1317 | 0 |
| geometry_stop_target_vs_entry | 1317 | 0 |
| entry_after_signal | 1317 | 0 |
| exit_same_session_day | 1317 | 0 |
| stop_entry_reachable_and_fill_rule | 1317 | 0 |
| vb_session_open_is_first_bar_at_or_after_0700 | 1317 | 0 |
| vb_level_open_pm_k_atr | 1317 | 0 |
| vb_stop_is_open | 1317 | 0 |
| vb_target_1_5x | 1317 | 0 |
| vb_entry_window | 1317 | 0 |
| stop_exit_reachable | 642 | 0 |
| stop_exit_price_le_stop_minus_slip | 335 | 0 |
| time_exit_at_or_after_2050 | 307 | 0 |
| time_exit_price_rule | 307 | 0 |
| target_exit_traded_through | 352 | 0 |
| target_exit_price_eq_target | 352 | 0 |
| stop_exit_price_ge_stop_plus_slip | 307 | 0 |
| session_gap_exit_is_first_bar_of_next_session | 16 | 0 |

### V3_VB_05 — 777 trades, 0 failed checks

| check | passed | failed |
|---|---|---|
| entries_per_session_day_within_cap | 1 | 0 |
| realised_R_arithmetic | 777 | 0 |
| planned_risk_eq_level_minus_stop | 777 | 0 |
| geometry_stop_target_vs_entry | 777 | 0 |
| entry_after_signal | 777 | 0 |
| exit_same_session_day | 777 | 0 |
| stop_entry_reachable_and_fill_rule | 777 | 0 |
| vb_session_open_is_first_bar_at_or_after_0700 | 777 | 0 |
| vb_level_open_pm_k_atr | 777 | 0 |
| vb_stop_is_open | 777 | 0 |
| vb_target_1_5x | 777 | 0 |
| vb_entry_window | 777 | 0 |
| time_exit_at_or_after_2050 | 477 | 0 |
| time_exit_price_rule | 477 | 0 |
| target_exit_traded_through | 101 | 0 |
| target_exit_price_eq_target | 101 | 0 |
| stop_exit_reachable | 194 | 0 |
| stop_exit_price_ge_stop_plus_slip | 92 | 0 |
| stop_exit_price_le_stop_minus_slip | 102 | 0 |
| session_gap_exit_is_first_bar_of_next_session | 5 | 0 |

### V3_VB_03_bias — 664 trades, 0 failed checks

| check | passed | failed |
|---|---|---|
| entries_per_session_day_within_cap | 1 | 0 |
| realised_R_arithmetic | 664 | 0 |
| planned_risk_eq_level_minus_stop | 664 | 0 |
| geometry_stop_target_vs_entry | 664 | 0 |
| entry_after_signal | 664 | 0 |
| exit_same_session_day | 664 | 0 |
| stop_entry_reachable_and_fill_rule | 664 | 0 |
| vb_session_open_is_first_bar_at_or_after_0700 | 664 | 0 |
| vb_level_open_pm_k_atr | 664 | 0 |
| vb_stop_is_open | 664 | 0 |
| vb_target_1_5x | 664 | 0 |
| vb_entry_window | 664 | 0 |
| vb_bias_from_prev_day_sma200 | 664 | 0 |
| stop_exit_reachable | 316 | 0 |
| stop_exit_price_ge_stop_plus_slip | 64 | 0 |
| time_exit_at_or_after_2050 | 177 | 0 |
| time_exit_price_rule | 177 | 0 |
| stop_exit_price_le_stop_minus_slip | 252 | 0 |
| target_exit_traded_through | 164 | 0 |
| target_exit_price_eq_target | 164 | 0 |
| session_gap_exit_is_first_bar_of_next_session | 7 | 0 |

### V3_VB_05_bias — 338 trades, 0 failed checks

| check | passed | failed |
|---|---|---|
| entries_per_session_day_within_cap | 1 | 0 |
| realised_R_arithmetic | 338 | 0 |
| planned_risk_eq_level_minus_stop | 338 | 0 |
| geometry_stop_target_vs_entry | 338 | 0 |
| entry_after_signal | 338 | 0 |
| exit_same_session_day | 338 | 0 |
| stop_entry_reachable_and_fill_rule | 338 | 0 |
| vb_session_open_is_first_bar_at_or_after_0700 | 338 | 0 |
| vb_level_open_pm_k_atr | 338 | 0 |
| vb_stop_is_open | 338 | 0 |
| vb_target_1_5x | 338 | 0 |
| vb_entry_window | 338 | 0 |
| vb_bias_from_prev_day_sma200 | 338 | 0 |
| stop_exit_reachable | 76 | 0 |
| stop_exit_price_le_stop_minus_slip | 64 | 0 |
| time_exit_at_or_after_2050 | 220 | 0 |
| time_exit_price_rule | 220 | 0 |
| target_exit_traded_through | 39 | 0 |
| target_exit_price_eq_target | 39 | 0 |
| stop_exit_price_ge_stop_plus_slip | 12 | 0 |
| session_gap_exit_is_first_bar_of_next_session | 3 | 0 |

### V3_VW_2s — 1291 trades, 0 failed checks

| check | passed | failed |
|---|---|---|
| entries_per_session_day_within_cap | 1 | 0 |
| realised_R_arithmetic | 1291 | 0 |
| planned_risk_eq_level_minus_stop | 1291 | 0 |
| geometry_stop_target_vs_entry | 1291 | 0 |
| entry_after_signal | 1291 | 0 |
| exit_same_session_day | 1291 | 0 |
| vw_vwap_and_band_recomputed | 1291 | 0 |
| vw_signal_close_beyond_band | 1291 | 0 |
| vw_adx_below_max | 1291 | 0 |
| vw_target_is_vwap | 1291 | 0 |
| vw_entry_is_next_m1_bar | 1291 | 0 |
| vw_market_fill_rule | 1291 | 0 |
| vw_signal_in_window | 1291 | 0 |
| vw_stop_1atr_beyond_signal_bar_extreme | 1291 | 0 |
| stop_exit_reachable | 852 | 0 |
| stop_exit_price_ge_stop_plus_slip | 484 | 0 |
| target_exit_traded_through | 418 | 0 |
| target_exit_price_eq_target | 418 | 0 |
| stop_exit_price_le_stop_minus_slip | 368 | 0 |
| time_exit_at_or_after_2050 | 21 | 0 |
| time_exit_price_rule | 21 | 0 |

### V3_VW_25s — 963 trades, 0 failed checks

| check | passed | failed |
|---|---|---|
| entries_per_session_day_within_cap | 1 | 0 |
| realised_R_arithmetic | 963 | 0 |
| planned_risk_eq_level_minus_stop | 963 | 0 |
| geometry_stop_target_vs_entry | 963 | 0 |
| entry_after_signal | 963 | 0 |
| exit_same_session_day | 963 | 0 |
| vw_vwap_and_band_recomputed | 963 | 0 |
| vw_signal_close_beyond_band | 963 | 0 |
| vw_adx_below_max | 963 | 0 |
| vw_target_is_vwap | 963 | 0 |
| vw_entry_is_next_m1_bar | 963 | 0 |
| vw_market_fill_rule | 963 | 0 |
| vw_signal_in_window | 963 | 0 |
| vw_stop_1atr_beyond_signal_bar_extreme | 963 | 0 |
| stop_exit_reachable | 644 | 0 |
| stop_exit_price_ge_stop_plus_slip | 362 | 0 |
| target_exit_traded_through | 286 | 0 |
| target_exit_price_eq_target | 286 | 0 |
| stop_exit_price_le_stop_minus_slip | 282 | 0 |
| time_exit_at_or_after_2050 | 33 | 0 |
| time_exit_price_rule | 33 | 0 |

### V3_VW_2s_adx15 — 453 trades, 0 failed checks

| check | passed | failed |
|---|---|---|
| entries_per_session_day_within_cap | 1 | 0 |
| realised_R_arithmetic | 453 | 0 |
| planned_risk_eq_level_minus_stop | 453 | 0 |
| geometry_stop_target_vs_entry | 453 | 0 |
| entry_after_signal | 453 | 0 |
| exit_same_session_day | 453 | 0 |
| vw_vwap_and_band_recomputed | 453 | 0 |
| vw_signal_close_beyond_band | 453 | 0 |
| vw_adx_below_max | 453 | 0 |
| vw_target_is_vwap | 453 | 0 |
| vw_entry_is_next_m1_bar | 453 | 0 |
| vw_market_fill_rule | 453 | 0 |
| vw_signal_in_window | 453 | 0 |
| vw_stop_1atr_beyond_signal_bar_extreme | 453 | 0 |
| target_exit_traded_through | 148 | 0 |
| target_exit_price_eq_target | 148 | 0 |
| stop_exit_reachable | 301 | 0 |
| stop_exit_price_ge_stop_plus_slip | 179 | 0 |
| stop_exit_price_le_stop_minus_slip | 122 | 0 |
| time_exit_at_or_after_2050 | 4 | 0 |
| time_exit_price_rule | 4 | 0 |

### V3_DC_20_10 — 81 trades, 0 failed checks

| check | passed | failed |
|---|---|---|
| entries_per_session_day_within_cap | 1 | 0 |
| realised_R_arithmetic | 81 | 0 |
| planned_risk_eq_level_minus_stop | 81 | 0 |
| geometry_stop_target_vs_entry | 81 | 0 |
| entry_after_signal | 81 | 0 |
| stop_entry_reachable_and_fill_rule | 81 | 0 |
| dc_level_is_prev_N_day_extreme | 81 | 0 |
| dc_initial_stop_closer_of_exit_channel_and_2atr | 81 | 0 |
| dc_stop_only_ratchets | 81 | 0 |
| dc_signal_is_first_m15_bar_of_entry_day | 81 | 0 |
| stop_exit_reachable | 80 | 0 |
| stop_exit_price_ge_stop_plus_slip | 34 | 0 |
| stop_exit_price_le_stop_minus_slip | 46 | 0 |

### V3_DC_55_20 — 42 trades, 0 failed checks

| check | passed | failed |
|---|---|---|
| entries_per_session_day_within_cap | 1 | 0 |
| realised_R_arithmetic | 42 | 0 |
| planned_risk_eq_level_minus_stop | 42 | 0 |
| geometry_stop_target_vs_entry | 42 | 0 |
| entry_after_signal | 42 | 0 |
| stop_entry_reachable_and_fill_rule | 42 | 0 |
| dc_level_is_prev_N_day_extreme | 42 | 0 |
| dc_initial_stop_closer_of_exit_channel_and_2atr | 42 | 0 |
| dc_stop_only_ratchets | 42 | 0 |
| dc_signal_is_first_m15_bar_of_entry_day | 42 | 0 |
| stop_exit_reachable | 41 | 0 |
| stop_exit_price_le_stop_minus_slip | 31 | 0 |
| stop_exit_price_ge_stop_plus_slip | 10 | 0 |

### V3_ORB_L10_h15 — 870 trades, 0 failed checks

| check | passed | failed |
|---|---|---|
| entries_per_session_day_within_cap | 1 | 0 |
| realised_R_arithmetic | 870 | 0 |
| planned_risk_eq_level_minus_stop | 870 | 0 |
| geometry_stop_target_vs_entry | 870 | 0 |
| entry_after_signal | 870 | 0 |
| exit_same_session_day | 870 | 0 |
| stop_entry_reachable_and_fill_rule | 870 | 0 |
| orb_range_from_m1 | 870 | 0 |
| orb_level_is_edge_plus_offset | 870 | 0 |
| orb_range_ge_min | 870 | 0 |
| orb_stop_opposite_edge_capped | 870 | 0 |
| orb_target_mult_x_range | 870 | 0 |
| orb_entry_in_window | 870 | 0 |
| orb_d1atr_is_previous_day | 870 | 0 |
| max_hold_exit_price_is_close_rule | 848 | 0 |
| max_hold_minutes_eq_config | 848 | 0 |
| target_exit_traded_through | 12 | 0 |
| target_exit_price_eq_target | 12 | 0 |
| hold_le_max_hold_when_not_max_hold_exit | 22 | 0 |
| stop_exit_reachable | 10 | 0 |
| stop_exit_price_ge_stop_plus_slip | 5 | 0 |
| stop_exit_price_le_stop_minus_slip | 5 | 0 |

### V3_VB_03_h15 — 1317 trades, 0 failed checks

| check | passed | failed |
|---|---|---|
| entries_per_session_day_within_cap | 1 | 0 |
| realised_R_arithmetic | 1317 | 0 |
| planned_risk_eq_level_minus_stop | 1317 | 0 |
| geometry_stop_target_vs_entry | 1317 | 0 |
| entry_after_signal | 1317 | 0 |
| exit_same_session_day | 1317 | 0 |
| stop_entry_reachable_and_fill_rule | 1317 | 0 |
| vb_session_open_is_first_bar_at_or_after_0700 | 1317 | 0 |
| vb_level_open_pm_k_atr | 1317 | 0 |
| vb_stop_is_open | 1317 | 0 |
| vb_target_1_5x | 1317 | 0 |
| vb_entry_window | 1317 | 0 |
| max_hold_exit_price_is_close_rule | 1261 | 0 |
| max_hold_minutes_eq_config | 1261 | 0 |
| target_exit_traded_through | 19 | 0 |
| target_exit_price_eq_target | 19 | 0 |
| hold_le_max_hold_when_not_max_hold_exit | 36 | 0 |
| stop_exit_reachable | 37 | 0 |
| stop_exit_price_ge_stop_plus_slip | 18 | 0 |
| stop_exit_price_le_stop_minus_slip | 19 | 0 |

### V3_VW_2s_h15 — 1439 trades, 0 failed checks

| check | passed | failed |
|---|---|---|
| entries_per_session_day_within_cap | 1 | 0 |
| realised_R_arithmetic | 1439 | 0 |
| planned_risk_eq_level_minus_stop | 1439 | 0 |
| geometry_stop_target_vs_entry | 1439 | 0 |
| entry_after_signal | 1439 | 0 |
| exit_same_session_day | 1439 | 0 |
| vw_vwap_and_band_recomputed | 1439 | 0 |
| vw_signal_close_beyond_band | 1439 | 0 |
| vw_adx_below_max | 1439 | 0 |
| vw_target_is_vwap | 1439 | 0 |
| vw_entry_is_next_m1_bar | 1439 | 0 |
| vw_market_fill_rule | 1439 | 0 |
| vw_signal_in_window | 1439 | 0 |
| vw_stop_1atr_beyond_signal_bar_extreme | 1439 | 0 |
| max_hold_exit_price_is_close_rule | 1162 | 0 |
| max_hold_minutes_eq_config | 1162 | 0 |
| stop_exit_reachable | 243 | 0 |
| stop_exit_price_le_stop_minus_slip | 114 | 0 |
| hold_le_max_hold_when_not_max_hold_exit | 269 | 0 |
| stop_exit_price_ge_stop_plus_slip | 129 | 0 |
| target_exit_traded_through | 34 | 0 |
| target_exit_price_eq_target | 34 | 0 |

## 3. Summary

| variant | trades | failed checks | exit reasons |
|---|---|---|---|
| V3_ORB_L10 | 870 | 0 | {'target': 431, 'stop': 412, 'time_exit': 18, 'session_gap_exit': 9} |
| V3_ORB_L15 | 870 | 0 | {'stop': 493, 'target': 328, 'time_exit': 39, 'session_gap_exit': 10} |
| V3_ORB_NY10 | 1043 | 0 | {'target': 428, 'stop': 391, 'time_exit': 220, 'session_gap_exit': 4} |
| V3_ORB_NY15 | 1045 | 0 | {'stop': 422, 'time_exit': 323, 'target': 295, 'session_gap_exit': 5} |
| V3_VB_03 | 1317 | 0 | {'stop': 622, 'target': 352, 'time_exit': 307, 'stop_same_minute': 20, 'session_gap_exit': 16} |
| V3_VB_05 | 777 | 0 | {'time_exit': 477, 'stop': 188, 'target': 101, 'stop_same_minute': 6, 'session_gap_exit': 5} |
| V3_VB_03_bias | 664 | 0 | {'stop': 302, 'time_exit': 177, 'target': 164, 'stop_same_minute': 14, 'session_gap_exit': 7} |
| V3_VB_05_bias | 338 | 0 | {'time_exit': 220, 'stop': 72, 'target': 39, 'stop_same_minute': 4, 'session_gap_exit': 3} |
| V3_VW_2s | 1291 | 0 | {'stop': 843, 'target': 418, 'time_exit': 21, 'stop_same_minute': 9} |
| V3_VW_25s | 963 | 0 | {'stop': 636, 'target': 286, 'time_exit': 33, 'stop_same_minute': 8} |
| V3_VW_2s_adx15 | 453 | 0 | {'stop': 296, 'target': 148, 'stop_same_minute': 5, 'time_exit': 4} |
| V3_DC_20_10 | 81 | 0 | {'trail_stop': 80, 'end_of_data': 1} |
| V3_DC_55_20 | 42 | 0 | {'trail_stop': 41, 'end_of_data': 1} |
| V3_ORB_L10_h15 | 870 | 0 | {'max_hold': 848, 'target': 12, 'stop': 10} |
| V3_VB_03_h15 | 1317 | 0 | {'max_hold': 1261, 'stop_same_minute': 20, 'target': 19, 'stop': 17} |
| V3_VW_2s_h15 | 1439 | 0 | {'max_hold': 1162, 'stop': 235, 'target': 34, 'stop_same_minute': 8} |

## 4. Problems

None.

## 5. Known approximations

- Data has no volume: the F3 'VWAP' is a time-weighted average of M1 closes (TWAP) from the 23:00 UTC session start.
- Session day = 23:00 → 23:00 UTC (engine_v2.daily_frame); the day label is the calendar date on which the session ends. D1 ATR(14) is a Wilder EWM from the first day of data (early values are rough; all inside the development period).
- The feed has no bar when no tick occurred and has occasional intraday gaps of 10–60 minutes; a stop that falls inside such a gap is filled at the next available open (max(stop, open) + slippage), exactly as in engine.py / engine_v2.py.
- 62 session days end before 20:50 UTC (early closes, feed outages). engine_v3 closes intraday positions at the first bar of the next session day ('session_gap_exit') and cancels pending orders ('CANCEL_session_ended'); engine_v2 lets such positions run into the next day. This is a v3-only correction, noted in VALIDATION_REPORT_v3.md.
- stop_same_minute (fill and stop in the same M1 bar) uses the engine_v2 convention: long exits at the bar low − slippage when the low is below the stop, short at stop + slippage.
- F2 'NY' ORB uses fixed UTC times (13:30–14:00); the NY equity open is 13:30 UTC only during US DST, 14:30 UTC in winter.
- F4 holds overnight and over weekends; an open F4 position at the end of the data is closed at the last bar ('end_of_data', one trade).
- A stop or market order whose first available fill (after a feed gap or a news bar) is already beyond the planned stop or target is NOT taken ('SKIP_gap_fill_past_stop/target', counter gap_fill_skipped). Booking such a fill with the planned geometry produced wrong R signs in the first run (a short filled above its stop, then 'stopped' at a profit). engine_v2 Trigger C has the same exposure in principle; none of its trades hit it.
- 21 US-DST-switch Sundays appear in the feed as a 60-bar pseudo session day (22:00-22:59 UTC); they enter engine_v2.daily_frame (shared, unchanged) as tiny daily bars and slightly depress the D1 ATR / rolling channels around those dates.
