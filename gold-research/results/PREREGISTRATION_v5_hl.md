# PREREGISTRATION v5 — "mark the highs and lows, trade the break" (HL), six frozen readings

Written 2026-11-13 04:22 UTC by the implementer, BEFORE `backtest/engine_v5_hl.py` existed and before any V5_HL
variant was run. Status: FROZEN. Nothing in this file may be added, removed, re-parameterised or re-ordered after the
first run. A null or negative result is a valid and expected outcome and will be reported as such.

Provenance. The coordinator's brief states that an earlier draft of these rules, with looser wording about
already-broken levels, was discarded on 2026-11-13 before any engine code existed or any variant was run. THIS FILE IS
THE ONLY FROZEN VERSION. The implementer checked the repository immediately before writing it (2026-11-13 04:22 UTC):
no `backtest/engine_v5*.py`, no `backtest/analyze_v5.py`, no `backtest/verify_v5_*.py`, no `results/V5_HL_*`
directory and no other `PREREGISTRATION_v5*` file existed. (`results/V5_london_only/` is a v1 variant of `engine.py`
from 2026-11-09 and has nothing to do with this study.)

Source of the idea (the user, Aayan, 2026-11-13): "mark the highs and lows of the chart and when it breaks either, buy
or sell"; he wants it to trade day to day. The idea is frozen below as six readings. Seventh look at the same data;
the multiple-testing caveat of VALIDATION_REPORT_v3.md applies and grows.

Already tested and rejected on this data (not duplicated here): London/NY opening-range breakout (v3 F1), Williams
volatility breakout from the 07:00 open (v3 F2), daily Donchian 20/10 and 55/20 held overnight (v3 F4).

Incumbent for comparison, V2_K_confirm ("v2.2"): development 29 trades, -0.023 R, PF 0.96, DD -7.1 R; validation 17
trades, +0.978 R, PF 3.01, DD -4.1 R; final test 26 trades, +0.191 R, PF 1.49, DD -5.2 R; 3-4 trades a month.

---------------------------------------------------------------------------------------------------------------------
## 1. Frozen rules (verbatim from the coordinator's brief)

LEVEL LIFE-CYCLE (every reading):
  - A marked level is LIVE from the bar close at which it is created until price first trades at or beyond its trigger
    price; from then on it is CONSUMED and never produces another order (no chasing a level that has already been
    broken). Trigger price: marked high + 0.10 for the buy stop, marked low - 0.10 for the sell stop. "Trades at or
    beyond": checked on M1 bars; a high is consumed when the bid high >= the buy trigger or when its buy stop fills
    (ask high >= trigger, the engine_v3 fill convention), whichever comes first; a low is consumed when the bid low <=
    the sell trigger. Consumption happens whether or not an order was resting there (outside the order window, while a
    position is open, after the daily cap, on a gap).
  - A newly created level of the same kind replaces the old one and is live.

ORDERS (every reading): at every M15 bar close whose close time is in [07:00, 16:00) UTC, if flat and the day's entry
cap is not reached, a buy stop rests at the trigger of the marked high if that level is live, and a sell stop rests at
the trigger of the marked low if that level is live (one or both). OCO: when one fills the other is cancelled. All
unfilled orders are cancelled at 16:00 and placed again from 07:00 the next day if their levels are still live. A
resting order's stop and target are computed when the order is first placed for a given (marked high, marked low) pair
and recomputed only when either marked level changes. After a position closes, orders are placed again at the next M15
bar close for levels that are still live. One position at a time. Size 1 R per trade.

STOP: the opposite marked level (live or consumed), with the distance from the trigger price clamped to [0.3 x
ATR14(M15) of the bar at whose close the order is computed, 0.6 x previous-session-day D1ATR]; an opposite level on
the wrong side of the trigger gives the floor distance; no opposite level yet = no order. TARGET (RR readings): trigger
+- 1.5 x that distance. TRAIL readings: no target; Chandelier 3 x ATR14(M15) of the last closed bar from the running
extreme since the fill, ratchet only, never beyond the current M1 bar's extreme. Planned risk for R follows engine_v3's
bookkeeping (|stop-order level - initial stop|), so R is comparable with every earlier variant. All positions flat at
20:50 UTC.

READINGS:
  HL_SW5_RR:      levels = the last CONFIRMED swing high and swing low on M15, pivot N = 5 (a bar whose high is >= the
                  highs of the 5 bars before it and of the 5 bars after it; it becomes the marked level at the close of
                  the 5th later bar, so there is no look-ahead; lows the same with <=); target 1.5 x risk; at most 3
                  entries per session day.
  HL_SW5_TRAIL:   same levels and entries, trail exit.
  HL_SW10_RR:     as HL_SW5_RR with N = 10.
  HL_PD_RR:       levels = the previous session day's high and low (engine_v2.daily_frame), created at the session-day
                  start (23:00 UTC), so a level traded through before 07:00 is already consumed; target 1.5 x risk; one
                  entry per session day.
  HL_PD_TRAIL:    as HL_PD_RR with the trail exit.
  HL_SW5_RR_BIAS: as HL_SW5_RR, but only the buy side when the previous session-day close is above its 200-day SMA and
                  only the sell side when it is below (no orders while the SMA is undefined).

Numeric parameters for perturbation: N, entry offset 0.10, stop cap 0.6, stop floor 0.3, target multiple 1.5, trail
multiple 3.0, max entries per day.

DAY-LEVEL STATISTICS (the user wants a day-to-day system, so report these for every variant, over the whole data and
per period): share of session days (Mon-Fri) with at least one trade; share of traded days that end with positive R;
mean R per traded day; worst day in R.

---------------------------------------------------------------------------------------------------------------------
## 2. Shared conventions (verbatim from the brief; copied from backtest/engine_v3.py)

Data: `data/xauusd_m1_utc.parquet` (M1 BID bars, tz-aware UTC, no volume). Costs and fill conventions are those of
backtest/engine_v3.py and must be copied exactly: spread 0.25 (ask = bid + spread), slippage 0.05, commission 0,
decisions on CLOSED M15 bars, fills simulated minute by minute, stop-first when stop and target hit in the same minute,
stop_same_minute, session_gap_exit at the first bar of a new session day (23:00-23:00 UTC day via
engine_v2.daily_frame), skip an entry whose fill would land beyond its own stop or target, 20:50 UTC time exit,
previous-session-day values for daily quantities, ATR of the last CLOSED bar for trailing, max_hold_minutes semantics
as engine_v3. Period splits by signal_bar_open: development 2021-01-04 to 2024-07-01, validation 2024-07-01 to
2025-09-01, final test 2025-09-01 to 2026-11-01.

---------------------------------------------------------------------------------------------------------------------
## 3. STRICT PASS RULE (pre-registered, verbatim)

STRICT PASS RULE (pre-registered): mean R > 0 in all three periods; pooled out-of-sample (validation + final test) 90 %
bootstrap CI for mean R excludes zero; PF > 1.10 in both held-out periods; at least 60 trades in each held-out period;
max DD <= 10 R in every period; OOS mean R ex-top-5 > 0; sign of OOS mean R unchanged in >= 75 % of +-20 %
single-parameter perturbations; no adversarial refutation. A variant that fails the strict rule is "more trades at a
smaller but positive edge" only if it is positive with PF > 1.10 in both held-out periods and DD <= 10 R; otherwise
"no edge".

Reading of the fallback label used by analyze_v5.py: "positive with PF > 1.10 in both held-out periods and DD <= 10 R"
= mean R > 0 AND PF > 1.10 in validation AND in final test, AND max DD <= 10 R in every one of the three periods.
"No adversarial refutation" cannot be evaluated by the analysis script; it is reported as "not evaluated here" and left
to the adversarial reviewers. The perturbation condition is evaluated from results/V5_<ID>/perturb.json when that file
exists (sign of pooled OOS mean R equal to the sign of the base run's pooled OOS mean R), otherwise "not run".

---------------------------------------------------------------------------------------------------------------------
## 4. Implementation decisions (the implementer's reading of every point the rules leave open; frozen with the rules)

D1 CLOCK. All times are on the dataset index clock exactly as engine_v3 reads the parquet (labelled UTC; results/
PROFILE_v4_dev.md §0 shows it behaves as London local time). No conversion anywhere; "UTC" below means this clock.

D2 BARS AND INDICATORS. M15 = `m1.resample("15min", label="left", closed="left")` OHLC with dropna (engine_v3).
ATR14(M15) = `engine.indicators` (Wilder RMA of the true range, atr_len 14), imported, not re-implemented. Levels are
tracked from the first M15 bar of the data, but no order is placed before M15 bar index 200 (engine_v3 warmup_bars)
or while ATR14 is NaN.

D3 SESSION DAY AND DAILY QUANTITIES. Session-day key of a bar = (t + 1 h).date (engine_v3 `skey` / `m1_day` /
`m15_day`). daily = `engine_v2.daily_frame(m1)`, imported. Previous session day = `prev_day(k)` = the daily row before
k (None for the first row), exactly as engine_v3. D1ATR = pdy.atr14; SMA200 = pdy.sma200; previous-day high/low =
pdy.high / pdy.low. NO special rule for the data's two known quirks, as in v3/v4: (a) on DST-mismatch days the feed
reopens at 22:00 and the 22:00-22:59 bars carry the old session-day key; (b) on DST-mismatch Sundays the 22:00-22:59
bars form a one-hour session day keyed to the Sunday, so on the following Monday "the previous session day" is that
one-hour stub (for D1ATR, SMA200 and, in the HL_PD readings, for the marked high and low). The number of affected
session days and trades is reported with the results; the rule is not changed.

D4 SWING PIVOTS. Bars are consecutive rows of the M15 frame (across the daily break, weekends and feed gaps, like the
indicators). Bar j is a swing high iff j has at least N bars on each side, high[j] >= max(high[j-N .. j-1]) and
high[j] >= max(high[j+1 .. j+N]); swing low iff low[j] <= min(low[j-N .. j-1]) and low[j] <= min(low[j+1 .. j+N]).
Ties are allowed on both sides exactly as written, so two bars with equal highs can both be pivots; each confirmation
is a NEW level (live, order parameters recomputed) even when its price equals the level it replaces. The pivot at bar
j becomes the marked level at the close of bar j+N (nominal close = open + 15 min). "Last confirmed" = most recently
confirmed; an older unbroken swing is forgotten when a newer one of the same kind is confirmed (higher or lower).

D5 ORDER OF EVENTS AT AN M15 CLOSE (bar i): (1) the M1 bars of bar i are simulated against the orders / position
standing since the close of bar i-1 (fills, exits, level consumption); (2) level creation: the pivot at bar i-N, if
any, becomes the marked level, replaces the old one, is live, and invalidates the cached order parameters; (3) order
step: if the nominal close time of bar i is in [07:00, 16:00) and the engine is flat, the resting OCO set is rebuilt
from the levels that are live now (so a level confirmed at this close can carry an order from this close). Orders act
on the M1 bars of bar i+1 onward. HL_PD: the two levels are created at engine_v3's new-session detection
(`k != day["key"]`), before the first M1 bar of the session day is simulated (as v3 F4 arms its orders); they replace
the previous day's pair and both start live; if the session day has no previous session day there are no levels.

D6 CONSUMPTION. Evaluated on EVERY M1 bar from the first M1 bar after the level's creation, in every state (no order,
resting order, open position, cap reached, outside the order window, weekend reopen). High: bid high >= marked high +
offset. Low: bid low <= marked low - offset. The whole minute's bid extreme is used, including the minute of a fill or
an exit (no intra-minute sequencing is assumed). Fill-based consumption: when a resting buy stop is triggered under
engine_v3's rule (ask high >= trigger) its high is consumed in that minute even if the bid high is still below the
trigger, whether the entry is taken or refused by the gap rule. The OCO sibling's level is NOT consumed by the
cancellation; it is consumed only by its own bid criterion (which is evaluated in the same minute too). In the
both-orders-in-one-minute case the order not chosen leaves its level live unless the bid criterion is met in that
minute (always met for the low, because the sell trigger test is the bid test). A consumed level stays the "marked
level" of its kind (and the reference for the opposite side's stop) until a new level of the same kind replaces it.
When neither an order nor a position exists, the M15 bar's high/low (= the extremes of its M1 bars) is used for the
same test; this is identical by construction.

D7 ORDERS. At each M15 close with nominal close time in [07:00, 16:00) (bars opening 06:45 ... 15:30), when flat and
entries today < cap: buy stop at marked high + offset if the high is live (and the bias allows longs), sell stop at
marked low - offset if the low is live (and the bias allows shorts). No order at all unless BOTH marked levels exist
("no opposite level yet = no order"), ATR14 and D1ATR are defined and the warm-up is over. The set is one engine_v3
pending of kind "stop" (OCO). Cancellation as engine_v3: at the first M1 bar with minute-of-day >= 16:00
(CANCEL_unfilled_at_cutoff), or at the first M1 bar of another session day (CANCEL_session_ended). While a position is
open or the cap is reached nothing rests. Entry cap = positions opened in the session day (stop_same_minute entries
count; entries refused by the gap rule do not), reset at the session-day change.

D8 ORDER PARAMETERS (cache). Stop and target of a side are computed at the first close at which that side's order is
placed after the most recent creation of EITHER marked level, with ATR14(M15) of the bar just closed and D1ATR of the
previous session day of that bar's session day. They are kept unchanged — across later closes, the 16:00 cancel, a
position in between, and session days — until either marked level is replaced by a new level. Consumption of a level
does not trigger recomputation.

D9 STOP DISTANCE. raw = trigger - marked low (buy) or marked high - trigger (sell); floor = 0.3 x ATR14(M15); cap =
0.6 x D1ATR; dist = min(max(raw, floor), cap) (if the floor exceeded the cap the cap would win). A raw distance <= 0
(opposite level on the wrong side) therefore gives the floor. Long stop = trigger - dist, short stop = trigger + dist.
RR target = trigger + 1.5 x dist (long) / trigger - 1.5 x dist (short). TRAIL: target = none. No level is rounded.

D10 FILLS (engine_v3 `fill_entry`, copied). Buy stop fills when ask high (bid high + 0.25) >= trigger at max(trigger,
ask open) + 0.05; sell stop fills when bid low <= trigger at min(trigger, bid open) - 0.05. Both in one minute: the
level nearer the open fills ((buy - ask open) <= (bid open - sell) -> buy). Gap rule: a fill at/beyond the order's own
stop or target is not taken (SKIP_gap_fill_past_stop / SKIP_gap_fill_past_target); the whole OCO set is removed (as
engine_v3 removes its pending), the triggered level is consumed, the day's cap is not charged, and orders for levels
that are still live are placed again at the next M15 close. Same-minute stop: long, fill bar's bid low <= stop ->
closed at (bid low - 0.05 if bid low < stop else stop - 0.05); short, ask high >= stop -> closed at stop + 0.05;
reason stop_same_minute (the long/short asymmetry is engine_v3's and is kept).

D11 EXITS (engine_v3 M1 loop, same order per minute): session_gap_exit when the bar's session day differs from the
position's (long bid open - 0.05, short ask open + 0.05); time_exit at the first bar with minute-of-day >= 20:50 (same
prices); stop (long bid low <= stop -> min(stop, bid open) - 0.05; short ask high >= stop -> max(stop, ask open) +
0.05); target on a strict trade-through (long bid high > target, short ask low < target) at the target; stop first
when both print in one minute; max_hold_minutes = None in all six readings (the engine_v3 code path is kept). TRAIL
readings, after the minute's exit tests (engine_v3 F4 / engine_v2 trail mechanics): hh = ll = fill at entry; hh =
max(hh, bid high), ll = min(ll, bid low) on every later minute; long: new = hh - 3 x ATR14 of the last closed M15 bar
(atr[i-1] while the M1 bars of bar i are simulated), accepted iff new > current stop and new < this minute's bid low;
short: new = ll + 3 x ATR14, accepted iff new < current stop and new > this minute's ask high. The fill minute itself
does not update the trail (as engine_v3). Exit reason "stop" when the stop is still the initial stop, else
"trail_stop".

D12 BIAS (HL_SW5_RR_BIAS). pdy.close > pdy.sma200 -> buy side only; pdy.close < pdy.sma200 -> sell side only; SMA200
NaN or exact equality -> no orders. The stop still references the opposite marked level (live or consumed).

D13 BOOKKEEPING. level = the stop-order level (trigger); planned_risk = |level - initial stop| = dist; pnl_per_oz =
sign x (exit - fill) - commission; realised_R = pnl_per_oz / planned_risk. signal_time = the nominal close time of the
last M15 bar that closed before the fill (the most recent order step at which the filled order was (re)placed);
signal_bar_open = that bar's open time (used for the period split). The time at which the stop/target were computed
(D8) is stored separately (calc_time). trades.csv has engine_v3's columns plus level_high, level_low and diagnostic
columns; skips.csv logs gap-rule refusals, 16:00 / session cancels, and the first occurrence per session day of each
no-order reason; config.json holds the config and counters; levels.csv lists every level with its creation and
consumption time. The engine prints trade counts and mechanical counters only (no performance figure), so the
hand-checks can be done before any statistic is read.

D14 PERTURBATION (robustness report only, never selection). One parameter at a time at 0.8x and 1.2x; integers rounded
and skipped if unchanged; only parameters the reading actually uses: pivot N (swing readings: 5 -> 4, 6; 10 -> 8, 12),
entry offset (0.08, 0.12), stop cap (0.48, 0.72), stop floor (0.24, 0.36), target multiple (RR readings: 1.2, 1.8),
trail multiple (TRAIL readings: 2.4, 3.6), max entries per day (3 -> 2, 4; 1 -> unchanged, skipped). Output
results/V5_<ID>/perturb.json = list of {param, mult, value, n_oos, meanR_oos, pf_oos} on pooled validation + final-test
trades; trades.csv is not touched.

D15 ANALYSIS (backtest/analyze_v5.py, modelled on analyze_v3.py). analyze.metrics for mean R, PF, win rate, total R,
max DD (trade sequence within the period), longest losing streak, median hold, 90 % bootstrap CI (10 000 resamples of
trades) and ex-top-5 mean; the bootstrap generator is re-seeded (20261109) before every metrics call so each CI depends
only on its own trade list. Trades/month = n / (period days / 30.4375). Session days = Mon-Fri session-day keys of
engine_v2.daily_frame inside the period (Sunday stubs excluded); a trade belongs to the session day of its entry
minute; day R = sum of the realised R of that day's trades. Day-level statistics per period and over the whole data:
share of session days with at least one trade, share of traded days with day R > 0, mean R per traded day, worst day
R; plus trades per session day. Only results/V5_HL_* directories are read (results/V5_london_only is v1).

D16 VERIFICATION BEFORE ANY STATISTIC IS READ. (a) two trades per variant hand-checked against the raw M1 bars
(bars around entry and exit printed; level, liveness, fill side/price, stop/target and R recomputed independently);
(b) an independent minute-by-minute replay of each variant written separately from the engine and compared trade by
trade; (c) invariant checks over all trades (entry window, cap, no overlap, stop-distance clamp, target multiple, each
level traded at most once, flat by 20:50). Bugs found are fixed and all six variants re-run before analyze_v5.py is
run for the first time.

Honest expectation (written before any run): costs are 0.35 USD per round trip against stops of a few USD on swing
levels, i.e. a drag of roughly 0.05-0.15 R per trade; breakouts of recent M15 swings in gold have no documented edge;
the three breakout families already tested on this data (v3 F1, F2, F4) failed. The most likely outcome is "no edge"
for the swing readings and a small-sample, near-zero result for the previous-day readings.
