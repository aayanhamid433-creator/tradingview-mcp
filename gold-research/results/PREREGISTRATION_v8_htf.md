# PREREGISTRATION v8 — bigger timeframe for the direction, lower timeframe for the trade
Frozen 2026-11-13 (commit time is the timestamp), BEFORE engine_v8_htf.py was written or any variant run.

Request (Aayan, 2026-11-13): "use the bigger time frame as a reference to see which direction and then trade on lower
time frame".

## Direction references (backtest/htf_refs.py, written for the event study below)

For every M1 bar the state comes from the last bar of the reference timeframe that closed BEFORE the bar of that
timeframe which contains the M1 bar (what TradingView returns on a lower-timeframe chart for
request.security(sym, tf, expr[1], lookahead_on)).

| reference | up | down |
|---|---|---|
| M15, H1, H4 | bar close above its EMA50 and the EMA50 above its value four bars earlier | mirrored |
| D1 | previous session-day close above its 200-day simple average | below it |

H1 bars start on the clock hour; H4 bars start at 22:00, 02:00, 06:00, 10:00, 14:00, 18:00 London time; the session day
runs 23:00 to 23:00. One definition for all three intraday references, the one already used in v7; nothing tuned.

## What was known when this file was written (development period only, 2021-01 to 2024-06)

Event study at every M15 close between 07:00 and 16:00 London time (31,193 points, 898 days). Gross bid-to-bid move in
the direction of the reference, USD per ounce, before the 0.35 USD round-trip cost; t-statistics clustered by day.

| reference | share of time up / down | next 15 min | next hour | next 4 hours | until 20:50 | until 20:50 by year 2021 / 22 / 23 / 24 |
|---|---|---|---|---|---|---|
| M15 | 47 % / 44 % | +0.002 (t 0.1) | +0.003 (t 0.1) | +0.100 (t 0.6) | +0.35 (t 1.0) | +0.19 / +0.64 / +0.46 / -0.08 |
| H1 | 47 % / 43 % | +0.005 (t 0.4) | +0.014 (t 0.3) | +0.065 (t 0.3) | +0.19 (t 0.5) | +0.51 / +0.23 / +0.53 / -1.05 |
| H4 | 49 % / 41 % | +0.003 (t 0.3) | +0.028 (t 0.5) | +0.216 (t 1.1) | +0.79 (t 1.7) | +0.81 / +0.35 / +1.51 / +0.57 |
| D1 | 54 % / 24 % | -0.017 (t -1.2) | -0.080 (t -1.4) | -0.213 (t -1.0) | -0.21 (t -0.4) | -0.98 / -0.46 / -0.11 / +0.54 |

Requiring two or more references to agree does not improve on H4 alone (H1+H4: +0.56 until 20:50, t 1.1; all four:
+0.44, t 0.5). Median ATR14(M15) at the sample points was 2.05 USD.

Reading: no reference says anything about the next 15 to 60 minutes (at most 3 cents against a cost of 35). The
4-hour trend shows a small tendency to continue for the rest of the day, positive in each development year but not
significant; the 200-day bias pointed the wrong way intraday in this period.
Already known from earlier rounds: M15 reference with 15-minute exits loses (QS_TREND_PB_H15, held-out -0.068 R); the
breakout with the M15 reference (HL_C_W01) is +0.006 R in development and +0.141 R held-out; the original breakout with
the D1 reference added (HL_SW5_RR_BIAS) is +0.035 R held-out against +0.019 R without it.

## Variants (13)

Costs, data, periods and conventions as in every engine (BID M1 bars, spread 0.25, slippage 0.05 per market or stop
fill, targets filled at their price when traded through, stop first when stop and target fall in one minute, same-minute
stop check on the fill minute, flat at 20:50, session-gap exit; cost stress at spread 0.50 / slippage 0.10).

ENTRY for families Q and N (the "lower timeframe"): the 5-minute pullback of v7, in the direction of the reference. A
5-minute bar trades through its EMA20(M5) and closes back on the direction side, and the previous 5-minute bar did not;
signal at 5-minute closes between 07:00 and 16:00 London time; market entry at the next 5-minute bar's open; one
position at a time.

Family Q, quick exit (stop 1 x ATR14(M15) of the last closed M15 bar from the fill, exit after 15 minutes, at most 6
entries per session day):

| id | reference |
|---|---|
| Q5_PB_H15_H1 | H1 |
| Q5_PB_H15_H4 | H4 |
| Q5_PB_H15_D1 | D1 |

(M15 reference = QS_TREND_PB_H15 of v7, already run.)

Family N, normal intraday trade (stop 0.25 x D1ATR from the fill, where D1ATR is the Wilder ATR14 of session days as
of the previous completed session day; target 1.5 R; flat at 20:50; at most 3 entries per session day):

| id | reference | difference |
|---|---|---|
| N5_PB_M15 | M15 | |
| N5_PB_H1 | H1 | |
| N5_PB_H4 | H4 | |
| N5_PB_D1 | D1 | |
| N5_PB_H4_TIGHT | H4 | stop 1 x ATR14(M15) instead of 0.25 x D1ATR |
| N5_PB_H4_EOD | H4 | no target: stop or the 20:50 flat |

Family B, the M15 breakout of v5 held for hours (HL_C_W01: swing 10, EMA50(M15) filter, minimum stop 0.10 x D1ATR,
orders 01:00-16:00, target 1.5 R, at most 3 entries), with a bigger reference on top. The reference is read at the order
step for the M15 bar that just closed: the buy order exists only while the reference is up, the sell order only while
it is down.

| id | change to HL_C_W01 |
|---|---|
| HL_C_W01_RH1 | H1 reference added |
| HL_C_W01_RH4 | H4 reference added |
| HL_C_W01_RD1 | D1 reference added (the engine's existing hl_bias = sma200) |
| HL_C_RH4ONLY | H4 reference instead of the EMA50(M15) filter |

## Expectations (written before running)

Q: all three lose about the cost per trade, like every quick variant so far. N: about zero; if any reference helps it
should be H4, and the wide stop should do better than the tight one because the drift needs hours. B: H4 on top of the
breakout may cut trades and drawdown; whether it raises the result per trade is open. D1 is expected to hurt in
development and help in 2024 to 2026, when gold trended up.

## Decision rule

The strict rule of v5 (mean R > 0 in all three periods, held-out CI excludes zero, PF > 1.10 in both held-out periods
at base AND stressed costs, at least 60 trades in each, max DD <= 10 R, ex-top-5 > 0, no adversarial refutation). These
are looks 19 to 31 at the same data. A null or negative result is valid.

## Addendum v8b — one side only (written 2026-11-13 BEFORE these runs, but AFTER all v8 results were seen: exploratory)

Origin: the placebo analysis of HL_C_W01_RH4 (VALIDATION_REPORT_v8.md section 7) split the trades by side. Over the six
years the buys taken with the 4-hour trend up made +0.18 R each (540 trades); the sells taken with it down made +0.01 R
each (376 trades), negative in development and positive in the held-out period. This was found by slicing every period,
so no part of the data is untouched by it and nothing below can count as validation.

| id | change to HL_C_W01_RH4 |
|---|---|
| HL_C_W01_RH4_LONG | buy orders only (no sell orders at all) |
| HL_C_W01_RH4_SHORT | sell orders only (shown for completeness) |

Purpose: exact numbers for the two sides run on their own (the daily cap and the one-position rule make a simple slice
inexact), and the drawdown of each, because the account simulation shows that the development drawdown decides whether
the account survives. Status of whatever comes out: a hypothesis to follow forward on demo, not a tested rule. Looks 32
and 33.
