# Mechanics validation — engine_v2.py (V2_0)

Validates the simulator's bookkeeping, not profitability.

## 0. Regression: v1-compatible configuration must reproduce V0_base

```
v1-compat check: v2 trades=477 v0 trades=477 identical=True
```

## 1. Per-trade checks on V2_0

Trades checked: 116; T1 (partial) reached in 36 trades.

| check | passed | failed |
|---|---|---|
| signal_in_window | 116 | 0 |
| entry_before_cutoff_and_after_signal_close | 116 | 0 |
| side_matches_bias | 116 | 0 |
| rr_at_placement_ge_min | 116 | 0 |
| stop_within_0.6_D1ATR | 116 | 0 |
| bias_from_prev_day | 116 | 0 |
| size_mult_correct | 116 | 0 |
| entry_not_in_news_window | 116 | 0 |
| geometry | 116 | 0 |
| pre_t1_exit_reason | 80 | 0 |
| realised_R_arithmetic | 116 | 0 |
| weighted_R | 116 | 0 |
| t1_reached_by_trade_through | 36 | 0 |
| post_t1_exit_reason | 36 | 0 |
| time_exit_at_or_after_2050 | 18 | 0 |
| breakeven_exit_price | 6 | 0 |
| daily_stop_enforced | 105 | 0 |
| weekly_stop_enforced | 86 | 0 |

## 2. Known approximations

- News gate uses first-Friday NFP and an unverified FOMC date list only (no CPI/PCE/GDP dates available offline).
- Bias is undefined for the first 252 session days (no trades), so biased variants start in 2022-01.
- Trail distance uses the ATR of the last closed M15 bar; the trail is evaluated on M1 running extremes and never moved beyond the current minute's extreme.
- Trigger B is OFF in V2_0; its mechanics are exercised only in V2_C/V2_D and were not independently re-derived here.
