# VALIDATION REPORT v5 — "mark the highs and lows, trade the break" (Aayan's idea), 2026-11-13

Status: **UNVALIDATED. No variant passes the pre-registered rule.** The improved variants are clearly better than the
original on the 28 held-out months and are regime-dependent: money in 2022, 2024, 2025 and 2026, losses in 2021 and 2023.
Best so far: HL_C_W01 (§10). Lower-timeframe entries are rejected (§11). Written by the main session; the planned adversarial agent verification could not run (usage limit) and is
replaced here by an independent replay and direct checks (§5). It is still to be run.

## 1. The idea and how it was frozen

Aayan, 2026-11-13: "mark the high and lows of the chart and when it breaks from either, buy or sell", to trade day to
day. Frozen before any run in results/PREREGISTRATION_v5_hl.md as six readings: a marked high and a marked low, a buy
stop 0.10 above the high and a sell stop 0.10 below the low between 07:00 and 16:00 London time (one cancels the other),
stop at the opposite marked level clamped to [0.3 x ATR14(M15), 0.6 x D1ATR], flat at 20:50. A level that price has
traded through is used up (no chasing). Levels are the last confirmed M15 swing high/low (pivot N = 5 or 10, confirmed
only N bars later) or the previous session day's high/low. Exit at 1.5 x risk or on a 3 x ATR trail.

After Aayan ran the Pine version (87 trades, PF 1.05) and asked for more profitability, eight improvement variants were
frozen in results/PREREGISTRATION_v5b_hl_improve.md before being run. Their hypotheses come from the development period
only (§4). The six readings' held-out results had been seen by then; that contamination is part of the record.

## 2. Method

Engine backtest/engine_v5_hl.py (M15 decisions, M1 fills, bid data with ask = bid + 0.25, slippage 0.05 per fill, stop
first on ambiguity, gap-fill rule, session-gap exit; mechanics copied from engine_v3). Periods by signal bar: development
2021-01-04 to 2024-07-01, validation to 2025-09-01, final test to 2026-11-01. 1 R = the planned risk of one trade.
Session times are on the dataset clock, which is London local time (PROJECT_STATE.md, clock correction).

## 3. The six frozen readings

| reading | development n / mean R / PF / max DD | validation | final test | held-out mean R [90 % CI] | trades per day |
|---|---|---|---|---|---|
| HL_SW5_RR (the Pine script's first default) | 1,276 / -0.005 / 0.99 / -70 R | 407 / -0.007 / 0.99 / -19 R | 367 / +0.048 / 1.10 / -31 R | +0.019 [-0.043, +0.083] | 1.27 |
| HL_SW5_TRAIL | 1,698 / -0.045 / 0.88 / -88 R | 545 / -0.047 / 0.87 / -42 R | 484 / -0.016 / 0.96 / -43 R | -0.032 [-0.084, +0.020] | 1.69 |
| HL_SW10_RR | 941 / -0.048 / 0.90 / -82 R | 282 / +0.112 / 1.30 / -8 R | 273 / +0.067 / 1.18 / -18 R | +0.090 [+0.024, +0.157] | 0.91 |
| HL_PD_RR | 394 / -0.010 / 0.97 / -20 R | 99 / +0.065 / 1.25 / -5 R | 78 / +0.099 / 1.39 / -4 R | +0.080 [-0.014, +0.175] | 0.29 |
| HL_PD_TRAIL | 394 / -0.037 / 0.79 / -18 R | 99 / +0.021 / 1.12 / -3 R | 78 / +0.085 / 1.58 / -3 R | +0.050 [-0.009, +0.111] | 0.29 |
| HL_SW5_RR_BIAS | 672 / -0.031 / 0.94 / -70 R | 286 / +0.000 / 1.00 / -15 R | 267 / +0.073 / 1.16 / -10 R | +0.035 [-0.038, +0.113] | 0.91 |

Reading. The original idea (small swings, 1.5 R target) trades on 97 % of days and is break-even over six years. In
development 39.3 % of its trades reached the 1.5 R target before the stop; a coin flip gives 40.0 %. The median stop was
6.5 USD, so the 0.35 USD round trip cost 0.054 R per trade, about the whole gross edge. The trailing exit is worse than
the target. Bigger swings and previous-day levels are positive on the held-out months and negative in development.
In the window of Aayan's TradingView run (2026-08-02 to 2026-10-30 in this data) the engine has 76 trades, +0.047 R,
PF 1.11, against his 87 trades and PF 1.05 to 2026-11-13: the script and the engine agree.

## 4. Improvement round (v5b, eight variants frozen before running)

Development-period splits of HL_SW5_RR that motivated them: stops tighter than 0.10 x D1ATR lost 0.66 R per trade (36
trades); breaks against the M15 EMA50 lost 0.087 R (328 trades) and breaks with it made 0.023 R (948); ADX above 25 was
worse than below; levels younger than an hour were worse than older ones. None of these splits had |t| above about 2.

Filters: MS = skip a side whose stop is nearer than 0.10 x D1ATR; T = buy side only above EMA50(M15), sell side only
below; Q = no orders when ADX14(M15) > 25; A = level at least 60 minutes old; H = no orders 07:00-08:00 and 13:00-14:00;
EOD = no target, exit at 20:50.

| variant | development n / mean R / PF / max DD | validation | final test | held-out mean R [90 % CI] | trades per day |
|---|---|---|---|---|---|
| HL_IMP_MS | 1,241 / +0.017 / 1.03 / -61 R | 397 / +0.014 / 1.03 / -13 R | 362 / +0.056 / 1.12 / -31 R | +0.034 [-0.029, +0.098] | 1.24 |
| HL_IMP_MS_T | 1,073 / -0.009 / 0.98 / -66 R | 358 / +0.072 / 1.16 / -12 R | 308 / +0.075 / 1.17 / -18 R | +0.073 [+0.007, +0.141] | 1.09 |
| HL_IMP_MS_T_Q | 787 / -0.001 / 1.00 / -57 R | 267 / +0.080 / 1.17 / -8 R | 233 / +0.055 / 1.12 / -16 R | +0.069 [-0.010, +0.148] | 0.82 |
| HL_IMP_MS_T_A | 731 / +0.025 / 1.05 / -44 R | 233 / +0.046 / 1.10 / -11 R | 212 / +0.111 / 1.26 / -6 R | +0.077 [-0.005, +0.161] | 0.73 |
| HL_IMP_MS_T_H | 853 / +0.003 / 1.01 / -64 R | 301 / +0.036 / 1.08 / -11 R | 265 / +0.028 / 1.06 / -21 R | +0.032 [-0.039, +0.105] | 0.93 |
| HL_IMP_MS_T_Q_A | 548 / +0.009 / 1.02 / -34 R | 186 / +0.039 / 1.08 / -10 R | 163 / +0.107 / 1.25 / -8 R | +0.071 [-0.023, +0.164] | 0.57 |
| HL_IMP_MS_EOD | 1,139 / -0.007 / 0.99 / -62 R | 372 / +0.008 / 1.02 / -17 R | 338 / +0.028 / 1.05 / -41 R | +0.018 [-0.066, +0.103] | 1.16 |
| **HL_IMP10_MS_T** (N = 10 + MS + T) | 859 / -0.034 / 0.93 / -56 R | 264 / +0.139 / 1.39 / -8 R | 247 / +0.102 / 1.29 / -10 R | **+0.121 [+0.051, +0.191]** | 0.84 |

The trend filter is the change that mattered: it lifts the held-out profit factor from about 1.04 to 1.17 on small
swings and from 1.24 to 1.34 on big swings. The hour filter, the ADX filter and the end-of-day exit did not help.

## 5. Checks on HL_IMP10_MS_T (the best variant)

- **Independent replay.** backtest/verify_v5_replay.py (written from the pre-registration, no engine import) reproduces
  the trade lists of HL_SW5_RR and HL_SW10_RR exactly (2,050 and 1,496 trades). backtest/verify_v5b_replay.py, with the
  two filters and the EMA re-implemented by hand, reproduces HL_IMP_MS, HL_IMP_MS_T and HL_IMP10_MS_T exactly (2,000,
  1,739 and 1,370 trades). The six frozen readings are unchanged by the filter code (regression identical).
- **Costs doubled** (spread 0.50, slippage 0.10): held-out +0.101 R, PF 1.28, max DD -9.9 R (base +0.121, 1.34, -10.2).
- **Parameter shifts** (pivot 8 / 12, offset, stop cap, stop floor, target 1.2 / 1.8, minimum stop, entries per day, one
  at a time): 14 of 14 keep a positive held-out mean, range +0.079 to +0.128 R. Without the trend filter: +0.090 R.
- **Both directions** make money on the held-out months: 287 buys at +0.108 R, 224 sells at +0.137 R.
- **Not a few lucky days:** the best 10 of 485 traded days carry 26 % of the held-out profit; mean R without the five
  best trades is +0.107. 75 % of the 28 held-out months are positive; worst month -3.0 R, best +8.1 R, median +1.1 R.
  Longest losing streak 6 trades. 52 % winners, average win 0.91 R, average loss 0.73 R; 49 % of trades end at the
  20:50 time exit, 28 % at the stop, 21 % at the target.
- **By year (all six years):**

| year | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| trades | 247 | 249 | 239 | 243 | 223 | 169 |
| mean R | -0.069 | +0.031 | -0.124 | +0.074 | +0.136 | +0.135 |
| total R | -17.1 | +7.8 | -29.6 | +17.9 | +30.4 | +22.8 |
| mean cost drag (0.35 USD / stop) | 0.044 R | 0.043 R | 0.050 R | 0.033 R | 0.018 R | 0.010 R |

  Development as a whole: -0.034 R, PF 0.93, max DD -56 R. About 0.03 R of the later improvement is the fixed spread
  becoming small against wider stops as gold's price and range rose; the rest is the market trending more. Within the
  development period the result does not depend on the daily volatility level (quartiles of D1ATR / price: +0.012,
  -0.099, -0.061, +0.011 R), so no volatility switch is supported by the data.

## 6. Verdict against the pre-registered rule

No variant passes: every one has a development mean R at or below about zero or a drawdown beyond 10 R.
"Better than the base, not tradable at 0.5 % risk": HL_IMP10_MS_T, HL_IMP_MS_T, HL_SW10_RR, HL_IMP_MS_T_Q.
"No improvement": HL_IMP_MS, HL_IMP_MS_T_H, HL_IMP_MS_EOD and the trail exit. HL_PD_RR and HL_IMP_MS_T_A, HL_IMP_MS_T_Q_A
are positive on small samples with confidence intervals that include zero.

## 7. What it means for Aayan

- The original breakout is a coin flip after costs. Filters cannot fix a coin flip; what changed the result was trading
  bigger swings, only in the direction of the 15-minute trend.
- HL_IMP10_MS_T on the 28 held-out months: 511 trades (18 a month, a trade on 80 % of days), +61.7 R in total. At
  0.25 % risk (125 USD per R) that is about +275 USD a month with a worst drawdown of 1,275 USD (2.5 %). At 0.5 % risk
  the drawdown is 2,550 USD (5.1 %), inside the account guard's halt zone, so 0.5 % is too large for the 6 % trailing rule.
- In a 2021- or 2023-type market the same rules lost 17 R and 30 R in a year, and the development drawdown was 56 R
  (14 % of the account at 0.25 % risk). The system cannot tell in advance which kind of year it is in. The account guard
  stops trading near a 5 % drawdown; that is the only protection, and it means the account is effectively spent.
- For comparison, v2.2 (the pullback system) made +21.6 R on the same 28 months with 43 trades and a 5.2 R drawdown, and
  was about flat in development. The improved breakout made about three times the total R with twelve times the trades,
  and has a much worse development record.
- Pine: pine/gold_hl_breakout.pine now defaults to HL_IMP10_MS_T (swing 10, trend filter on, minimum stop 0.10, risk
  0.25 %). The original is one click away (swing 5, trend off, minimum stop 0).

## 8. Caveats

Fourteen variants of one idea on data already examined about sixty times; the improvement hypotheses were formed after
the six readings' held-out results were known; the held-out months are one strongly trending, volatile gold regime; the
constant 0.25 USD spread flatters recent years (FOREX.com showed 0.55-0.65 USD off-peak on 2026-11-12/13; doubling costs
is tested in §5); no volume; no news gate in the engine; approximate session-day boundary. The first clean test is the
forward test.

## 9. Files (see also the lists in §10 and §11)

backtest/engine_v5_hl.py, verify_v5_replay.py, verify_v5b_replay.py, verify_v5_handcheck.py (left unfinished by the
interrupted implementer; not relied on); results/PREREGISTRATION_v5_hl.md, PREREGISTRATION_v5b_hl_improve.md,
results/V5_HL_*/{trades.csv, skips.csv, levels.csv, config.json}, results/summary_v5.md; pine/gold_hl_breakout.pine.

## 10. v5c: more trades and more profit from the improved breakout (frozen addendum, run 2026-11-13)

Aayan after HL_IMP10_MS_T: "the trades are lower and the profit isn't that much". Eight exploratory variants on that base
(its held-out results were known), frozen in the v5c addendum of results/PREREGISTRATION_v5b_hl_improve.md with the
criterion "raises the total R in BOTH development and held-out, held-out PF not below 1.25, held-out drawdown not beyond 12 R".

| variant | development n / mean R / PF / total / max DD | held-out n / mean R / PF / total / max DD | trades per day | criterion |
|---|---|---|---|---|
| HL_IMP10_MS_T (base, orders 07:00-16:00, target 1.5 R) | 859 / -0.034 / 0.93 / -29 R / -56 R | 511 / +0.121 / 1.34 / +62 R / -10 R | 0.84 | |
| **HL_C_W01** (orders 01:00-16:00) | 1,017 / +0.006 / 1.01 / +6 R / -27 R | 666 / +0.141 / 1.37 / +94 R / -9 R | 1.09 | **met** |
| HL_C_W0119 (orders 01:00-19:00) | 1,098 / +0.007 / 1.02 / +8 R / -26 R | 707 / +0.134 / 1.36 / +95 R / -10 R | 1.16 | met |
| HL_C_W19 (orders 07:00-19:00) | 952 / -0.026 / 0.94 / -25 R / -54 R | 558 / +0.114 / 1.33 / +64 R / -13 R | 0.91 | drawdown |
| HL_C_E5 (5 entries a day, to 19:00) | 953 / -0.025 / 0.94 / -24 R / -53 R | 559 / +0.114 / 1.33 / +64 R / -13 R | 0.92 | drawdown |
| HL_C_T20 (target 2.0 R) | 850 / -0.045 / 0.91 / -38 R / -64 R | 509 / +0.135 / 1.36 / +69 R / -15 R | 0.83 | development worse |
| HL_C_T30 (target 3.0 R) | 847 / -0.037 / 0.93 / -31 R / -61 R | 508 / +0.136 / 1.36 / +69 R / -14 R | 0.83 | development worse |
| HL_C_EOD (no target) | 847 / -0.012 / 0.98 / -10 R / -46 R | 508 / +0.141 / 1.37 / +71 R / -18 R | 0.83 | drawdown |
| HL_C_W19_T20 | 934 / -0.039 / 0.92 / -36 R / -63 R | 552 / +0.131 / 1.36 / +72 R / -18 R | 0.90 | development worse |

Letting orders rest from 01:00 instead of 07:00 is the one change that helps everywhere: half again as much held-out
profit, a trade on 94 % of days, the development period turns from a 29 R loss into break-even and its drawdown halves.
Wider targets and later hours do not meet the criterion.

Checks on HL_C_W01: independent replay IDENTICAL (1,683 trades). Costs doubled: held-out +0.123 R, PF 1.31, +82 R,
drawdown -10.6 R; development -0.037 R, drawdown -57 R. Costs tripled: held-out +0.104 R, PF 1.26. 18 of 18 one-at-a-time
shifts keep a positive held-out mean (order start 00:00 / 02:00 / 03:00 / 05:00, end 15:00 / 17:00, pivot 8 / 12, target
1.2 / 1.8, minimum stop, stop cap, offset, entries a day): +0.108 to +0.149 R. By entry block, held-out: 01:00-07:00 369
trades +0.144 R; 07:00-12:00 161 trades +0.173 R; 12:00-16:00 136 trades +0.097 R (development: +0.027 / +0.009 / -0.051).
Held-out by side: 361 buys +0.207 R, 305 sells +0.064 R. Held-out months: 75 % positive, worst -4.2 R, best +12.5 R,
median +3.6 R; development months: 52 % positive, worst -13.9 R. Longest held-out losing streak 8.

| year | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| HL_C_W01 total R | -8.2 | +10.1 | -10.5 | +32.5 | +46.5 | +29.3 |

Last three months of the data (2026-08-02 to 2026-10-30, the window Aayan can see in TradingView): HL_C_W01 77 trades,
-2.7 R (its worst stretch of the final test); HL_IMP10_MS_T 54 trades, +3.8 R. Over the 14 months of the final test:
+48.4 R against +25.1 R, 11 against 9 positive months. The default is chosen on the six years, not on three months.

Verdict: against the strict rule HL_C_W01 has mean R > 0 in all three periods, a held-out CI that excludes zero, PF 1.35
and 1.39, drawdown within 10 R in both held-out periods, and fails only the development drawdown (-27 R) with a
development edge of zero. Still UNVALIDATED: exploratory on known held-out data, regime-dependent, and negative in
development once the spread is doubled. Money at 0.25 % risk (125 USD per R): held-out +420 USD a month on average
(+367 with doubled costs), worst drawdown about 1,160 USD; the development drawdown would be 3,340 USD (6.7 %).
Pine default: orders from 01:00.

## 11. v6: levels on the 15-minute chart, entries on the 5-minute or 1-minute chart (frozen results/PREREGISTRATION_v6_mtf.md)

Aayan's proposal for more trades. Signal = a completed M5 (or M1) bar closing beyond the marked M15 level; market entry
on the next minute; stop behind the signal bar (at least 1 x ATR14 of that timeframe); target 2 R; same window, trend
filter, daily cap and exits. Engine backtest/engine_v6_mtf.py (mechanical assertions and hand checks passed).

| variant | development n / mean R / PF | validation | final test | held-out mean R | held-out, costs doubled | median stop (USD) |
|---|---|---|---|---|---|---|
| MTF10_M5 | 1,059 / -0.243 / 0.68 | 328 / -0.069 / 0.90 | 301 / -0.025 / 0.96 | -0.048 | -0.121 | 2.9 |
| MTF10_M1 | 1,094 / -0.312 / 0.61 | 337 / -0.254 / 0.67 | 314 / -0.120 / 0.84 | -0.190 | -0.288 | 1.5 |
| MTF5_M5 | 1,463 / -0.263 / 0.65 | 508 / -0.177 / 0.76 | 430 / -0.023 / 0.97 | -0.107 | -0.178 | 2.6 |
| MTF5_M1 | 1,505 / -0.315 / 0.61 | 531 / -0.258 / 0.67 | 464 / -0.102 / 0.86 | -0.185 | -0.299 | 1.4 |
| MTF10_M5_T15 (target 1.5 R) | 1,059 / -0.218 / 0.69 | 328 / -0.104 / 0.84 | 302 / -0.060 / 0.90 | -0.083 | -0.122 | 2.9 |
| MTF10_M5_T30 (target 3 R) | 1,056 / -0.208 / 0.74 | 328 / -0.087 / 0.88 | 299 / +0.005 / 1.01 | -0.043 | -0.128 | 2.9 |
| MTF10_M5_NOTREND | 1,220 / -0.222 / 0.70 | 359 / -0.063 / 0.91 | 341 / -0.023 / 0.97 | -0.043 | -0.121 | 2.8 |

Rejected. Every variant loses in development and validation, and every one loses in all three periods once costs are
doubled. The stop behind a 5-minute or 1-minute bar is 1.5 to 3 USD (4 to 9 USD in 2026), so the 0.35 USD round trip is
0.09 to 0.33 R per trade; before costs the entries are about break-even (gross R per year between -0.15 and +0.09).
Development drawdowns are 240 to 480 R. The 1-minute versions hold a median of five minutes and had days of -13 R on
news spikes. Lower-timeframe entries add trades, not profit, and are not in the Pine script.

Files for §10 and §11: backtest/engine_v5_hl.py (V5C variants), backtest/engine_v6_mtf.py, backtest/verify_v5b_replay.py,
results/V5_HL_C_*/, results/V6_MTF*/ (and *_stress/), results/PREREGISTRATION_v6_mtf.md, results/summary_v5.md, results/summary_v6.md.

