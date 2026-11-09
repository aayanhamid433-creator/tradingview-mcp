# FORWARD_TEST_PROTOCOL — prospective demo evaluation of GOLD_PLAYBOOK v1.0

Written 2026-11-09, **before** any forward-test result exists. Status: NOT STARTED (needs a demo account on the broker/feed Aayan will use).

## Purpose
Check, on live-updating data with real spreads and fills, whether the frozen v1.0 rules behave as the backtest assumed. A forward test does not prove an edge; it mainly catches execution, data and process problems.

## Design
| Item | Value |
|---|---|
| Account | demo (or prop-firm evaluation only if its rules are verified first), MT5, XAUUSD |
| Strategy | v1.0 exactly as frozen; no discretionary overrides. Proposals for v1.1 are logged, not traded |
| Observation period | 3 calendar months minimum, or until 60 logged eligible setups (whichever is later) |
| Minimum usable sample | 60 setups with a decision (trade or WAIT) and 40 filled trades. These are reporting thresholds, not proof thresholds: no number of trades guarantees an edge |
| Risk | fixed fraction per trade chosen by Aayan (to be set before the first trade); sizing by playbook §11 once inputs exist; otherwise paper-only in R |
| What is logged | every eligible setup and every WAIT with its reason, using journal/GOLD_TRADE_JOURNAL.csv; every plan gets a setup_id before the outcome is known |
| Quotes | the bid/ask and spread shown by the platform at decision time, typed into the journal |
| News | checked before each plan from the official BLS/Fed schedules or a dated calendar; status recorded |
| Review | weekly: fill quality (planned vs actual), spread at entry, slippage, rule deviations; monthly: R statistics vs the backtest's validation+test distribution |
| Stop rules for the experiment | the experiment is **not** stopped early for good results. It is paused only for a process failure (data/feed outage, rule-execution errors) or if the account's own risk limits are hit |
| Success / failure reading | compare realised mean R and win rate with the backtest's out-of-sample values; a drawdown deeper than the backtest's −22.7 R or a losing streak longer than 8 is a flag for review, not an automatic rule change |

## Freeze and version control
- v1.0 stays frozen for the whole observation period.
- Proposed changes go to PROJECT_STATE.md with the reason and the date; they are evaluated on fresh data only.
- Original plans, losing trades and earlier versions are never edited after the fact.

## Journal fields (schema)
setup_id, analysis_time_utc, chart_time_utc, symbol, broker_feed, strategy_version, evidence_status, session, timeframes, matched_rules, failed_rules, decision, planned_order_type, planned_entry, planned_stop, planned_targets, planned_expiry, quoted_spread, news_status, planned_risk, actual_fill, actual_exit, actual_costs, realised_R, rule_deviation, source_chart_reference, outcome_status

outcome_status values: PENDING_TRIGGER, CANCELLED, FILLED_OPEN, CLOSED_TARGET, CLOSED_STOP, CLOSED_TIME, CLOSED_MANUAL(deviation), NOT_TAKEN(WAIT). Simulated and actual results are kept in separate rows and never merged.
