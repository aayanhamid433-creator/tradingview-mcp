# VALIDATION_REPORT v2 — GOLD_PLAYBOOK v2.0 CANDIDATE backtest (HistData M1, 2021-01 → 2026-10)

Report date: 2026-11-09. Engine: backtest/engine_v2.py (regression-checked against v1.0: the v1-compatible configuration reproduces V0_base's 477 trades exactly). Mechanics validation: results/VALIDATION_MECHANICS_v2.md (116/116 V2_0 trades pass 18 checks, 0 problems). Full tables: results/summary_v2.md, results/summary_v2.json.

**Pre-registered verdict for V2_0: INCONCLUSIVE.** It beats v1.0 out of sample on mean R and profit factor, but with 23 and 38 trades in the two held-out periods (threshold 60 each), a bootstrap interval that touches zero, and a negative mean once the five best trades are removed.

**Contamination reminder (playbook v2 §11):** the bias layer, the 1.5 minimum reward/risk and the exits were chosen after v1.0's results on this same data were known. This run can **reject** layers that clearly hurt; it cannot **support** v2.0. Clean evidence has to come from broker data not yet seen and from the forward test.

Plain English: filtering v1.0's trades by the daily trend and letting winners run turned a break-even system into one that made about 21 R over 61 out-of-sample trades with a 7 R worst drawdown. That is encouraging but is built on a dozen big winning days in 2025, a year in which gold rose about 50 %. The breakout trigger lost money in every period and is out. The momentum "second vote" only reduced size on trades that went on to win and is out.

## 1. Cross-variant results (R per full-size trade; weighted by size multiplier where applicable)

| variant | what it tests | dev n / mean R | validation n / mean R / PF | final test n / mean R / PF | OOS n / mean R / PF | OOS 90 % CI | OOS max DD | OOS mean R ex-top-5 |
|---|---|---|---|---|---|---|---|---|
| V0_base (v1.0) | baseline | 254 / −0.083 | 107 / +0.208 / 1.39 | 116 / −0.046 / 0.93 | 223 / +0.076 / 1.13 | [−0.070, +0.227] | −22.7 | +0.002 |
| **V2_0** | full default build | 55 / −0.256 | 23 / +0.752 / 2.40 | 38 / +0.089 / 1.22 | 61 / +0.339 / 1.74 | [−0.012, +0.731] | −7.2 | −0.057 |
| V2_A | no bias layer | 158 / +0.026 | 59 / +0.442 / 1.76 | 99 / +0.022 / 1.03 | 158 / +0.179 / 1.28 | [−0.070, +0.439] | −22.2 | −0.050 |
| V2_B | SMA200 only, no momentum vote | 59 / −0.183 | 23 / +0.752 / 2.40 | 38 / +0.176 / 1.30 | 61 / +0.393 / 1.69 | [−0.012, +0.824] | −10.9 | −0.044 |
| V2_C | breakout trigger only | 189 / −0.204 | 101 / +0.011 / 1.02 | 66 / −0.064 / 0.89 | 167 / −0.019 / 0.97 | [−0.205, +0.173] | −25.9 | −0.141 |
| V2_D | pullback + breakout | 225 / −0.165 | 113 / −0.024 / 0.97 | 90 / −0.085 / 0.84 | 203 / −0.051 / 0.92 | [−0.221, +0.126] | −32.4 | −0.177 |
| V2_E | min RR 1.0 | 96 / −0.237 | 62 / +0.386 / 1.80 | 48 / −0.030 / 0.93 | 110 / +0.205 / 1.45 | [−0.022, +0.443] | −9.6 | −0.028 |
| V2_F | v1.0 exits (no partial, no trail) | 63 / −0.390 | 24 / +0.295 / 1.53 | 38 / +0.173 / 1.42 | 62 / +0.220 / 1.47 | [−0.046, +0.497] | −6.5 | +0.008 |
| V2_G | no daily/weekly stops | identical to V2_0 (the stops never bound) | | | | | | |
| V2_H | cost stress (0.50 spread, 0.15 slippage) | 59 / −0.364 | 24 / +0.610 / 2.02 | 40 / +0.017 / 1.04 | 64 / +0.239 / 1.48 | [−0.102, +0.629] | −7.0 | −0.141 |
| V2_I | v1.0 signal window (07:00–15:45) | 43 / −0.130 | 21 / +0.920 / 2.87 | 34 / +0.101 / 1.24 | 55 / +0.414 / 1.93 | [+0.030, +0.851] | −7.7 | −0.022 |

Biased variants (V2_0, B, E, F, G, H, I) have no trades before 2022-01 because the bias needs 252 session days of warm-up; their development rows cover 2022-01 → 2024-06.

## 2. What each layer did

| Layer | Evidence from this run | Decision for v2.1 |
|---|---|---|
| L1 bias (SMA200 direction) | Cuts trades 158 → 61 out of sample, raises mean R +0.179 → +0.393 and cuts max DD −22 → −11 R (V2_A vs V2_B). But it made development **worse** (+0.026 → −0.183), and what it mostly removed were shorts (111 → 22) during a six-year uptrend, i.e. much of the gain is long beta. | **Keep, unproven.** Only broker data and the forward test can separate trend filter from beta. |
| L1 momentum vote (0.5× size on disagreement) | Same 61 trades as V2_B; disagreement trades averaged +0.301 R, so halving them only reduced total R (+0.339 vs +0.393 weighted). | **Drop.** No value shown. |
| Trigger A (v1.0 pullback) | Carries the whole result. | Keep. |
| Trigger B (Asian-range breakout) | Negative in every period alone (OOS −0.019, PF 0.97, DD −26 R) and drags the combination below zero (V2_D). Matches the published 288-variant finding. | **Reject.** |
| Min RR 1.5 vs 1.0 | Similar total R (20.7 vs 22.6) from fewer trades (61 vs 110); higher mean, lower DD. | Keep 1.5 (either is defensible). |
| L5 partial + Chandelier trail | Raises OOS mean R (+0.339 vs +0.220 with v1.0 exits) but makes the result depend on a dozen runners: 12 time exits averaged +2.4 R and 12 trail stops +1.4 R; ex-top-5 mean turns negative (−0.057 vs +0.008). T1 was reached in 41 % of trades. | Keep, flagged: the edge, if any, is in letting trend days run. |
| L0 daily/weekly stops | Never bound (7 setups skipped in six years); zero cost, zero benefit here. | Keep as account protection. |
| L0 widened window (to 16:45) | The six extra late trades cost about 2 R; V2_I with the v1.0 window is the only variant whose CI excludes zero (one of ten variants, expected by chance about half the time at 90 %). | Revert to 07:00–15:45. |
| Costs | Stress costs still leave OOS mean R +0.239 (v1.0 fell to −0.020 under the same stress): fewer, larger trades are less cost-sensitive. | — |
| Session | New York signals again dominate (V2_0: NY 26 trades +0.708 R, PF 3.1; London 35 trades +0.065). Third look at the same pattern (P1). | Do **not** adopt on this data; test P1 only on broker data / forward. |
| Year | 2024 H2 −0.29, **2025 +1.10** (21 trades), 2026 +0.03 mean R. | Regime dependence is the main risk. |

## 3. Verdict against the pre-registered rule (playbook v2 §11)

| Condition | V2_0 | Met? |
|---|---|---|
| ≥ 60 trades in validation and in final test | 23 / 38 | no |
| mean R > 0 in both | +0.752 / +0.089 | yes |
| PF > 1.10 in both | 2.40 / 1.22 | yes |
| 90 % bootstrap CI (validation+test) excludes zero | [−0.012, +0.731] | no |
| mean R ex-top-5 > 0 | −0.057 | no |
| beats v1.0 on OOS mean R and PF | +0.339 vs +0.076; 1.74 vs 1.13 | yes |

REJECTED conditions not met either (OOS mean R > 0; stress mean R positive in validation). **INCONCLUSIVE.** Layers rejected: Trigger B, momentum vote, widened window.

## 4. Proposed v2.1 (logged in PROJECT_STATE.md as P6; not yet evaluated on fresh data)

v2.0 minus Trigger B, minus the momentum vote, with the 07:00–15:45 window. On this data that configuration is V2_I-like (55 OOS trades, +0.414 R, PF 1.93, max DD −7.7 R) **and is the product of three looks at the same six years**; its first clean test is the broker export and the paper trade.

## 5. Sample-size reality

At σ ≈ 1.4 R per trade (observed) and a hoped-for 0.3 R edge, distinguishing from zero at 90 % one-sided needs about 36 trades; at a realistic 0.1 R edge, about 320. v2.1 generates roughly 25–40 trades a year on this data. A three-month paper trade will produce 6–10 trades: it validates execution and discipline, not the edge.

## 6. Files

backtest/engine_v2.py, analyze_v2.py, validate_engine_v2.py; results/V2_*/{trades.csv, skips.csv, config.json}; results/summary_v2.md, summary_v2.json, VALIDATION_MECHANICS_v2.md.

## 7. v2.2 candidates (added 2026-11-12, fourth look at the same data)

Aayan asked for the strategy to be improved. Three principled changes that no earlier pass had tested were run through the same engine and validator (`backtest/engine_v2.py`, variants V2_J/K/L):

| variant | dev n / mean R | validation n / mean R / PF | final test n / mean R / PF | OOS n / mean R / PF | OOS 90 % CI | OOS max DD | OOS mean R ex-top-5 |
|---|---|---|---|---|---|---|---|
| v2.1 (reference) | 43 / -0.130 | 21 / +0.920 / 2.87 | 34 / +0.101 / 1.24 | 55 / +0.414 / 1.93 | [+0.030, +0.851] | -7.7 | -0.022 |
| V2_K: touch bar must close on the trend side of EMA20 | 29 / -0.023 | 17 / +0.978 / 3.01 | 26 / +0.191 / 1.49 | 43 / +0.502 / 2.17 | [+0.043, +1.028] | -5.2 | -0.023 |
| V2_J: New York signals only (12:00–15:45 UTC) | 23 / -0.515 | 10 / +1.106 / 3.71 | 11 / +0.955 / 11.44 | 21 / +1.027 / 5.24 | [+0.437, +1.693] | -2.0 | +0.325 |
| V2_L: both | 14 / -0.277 | 6 / +1.437 / 5.23 | 9 / +0.985 / 9.80 | 15 / +1.166 / 6.74 | [+0.455, +2.017] | -1.1 | +0.289 |

**Reading.** The close-confirmation rule improves every out-of-sample statistic and, unlike every other variant so far, also improves the development period (−0.13 → −0.02 R) while keeping a usable trade count. It is adopted as **v2.2** (P7). The New York-only window again looks best out of sample and again loses in development on a small sample, the signature of a regime artefact; it remains an option (P1), not the default. Fourth-look caveat: all of these were chosen after seeing earlier results on this data; the forward test on the broker account is the only clean evidence.

**v2.2 = v2.1 + touch-bar close confirmation.** Pine script default MODE set to v2.2; v2.1 and New York-only remain selectable.

## 8. "One trade every day" (added 2026-11-12, fifth look at the same data)

Aayan asked for the system to trade every day. Pre-registered before running: Trigger C, a market order on the next minute if the session day has had no entry by a fixed bar, stop 1.5 × ATR14(M15), first target at 1.5 × that distance, same partial / trail / 20:50 exits, same gates. Three direction and timing rules, all on top of v2.2 (`engine_v2.py` variants V2_M/N/O):

| variant | forced trades (trig C) | C: dev mean R | C: validation mean R | C: final test mean R | C: all-period total R | whole system max DD (dev / val / test) | losing days |
|---|---|---|---|---|---|---|---|
| V2_M: 13:30 UTC, direction = daily SMA200 bias | 1,032 | −0.047 | −0.028 | +0.064 | −14.3 | −41 / −21 / −18 R | 59 % |
| V2_N: 13:30 UTC, direction = +DI vs −DI, no bias | 1,163 | −0.042 | −0.074 | +0.027 | −40.3 | −46 / −26 / −15 R | 60 % |
| V2_O: 08:00 UTC, direction = daily SMA200 bias | 1,130 | −0.124 | +0.081 | −0.129 | −83.8 | −87 / −16 / −71 R | 60 % |

The pullback trades (trig A) inside these runs are unchanged from v2.2. The forced trades win about 40 % of the time with a profit factor of 0.77–1.13: a direction call with no edge, minus spread and commission, which on a 7 USD stop cost about 0.05 R per trade. The drawdowns of 40–87 R would close a 6 % trailing account at any risk size. Six of nine period results are negative; the one positive period (V2_O validation) is followed by the worst final test.

**Verdict: rejected.** A trade every day cannot be made from this data; the market does not offer a daily edge at this timeframe, only on the days the pullback setup appears. Not added to the Pine script. If Aayan wants it for paper trading only, it goes in as a separate mode labelled with this result.
