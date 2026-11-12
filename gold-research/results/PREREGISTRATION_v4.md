# PREREGISTRATION v4 — frozen family list (selection judge, 2026-11-12, written BEFORE any v4 run)

Status: FROZEN. This file was written by the selection judge from the three designers' proposals without running
anything and without looking at any data. Nothing in it may be added, removed, re-parameterised or re-ordered after
the first v4 run; perturbation and cost-stress runs are listed here so that they are pre-registered too.
Implementer: one engine file per family, `backtest/engine_v4_<file_stem>.py`, outputs in `results/V4_<variant id>/`
(trades.csv, skips.csv, config.json with engine_v3's columns and counters, plus hold_minutes and signal_date).

Selected: 5 families (F5-F9), 15 variants (cap was 6 / 18). One 15-minute variant (FIXT_US_15M). One family (F5)
has in-sample support; the other four are pre-registered null tests that fire on 63-98% of session days.

---------------------------------------------------------------------------------------------------------------------
## 0. Shared conventions (apply to every family; copied from backtest/engine_v3.py, engine_v2.py, engine.py)

CLOCK. All times are on the dataset index clock exactly as engine_v3 reads `data/xauusd_m1_utc.parquet`
(`pd.read_parquet`, tz-aware index labelled UTC). PROFILE_v4_dev §0 reports that this clock behaves as London local
time: the daily reopen is 23:00 on it all year except 59 US/EU DST-mismatch days (2021-01 to 2024-07) on which the feed
reopens at 22:00 and the US 08:30-ET releases land at 12:30. NO conversion is applied anywhere: this is the clock on
which every tested strategy's 23:00->23:00 session day and 20:50 time exit are defined, and "UTC" in the shared
conventions means this clock. Every time below is on it.

DATA AND BARS. BID M1 bars; ask = bid + spread. M15 = `m1.resample("15min", label="left", closed="left")` OHLC with
dropna; indicators = `engine.indicators` (ATR14 = `wilder_rma` of true range, adx_len 14, atr_len 14); warmup_bars = 200
M15 bars. Session-day key of any bar: k = (t + 1h).date (engine_v3 `m1_day` / `skey` / `m15_day`). Daily frame =
`engine_v2.daily_frame(m1)`: session-day OHLC labelled by the date on which the session ends, `sma200` = rolling mean of
200 session-day closes, `atr14` = EWM(alpha = 1/14, adjust = False) of session-day true range. Previous session day =
`prev_day(k)` = the daily row before k (None for the first row). D1ATR = pdy.atr14. On DST-mismatch days the 22:00-22:59
bars carry the previous session-day key (accepted quirk shared by every engine; no special rule anywhere).

COSTS (E.BASE_CONFIG, fixed): spread 0.25 USD, slippage 0.05 USD per fill, commission 0. No news gate in any backtest.

DECISIONS. Only at the close of a closed M15 bar i (after bar i's M1 bars have been simulated); an order placed at that
close acts on the M1 bars of bar i+1 onward. Exception: an order placed "at the session start" is placed at engine_v3's
new-session detection (`k != day["key"]`), before the session day's first M1 bar is simulated, exactly as F4 DC arms.

FILLS (engine_v3 `fill_entry`). Market order (pending kind "market"): long fill = bid open + 0.25 + 0.05, short fill =
bid open - 0.05, on the first simulated M1 bar. Stop order (pending kind "stop"): buy fills when ask high >= level at
max(level, ask open) + 0.05; sell fills when bid low <= level at min(level, bid open) - 0.05; both in one minute -> the
level nearer the open fills ((buy - ask open) <= (bid open - sell) -> buy). Limit order (pending kind "limit", NEW, F8
only): defined in F8. Gap rule: if the fill is already at/beyond the order's own stop (long fill <= stop, short fill >=
stop) or target (long fill >= target, short fill <= target) the order is not taken: SKIP_gap_fill_past_stop /
SKIP_gap_fill_past_target. Same-minute stop: long, if the fill bar's bid low <= stop -> closed at (bid low - 0.05 if bid
low < stop else stop - 0.05); short, if ask high >= stop -> closed at stop + 0.05; reason stop_same_minute.

OPEN POSITION, per M1 bar, in this order: (1) session_gap_exit if the bar's session key differs from the position's
(long bid open - 0.05, short ask open + 0.05); (2) time_exit at the first bar with minute-of-day >= 20:50 (same prices)
— F5 replaces this test with a session-minute test, see F5; (3) stop: long bid low <= stop -> min(stop, bid open) - 0.05,
short ask high >= stop -> max(stop, ask open) + 0.05; target: long bid high > target, short ask low < target (strict
trade-through) -> filled at the target; stop first when both print in the same minute (ambiguous flag); (4) max_hold
(only where set): if bar_time - entry_time >= max_hold_minutes - 1 min -> closed at the bar's close (+1 min timestamp)
at bid close - 0.05 (long) / bid close + 0.25 + 0.05 (short), reason max_hold. Pending orders: cancelled with
CANCEL_unfilled_at_cutoff at the first bar with minute-of-day >= cancel time, or CANCEL_session_ended when the session
key changes. No level is rounded (engine_v3 convention; the designers' 0.01 rounding is dropped for uniformity).

BOOKKEEPING. planned_risk = |level - stop| (level = fill for market orders, the limit level for F8); R =
pnl_per_oz / planned_risk, pnl_per_oz = sign x (exit - fill) - commission. signal_bar_open = the open time of the
decision bar (family-specific below). Periods by signal_bar_open: development [2021-01-04, 2024-07-01), validation
[2024-07-01, 2025-09-01), final test [2025-09-01, 2026-11-01). Trades with hold_minutes < 3 are flagged (account rule).

EVALUATION AND ROBUSTNESS (pre-registered). Metrics and decision rule as backtest/analyze_v3.py (mean R, PF, n, max DD
in R per period, trades/month; usability bar max DD <= 10 R in every period; "fires on >= 60% of session days" is the
daily-trade bar the designers used). After the main runs: (a) +-20% one-at-a-time perturbation of every parameter
marked [numeric], reported as robustness only; (b) for EVERY F5 variant, regardless of outcome, a cost-stress rerun at
spread 0.50 / slippage 0.15 (as V1_cost_stress), because a constant 0.25 spread overstates reopen-hour fills.
Neither (a) nor (b) may be used to pick parameters.

---------------------------------------------------------------------------------------------------------------------
## 1. Selection summary (ranked)

| rank | id | family | file_stem | variants | fires on | honest expectation |
|---|---|---|---|---|---|---|
| 1 | F5 | ASIA_HOLD fixed-time Asian-block hold | asia_hold | ASIA_LONG_2300, ASIA_LONG_2330, ASIA_SMA200L_2330, ASIA_MOM20_2330, ASIA_MOM20L_2330, ASIA_MOM5_2330 | 93-97% (conditional 55-75%) | +0.45 USD/oz net at 23:00 (upper bound), +0.1..+0.3 at 23:30; ~+0.02 R |
| 2 | F6 | RSI2_M15 two-bar RSI exhaustion fade | rsi2_m15 | RSI2_BASE, RSI2_RSI3 | ~95% / ~61% | null (-0.05..-0.25 USD) |
| 3 | F7 | FIXT_US first-US-hour continuation | fixt_us | FIXT_US_1H, FIXT_US_2H, FIXT_US_15M | 75-85% / ~60-70% | null (~-0.35 USD, -0.04 R); 15M -0.05..-0.10 R |
| 4 | F8 | PDLVL_FADE previous-day level fade, limits | pdlvl_fade | PDL_FADE_PDHL, PDL_FADE_PIV | 63% / 81% | -0.1..+0.1 R, most likely null |
| 5 | F9 | ASIA_REJ Asian-range probe-and-reject fade | asia_rej | ASIA_REJ_LDN, ASIA_REJ_NY | 66% / 79% | 0 +/- 0.1 R |

---------------------------------------------------------------------------------------------------------------------
## 2. Families (full specification)

### F5 — ASIA_HOLD (file_stem asia_hold)
Fixed-time hold through the Asian block (session reopen -> 06:50), direction from a previous-session-day rule, D1ATR
disaster stop, no target. Merger of FIXT_ASIA (Designer A) and MDM_ASIA (Designer B): same trade, one family.

RULES.
SESSION MINUTE: smin(t) = (60*hour + minute + 60) mod 1440 = minutes since the 23:00 session start (23:00 -> 0,
23:30 -> 30, 06:50 -> 470). Every time test of this family is on smin because the hold crosses midnight: engine_v3's
`mod >= texit_min` time-exit test and any minute-of-day cancel test MUST NOT be used (they would close a 23:00
position in its fill minute). session_gap_exit applies unchanged (position closed at the first bar whose session key
differs from the entry's).
DAILY INPUTS (previous session day only): daily = engine_v2.daily_frame(m1); i = dpos[k]; pdy = daily.iloc[i-1];
D1ATR = pdy.atr14; SMA = daily.close.rolling(sma_len).mean() at row i-1 (sma_len 200 = pdy.sma200, exactly as
V3_VB_03_bias); mom_N = daily.close.iloc[i-1] - daily.close.iloc[i-1-N] (both rows must exist).
SKIPS (no trade that day): pdy missing or D1ATR NaN -> SKIP_d1atr_undefined. ASIA_SMA200L_2330: SMA NaN ->
SKIP_bias_undefined; pdy.close <= SMA -> SKIP_bias_short_side. ASIA_MOM20_2330 / ASIA_MOM5_2330 / ASIA_MOM20L_2330:
row i-1-N missing -> SKIP_mom_undefined; mom_N == 0 -> SKIP_mom_zero. ASIA_MOM20L_2330: mom_N <= 0 ->
SKIP_mom_not_positive.
DIRECTION: ASIA_LONG_2300, ASIA_LONG_2330, ASIA_SMA200L_2330, ASIA_MOM20L_2330: long. ASIA_MOM20_2330, ASIA_MOM5_2330:
long if mom_N > 0, short if mom_N < 0.
DECISION AND ORDER. entry_smin = 0 (ASIA_LONG_2300 only): the market order is placed at the new-session detection
(before the session day's first M1 bar is simulated, as F4 DC arms its orders), using pdy only; it fills at the open of
the session day's FIRST M1 bar; if that bar has smin > entry_tolerance_min (5), i.e. the feed reopened after 23:05,
the order is cancelled (CANCEL_no_entry_bar). entry_smin = 30 (all other variants): decision at the close of the M15
bar of session day k whose open time has smin 15 (the 23:15 bar, minute-of-day 1395; close 23:30); the market order
fills at the open of the first M1 bar with smin >= 30 (normally the first M1 bar of the 23:30 M15 bar); if that bar
has smin > 35 the order is cancelled (CANCEL_no_entry_bar); if session day k has no 23:15 M15 bar (feed gap) ->
SKIP_decision_bar_missing. General rule used only by the entry_smin perturbation (24-36): decision at the close of the
latest M15 bar whose close smin <= entry_smin; fill at the first M1 bar with smin >= entry_smin; cancel if that bar's
smin > entry_smin + 5.
FILL: engine_v3.fill_entry with level None (long bid open + 0.25 + 0.05; short bid open - 0.05); the gap rule is moot
(stop defined from the fill); same-minute stop check as fill_entry.
STOP: long fill - stop_d1atr x D1ATR; short fill + stop_d1atr x D1ATR; set at the fill, never moved. Each later M1 bar,
in this order: (1) session_gap_exit; (2) time_exit if smin >= exit_smin (470): long bid open - 0.05, short ask open +
0.05; (3) stop: long bid low <= stop -> min(stop, bid open) - 0.05; short ask high >= stop -> max(stop, ask open) + 0.05.
TARGET: none (stop-first ambiguity moot). max_hold_minutes: None. One order per session day; no re-entry after a stop;
no pyramiding; no trailing; no partial; no news gate.
BOOKKEEPING: planned_risk = stop_d1atr x D1ATR = |fill - stop|; signal_time = signal_bar_open = the open time of the
session day's first M15 bar (t15[i] at the new-session detection, as F4 DC) for ASIA_LONG_2300, and the 23:15 bar's
open time for the other variants; period by signal_bar_open.
ACCOUNT NOTES (outside the backtest): the position is open at the account's 00:00 UTC equity mark (its floating P&L
sets that day's daily-limit base; maximum floating loss = 1 R = 250 USD); the 06:50 exit is 10 minutes before the 07:00
London red-folder slot; hold about 7.3-7.8 h; never held through the 22:00-23:00 break; Sunday 23:00/23:30 entries face
the weekend gap and the week's widest spreads, which the constant 0.25 spread flatters (hence the cost-stress rerun).

ENTRY. Market order. ASIA_LONG_2300: placed at the session start, filled at the open of the session day's first M1 bar
(nominal 23:00) at bid open + 0.25 + 0.05; cancelled if that bar opens after 23:05. All other variants: decision at the
close of the 23:15 M15 bar (23:30), filled at the open of the first M1 bar at/after 23:30 at bid open + 0.25 + 0.05
(long) / bid open - 0.05 (short); cancelled if that bar opens after 23:35. Direction per variant as above.

EXIT. Hard stop at fill -/+ 1.0 x D1ATR (previous session day's atr14) from the fill minute, never moved, filled at
min(stop, bid open) - 0.05 (long) / max(stop, ask open) + 0.05 (short); no target; otherwise time exit at the open of
the first M1 bar with session minute >= 470 (06:50) at bid open - 0.05 (long) / ask open + 0.05 (short);
session_gap_exit at the next session's first bar if the feed ends before 06:50.

PARAMS. entry_smin: 0 for ASIA_LONG_2300 [structural, not perturbed: the session's first bar]; 30 for all other
variants [numeric; perturb 24-36 with the general rule]. entry_tolerance_min = 5 [fixed; feed-gap guard].
exit_smin = 470 (06:50) [numeric; perturb 376-564]. stop_d1atr = 1.0 [numeric; 0.8-1.2] on pdy.atr14 (daily ATR length
14 is the shared daily frame, not perturbed). target = none [fixed]. max_hold_minutes = None [fixed]. direction_rule =
long | sma200_long | mom_sign | mom_long [structural per variant]. sma_len = 200 [numeric; 160-240; ASIA_SMA200L_2330
only]. mom_lookback_days N = 20 (ASIA_MOM20_2330, ASIA_MOM20L_2330) / 5 (ASIA_MOM5_2330) [integer numeric; perturb
16-24 / 4-6]. max_orders_per_session_day = 1 [fixed]. costs spread 0.25 / slippage 0.05 / commission 0 [fixed]. news
gate none [fixed]. Robustness: +-20% perturbations and the spread 0.50 / slippage 0.15 cost-stress rerun for every
variant (pre-registered in §0).

VARIANTS.
- ASIA_LONG_2300: entry_smin=0 (23:00, first bar of the session day); exit_smin=470; stop_d1atr=1.0; direction long;
  no bias. The literature window as profiled (23:00->07:00 gross +0.80 USD/day in development, net about +0.45 before
  stop-outs, about +0.02 R at a ~24 USD stop). An UPPER BOUND: the modelled 0.25 spread at the reopen is 4-10x too
  tight (third-party logs 1.2-2.8 USD for 5-20 minutes), so a positive result is necessary but not sufficient. Fires on
  ~93% of session days.
- ASIA_LONG_2330: entry_smin=30 (23:30); exit_smin=470; stop_d1atr=1.0; direction long; no bias. The BASE and the
  live-relevant test: skips the reopen's first 30 minutes. Expected gross +0.4..+0.6 USD, net +0.1..+0.3. If
  ASIA_LONG_2300 is positive and ASIA_LONG_2330 is not, the family is a reopen-spread artefact. Fires ~93%.
- ASIA_SMA200L_2330: as ASIA_LONG_2330 but long only when pdy.close > SMA200 of session-day closes (sma_len=200).
  Trend-expression test (2022, the flat year, had no drift). Expected per-trade mean above the base, firing ~65-75% of
  days (fewer in development because of 2022 H2); trades from about 2021-10 (200-day warm-up). No short leg: the
  profile shows no negative drift below the SMA200.
- ASIA_MOM20_2330: as ASIA_LONG_2330 but direction = sign of the 20-session-day close momentum, both sides. The
  symmetric test of "the trend is expressed in Asian hours". Fires ~97% of days. Expected net 0..+0.25 USD in trending
  years, negative in flat years.
- ASIA_MOM20L_2330: as ASIA_MOM20_2330 but long only (mom_20 <= 0 -> no trade). Momentum-filtered drift; expected
  55-65% of days in development, possibly under 60% in a down-trend (flagged). ASIA_MOM20_2330 minus ASIA_MOM20L_2330
  measures what the short side adds or costs.
- ASIA_MOM5_2330: as ASIA_MOM20_2330 with N=5. Lookback test: if it matches ASIA_MOM20_2330 the lookback is
  irrelevant and the result is the Asian drift, not momentum; if worse, short-horizon sign flips cost the drift.

WHY SELECTED (rank 1). The only family whose base effect covers costs in the development profile (23:00-07:00 mean
+0.80 USD/oz per session day, t +3.7, bootstrap CI [+0.38, +1.22], n 840, positive in 3 of 4 years, absent in 2022),
with literature behind it (Speck 2013; Donati & Jung 2019; Batten, Lucey, McGroarty, Peat & Urquhart 2017; Lou, Polk &
Skouras 2019 as the equity analogue). Fires on 93-97% of session days. No tested family trades 23:00-07:00. One engine
change (session-minute exit). MERGER AND HARMONISATION, done before any run: FIXT_ASIA and MDM_ASIA trade the same
thing, so A's specification (session-minute logic, tolerance, skips) is kept and B's momentum rules become variants;
all conditional variants enter at 23:30 (A's spread-realistic minute; B's 23:15 and A's 23:00-with-SMA200 are dropped so
that each variant differs from the base in exactly one factor) and all use the 1.0 x D1ATR stop (B's 0.5 would double
the R-drawdown of a ~+0.02 R/trade series; both designers put the 1.0-stop drawdown near the 10 R bar). Honest
expectation: about +0.02 R per trade with sd ~0.26 R, positive on ~56% of days, PF ~1.15 if the drift persists; a
daily sd 14x the daily mean; it cannot make money every day and it cannot satisfy the 15-minute preference (largest
mean M15 move of any hour is 0.108 USD vs a 0.30 round trip).

### F6 — RSI2_M15 (file_stem rsi2_m15)
Two-bar RSI exhaustion fade on M15 with ATR stop/target and a 60-minute maximum hold (Designer C).

RULES.
Shared §0 throughout (dataset clock; key (t+1h).date; engine_v3 fills, costs, gap rule, stop_same_minute, stop-first,
strict trade-through target, 20:50 time_exit, session_gap_exit, max_hold definition). RSI(n) on M15 closes, computed on
consecutive M15 bars across the daily break exactly like the EMA/ATR: d = close - previous close; gain = max(d, 0);
loss = max(-d, 0); avg_gain = engine.wilder_rma(gain, n); avg_loss = engine.wilder_rma(loss, n); RSI = 100 - 100 / (1 +
avg_gain / avg_loss); avg_loss == 0 -> 100 (50 if avg_gain is also 0).
1) Decisions only at the close of M15 bars whose OPEN time is in [07:00, 15:45] (minute-of-day 420..945; fills
07:15-16:00). 2) Signal: RSI(rsi_len) <= rsi_x -> long; RSI(rsi_len) >= 100 - rsi_x -> short; skip the bar if ATR14 or
RSI is NaN. 3) One trade per session day: the first signal whose order is filled; no signal is evaluated while an order
is pending, while a position is open, or after the day's trade has closed; a signal skipped by the gap rule or the
blackout does NOT consume the day. 4) Levels fixed at signal time from the signal bar (the last closed bar): long stop =
signal low - stop_atr x ATR14(signal bar); long target = signal close + target_atr x ATR14(signal bar); short stop =
signal high + stop_atr x ATR14; short target = signal close - target_atr x ATR14. 5) Blackout: a signal whose fill
minute (the first M1 bar after the signal bar's close, nominally the close time) opens in [13:25, 13:35] inclusive is
skipped (SKIP_news_blackout; in practice the 13:15 signal bar) — approximates the account's +-5-minute news rule at the
08:30-ET slot and the unrealistic 0.25 spread at 13:30. 6) Entry: pending kind "market" -> fill_entry; gap rule
(SKIP_gap_fill_past_stop / _target, day stays open); same-minute stop. 7) Open position per M1 bar: session_gap_exit;
time_exit at the first bar with minute-of-day >= 20:50; stop; target; stop first; max_hold (engine_v3 definition).
8) planned_risk = |fill - stop|; signal_time = signal bar close, signal_bar_open = signal bar open; trades with
hold_minutes < 3 flagged and P&L reported with and without their profits. No partial exits, trailing, news calendar
or re-entry.

ENTRY. Market order on the first M1 bar after the signal bar closes: long at bid open + 0.25 + 0.05 when RSI(rsi_len)
of the just-closed M15 bar <= rsi_x; short at bid open - 0.05 when RSI >= 100 - rsi_x; signal bars opening 07:00-15:45;
fill minutes opening 13:25-13:35 skipped; not taken if the fill is already beyond the pre-set stop or target.

EXIT. First of: (a) stop at signal low - 1.5 x ATR14 (long) / signal high + 1.5 x ATR14 (short), filled at min(stop,
bid open) - 0.05 / max(stop, ask open) + 0.05, stop-first; (b) target at signal close +/- 1.0 x ATR14 on a trade-through
(bid high > target long / ask low < target short), filled at the target; (c) max_hold_minutes = 60: closed at the close
of the M1 bar that closes 60 minutes after the open of the fill minute, at bid close - 0.05 (long) / bid close + 0.25 +
0.05 (short); (d) 20:50 time exit at the first M1 open at/after 20:50 (bid open - 0.05 long / ask open + 0.05 short);
(e) session_gap_exit.

PARAMS. rsi_len = 2 (RSI2_RSI3: 3) [integer, structural, not perturbed]. rsi_x = 5 [numeric; 4-6]. stop_atr = 1.5
[numeric; 1.2-1.8]. target_atr = 1.0 [numeric; 0.8-1.2]. max_hold_minutes = 60 [numeric; 48-72]. signal window
07:00-15:45 by signal-bar open [fixed]. blackout 13:25-13:35 on the fill minute [fixed]. time_exit 20:50 [fixed]. one
trade per session day [fixed]. atr_len 14 [fixed, engine]. costs fixed. Development sizes: median ATR14(M15) 1.7 (07:00)
to 3.2 USD (15:00), so target 1.7-3.2 USD and planned risk about 3-4 USD, scaling with ATR later.

VARIANTS.
- RSI2_BASE: rsi_len=2, rsi_x=5, stop_atr=1.5, target_atr=1.0, max_hold_minutes=60, window 07:00-15:45. Development
  trigger count (designer, counts only): RSI(2) <= 5 or >= 95 on 98% of session days, ~5 bars/day; first signal in the
  07:00 hour on 38% of days, 07:00-09:00 on 61%, so largely a London-open thrust fade. ~0.95 trades/day expected.
- RSI2_RSI3: rsi_len=3, otherwise as RSI2_BASE. Rarer, stronger exhaustion (3-4 consecutive bars one way); fires on
  61.4% of development days, 1.55 signals/day, 13:00-15:00 cluster; sits at the 60% bar and may fall below it.

WHY SELECTED (rank 2). The best-known published short-term reversal rule (Connors & Alvarez 2008), never tested on
gold intraday; weak but non-zero development support (M15 lag-1 autocorrelation -0.0135, robust t -1.6; an hour of
>= 2 ATR followed by -0.19 USD against it in the next hour, t -1.8; the 2-3-bar thrust itself unprofiled). Fires on
about 95% of session days. Genuinely distinct: no tested family uses an oscillator extreme, a fixed-time exit, or
enters at market against the last 2-3 bars without a trend filter (the TWAP reversion needed ADX < 20 and targeted a
running average). Implementable with engine_v3 mechanics plus an RSI function. Honest expectation: null after the
0.35 USD round trip (-0.05 to -0.25 USD, about -0.02 to -0.07 R); a daily family of +-0.5 R trades shows a 15-20 R
drawdown over 3.5 years by chance alone, so the 10 R bar is informative only if the mean is clearly positive. The
RSI2_H15 twin is not registered (rule 2 of the selection).

### F7 — FIXT_US (file_stem fixt_us)
Fixed-time continuation of the first US hour(s): the net move of a 13:30-anchored window of W closed M15 bars sets the
direction; market entry at the window's end; stop at the window's opposite extreme (D1ATR-floored/capped); no target;
20:50 exit (Designer B). FIXT_US_15M is the single 15-minute variant of v4.

RULES.
Shared §0 throughout. WINDOW: the W consecutive M15 bars whose open times are 13:30 + 15n, n = 0..W-1 (minute-of-day
810 + 15n), all with the current session key; W = 4 -> 13:30, 13:45, 14:00, 14:15 (decision at the 14:15 bar's close =
14:30); W = 8 -> through the 15:15 bar (decision 15:30); W = 1 -> the 13:30 bar only (decision 13:45). The decision
fires at the close of the bar with minute-of-day 810 + 15(W-1); the day is then DONE (one attempt per session day,
whatever follows). SKIPS: any window bar missing, non-consecutive or of another session day -> SKIP_window_bars_missing;
pdy missing / D1ATR NaN or ATR14(M15) of the last window bar NaN -> SKIP_atr_undefined. DECISION: move = close(last
window bar) - open(first window bar); gate |move| >= gate_move_atr x ATR14(M15, last window bar) else
SKIP_gate_small_move; direction long if move > 0, short if move < 0. ENTRY: pending kind "market" filled at the open of
the first M1 bar at/after the decision time (long bid open + 0.25 + 0.05; short bid open - 0.05); if that bar opens
more than entry_tolerance_min = 5 minutes after the decision time (feed gap) -> SKIP_late_open. STOP: raw_stop = min(bid
lows of the window bars) - stop_buffer (long) / max(bid highs of the window bars) + stop_buffer (short), computed at the
decision; at the fill minute: (i) gap rule against raw_stop (long fill <= raw_stop / short fill >= raw_stop ->
SKIP_gap_fill_past_stop); (ii) dist = min(max(|fill - raw_stop|, stop_floor_d1atr x D1ATR), stop_cap_d1atr x D1ATR);
final stop = fill - dist (long) / fill + dist (short), never moved; (iii) same-minute stop check against the final stop;
planned_risk = dist. TARGET: none for FIXT_US_1H / FIXT_US_2H; FIXT_US_15M: fill + target_mult x (high - low of the
13:30 bar) (long) / fill - target_mult x range (short), strict trade-through as engine_v3. EXIT: stop; time_exit at the
first M1 bar with minute-of-day >= 20:50; session_gap_exit; FIXT_US_15M additionally max_hold_minutes = 15 (engine_v3
definition). No trailing, partial, re-entry or news gate. signal_time = decision bar close, signal_bar_open = the
decision (last window) bar's open. LIVE NOTES: the 14:30 / 15:30 / 13:45 entries are >= 15 minutes from the 13:30 and
15:00 release slots; FOMC 19:00/19:30 falls inside the 1H/2H hold; on DST-mismatch days the US releases land at 12:30
and the window misses them (accepted, as ORB NY). A FIXT_US_15M target hit within 3 minutes of the fill loses its
profit under the account rule (flagged).

ENTRY. Market order at the open of the first M1 bar at/after 14:30 (FIXT_US_1H), 15:30 (FIXT_US_2H) or 13:45
(FIXT_US_15M), in the direction of the net move (last close - first open) of the just-closed 13:30-anchored window,
provided |move| >= gate_move_atr x ATR14(M15) (0.5 for 1H/2H, 0.3 for 15M); long bid open + 0.25 + 0.05, short bid
open - 0.05; one attempt per session day; skipped if the entry bar is > 5 minutes late.

EXIT. Stop at the window's opposite extreme -/+ 0.10 USD with the distance from the fill floored at 0.25 x D1ATR (0.10
for 15M) and capped at 0.60 x D1ATR; 1H/2H: no target, time exit at the first M1 bar >= 20:50 (bid open - 0.05 long /
ask open + 0.05 short), session_gap_exit; 15M: target = 1.0 x the 13:30 bar's range from the fill on a trade-through,
or max_hold_minutes = 15 (closed at the close of the M1 bar that closes 15 minutes after the open of the fill minute, at
bid close - 0.05 long / bid close + 0.25 + 0.05 short), whichever first; stop first in a same-minute conflict.

PARAMS. window_start = 13:30 [fixed]. window_bars W = 4 (2H: 8; 15M: 1) [integer, structural, not perturbed; +-1 M15
bar shift reported as a robustness check only]. gate_move_atr = 0.5 (15M: 0.3) [numeric]. stop_buffer = 0.10 USD
[numeric]. stop_floor_d1atr = 0.25 (15M: 0.10) [numeric]. stop_cap_d1atr = 0.60 [numeric]. target_mult = None (15M:
1.0 x the 13:30 bar range) [numeric, 15M only]. max_hold_minutes = None (15M: 15) [numeric, 15M only; 12-18].
time_exit = 20:50 [fixed]. entry_tolerance_min = 5 [fixed]. atr_len = 14 [fixed]. one entry per session day [fixed].
costs fixed.

VARIANTS.
- FIXT_US_1H: W=4 (entry 14:30), gate_move_atr=0.5, stop_buffer=0.10, stop_floor_d1atr=0.25, stop_cap_d1atr=0.60,
  target=None, time_exit=20:50. The lens's central claim on the one unmeasured window. Expected null: gross 0 +/- 0.4
  USD, net ~-0.35 USD (~-0.04 R); fires on ~75-80% of session days.
- FIXT_US_2H: W=8 (entry 15:30), otherwise as FIXT_US_1H. Window covers both US release slots, the COMEX open and the
  NYSE open; remaining hold 15:30-20:50 (profile 15:00->20:50 mean +0.15, t 0.4). Expected null; fires ~85%.
- FIXT_US_15M: W=1 (entry 13:45), gate_move_atr=0.3, stop_buffer=0.10, stop_floor_d1atr=0.10, stop_cap_d1atr=0.60,
  target_mult=1.0 x (13:30 bar range), max_hold_minutes=15, time_exit=20:50. The in-and-out-within-15-minutes test:
  ride the 13:30 release bar for one more quarter-hour. Expected -0.05 to -0.10 R (release reaction complete within
  90 s; large hours revert); kept because it is the single quarter-hour whose gross move (~1.5-2 USD in development,
  4-6 USD in 2025-26) is not dwarfed by the 0.35 USD cost. Expected firing ~60-70%; report the development firing
  rate, do not retune.

WHY SELECTED (rank 3). The one intraday-continuation window the development profile did not measure (13:30-14:30 ->
rest of day), carrying the information hour of the day (the 13:30 minute has 4-5x the range of 12:30; hours 13-15
build the day), with real literature (Gao, Han, Li & Zhou 2018 JFE intraday momentum; Xu, Bouri, Saeed & Wen 2020 for
commodity ETFs including GLD). Fires on 75-85% of session days. Distinct from ORB NY (stop orders at the 13:30-14:00
range edges, 1-1.5 x range target, coin flip) and from V2_N (forced 13:30 entry on the M15 DI regime, tight ATR14 stop,
partial/trail, lost): here the direction is the completed window's own net move, entry at market at 14:30/15:30, no
target, stop at the window's opposite extreme floored/capped in D1ATR. Honest expectation null (neighbouring windows
show rho -0.02; ~-0.35 USD, -0.04 R per trade; 15-25 R/yr drawdown under a null edge, failing the 10 R bar). FIXT_US_15M
is the ONLY 15-minute variant registered in v4 and the best available test of the user's preference.

### F8 — PDLVL_FADE (file_stem pdlvl_fade)
Previous-day high/low or floor-trader pivot fade with resting OCO limit orders, tight D1ATR stop, 1.5 R target
(Designer C). The only passive-order family in the project.

RULES.
Shared §0 throughout. pdy = prev_day(k): H = pdy.high, L = pdy.low, C = pdy.close, D1ATR = pdy.atr14. 1) Level set:
PDL_FADE_PDHL {PDH = H, PDL = L}; PDL_FADE_PIV {S1, PP, R1} with PP = (H + L + C) / 3, R1 = 2 PP - L, S1 = 2 PP - H.
2) Placement decision at the close of the M15 bar with open time 06:45 of session day k (close 07:00); c = that bar's
close. If session day k has no 06:45 bar -> SKIP_placement_bar_missing; pdy missing or D1ATR NaN ->
SKIP_d1atr_undefined. Candidate levels above c: level - c >= min_dist_d1atr x D1ATR; below c: c - level >=
min_dist_d1atr x D1ATR. Sell limit at U = the NEAREST qualifying level above c; buy limit at D = the NEAREST qualifying
level below c; only one side if only one qualifies; none -> SKIP_no_level. The two orders are OCO. (This fades the move
INTO the nearest level from whichever side it is approached: c above PDH -> only a buy limit at PDH; c inside the
range -> both extremes faded.) 3) Orders are active from the first M1 bar at/after 07:00 (the M1 bars of the 07:00 M15
bar onward) until the first M1 bar with minute-of-day >= 16:00 (CANCEL_unfilled_at_cutoff) or the session change
(CANCEL_session_ended). On M1 bars opening in [13:25, 13:35] inclusive no fill is evaluated (orders stay alive; a
level crossed during the blackout fills on the next qualifying bar under the normal rule, subject to the gap rule).
4) Limit fill rule (new pending kind "limit"): buy limit D fills on the first active M1 bar with ask low (= bid low +
0.25) <= D - through, at min(D, ask open) + 0.05; sell limit U fills on the first active M1 bar with bid high >= U +
through, at max(U, bid open) - 0.05; "through" = 0.10 USD: the market must trade through the level, a touch is not a
fill. Both sides in one minute: the level nearer the bar's open fills first — if (ask open - D) <= (U - bid open) the
buy fills, else the sell (mirror of engine_v3's both_sides rule). 5) Stop and target fixed at placement from the level
and D1ATR: long stop = D - stop_d1atr x D1ATR, long target = D + target_mult x stop_d1atr x D1ATR; short stop = U +
stop_d1atr x D1ATR, short target = U - target_mult x stop_d1atr x D1ATR. planned_risk = stop_d1atr x D1ATR (level to
stop; engine_v3 open_pos with the limit level as `level`). 6) Gap rule: a fill at/beyond its own stop or target is not
taken (SKIP_gap_fill_past_stop / _target) and the day is done (both orders cancelled). 7) One trade per session day:
the first fill cancels the other order; no re-placement after a stop-out. 8) Same-minute stop check as fill_entry (long
bid low <= stop; short ask high >= stop), stop-first ambiguity, strict trade-through target, 20:50 time_exit,
session_gap_exit; no max_hold, partial, trailing or news calendar; trades with hold_minutes < 3 flagged. signal_time =
07:00 (placement), signal_bar_open = the 06:45 bar's open.

ENTRY. Resting OCO limit orders placed at 07:00 from the 06:45 close: sell limit at the nearest qualifying previous-day
level above, buy limit at the nearest qualifying level below, minimum distance 0.05 x D1ATR from the 06:45 close; filled
only on a 0.10 USD trade-through of the level at level +/- 0.05 slippage (or the better opening price on a gap, subject
to the gap-skip rule); active 07:00-16:00 except 13:25-13:35.

EXIT. First of: (a) stop 0.10 x D1ATR beyond the level (short U + 0.10 D1ATR at max(stop, ask open) + 0.05; long
D - 0.10 D1ATR at min(stop, bid open) - 0.05), stop-first; (b) target 0.15 x D1ATR on the other side of the level
(= 1.5 R) on a strict trade-through, filled at the target; (c) 20:50 time exit at the first M1 open at/after 20:50 (bid
open - 0.05 long / ask open + 0.05 short); (d) session_gap_exit. No trailing, no max_hold.

PARAMS. stop_d1atr = 0.10 [numeric; 0.08-0.12]. target_mult = 1.5 [numeric; 1.2-1.8]. min_dist_d1atr = 0.05 [numeric;
0.04-0.06]. through = 0.10 USD [numeric; 0.08-0.12]. level_set = {PDH, PDL} | {S1, PP, R1} [structural per variant].
placement at the 06:45 bar close (07:00), cancel 16:00, blackout 13:25-13:35, time_exit 20:50, one trade per day, OCO
[fixed]. costs fixed. Development sizes: median D1ATR 23-27 USD, so stop ~2.4 USD and target ~3.6 USD; nearest placed
level a median 0.42 x D1ATR (~10 USD) from the 06:45 close for the PD set, 0.27 x D1ATR for the pivot set.

VARIANTS.
- PDL_FADE_PDHL: level_set={PDH, PDL}, stop_d1atr=0.10, target_mult=1.5, min_dist_d1atr=0.05, through=0.10, active
  07:00-16:00, no max_hold. Base. Development count (designer, counts only): orders placed on 899 of 902 session days,
  filled on 570 (63%; 280 sells, 290 buys); first fills cluster 07:00-09:00 (28%) and 13:00-16:00 (41%).
- PDL_FADE_PIV: level_set={S1, PP, R1}, otherwise as PDL_FADE_PDHL. Classical floor-trader pivots including the pivot
  itself (a PP retest from either side is faded). Development count: filled on 81% of days (365 sells, 365 buys),
  nearest level a median 0.27 x D1ATR away. More trades, weaker levels: does the specific published level matter?
  (Without PP the fill rate is 58%, below the 60% bar, which is why PP is included.)

WHY SELECTED (rank 4). Osler (2000 FRBNY EPR; 2003 J. Finance): intraday FX rates bounce off published
support/resistance levels far more often than chance, explained by stop-loss / take-profit order clustering;
floor-trader pivots are the most widely published such levels (no peer-reviewed gold test). Development profile: weak
long-side support (hours ending within 0.3 ATR of the PDL move +0.35 USD in the next hour, t 1.4, 56% up), none at the
PDH in a rising sample, and a level that breaks tends to keep going (hence the tight stop). Nothing tested rests limit
orders or uses PDH/PDL/pivots as entry levels (engine_v2 used PDH/PDL only to cap a target; Donchian buys the N-day
high on a stop and holds for days). Fires on 63-81% of session days. Needs one new pending kind in the engine loop,
fully specified above. Honest expectation: breakeven win rate ~46% after costs; -0.1 to +0.1 R per trade, most likely
null; a positive long side with a negative short side would be trend beta, not a level effect, so both sides are
reported separately. The PDL_FADE_H15 twin is not registered (rule 2).

### F9 — ASIA_REJ (file_stem asia_rej)
Asian-range probe-and-reject fade during London (and the NY morning): a closed M15 bar that trades beyond the Asian
high/low and closes back inside the range; market entry; stop beyond the probe extreme; target the range midpoint
(Designer C). The mirror of the two tested range-breakout families.

RULES.
Shared §0 throughout. 1) Asian range of the CURRENT session day k = max bid high / min bid low of the M1 bars with key k
and (hour >= 23 or hour < 7) (engine_v2's asia_hi / asia_lo definition: 23:00 of the previous date through 06:59); if
fewer than min_asia_bars = 400 of the 480 M1 bars exist -> SKIP_asia_bars_missing; pdy missing or D1ATR NaN ->
SKIP_d1atr_undefined. 2) Range filter: (asia_high - asia_low) < min_range_d1atr x D1ATR -> SKIP_range_too_small (day
skipped). Targets: short target = asia_high - target_frac x range, long target = asia_low + target_frac x range (0.5 =
the midpoint, mid). 3) Decisions at the close of M15 bars whose OPEN time is in [07:00, 11:45] (ASIA_REJ_LDN) or [07:00,
15:45] (ASIA_REJ_NY). Short signal: bar high > asia_high AND bar close <= asia_high. Long signal: bar low < asia_low AND
bar close >= asia_low. A bar satisfying both (sweeps both edges) is ignored; skip if ATR14 is NaN. 4) Stop from the
signal bar: short stop = signal high + buffer, long stop = signal low - buffer, buffer = max(buffer_min, buffer_atr x
ATR14(M15, signal bar)). 5) Target-side and reward/risk filter using the signal close as the expected fill: a short
requires close > target and a long requires close < target, else SKIP_target_passed; RR = (close - target) / (stop -
close) for shorts, (target - close) / (close - stop) for longs; RR < min_rr -> SKIP_rr_too_low; a skipped signal leaves
the day open for a later signal. 6) Blackout: a signal whose fill minute opens in [13:25, 13:35] inclusive is skipped
(SKIP_news_blackout; reachable only in ASIA_REJ_NY, the 13:15 signal bar). 7) One trade per session day: the first
filled signal; no signal is evaluated while an order is pending, while a position is open, or after the day's trade has
closed; a skipped signal does not consume the day. 8) Entry: pending kind "market" -> fill_entry on the next M1 bar
(short bid open - 0.05; long bid open + 0.25 + 0.05); gap rule (fill at/beyond the stop or the target ->
SKIP_gap_fill_past_stop / _target, day stays open); same-minute stop; then stop-first ambiguity, strict trade-through
target filled at the target, 20:50 time_exit, session_gap_exit; no max_hold, partial, trailing, news calendar or
re-entry; trades with hold_minutes < 3 flagged. signal_time = signal bar close, signal_bar_open = signal bar open.

ENTRY. Market order on the first M1 bar after the signal bar closes: short at bid open - 0.05 after a bar that traded
above the Asian high and closed at/below it; long at bid open + 0.25 + 0.05 after a bar that traded below the Asian low
and closed at/above it; signal bars opening 07:00-11:45 (LDN) or 07:00-15:45 (NY); RR to the midpoint >= 1.0 at the
signal close; not taken if the fill is already beyond the stop or the midpoint.

EXIT. First of: (a) stop just beyond the probe extreme — short at signal high + max(0.30, 0.10 x ATR14), long at signal
low - max(0.30, 0.10 x ATR14), filled at max(stop, ask open) + 0.05 (short) / min(stop, bid open) - 0.05 (long),
stop-first; (b) target = Asian-range midpoint on a strict trade-through (ask low < mid short / bid high > mid long),
filled at mid; (c) 20:50 time exit at the first M1 open at/after 20:50 (bid open - 0.05 long / ask open + 0.05 short);
(d) session_gap_exit. No max_hold, no trailing.

PARAMS. min_range_d1atr = 0.20 [numeric; 0.16-0.24]. buffer_min = 0.30 USD [numeric; 0.24-0.36]. buffer_atr = 0.10
[numeric; 0.08-0.12]. min_rr = 1.0 [numeric; 0.8-1.2]. target_frac = 0.5 [numeric; 0.4-0.6]. Asian window 23:00-06:59
M1, min_asia_bars 400, signal window 07:00-11:45 (NY variant 07:00-15:45) by signal-bar open, blackout 13:25-13:35 on
the fill minute, time_exit 20:50, one trade per day [fixed]. costs fixed. Development sizes: Asian range median 0.35 x
D1ATR (~8 USD), so the midpoint target is ~4 USD; the probe-bar stop is typically 1-2.5 USD.

VARIANTS.
- ASIA_REJ_LDN: signal window 07:00-11:45, min_range_d1atr=0.20, buffer_min=0.30, buffer_atr=0.10, min_rr=1.0,
  target_frac=0.5, no max_hold. Base (London only). Development count (designer, counts only): a qualifying
  probe-and-reject bar with RR >= 1 on 66% of session days (599 of 902; 44 days skipped for a small range), 1.77
  signals/day; the first signal is the 07:00 London-open bar on 43% of signal days.
- ASIA_REJ_NY: signal window 07:00-15:45, otherwise as ASIA_REJ_LDN. Do probes of the Asian range still fail once New
  York is in? Development count: 79% of days, 2.85 signals/day (NY adds first signals on 111 days); the 13:15 signal
  bar is blackout-skipped.

WHY SELECTED (rank 5, last kept). Zero prior (Raschke & Connors' Turtle Soup in intraday form; the "London sweep" of
the Asian range is folklore; the breakout side was rejected as V2_C and was a coin flip as ORB London, which does not
make the fade positive since costs eat both), but it is the exact mirror of two tested range families with a different
trigger (a closed bar that probes beyond the Asian edge and closes back inside), a different order type (market after
the failed probe), a tight stop beyond the probe extreme and the midpoint as target, and it tells the project whether
the Asian range matters at all once both sides have been tried. Fires on 66-79% of session days; fully implementable
with engine_v3 mechanics and engine_v2's Asian-range definition. Honest expectation 0 +/- 0.1 R; the failure mode is
re-probes hitting the tight stop before the move to the midpoint. ASIA_REJ_H15 is not registered (rule 2).

---------------------------------------------------------------------------------------------------------------------
## 3. Rejected, merged or replaced (with reasons)

1. GAPGO (GAPGO_D, GAPGO_L, GAPGO_ALL — overnight-move continuation into London/New York; Designer B). Lowest prior of
   all proposals: the literature points the other way (Lou, Polk & Skouras 2019 tug of war; the gold overnight-vs-day
   studies find positive overnight / negative day returns) and so does the development profile (no continuation at any
   measured window; block means Asia +0.80, London -0.14, NY -0.38; previous-day sign -> next day rho -0.007/-0.012); the
   designer's own expectation is null to negative. Weakest distinctness: the same bet as Williams VB from the 07:00
   open, ORB London and the rejected V2_C Asian-range breakout (go with the London-morning direction). Its mirror (fade
   the overnight move) is mostly the unconditional US-hours short that Designer A measured at 0.007 sd per trade and did
   not register. Under a null edge its drawdown is 15-25 R/yr. With the 6-family cap it ranks seventh of seven. NOT
   registered in either direction; no fade family may be built from its absence without a new pre-registration.
2. MDM_ASIA as a separate family (MDM_ASIA_20, MDM_ASIA_5, MDM_ASIA_20L: 23:15 entry, 0.5 x D1ATR stop). Trades the
   same thing as FIXT_ASIA (a fixed-clock Asian hold with a D1ATR stop and no target) -> merged into F5 as
   ASIA_MOM20_2330, ASIA_MOM5_2330, ASIA_MOM20L_2330 with the family's 23:30 entry and 1.0 x D1ATR stop (harmonised before
   any run so that each F5 variant differs from the base in exactly one factor).
3. FIXT_ASIA_3 (23:00 entry with the SMA200 bias; Designer A). Replaced by ASIA_SMA200L_2330 for the same reason; the
   23:00 entry is retained only in ASIA_LONG_2300, the reopen-spread upper bound.
4. RSI2_H15, PDL_FADE_H15, ASIA_REJ_H15 (15-minute max-hold twins; Designer C). Dropped under selection rule 2: their
   designers' own arithmetic puts the expected gross move below the 0.30-0.35 USD round trip (largest mean M15 move of
   any hour +0.108 USD; a level bounce or midpoint reversion is a 1-3 hour trade; expected net -0.2 to -0.3 USD per
   trade), and the 15-minute max-hold twin mechanism is on the already-tested list (V3 h15 twins: 95%+ max_hold exits,
   median |R| ~0.2, PF 0.7-0.85, no edge created). FIXT_US_15M is retained as the single 15-minute test of v4.
5. Lens items the designers examined and declined, recorded so they are not re-proposed: London AM/PM fix trades
   (10:30->15:00 mean 0.00; the 10:30->11:00 long nets -0.11 USD; the within-auction 4-minute trade is unreachable on
   closed M15 bars); day-of-week rules (all CIs include zero); the daily-break gap (+0.04/day, untradable) and the
   US-hours fixed short (0.007 sd per trade); pre-/post-NY-open windows (|t| <= 1.7, alternating signs); previous-day
   direction / CLV / NR7 / inside-day filters (|t| <= 1.3, no next-day expansion); the EMA-slope/Keltner fixed-time
   entry (duplicates V2_N); Bollinger(20,2) touch-and-reverse (same mechanism as the rejected TWAP reversion);
   reversion of the 07:00-08:00 move (no continuation and no reversal in the profile); the one-hour 23:00->00:00
   reopen long (its whole margin sits inside the reopen spread; its contribution is isolated by ASIA_LONG_2300 vs
   ASIA_LONG_2330 anyway); the Asian-range breakout (tested as V2_C). Agreed; none registered.

---------------------------------------------------------------------------------------------------------------------
## 4. Frozen statement

This list — five families F5 (ASIA_HOLD), F6 (RSI2_M15), F7 (FIXT_US), F8 (PDLVL_FADE), F9 (ASIA_REJ) with exactly the
fifteen variants ASIA_LONG_2300, ASIA_LONG_2330, ASIA_SMA200L_2330, ASIA_MOM20_2330, ASIA_MOM20L_2330, ASIA_MOM5_2330,
RSI2_BASE, RSI2_RSI3, FIXT_US_1H, FIXT_US_2H, FIXT_US_15M, PDL_FADE_PDHL, PDL_FADE_PIV, ASIA_REJ_LDN, ASIA_REJ_NY, their
rules, entry and exit definitions, parameter defaults, the +-20% perturbation ranges and the F5 cost-stress rerun — is
frozen as of this file's creation on 2026-11-12, before any v4 engine has been written or run. No family, variant,
parameter, time, level, filter, exit or evaluation rule may be added, removed, re-tuned or re-interpreted after any
result from the development, validation or final-test period has been seen; the development period is in-sample, the
validation and final-test periods are held out and may not be used to choose among variants or parameters; the
perturbation and cost-stress runs are robustness reports, not selection steps; a family that is implemented differently
from this file must be re-run as specified here, and a deviation that cannot be removed must be logged in the results
with its reason. A null or negative result for any or all of these families is a valid, expected outcome and will be
reported as such; the single family with in-sample support (F5) carries the pre-registered caveat that its 23:00
variant is a spread-dependent upper bound and that no variant can satisfy the user's 15-minute preference, which the
development profile's arithmetic already rules out for every fixed-time trade on this data.
