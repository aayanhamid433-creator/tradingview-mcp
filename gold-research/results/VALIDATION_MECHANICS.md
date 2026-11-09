# Mechanics validation of the backtest engine (GOLD_PLAYBOOK v1.0)

This validates the simulator's bookkeeping, not profitability.

## 1. Indicator cross-check (independent loop implementation vs engine)

| indicator | max abs difference over all bars |
|---|---|
| ADX | 7.11e-14 |
| plusDI | 4.26e-14 |
| minusDI | 4.26e-14 |
| ATR | 4.26e-14 |
| EMA | 0.00e+00 |

ADX range 5.5–78.9; share of M15 bars with ADX>30: 29.3%

## 2. P&L arithmetic checks

| side | level | stop | entry fill | exit | commission | expected R | computed R |
|---|---|---|---|---|---|---|---|
| long | 2000.1 | 1995.1 | 2000.15 | 1995.05 | 0.0 | -1.0200 | -1.0200 |
| long | 2000.1 | 1995.1 | 2000.15 | 2010.0 | 0.0 | 1.9700 | 1.9700 |
| short | 1999.9 | 2004.9 | 1999.85 | 2004.95 | 0.0 | -1.0200 | -1.0200 |
| short | 1999.9 | 2004.9 | 1999.85 | 1990.0 | 0.07 | 1.9560 | 1.9560 |

A stopped trade with 0.05 slippage realises −1.02 R (loss exceeds the planned 1 R), as intended.

## 3. Independent re-derivation of every V0_base trade from raw M1 data

Trades checked: 477

| check | passed | failed |
|---|---|---|
| signal_conditions | 477 | 0 |
| entry_level | 477 | 0 |
| entry_minute | 477 | 0 |
| stop_rule | 477 | 0 |
| geometry | 477 | 0 |
| exit_rule | 477 | 0 |
| exit_price | 477 | 0 |
| pnl_sign | 477 | 0 |

Notes: the engine's stop uses the lowest low from the first touch bar through the fill minute (the verifier recomputes it from M1 lows directly);
short-side stop/target tests use ask = bid + spread; exits are re-derived by scanning M1 bars after the entry minute.

## 4. Hand-check examples (development period)

### Trade: short signalled by M15 bar opening 2021-01-08 14:00:00+00:00 (ADX 51.8, +DI 9.5, −DI 27.0, EMA20 1890.26, bar H/L 1892.63/1886.26)

- Entry stop level 1886.16; filled 2021-01-08 14:25:00+00:00 at 1886.11; stop 1893.14; target 1876.19; planned risk 6.98 USD/oz; exit 2021-01-08 14:42:00+00:00 at 1876.19 (target); realised +1.42 R

M1 bars around the entry (bid):

| time (UTC) | open | high | low | close |
|---|---|---|---|---|
| 2021-01-08 14:23 | 1887.69 | 1887.84 | 1887.18 | 1887.22 |
| 2021-01-08 14:24 | 1887.12 | 1887.56 | 1886.53 | 1886.84 |
| 2021-01-08 14:25 | 1886.79 | 1887.39 | 1885.72 | 1886.27 |
| 2021-01-08 14:26 | 1886.27 | 1887.28 | 1885.76 | 1886.17 |

M1 bars around the exit (bid):

| time (UTC) | open | high | low | close |
|---|---|---|---|---|
| 2021-01-08 14:40 | 1880.55 | 1880.64 | 1878.51 | 1879.19 |
| 2021-01-08 14:41 | 1879.24 | 1879.72 | 1878.60 | 1879.19 |
| 2021-01-08 14:42 | 1879.24 | 1879.29 | 1872.13 | 1873.47 |
| 2021-01-08 14:43 | 1873.47 | 1874.21 | 1871.41 | 1871.83 |

### Trade: short signalled by M15 bar opening 2021-01-14 07:15:00+00:00 (ADX 36.9, +DI 15.7, −DI 28.5, EMA20 1842.21, bar H/L 1842.22/1838.85)

- Entry stop level 1838.75; filled 2021-01-14 07:42:00+00:00 at 1838.70; stop 1842.54; target 1828.52; planned risk 3.80 USD/oz; exit 2021-01-14 07:58:00+00:00 at 1842.59 (stop); realised -1.03 R

M1 bars around the entry (bid):

| time (UTC) | open | high | low | close |
|---|---|---|---|---|
| 2021-01-14 07:40 | 1839.44 | 1839.44 | 1839.02 | 1839.12 |
| 2021-01-14 07:41 | 1839.12 | 1839.35 | 1838.99 | 1839.24 |
| 2021-01-14 07:42 | 1839.16 | 1839.23 | 1838.54 | 1838.61 |
| 2021-01-14 07:43 | 1838.62 | 1838.86 | 1836.94 | 1837.53 |

M1 bars around the exit (bid):

| time (UTC) | open | high | low | close |
|---|---|---|---|---|
| 2021-01-14 07:56 | 1840.31 | 1841.40 | 1840.31 | 1841.21 |
| 2021-01-14 07:57 | 1841.24 | 1842.27 | 1841.24 | 1842.07 |
| 2021-01-14 07:58 | 1842.07 | 1842.33 | 1841.69 | 1842.32 |
| 2021-01-14 07:59 | 1842.32 | 1842.35 | 1841.38 | 1842.14 |

### Trade: short signalled by M15 bar opening 2022-02-15 14:15:00+00:00 (ADX 50.4, +DI 19.6, −DI 24.9, EMA20 1854.45, bar H/L 1857.03/1853.42)

- Entry stop level 1853.32; filled 2022-02-15 14:30:00+00:00 at 1853.27; stop 1857.42; target 1844.40; planned risk 4.09 USD/oz; exit 2022-02-15 20:50:00+00:00 at 1853.64 (time_exit); realised -0.09 R

M1 bars around the entry (bid):

| time (UTC) | open | high | low | close |
|---|---|---|---|---|
| 2022-02-15 14:28 | 1855.68 | 1855.95 | 1855.10 | 1855.21 |
| 2022-02-15 14:29 | 1855.23 | 1855.23 | 1853.63 | 1853.63 |
| 2022-02-15 14:30 | 1853.68 | 1854.18 | 1852.44 | 1853.17 |
| 2022-02-15 14:31 | 1853.17 | 1853.42 | 1851.71 | 1852.11 |

M1 bars around the exit (bid):

| time (UTC) | open | high | low | close |
|---|---|---|---|---|
| 2022-02-15 20:48 | 1853.36 | 1853.55 | 1853.36 | 1853.47 |
| 2022-02-15 20:49 | 1853.47 | 1853.73 | 1853.08 | 1853.27 |
| 2022-02-15 20:50 | 1853.34 | 1853.59 | 1853.20 | 1853.33 |
| 2022-02-15 20:51 | 1853.32 | 1853.39 | 1852.70 | 1852.72 |
