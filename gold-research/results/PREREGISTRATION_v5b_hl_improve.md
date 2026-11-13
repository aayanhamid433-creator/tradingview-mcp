# PREREGISTRATION v5b — improving the high/low breakout (frozen 2026-11-13 04:45 UTC, BEFORE any of these variants was run)

Request (Aayan, 2026-11-13, after running `pine/gold_hl_breakout.pine` in TradingView: 87 trades, PF 1.05):
"i like the trades now we have [to] improve the profitability".

## What was known when this file was written

- The six frozen readings of results/PREREGISTRATION_v5_hl.md had been run on all periods (results/V5_HL_*). Their
  held-out results HAVE been seen. Base reading HL_SW5_RR: development 1,276 trades, -0.005 R, PF 0.99, max DD -70 R;
  validation 407 trades, -0.007 R, PF 0.99; final test 367 trades, +0.048 R, PF 1.10.
- The hypotheses below come from the DEVELOPMENT period only (signal_bar_open < 2024-07-01) of HL_SW5_RR, by splitting
  its 1,276 trades on attributes known at the order step. No held-out trade was split or inspected by attribute.

| development-period split of HL_SW5_RR | n | mean R | PF |
|---|---|---|---|
| all | 1,276 | -0.005 | 0.99 |
| stop distance <= 0.10 x D1ATR | 36 | -0.662 | 0.33 |
| stop distance > 0.10 x D1ATR | 1,240 | +0.014 | 1.03 |
| break in the direction of EMA50(M15) | 948 | +0.023 | 1.05 |
| break against EMA50(M15) | 328 | -0.087 | 0.86 |
| ADX14(M15) <= 25 at the order step | 825 | +0.039 | 1.08 |
| ADX14(M15) > 25 | 451 | -0.086 | 0.83 |
| level younger than 1 hour | 647 | -0.041 | 0.92 |
| level 1 hour or older | 629 | +0.023 | 1.05 |
| entry in the 07:00 hour | 301 | -0.039 | 0.93 |
| entry in the 13:00 hour | 147 | -0.073 | 0.86 |
| exits at 20:50 (neither stop nor target hit) | 273 | +0.173 | 2.24 |

- Median stop distance 6.53 USD, so the 0.35 USD round-trip cost is a median 0.054 R per trade. Excluding time exits,
  39.3 % of trades reach the 1.5 R target before the stop; a driftless random walk gives 40.0 %. The entry has no
  directional edge in development; the splits above are weak (no |t| above about 2) and were found by looking.
- Expectation, stated before running: the filters shrink out of sample; the most likely outcome is PF between 0.95 and
  1.10 in the held-out periods and drawdowns far above 10 R. A null result is the expected result.

## Variants (all = HL_SW5_RR unless stated; every other rule, cost and convention of PREREGISTRATION_v5_hl.md unchanged)

Filters, evaluated at every order step (M15 close with close time in [07:00, 16:00), flat, below the daily cap):

- MS  (minimum stop): a side gets no order while its stop distance is below 0.10 x previous-session-day D1ATR.
- T   (trend): buy side only if the order-step bar closes above EMA50(M15, on closes, adjust=False); sell side only if below.
- Q   (quiet): no orders at an order step whose bar has ADX14(M15) > 25.
- A   (mature level): a side gets an order only once its level is at least 60 minutes old (order-step close time - creation time).
- H   (hours): no order rests during 07:00-08:00 or 13:00-14:00 (order steps with close time in those hours place nothing).
- EOD (exit): no target and no trail; the initial stop stays; exit at 20:50.

| id | definition |
|---|---|
| HL_IMP_MS | MS |
| HL_IMP_MS_T | MS + T |
| HL_IMP_MS_T_Q | MS + T + Q |
| HL_IMP_MS_T_A | MS + T + A |
| HL_IMP_MS_T_H | MS + T + H |
| HL_IMP_MS_T_Q_A | MS + T + Q + A |
| HL_IMP_MS_EOD | MS + EOD exit |
| HL_IMP10_MS_T | pivot N = 10 with MS + T |

Numeric parameters: MS 0.10, EMA length 50, ADX max 25, age 60 minutes. No parameter is tuned after the run.

## Decision rule (same strict rule as v5)

Mean R > 0 in all three periods; pooled held-out 90 % bootstrap CI excludes zero; PF > 1.10 in both held-out periods; at
least 60 trades in each; max DD <= 10 R in every period; held-out mean R ex-top-5 > 0. A variant that is positive with
PF > 1.10 in both held-out periods but fails the drawdown or development test is reported as "better than the base,
not tradable at 0.5 % risk". Anything else is "no improvement".

Multiple-testing note: with the six v5 readings these are 14 looks at the breakout idea, on data that had been looked at
about 60 times before. A single passing variant would need the forward test before it means anything.

---

# v5c addendum — more trades and more profit from the improved breakout (frozen 2026-11-13, before any v5c run)

Request (Aayan, after HL_IMP10_MS_T): "the trades are lower and the profit isn't that much". His proposal, entries on M5
or M1, was tested separately (PREREGISTRATION_v6_mtf.md) and loses in every period. These variants test the two other
levers on the improved base HL_IMP10_MS_T (pivot 10, minimum stop 0.10, EMA50 trend, target 1.5 R, orders 07:00-16:00):
longer order hours and a wider or absent target. Its held-out results are known; these are exploratory.

| id | change from HL_IMP10_MS_T |
|---|---|
| HL_C_W19 | orders 07:00-19:00 |
| HL_C_W01 | orders 01:00-16:00 |
| HL_C_W0119 | orders 01:00-19:00 |
| HL_C_T20 | target 2.0 R |
| HL_C_T30 | target 3.0 R |
| HL_C_EOD | no target, exit 20:50 |
| HL_C_W19_T20 | orders 07:00-19:00 and target 2.0 R |
| HL_C_E5 | at most 5 entries per session day (base 3), orders 07:00-19:00 |

Pre-stated criterion: a change counts as an improvement only if, against HL_IMP10_MS_T, it raises the total R in BOTH the
development period and the pooled held-out period without lowering the held-out profit factor below 1.25 or deepening
the held-out drawdown beyond 12 R. Anything else is "no improvement". Nothing here can pass the strict rule, because the
base itself is negative in development.
