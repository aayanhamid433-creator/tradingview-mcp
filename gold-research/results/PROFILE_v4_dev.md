# PROFILE v4 — XAUUSD intraday behaviour, DEVELOPMENT PERIOD ONLY

Generated 2026-11-12 19:23 UTC by backtest/profile_v4_dev.py. Data: HistData M1 BID, cut to 2021-01-03 23:00 .. 2024-07-01 00:00 (exclusive) before any computation; session days 2021-01-04 .. 2024-06-28. Descriptive only; no strategy was run and nothing was tuned. Validation and test periods were not loaded.

## 0. Data, clock and coverage

- Bars in the cut: 1,192,460; kept 1,189,109 after dropping 3,351 bars (Sunday one-hour stubs on DST-mismatch weeks, the 2024-07-01 one-hour stub, and 22:00-22:59 bars that the 23:00 session rule assigns to the wrong day).
- Weekday session days: 901 (3.48 calendar years, 259 session days per year). Complete days (>= 1300 of 1380 M1 bars): 761; incomplete: 140 (feed gaps, 119 of them in 2023, where whole alternating hours are missing on many days between February and July). Window statistics below use a day only when the bars at both window boundaries exist; hour statistics use hours with >= 45 bars.
- DST-mismatch days (US daylight time on, EU off: mid/late March and late Oct/early Nov): 59. On those days the daily break is at 21:00-22:00 and the US 08:30 ET releases land at 12:30 on this clock instead of 13:30; they are kept (the engines keep them too).

**The dataset clock is London local time, not UTC.** HistData stamps are documented as fixed EST, but the mean 1-minute range at the minute of the 08:30 ET data releases (and the 08:20 ET COMEX open, 10:00 ET releases) sits at the same clock minute in summer and winter, and the daily break (17:00-18:00 New York) sits at 22:00-23:00 in every month except the DST-mismatch weeks. Both are impossible on a true UTC axis and exactly what a clock following EU daylight time (GMT/BST) produces. Consequences: the project's "07:00 UTC" London open is 07:00 London time all year; "13:30 UTC" is 08:30 New York all year (except mismatch weeks); the 20:50 time exit is 15:50 New York; the LBMA auctions (10:30 / 15:00 London) are at 10:30 / 15:00 on this clock all year. The times in this report are on this clock.

| months | 12:20 | 12:30 | 13:20 | 13:30 | 14:00 | 15:00 | 21:59 | 22:00 | 23:00 |
|---|---|---|---|---|---|---|---|---|---|
| Apr-Sep (BST) | 0.514 | 0.601 | 1.553 | 2.807 | 1.443 | 2.270 | 0.526 | n/a | 1.282 |
| Nov-Feb (GMT) | 0.537 | 0.681 | 1.367 | 2.632 | 1.210 | 1.957 | 0.445 | n/a | 1.294 |

Mean 1-minute bar range (USD) at the named minute: the 13:30 / 15:00 spikes and the empty 22:00 minute do not move between seasons.

| year | session days | complete | incomplete | DST-mismatch | mean close | median day range | median D1 ATR14 |
|---|---|---|---|---|---|---|---|
| 2021 | 258 | 250 | 8 | 15 | 1799 | 21.1 | 23.5 |
| 2022 | 258 | 250 | 8 | 15 | 1801 | 23.1 | 24.8 |
| 2023 | 257 | 138 | 119 | 15 | 1943 | 20.6 | 23.6 |
| 2024 | 128 | 123 | 5 | 14 | 2207 | 28.0 | 28.3 |

## 1. M15 close-to-close returns by hour, weekday and session block; fixed-time trades

Per-bar return = close minus the previous M15 close when the previous bar is the consecutive bar of the same session day; for the first bar of a day (and a bar after a feed gap) it is close minus open, so the day's bars sum to the session open-to-close move. Hours are the bar's OPEN hour on the dataset clock; session order 23:00 -> 21:00.

### 1a. By hour of day (per M15 bar) and the matching one-hour fixed-time trade

| hour | bars | mean USD/bar | median | mean bp/bar | median bp | t (bar) | days | hour trade mean USD | t (day) | 95% CI | net long (-0.25) | net short (-0.25) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 23 | 3367 | +0.108 | +0.060 | +0.54 | +0.30 | +3.2 | 797 | +0.44 | +3.8 | [+0.22, +0.67] | +0.19 | -0.69 |
| 00 | 3404 | +0.033 | +0.020 | +0.19 | +0.11 | +1.7 | 851 | +0.10 | +1.4 | [-0.04, +0.25] | -0.15 | -0.35 |
| 01 | 3604 | -0.010 | -0.013 | -0.05 | -0.07 | -0.4 | 901 | -0.04 | -0.5 | [-0.22, +0.14] | -0.29 | -0.21 |
| 02 | 3604 | +0.038 | +0.014 | +0.20 | +0.07 | +1.4 | 901 | +0.15 | +1.3 | [-0.09, +0.37] | -0.10 | -0.40 |
| 03 | 3604 | +0.018 | -0.002 | +0.10 | -0.01 | +0.9 | 901 | +0.07 | +0.9 | [-0.09, +0.23] | -0.18 | -0.32 |
| 04 | 3604 | -0.009 | -0.010 | -0.05 | -0.05 | -0.6 | 900 | -0.03 | -0.5 | [-0.15, +0.09] | -0.28 | -0.22 |
| 05 | 3600 | +0.002 | -0.020 | +0.01 | -0.11 | +0.1 | 900 | +0.01 | +0.1 | [-0.12, +0.15] | -0.24 | -0.26 |
| 06 | 3600 | +0.016 | +0.019 | +0.10 | +0.10 | +0.7 | 900 | +0.06 | +0.7 | [-0.10, +0.22] | -0.19 | -0.31 |
| 07 | 3600 | -0.003 | +0.010 | -0.01 | +0.05 | -0.1 | 899 | -0.00 | -0.0 | [-0.20, +0.21] | -0.25 | -0.25 |
| 08 | 3596 | -0.027 | -0.040 | -0.13 | -0.20 | -0.9 | 896 | -0.10 | -0.9 | [-0.33, +0.11] | -0.35 | -0.15 |
| 09 | 3588 | -0.017 | +0.000 | -0.10 | +0.00 | -0.6 | 880 | -0.07 | -0.7 | [-0.27, +0.12] | -0.32 | -0.18 |
| 10 | 3532 | +0.032 | +0.020 | +0.17 | +0.11 | +1.4 | 829 | +0.09 | +1.0 | [-0.10, +0.27] | -0.16 | -0.34 |
| 11 | 3373 | -0.031 | -0.040 | -0.18 | -0.21 | -1.2 | 792 | -0.17 | -1.6 | [-0.38, +0.03] | -0.42 | -0.08 |
| 12 | 3364 | -0.038 | -0.016 | -0.17 | -0.09 | -1.3 | 801 | -0.14 | -1.4 | [-0.35, +0.06] | -0.39 | -0.11 |
| 13 | 3408 | +0.026 | +0.014 | +0.12 | +0.08 | +0.5 | 794 | +0.08 | +0.4 | [-0.34, +0.51] | -0.17 | -0.33 |
| 14 | 3348 | -0.051 | -0.010 | -0.24 | -0.06 | -1.0 | 796 | -0.14 | -0.7 | [-0.56, +0.29] | -0.39 | -0.11 |
| 15 | 3404 | +0.017 | +0.075 | +0.09 | +0.40 | +0.3 | 791 | +0.06 | +0.3 | [-0.37, +0.48] | -0.19 | -0.31 |
| 16 | 3348 | +0.021 | +0.055 | +0.13 | +0.29 | +0.6 | 793 | +0.11 | +0.7 | [-0.20, +0.39] | -0.14 | -0.36 |
| 17 | 3363 | -0.054 | -0.040 | -0.31 | -0.19 | -1.9 | 783 | -0.21 | -1.7 | [-0.46, +0.03] | -0.46 | -0.04 |
| 18 | 3336 | +0.050 | +0.000 | +0.25 | +0.00 | +1.8 | 783 | +0.15 | +1.3 | [-0.07, +0.37] | -0.10 | -0.40 |
| 19 | 3290 | +0.014 | +0.000 | +0.07 | +0.00 | +0.5 | 770 | +0.08 | +0.6 | [-0.18, +0.34] | -0.17 | -0.33 |
| 20 | 3284 | -0.033 | -0.030 | -0.17 | -0.15 | -1.5 | 731 | -0.16 | -1.6 | [-0.34, +0.03] | -0.41 | -0.09 |
| 21 | 3080 | -0.013 | -0.019 | -0.07 | -0.09 | -0.8 | 770 | -0.05 | -0.7 | [-0.17, +0.08] | -0.30 | -0.20 |

### 1b. By weekday of the session day

| weekday | bars | mean USD/bar | median | mean bp/bar | median bp | t (bar) | days | session open->close | t | 95% CI | 07:00->20:50 | t | 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Mon | 15415 | -0.013 | -0.030 | -0.07 | -0.17 | -0.9 | 161 | -1.39 | -1.1 | [-3.74, +1.09] | -0.71 | -0.6 | [-2.72, +1.42] |
| Tue | 16096 | -0.000 | +0.000 | +0.00 | +0.00 | -0.0 | 173 | -0.17 | -0.1 | [-2.47, +2.05] | -1.28 | -1.2 | [-3.39, +0.83] |
| Wed | 16106 | +0.014 | +0.007 | +0.08 | +0.04 | +1.0 | 171 | +1.46 | +1.2 | [-0.97, +3.78] | +0.90 | +0.8 | [-1.28, +3.00] |
| Thu | 16064 | +0.004 | +0.010 | +0.01 | +0.06 | +0.3 | 169 | +1.37 | +1.0 | [-1.18, +3.98] | -0.08 | -0.1 | [-2.38, +2.32] |
| Fri | 15620 | +0.015 | +0.030 | +0.09 | +0.15 | +1.0 | 167 | +1.40 | +0.9 | [-1.65, +4.19] | -0.76 | -0.5 | [-3.72, +2.25] |

### 1c. By session block (per M15 bar) and the block 'buy at open, sell at close' trade (0.25 spread per round trip subtracted)

| block | bars | mean USD/bar | median | mean bp/bar | median bp | t (bar) | days | trade mean USD | mean bp | median | sd | t (day) | 95% CI | net long/trade | net short/trade | cum net long | cum net short |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Asia 23:00-07:00 | 28387 | +0.024 | +0.010 | +0.13 | +0.05 | +2.9 | 840 | +0.80 | +4.3 | +0.66 | 6.26 | +3.7 | [+0.38, +1.22] | +0.55 | -1.05 | +464 | -884 |
| London 07:00-12:00 | 17689 | -0.009 | -0.010 | -0.05 | -0.05 | -0.8 | 841 | -0.14 | -0.8 | -0.11 | 6.86 | -0.6 | [-0.61, +0.30] | -0.39 | -0.11 | -327 | -94 |
| NY 12:00-20:50 | 29324 | -0.005 | +0.000 | -0.02 | +0.00 | -0.4 | 805 | -0.38 | -1.8 | -0.94 | 13.53 | -0.8 | [-1.33, +0.55] | -0.63 | +0.13 | -508 | +105 |
| late 20:50-END | 3901 | -0.014 | -0.013 | -0.08 | -0.07 | -0.9 | 821 | -0.02 | -0.1 | -0.07 | 1.94 | -0.3 | [-0.15, +0.12] | -0.27 | -0.23 | -220 | -191 |
| 07:00-20:50 (intraday window) | - | - | - | - | - | - | 821 | -0.38 | -1.8 | -0.56 | 15.44 | -0.7 | [-1.43, +0.65] | -0.63 | +0.13 | -516 | +106 |
| session open -> close | - | - | - | - | - | - | 841 | +0.55 | +3.0 | +1.23 | 16.87 | +0.9 | [-0.56, +1.67] | +0.30 | -0.80 | +250 | -670 |

Cumulative columns: sum over all development session days of (move - 0.25) for always-long and (-move - 0.25) for always-short.

### 1d. Block trade mean by year (USD/oz per day, t in brackets)

| block | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|
| Asia 23:00-07:00 | +1.03 (+2.9) n=255 | -0.02 (-0.1) n=258 | +1.38 (+3.7) n=199 | +1.11 (+1.6) n=128 |
| London 07:00-12:00 | -0.69 (-1.9) n=257 | -0.19 (-0.4) n=258 | +0.31 (+0.8) n=198 | +0.39 (+0.5) n=128 |
| NY 12:00-20:50 | -0.44 (-0.6) n=251 | +0.01 (+0.0) n=250 | -1.09 (-1.1) n=181 | -0.00 (-0.0) n=123 |
| late 20:50-END | -0.26 (-2.0) n=251 | +0.19 (+1.7) n=250 | -0.21 (-2.2) n=197 | +0.35 (+1.4) n=123 |
| 07:00-20:50 (intraday window) | -1.18 (-1.4) n=251 | -0.15 (-0.1) n=250 | -0.12 (-0.1) n=197 | +0.37 (+0.2) n=123 |
| session open -> close | -0.34 (-0.4) n=256 | +0.01 (+0.0) n=258 | +1.53 (+1.3) n=199 | +1.88 (+1.0) n=128 |

## 2. London fix windows (LBMA auctions 10:30 and 15:00 London time = 10:30 and 15:00 on this clock all year)

| window | days | mean USD/oz | median | sd | t | 95% CI (boot) | share > 0 | mean bp | net long | net short | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 07:00 -> 10:30 (London open to AM fix) | 883 | -0.25 | -0.06 | 6.01 | -1.2 | [-0.64, +0.15] | 49% | -1.3 | -0.50 | -0.00 | -0.68 | +0.02 | -0.15 | -0.13 |
| 10:30 -> 15:00 (AM fix to PM fix) | 839 | +0.00 | -0.06 | 9.92 | +0.0 | [-0.62, +0.66] | 50% | +0.1 | -0.25 | -0.25 | -0.53 | -0.02 | +0.81 | -0.12 |
| 15:00 -> 20:50 (PM fix to time exit) | 784 | +0.15 | +0.04 | 9.88 | +0.4 | [-0.52, +0.83] | 50% | +0.8 | -0.10 | -0.40 | +0.02 | -0.18 | +0.37 | +0.82 |
| 10:00 -> 10:30 (30 min before AM fix) | 883 | -0.07 | -0.14 | 2.04 | -1.0 | [-0.20, +0.07] | 46% | -0.3 | -0.32 | -0.18 | -0.37 | +0.19 | -0.05 | -0.01 |
| 10:30 -> 11:00 (30 min after AM fix) | 829 | +0.19 | +0.18 | 1.86 | +3.0 | [+0.07, +0.32] | 56% | +1.0 | -0.06 | -0.44 | +0.24 | +0.10 | +0.18 | +0.30 |
| 14:30 -> 15:00 (30 min before PM fix) | 796 | -0.08 | +0.03 | 4.70 | -0.5 | [-0.41, +0.25] | 51% | -0.3 | -0.33 | -0.17 | -0.42 | +0.39 | -0.03 | -0.42 |
| 15:00 -> 15:30 (30 min after PM fix) | 851 | +0.07 | -0.10 | 4.64 | +0.4 | [-0.25, +0.39] | 49% | +0.4 | -0.18 | -0.32 | +0.14 | +0.07 | -0.04 | +0.08 |

## 3. Continuation (sign of an earlier move -> mean of the later move)

### 3a. First London hour 07:00-08:00 -> rest of day 08:00-20:50

| window | days | mean USD/oz | median | sd | t | 95% CI (boot) | share > 0 | net of 0.30 in the implied direction |
|---|---|---|---|---|---|---|---|---|
| 08:00-20:50 given 07:00-08:00 up | 388 | -0.48 | -1.66 | 14.16 | -0.7 | [-1.88, +0.99] | 46% | +0.18 (short) |
| 08:00-20:50 given 07:00-08:00 down | 433 | -0.29 | +0.07 | 16.08 | -0.4 | [-1.78, +1.25] | 50% | -0.01 (short) |
| follow: sign(07:00-08:00) x 08:00-20:50 | 821 | -0.07 | -0.64 | 15.20 | -0.1 | [-1.15, +1.01] | 48% | -0.37 |
| follow, abs(07:00-08:00) >= median (1.68) | 411 | -0.26 | -1.39 | 15.86 | -0.3 | [-1.84, +1.20] | 46% | -0.56 |

Pearson correlation of the two moves: -0.022 (t -0.6, n=821); mean 08:00-20:50 unconditional -0.38.

### 3b. 12:00-13:00 -> 13:00-20:50

| window | days | mean USD/oz | median | sd | t | 95% CI (boot) | share > 0 | net of 0.30 in the implied direction |
|---|---|---|---|---|---|---|---|---|
| 13:00-20:50 given 12:00-13:00 up | 378 | -0.63 | -0.92 | 13.14 | -0.9 | [-1.93, +0.67] | 46% | +0.33 (short) |
| 13:00-20:50 given 12:00-13:00 down | 398 | +0.45 | -0.04 | 13.27 | +0.7 | [-0.88, +1.79] | 50% | +0.15 |
| follow: sign(12:00-13:00) x 13:00-20:50 | 776 | -0.54 | -0.48 | 13.20 | -1.1 | [-1.45, +0.44] | 48% | -0.84 |
| follow, abs(12:00-13:00) >= median (1.70) | 388 | -0.55 | +0.01 | 13.80 | -0.8 | [-1.94, +0.80] | 50% | -0.85 |

Pearson correlation of the two moves: -0.023 (t -0.6, n=776); mean 13:00-20:50 unconditional -0.07.

### 3c. Previous session day close-to-close -> next day 07:00-20:50

| window | days | mean USD/oz | median | sd | t | 95% CI (boot) | share > 0 | net of 0.30 in the implied direction |
|---|---|---|---|---|---|---|---|---|
| next 07:00-20:50 given prev day c-to-c up | 414 | -0.99 | -0.66 | 15.10 | -1.3 | [-2.50, +0.50] | 47% | +0.69 (short) |
| next 07:00-20:50 given prev day c-to-c down | 405 | +0.18 | -0.37 | 15.78 | +0.2 | [-1.35, +1.62] | 49% | -0.12 |
| follow: sign(prev day c-to-c) x next 07:00-20:50 | 819 | -0.59 | -0.29 | 15.43 | -1.1 | [-1.66, +0.49] | 49% | -0.89 |
| follow, abs(prev day c-to-c) >= median (9.15) | 410 | -0.55 | +0.12 | 15.91 | -0.7 | [-2.15, +0.98] | 50% | -0.85 |

Pearson correlation of the two moves: -0.007 (t -0.2, n=819); mean next 07:00-20:50 unconditional -0.41.

### 3c'. Previous session day open-to-close -> next day 07:00-20:50

| window | days | mean USD/oz | median | sd | t | 95% CI (boot) | share > 0 | net of 0.30 in the implied direction |
|---|---|---|---|---|---|---|---|---|
| next 07:00-20:50 given prev day o-to-c up | 425 | -0.96 | -0.67 | 15.00 | -1.3 | [-2.46, +0.46] | 47% | +0.66 (short) |
| next 07:00-20:50 given prev day o-to-c down | 395 | +0.19 | -0.31 | 15.88 | +0.2 | [-1.33, +1.82] | 49% | -0.11 |
| follow: sign(prev day o-to-c) x next 07:00-20:50 | 820 | -0.59 | -0.33 | 15.43 | -1.1 | [-1.66, +0.46] | 49% | -0.89 |
| follow, abs(prev day o-to-c) >= median (9.03) | 410 | -0.70 | +0.32 | 15.85 | -0.9 | [-2.29, +0.83] | 50% | -1.00 |

Pearson correlation of the two moves: -0.012 (t -0.3, n=820); mean next 07:00-20:50 unconditional -0.40.

### 3d. Previous day's close location value (CLV = (close - low) / (high - low)) -> next day's moves

| prev-day CLV bin | days | next 07:00->20:50 mean | t | 95% CI | next session open->close mean | t | 95% CI |
|---|---|---|---|---|---|---|---|
| (0.0, 0.2] | 181 | -0.23 | -0.2 | [-2.35, +1.99] | +0.15 | +0.1 | [-2.43, +2.67] |
| (0.2, 0.4] | 176 | +0.39 | +0.3 | [-1.90, +2.74] | +2.15 | +1.7 | [-0.30, +4.53] |
| (0.4, 0.6] | 142 | -0.38 | -0.3 | [-2.81, +2.07] | +0.93 | +0.6 | [-2.14, +3.72] |
| (0.6, 0.8] | 142 | -1.44 | -1.2 | [-3.81, +0.93] | -0.73 | -0.6 | [-3.46, +1.67] |
| (0.8, 1.0] | 179 | -0.56 | -0.5 | [-2.95, +1.73] | -0.03 | -0.0 | [-2.49, +2.21] |

Correlation prev-day CLV vs next 07:00-20:50 move: -0.020. Unconditional next 07:00-20:50 mean -0.38 USD, session open->close mean +0.55 USD.

## 4. Autocorrelation, variance ratios, intraday range development, NR7 / inside days

### 4a. Autocorrelation of within-session returns (consecutive bars of the same session day only)

| series | pairs | rho | naive t (rho sqrt N) | robust t (HC0) | slope: next bar per 1 USD |
|---|---|---|---|---|---|
| M15 lag 1 | 76411 | -0.0135 | -3.7 | -1.6 | -1.34% |
| M15 lag 2 | 74968 | +0.0056 | +1.5 | +0.8 | +0.56% |
| M15 lag 3 | 73525 | -0.0051 | -1.4 | -0.7 | -0.50% |
| M15 lag 4 | 72539 | -0.0023 | -0.6 | -0.4 | -0.23% |
| H1 lag 1 | 17386 | -0.0054 | -0.7 | -0.4 | -0.54% |
| H1 lag 2 | 16473 | +0.0143 | +1.8 | +1.3 | +1.42% |
| H1 lag 3 | 15569 | -0.0205 | -2.6 | -1.8 | -2.05% |
| H1 lag 4 | 14666 | +0.0173 | +2.1 | +1.7 | +1.74% |

### 4b. Variance ratios VR(q) = Var(q-bar return) / (q x Var(1-bar return)), within session days; z = Lo-MacKinlay heteroskedasticity-robust

| series | VR(q) | robust z |
|---|---|---|
| M15 (q bars of 15 min) q=1 | 1.000 | - |
| M15 (q bars of 15 min) q=2 | 0.987 | -1.5 |
| M15 (q bars of 15 min) q=3 | 0.986 | -1.1 |
| M15 (q bars of 15 min) q=4 | 0.983 | -1.1 |
| M15 (q bars of 15 min) q=5 | 0.981 | -1.1 |
| M15 (q bars of 15 min) q=6 | 0.980 | -1.1 |
| M15 (q bars of 15 min) q=7 | 0.979 | -1.0 |
| M15 (q bars of 15 min) q=8 | 0.976 | -1.1 |
| H1 (q hours) q=1 | 1.000 | - |
| H1 (q hours) q=2 | 0.995 | -0.4 |
| H1 (q hours) q=3 | 1.002 | +0.1 |
| H1 (q hours) q=4 | 0.996 | -0.1 |
| H1 (q hours) q=5 | 0.999 | -0.0 |
| H1 (q hours) q=6 | 1.002 | +0.1 |
| H1 (q hours) q=7 | 1.005 | +0.2 |
| H1 (q hours) q=8 | 1.010 | +0.3 |

VR below 1 = mean reversion at that horizon, above 1 = momentum (positive autocorrelation); |z| > 2 is the usual significance mark.

### 4c. Intraday range as a share of the previous session day's range, by hour (hours with >= 45 bars; previous-day range from the daily frame)

| hour (open) | hours | hour range / prev day range: median | mean | session range so far / prev day range: median | mean | share with session range >= prev day range |
|---|---|---|---|---|---|---|
| 23:00 | 840 | 0.101 | 0.133 | 0.10 | 0.13 | 0% |
| 00:00 | 850 | 0.105 | 0.124 | 0.15 | 0.18 | 0% |
| 01:00 | 900 | 0.148 | 0.174 | 0.21 | 0.25 | 1% |
| 02:00 | 900 | 0.172 | 0.204 | 0.28 | 0.33 | 1% |
| 03:00 | 900 | 0.132 | 0.154 | 0.31 | 0.37 | 2% |
| 04:00 | 900 | 0.106 | 0.123 | 0.33 | 0.39 | 3% |
| 05:00 | 899 | 0.116 | 0.132 | 0.35 | 0.41 | 3% |
| 06:00 | 899 | 0.145 | 0.171 | 0.38 | 0.45 | 4% |
| 07:00 | 899 | 0.187 | 0.213 | 0.43 | 0.50 | 5% |
| 08:00 | 898 | 0.203 | 0.236 | 0.48 | 0.55 | 8% |
| 09:00 | 896 | 0.179 | 0.208 | 0.52 | 0.59 | 10% |
| 10:00 | 882 | 0.161 | 0.185 | 0.54 | 0.62 | 12% |
| 11:00 | 842 | 0.161 | 0.189 | 0.58 | 0.65 | 13% |
| 12:00 | 840 | 0.181 | 0.218 | 0.61 | 0.70 | 17% |
| 13:00 | 851 | 0.349 | 0.435 | 0.72 | 0.84 | 28% |
| 14:00 | 836 | 0.370 | 0.431 | 0.80 | 0.94 | 35% |
| 15:00 | 850 | 0.323 | 0.407 | 0.89 | 1.04 | 42% |
| 16:00 | 836 | 0.235 | 0.280 | 0.90 | 1.06 | 43% |
| 17:00 | 839 | 0.177 | 0.207 | 0.93 | 1.09 | 45% |
| 18:00 | 831 | 0.172 | 0.201 | 0.95 | 1.11 | 47% |
| 19:00 | 815 | 0.133 | 0.186 | 0.98 | 1.14 | 49% |
| 20:00 | 820 | 0.126 | 0.156 | 1.00 | 1.15 | 50% |
| 21:00 | 769 | 0.089 | 0.110 | 1.01 | 1.17 | 50% |

### 4d. NR7 and inside days -> next day's range

| condition (day d) | days | frequency | range(d+1)/range(d): median | range(d+1)/ATR14(d): median | mean | share range(d+1) > ATR14(d) | abs(open->close)(d+1)/ATR14(d): median |
|---|---|---|---|---|---|---|---|
| all days | 900 | 100.0% | 0.99 | 0.90 | 1.00 | 40% | 0.37 |
| NR7 | 126 | 14.0% | 1.68 | 0.94 | 1.00 | 44% | 0.38 |
| inside day | 125 | 13.9% | 1.39 | 0.91 | 1.04 | 44% | 0.39 |
| NR7 and inside | 45 | 5.0% | 1.81 | 0.97 | 1.02 | 47% | 0.40 |
| not NR7 | 774 | 86.0% | 0.91 | 0.90 | 1.00 | 39% | 0.36 |

NR7 = range of day d is the narrowest of the last seven session days. The ratio to the day's own range is mechanically > 1 after a narrow day; the ATR-normalised columns are the fair test of 'expansion'.

## 5. Mean reversion

### 5a. After an hour whose open-to-close move is >= k x ATR14(M15): the next hour's move (close of the signal hour -> close of the next hour)

| k | subset | hours | events/yr | days/yr | mean next-hour move in prior direction | median | t | 95% CI | share continuing | net follow (-0.30) | net fade (-0.30) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.5 | all hours | 3783 | 1087 | 255 | -0.07 | -0.10 | -1.0 | [-0.21, +0.07] | 49% | -0.37 | -0.23 |
| 1.5 | signal hour ends 07:00-19:00 | 2627 | 755 | 245 | +0.00 | -0.06 | +0.0 | [-0.17, +0.18] | 49% | -0.30 | -0.30 |
| 2.0 | all hours | 2007 | 577 | 234 | -0.19 | -0.19 | -1.8 | [-0.40, +0.02] | 47% | -0.49 | -0.11 |
| 2.0 | signal hour ends 07:00-19:00 | 1453 | 418 | 212 | -0.09 | -0.15 | -0.7 | [-0.35, +0.16] | 48% | -0.39 | -0.21 |
| 3.0 | all hours | 546 | 157 | 122 | -0.18 | -0.23 | -0.7 | [-0.68, +0.33] | 48% | -0.48 | -0.12 |
| 3.0 | signal hour ends 07:00-19:00 | 422 | 121 | 99 | +0.14 | +0.06 | +0.5 | [-0.42, +0.71] | 51% | -0.16 | -0.44 |

Reference: mean |next-hour move| over all complete hours 2.29 USD; mean ATR14(M15) 2.28 USD; hours with move >= 2 ATR: 10.9% of hours.

### 5b. Distance from the session TWAP (engine_v3.session_twap, from 23:00) at the hour end, in ATR14(M15) units, deciles -> next-hour move

| decile | distance range (ATR) | mean distance | hours | mean next-hour move USD | t | 95% CI | mean move toward TWAP | net fade (-0.30) |
|---|---|---|---|---|---|---|---|---|
| 1 | -10.47 .. -3.22 | -4.60 | 1072 | -0.12 | -0.8 | [-0.39, +0.15] | -0.12 | -0.42 |
| 2 | -3.22 .. -2.08 | -2.61 | 1072 | +0.00 | +0.0 | [-0.24, +0.25] | +0.00 | -0.30 |
| 3 | -2.08 .. -1.29 | -1.68 | 1072 | -0.07 | -0.6 | [-0.30, +0.15] | -0.07 | -0.37 |
| 4 | -1.29 .. -0.62 | -0.95 | 1072 | -0.21 | -1.8 | [-0.45, +0.01] | -0.21 | -0.51 |
| 5 | -0.62 .. +0.00 | -0.32 | 1072 | +0.02 | +0.2 | [-0.22, +0.26] | +0.04 | -0.26 |
| 6 | +0.00 .. +0.68 | +0.36 | 1072 | -0.09 | -0.8 | [-0.33, +0.13] | +0.09 | -0.21 |
| 7 | +0.68 .. +1.38 | +1.03 | 1072 | +0.31 | +2.8 | [+0.10, +0.52] | -0.31 | -0.61 |
| 8 | +1.39 .. +2.19 | +1.77 | 1072 | +0.15 | +1.2 | [-0.08, +0.39] | -0.15 | -0.45 |
| 9 | +2.20 .. +3.39 | +2.76 | 1072 | +0.07 | +0.5 | [-0.17, +0.33] | -0.07 | -0.37 |
| 10 | +3.39 .. +11.98 | +4.70 | 1072 | -0.28 | -2.0 | [-0.57, -0.02] | +0.28 | -0.02 |

Correlation of TWAP distance with the next-hour move: +0.005 over 10720 hours (a negative value means reversion toward the TWAP).

### 5c. Position relative to the previous session day's high (PDH) and low (PDL) at the hour end -> next-hour move (hour ends 07:00-19:00)

| position of the close vs previous day's range | hours | per year | mean next-hour move | median | t | 95% CI | share up |
|---|---|---|---|---|---|---|---|
| below PDL by > 25% of range | 866 | 249 | -0.34 | -0.24 | -2.1 | [-0.64, -0.03] | 47% |
| 0-25% of range below PDL | 725 | 208 | +0.10 | +0.05 | +0.6 | [-0.20, +0.39] | 51% |
| lowest quarter of prev range | 1623 | 466 | +0.07 | +0.06 | +0.7 | [-0.12, +0.25] | 51% |
| second quarter | 1950 | 560 | -0.12 | -0.05 | -1.4 | [-0.28, +0.05] | 49% |
| third quarter | 1980 | 569 | +0.14 | +0.06 | +1.6 | [-0.03, +0.30] | 51% |
| top quarter | 1629 | 468 | +0.05 | -0.03 | +0.5 | [-0.14, +0.23] | 50% |
| 0-25% of range above PDH | 930 | 267 | -0.13 | +0.05 | -0.9 | [-0.39, +0.13] | 51% |
| above PDH by > 25% of range | 1004 | 289 | -0.15 | -0.02 | -1.0 | [-0.47, +0.13] | 49% |

| distance to the level (ATR14 M15) | hours | per year | mean next-hour move | median | t | 95% CI | share up |
|---|---|---|---|---|---|---|---|
| within 0.3 ATR of PDH | 286 | 82 | +0.23 | +0.10 | +0.9 | [-0.26, +0.72] | 51% |
| within 0.3 ATR of PDL | 273 | 78 | +0.35 | +0.43 | +1.4 | [-0.13, +0.84] | 56% |
| above PDH by > 0.3 ATR | 1801 | 518 | -0.15 | -0.01 | -1.4 | [-0.35, +0.05] | 50% |
| below PDL by > 0.3 ATR | 1454 | 418 | -0.19 | -0.17 | -1.6 | [-0.43, +0.04] | 48% |

## 6. Every registered pattern with |t| > 2 or a 95 % CI excluding zero, sized net of a 0.30 USD round trip

96 patterns were registered in sections 1-5; at |t| > 2 about 4.4 of them would pass by chance alone with no edge. 6 pass. The trade direction is the sign of the in-sample mean (long if positive, short if negative), chosen after seeing it. 'net' = |mean| - 0.30 USD per oz per trade; 'events/yr' = events per calendar year in the development data and 'session days/yr' = distinct session days per year on which the pattern fires (hour-level patterns cluster on days, and their t treats every hour as independent, so it is overstated where events/yr is much larger than session days/yr); 'same-sign years' = number of the 4 development years (2024 = Jan-Jun) whose mean has the same sign as the overall mean.

| section | pattern | direction | events | events/yr | session days/yr | mean USD/oz | sd | t | 95% CI | net of 0.30 | covers cost | same-sign years | mean by year |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1a hour trade | 23:00 -> 00:00 | long | 797 | 229 | 229 | +0.44 | 3.30 | +3.8 | [+0.22, +0.67] | +0.14 | yes | 4/4 | 2021:+0.11 2022:+0.24 2023:+1.13 2024:+0.67 |
| 1c block trade | Asia 23:00-07:00 | long | 840 | 241 | 241 | +0.80 | 6.26 | +3.7 | [+0.38, +1.22] | +0.50 | yes | 3/4 | 2021:+1.03 2022:-0.02 2023:+1.38 2024:+1.11 |
| 2 fix window | 10:30 -> 11:00 (30 min after AM fix) | long | 829 | 238 | 238 | +0.19 | 1.86 | +3.0 | [+0.07, +0.32] | -0.11 | no | 4/4 | 2021:+0.24 2022:+0.10 2023:+0.18 2024:+0.30 |
| 5b TWAP decile | next-hour move, TWAP-distance decile 7 (mean dist +1.03 ATR) | long | 1072 | 308 | 157 | +0.31 | 3.65 | +2.8 | [+0.10, +0.52] | +0.01 | yes | 4/4 | 2021:+0.10 2022:+0.72 2023:+0.06 2024:+0.28 |
| 5c PDH/PDL position | next-hour move, below PDL by > 25% of range | short | 866 | 249 | 48 | -0.34 | 4.69 | -2.1 | [-0.64, -0.03] | +0.04 | yes | 4/4 | 2021:-0.30 2022:-0.25 2023:-0.14 2024:-1.03 |
| 5b TWAP decile | next-hour move, TWAP-distance decile 10 (mean dist +4.70 ATR) | short | 1072 | 308 | 94 | -0.28 | 4.63 | -2.0 | [-0.57, -0.02] | -0.02 | no | 4/4 | 2021:-0.42 2022:-0.01 2023:-0.33 2024:-0.50 |

Patterns that both pass and cover the 0.30 cost on average: 4 of 6. Those with the same sign in every development year: 3.

Plain-language reading of this table:

- The only patterns above |t| = 3 are two faces of one thing: the long drift in the Asian block and in its first hour (23:00-00:00, the hour after the daily break). That hour alone contributes +0.44 of the block's +0.80 USD/day (55%), and it is the hour where the constant 0.25 spread is least realistic (reopen spreads are several times wider). 2022, the one development year in which gold did not rise, shows none of it.
- No 15-minute hold covers costs anywhere in the day: the largest mean M15 return of any hour is +0.108 USD (hour 23), a tenth of a 0.30 round trip. Every fixed-time trade that clears 0.30 holds for one hour or longer, in the Asian session.
- None of the continuation tests (section 3) and none of the after-a-large-move tests (5a) pass; the TWAP-decile and PDH/PDL hits are single bins with no monotonic pattern across neighbouring bins and |t| of 2.0-2.8, exactly what 4-5 false positives among 96 tests look like.

## 7. Do the well-known gold intraday effects show up in the development data?

| effect | development data | shows up? | note |
|---|---|---|---|
| Asian-session drift (price rises 23:00-07:00) | +0.80 USD/day (+4.3 bp), t +3.7, CI [+0.38, +1.22], n=840 | YES | net long after 0.25 spread +0.55 USD/day; by year 2021:+1.03 2022:-0.02 2023:+1.38 2024:+1.11; +0.44 of it is the 23:00-00:00 reopen hour; absent in 2022 when gold was flat, so it reads as the up-trend expressed in Asian hours |
| AM-fix to PM-fix decline (10:30 -> 15:00 falls) | +0.00 USD/day (+0.1 bp), t +0.0, CI [-0.62, +0.66], n=839, share of days negative 50% | NO (not distinguishable from zero) | net short after 0.25 spread -0.25 USD/day; by year 2021:-0.53 2022:-0.02 2023:+0.81 2024:-0.12 |
| Overnight (daily-break gap) vs intraday (open -> close) split | gap +0.04 USD/day (t +0.6), cumulative +32 USD; intraday +0.55 USD/day (t +0.9), cumulative +460 USD | neither part is distinguishable from zero | the gap is a 1-hour break (3 days at weekends); it is not tradable (no fills during the break, wide spreads at the reopen) |
| Non-US hours vs US hours (23:00 -> 12:00 vs 12:00 -> close) | 23:00-12:00 +0.62 USD/day (t +1.9); 12:00-close -0.45 USD/day (t -1.0) | NO clean split | London 07:00-12:00 alone -0.14 (t -0.6); NY 12:00-20:50 alone -0.38 (t -0.8) |

## 8. Caveats

- In-sample description of 3.5 years dominated by a rising gold price (mean close by year in section 0); any long-biased number partly measures that trend, which is not a repeatable intraday edge. The t-statistics assume independent days; overlapping windows within a day are not independent.
- Spread is a constant 0.25 (BASE_CONFIG). Real spreads are wider in Asia, around the daily break and around releases; Asia and 'late' block figures are therefore optimistic. No slippage is charged in sections 1-5 (engine_v3 charges 0.05 per fill).
- 2023 Feb-Jul has many days with missing hours; window figures skip days whose boundary bars are absent, hour figures skip thin hours, so the 2023 counts are lower. The feed clock is London local time (section 0); the US-anchored measures are shifted by one hour on the DST-mismatch days.
- Section 6 performs many comparisons; the count of expected false positives is stated there. Nothing in this profile was tuned, and the validation / final-test periods were not loaded.
