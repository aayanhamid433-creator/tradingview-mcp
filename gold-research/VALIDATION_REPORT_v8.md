# VALIDATION REPORT v8 — bigger timeframe for the direction, lower timeframe for the trade, 2026-11-13

Status: **the idea helps in one place and nowhere else.** With a quick exit it loses with every reference. With a
5-minute entry held for hours it is about zero. On the 15-minute breakout, the 4-hour direction on top gives fewer and
better trades: the best version of the breakout so far (HL_C_W01_RH4). It still fails the strict rule on the development
period (PF 1.08, drawdown -24.6 R). Engine and references reproduced by an independent replay (identical trade lists);
adversarial agent verification is noted in §7.

## 1. Request and rules

Aayan, 2026-11-13: "use the bigger time frame as a reference to see which direction and then trade on lower time
frame". Frozen before any strategy run in results/PREREGISTRATION_v8_htf.md: four direction references (M15, H1, H4 =
bar above its rising EMA50 or below its falling EMA50, taken from the last closed bar; D1 = previous close against the
200-day average) and thirteen variants in three families. 1 R = the planned risk of one trade.

## 2. Does a bigger timeframe tell the direction? (development period only, measured before any strategy was run)

Every M15 close between 07:00 and 16:00 London time, 2021-01 to 2024-06 (31,193 points, 898 days). Gross move in the
direction of the reference, USD per ounce, before the 0.35 USD round-trip cost; t-statistics clustered by day.

| reference | next 15 min | next hour | next 4 hours | until 20:50 | until 20:50 by year 2021 / 22 / 23 / 24 |
|---|---|---|---|---|---|
| M15 | +0.002 (t 0.1) | +0.003 (t 0.1) | +0.100 (t 0.6) | +0.35 (t 1.0) | +0.19 / +0.64 / +0.46 / -0.08 |
| H1 | +0.005 (t 0.4) | +0.014 (t 0.3) | +0.065 (t 0.3) | +0.19 (t 0.5) | +0.51 / +0.23 / +0.53 / -1.05 |
| H4 | +0.003 (t 0.3) | +0.028 (t 0.5) | +0.216 (t 1.1) | +0.79 (t 1.7) | +0.81 / +0.35 / +1.51 / +0.57 |
| D1 | -0.017 (t -1.2) | -0.080 (t -1.4) | -0.213 (t -1.0) | -0.21 (t -0.4) | -0.98 / -0.46 / -0.11 / +0.54 |

No reference says anything about the next 15 to 60 minutes: at most 3 cents against a cost of 35. The 4-hour trend
shows a small tendency to continue for the rest of the day, positive in each development year. Requiring several
references to agree does not improve on H4 alone.

## 3. Results

Columns: mean R / PF per period; held-out = validation + final test (2024-07 to 2026-10) with a 90 % bootstrap interval.

### 3.1 Family Q: 5-minute pullback entry in the reference direction, out after 15 minutes

| reference | trades per day | development | validation | final test | held-out mean R | held-out, costs doubled |
|---|---|---|---|---|---|---|
| M15 (QS_TREND_PB_H15, v7) | 5.7 | -0.187 / 0.54 | -0.106 / 0.67 | -0.030 / 0.89 | -0.068 [-0.087, -0.050] | -0.145 |
| H1 (Q5_PB_H15_H1) | 5.7 | -0.187 / 0.54 | -0.101 / 0.69 | -0.040 / 0.85 | -0.071 [-0.090, -0.051] | -0.146 |
| H4 (Q5_PB_H15_H4) | 5.5 | -0.195 / 0.53 | -0.102 / 0.69 | -0.043 / 0.84 | -0.072 [-0.091, -0.053] | -0.147 |
| D1 (Q5_PB_H15_D1) | 5.8 | -0.194 / 0.53 | -0.091 / 0.72 | -0.027 / 0.89 | -0.059 [-0.077, -0.041] | -0.136 |

The reference makes no difference. Every quick variant loses about the cost of the trade, as §2 predicts.

### 3.2 Family N: the same 5-minute entry, stop 0.25 x D1ATR, target 1.5 R, flat at 20:50, at most 3 a day

| variant | trades per day | development (drawdown) | validation | final test | held-out mean R | held-out, costs doubled |
|---|---|---|---|---|---|---|
| N5_PB_M15 | 1.8 | -0.048 / 0.92 (-111 R) | +0.033 / 1.06 | +0.037 / 1.07 | +0.035 [-0.022, +0.091] | +0.006 |
| N5_PB_H1 | 1.8 | -0.070 / 0.88 (-131 R) | +0.052 / 1.10 | +0.055 / 1.11 | +0.053 [-0.002, +0.111] | +0.029 |
| N5_PB_H4 | 1.8 | -0.057 / 0.90 (-100 R) | -0.016 / 0.97 | +0.042 / 1.08 | +0.012 [-0.046, +0.068] | -0.015 |
| N5_PB_D1 | 1.8 | -0.091 / 0.85 (-146 R) | +0.030 / 1.06 | +0.047 / 1.09 | +0.038 [-0.018, +0.094] | +0.018 |
| N5_PB_H4_TIGHT (stop 1 x ATR14(M15)) | 2.8 | -0.203 / 0.71 (-506 R) | -0.073 / 0.88 | -0.092 / 0.86 | -0.083 [-0.131, -0.035] | -0.170 |
| N5_PB_H4_EOD (no target) | 1.5 | +0.012 / 1.02 (-41 R) | +0.031 / 1.05 | +0.098 / 1.18 | +0.063 [-0.019, +0.150] | +0.036 |

About zero: negative in development for five of six, held-out intervals all include zero, drawdowns of 40 to 500 R.
A 5-minute pullback is not an entry worth having, whatever the reference. The tight stop loses outright.

### 3.3 Family B: the 15-minute breakout held for hours (HL_C_W01) with a bigger reference on top

| variant | trades per day (days traded) | development (drawdown) | validation (drawdown) | final test (drawdown) | held-out mean R, total | held-out, costs doubled |
|---|---|---|---|---|---|---|
| HL_C_W01 (no bigger reference) | 1.09 (94 %) | +0.006 / 1.01 (-26.7 R) | +0.136 / 1.35 (-5.4) | +0.147 / 1.39 (-9.3) | +0.141 [+0.076, +0.206], +94.1 R | +0.123 |
| HL_C_W01_RH1 (+ H1) | 0.79 (72 %) | +0.021 / 1.05 (-27.6 R) | +0.154 / 1.41 (-6.0) | +0.173 / 1.47 (-8.4) | +0.163 [+0.084, +0.241], +78.2 R | +0.157 |
| **HL_C_W01_RH4 (+ H4)** | 0.71 (66 %) | +0.036 / 1.08 (-24.6 R) | +0.131 / 1.33 (-6.3) | +0.242 / 1.69 (-5.3) | **+0.188 [+0.107, +0.270], +81.0 R** | +0.178 |
| HL_C_W01_RD1 (+ D1) | 0.74 (69 %) | +0.033 / 1.07 (-32.2 R) | +0.140 / 1.37 (-5.7) | +0.158 / 1.43 (-7.2) | +0.148 [+0.071, +0.227], +66.8 R | +0.132 |
| HL_C_RH4ONLY (H4 instead of the M15 filter) | 0.77 (70 %) | +0.032 / 1.07 (-30.3 R) | +0.117 / 1.28 (-6.8) | +0.204 / 1.56 (-7.3) | +0.162 [+0.085, +0.241], +76.0 R | +0.154 |

Every bigger reference raises the result per trade and removes about a third of the trades. H4 on top of the M15
filter is the best in both development and the held-out period.

HL_C_W01_RH4 against the version without it:

| | HL_C_W01 | HL_C_W01_RH4 |
|---|---|---|
| R by year 2021 / 22 / 23 / 24 / 25 / 26 | -8.2 / +10.1 / -10.5 / +32.5 / +46.5 / +29.3 | +8.2 / +21.1 / -12.8 / +17.2 / +42.5 / +29.2 |
| held-out: trades, win rate, PF | 666, 50 %, 1.37 | 431, 54 %, 1.50 |
| held-out months positive | 21 of 28 (75 %), worst -4.2 R | 24 of 28 (86 %), worst -3.6 R |
| drawdown held-out / whole sample | -9.3 R / -26.7 R | -6.3 R / -24.6 R |
| worst day | -3.1 R | -2.0 R |
| Aayan's tester window, 2026-08-02 to 2026-10-30 | 77 trades, -2.7 R | 51 trades, +7.2 R |
| median time in a trade | 8.2 hours | 7.7 hours |

What the filter removes. Of the 1,683 trades of HL_C_W01, the 785 that the H4 reference would have blocked made
+0.004 R each over the six years; the 898 it keeps made +0.108 R each (difference +0.104 R, t 2.1; development +0.073,
held-out +0.154). Trades against the 4-hour trend earned nothing.

## 4. Robustness of HL_C_W01_RH4 (exploratory, one change at a time; these are not candidates)

Reference definition (held-out mean R; development mean R):

| change | held-out | development |
|---|---|---|
| as frozen (EMA50, slope over 4 bars, bars from 22:00) | +0.188 | +0.036 |
| EMA length 40 / 60 | +0.200 / +0.201 | +0.037 / +0.060 |
| slope over 3 / 5 bars | +0.192 / +0.192 | +0.035 / +0.034 |
| 4-hour bars on the clock (00:00) | +0.193 | +0.046 |
| price against the EMA50 only / slope only | +0.189 / +0.173 | +0.037 / +0.031 |
| reference timeframe 2 h / 3 h / 6 h / 8 h / 12 h | +0.146 / +0.178 / +0.175 / +0.169 / +0.158 | +0.040 / +0.041 / +0.047 / +0.030 / +0.006 |

All twelve stay above the version without a reference in both periods; the result changes smoothly with the timeframe,
so 4 hours is not an isolated peak.
Breakout parameters +-20 % (swing size, entry offset, stop cap, stop floor, target, daily cap): held-out +0.140 to
+0.202 R, PF 1.39 to 1.52, twelve of twelve positive (results/V5_HL_C_W01_RH4/perturb.json).
Costs doubled: held-out +0.178 R (PF 1.28 and 1.68); development -0.005 R.
Independent replay (backtest/verify_v5b_replay.py: flat one-minute loop, references rebuilt with pandas instead of
htf_refs.py): identical trade lists for HL_C_W01 (1,683), _RH4 (1,116), _RH1 (1,221), _RD1 (970), HL_C_RH4ONLY (1,226).

## 5. Verdict

Against the strict rule, HL_C_W01_RH4: mean R positive in all three periods (yes); held-out interval excludes zero
(yes); PF above 1.10 in both held-out periods at base and doubled costs (yes: 1.33, 1.69 and 1.28, 1.68); at least 60
trades (yes); ex-top-5 positive (yes, +0.173); perturbations positive (24 of 24); maximum drawdown at most 10 R:
**no** in development (-24.6 R; held-out -6.3 R). Development is break-even (PF 1.08) and zero with doubled costs; 2023
loses 12.8 R. So it is the best breakout version and still a regime-dependent one.

Decision: the Pine script's default becomes the 4-hour reference (input "BIGGER TIMEFRAME for the direction": Off /
1 hour / 4 hours). Risk stays at 0.25 %.

Money at 0.25 % risk on 50,000 USD (125 USD per R): the last 28 months made about 2.9 R = 360 USD a month with a worst
drawdown of about 790 USD. A market like 2021 to 2023 gave a drawdown of 24.6 R = about 3,100 USD, which is the size of
the firm's trailing limit (3,000 USD); the account guard stops new trades 500 USD before the floor. Surviving a repeat
of that period with room to spare needs about 0.10 % risk.

## 6. Caveats

Looks 19 to 31 at the same data, and HL_C_W01_RH4 is the best of four family-B variants, chosen after seeing all
periods; the H4 expectation was written down beforehand from the development event study, but the margin over the
other references is within noise. The filter effect itself (kept against removed trades) is t 2.1 on the whole sample.
The held-out period is a strong uptrend in gold; longs made +0.216 R and shorts +0.139 R there, but in development
shorts lost (-0.049 R). Bid data with a constant modelled spread; orders from 01:00 London time meet wider real spreads
than the model in the Asian hours. TradingView builds 4-hour bars from the 17:00 New York session start; the engine
uses 22:00 London time, which differs by an hour for a few weeks a year (the clock-anchored variant in §4 shows the
anchor does not matter).

## 7. Verification log

- Independent replay: identical (see §4).
- Agent verification (independent re-implementation from the frozen rules, overfitting review, Pine review): see the
  entries appended below when the runs finish.

## 8. Files

backtest/htf_refs.py, backtest/engine_v8_htf.py (families Q and N), backtest/engine_v5_hl.py (hl_ref, family B),
backtest/verify_v5b_replay.py, results/PREREGISTRATION_v8_htf.md, results/V8H_*/ (and *_stress/), results/V5_HL_C_W01_RH1,
_RH4, _RD1, V5_HL_C_RH4ONLY (and *_stress/), results/summary_v8.md, pine/gold_hl_breakout.pine.
