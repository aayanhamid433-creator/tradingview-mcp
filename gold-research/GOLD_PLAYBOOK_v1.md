# GOLD_PLAYBOOK v1.0 — "Holy Grail" trend-pullback, intraday XAUUSD

**Status:** FROZEN 2026-11-09 00:30 UTC, before any backtest result was inspected.
**Validation status:** see VALIDATION_REPORT.md (this file never changes to match results; changes go to a new version).
**Owner:** Aayan. **Prepared by:** Claude (research assistant).
**Plain-English summary:** When gold is in a strong, measurable trend (ADX above 30), wait for the price to pull back and touch the 20-period exponential moving average, then enter in the trend direction when price turns back up (or down) past the high (or low) of the pullback candle. The stop goes just beyond the pullback low (or high); the target is a retest of the recent high (or low).

Every rule below is tagged:
- **SOURCE RULE** — stated explicitly by the cited source.
- **PROPOSED ADAPTATION** — introduced for this project (a frozen research assumption, not the source author's rule and not an evidence-backed risk limit).
- **UNRESOLVED** — not specified by the source and deliberately not used in v1.0.

Primary source for the pattern: Linda Bradford Raschke, interview by David Vomund, *AIQ Opening Bell Monthly*, Vol. 6 Issue 8, August 1997, box "Holy Grail Pattern — Buy rules (sells are reversed)", PDF read in full on 2026-11-09 from https://lindaraschke.net/wp-content/uploads/2026/01/august1997.pdf. The pattern is also published in Connors & Raschke, *Street Smarts* (1995/1996), which was not accessible to us; see RESEARCH_SOURCES.md for evidence labels.

---

## 1. Instrument and feed assumptions

| Item | Value | Tag |
|---|---|---|
| Instrument | XAUUSD (spot gold vs USD CFD) on MetaTrader 5. Broker and symbol **unconfirmed** by Aayan. | assumption |
| Research data | HistData.com 1-minute BID bars, 2021-01-04 → 2026-10-30, converted to UTC (see data/DATA_AUDIT.md). Not the broker feed. | assumption |
| Ask price | bid + constant modelled spread (data has no ask). | PROPOSED ADAPTATION |
| Contract | 100 oz per 1.00 lot assumed for sizing examples only; must be confirmed from the broker's MT5 symbol specification. No lot sizes are produced until §11 inputs exist. | assumption |
| Timezone | All rules in UTC. Display in America/Toronto. Journals keep UTC. | convention |

## 2. Holding period and timeframes

| Item | Value | Tag |
|---|---|---|
| Holding period | Intraday only. All positions closed by 20:50 UTC the same day. | PROPOSED ADAPTATION |
| Decision timeframe | M15 bars, UTC-aligned (bar label = open time). All signals use the **closed** M15 bar. | PROPOSED ADAPTATION (source shows daily bars but states the pattern is generic; timeframe is the project's choice) |
| Fill timeframe | M1 bars simulate order execution after the M15 signal bar closes. | PROPOSED ADAPTATION |
| Context timeframes | H4 and H1 are for the human's situational awareness only; **no rule in v1.0 reads them**. | convention |

## 3. Sessions and daylight-saving handling

| Item | Value | Tag |
|---|---|---|
| Entry window | New pending orders only when the signal bar closes between **07:00 and 15:45 UTC** inclusive (orders may therefore trigger up to 16:00 UTC). This covers the London morning and the New York morning including the COMEX 08:20 ET open. | PROPOSED ADAPTATION |
| Pending-order cut-off | Any unfilled pending order is cancelled at 16:00 UTC. | PROPOSED ADAPTATION |
| Forced exit | Any open position is closed at market on the first M1 bar at or after 20:50 UTC (before the broker daily break and swap time, which falls at 21:00–22:00 UTC depending on US DST). | PROPOSED ADAPTATION |
| DST | Windows are fixed in UTC and **not** shifted for London/New York DST. This is a deliberate simplification; the effect is that in summer the window starts one hour "later" in London local time. Recorded as a known limitation. | PROPOSED ADAPTATION |
| Session labels for reporting | London = signal bar 07:00–11:59 UTC; New York = 12:00–15:45 UTC. | convention |

## 4. Objective trend classification

Plain English: ADX (Average Directional Index) is a 0–100 number that measures how strongly price is trending, regardless of direction. +DI and −DI are the two directional lines that feed it.

| Rule | Definition | Tag |
|---|---|---|
| Indicators | Wilder ADX(14), +DI(14), −DI(14) and EMA(20) of close, all on closed M15 bars. ATR(14) (Wilder) on M15 for buffers. | SOURCE RULE for ADX 14 and EMA 20 ("The 14-period ADX…", "20 period exponential moving average"); ATR use is PROPOSED |
| Trend present ("armed") | At the signal bar *t*: ADX[t] > 30 **and** there exists a bar *k* in [t−10, t] with ADX[k] > 30 and ADX[k] > ADX[k−1]. | SOURCE RULE "must initially be greater than 30 and rising"; the 10-bar look-back that operationalises "initially" is PROPOSED |
| Trend direction | Long setups only if +DI[t] > −DI[t]; short setups only if −DI[t] > +DI[t]. | PROPOSED ADAPTATION (source gives buy rules and says "sells are reversed" without a direction test) |
| Not a trend | Any bar failing the above → no setup, decision = WAIT. | convention |

## 5. Setup, confirmation and entry

Long case; the short case mirrors every inequality.

| Step | Rule | Tag |
|---|---|---|
| 5.1 Touch bar | Closed M15 bar *t* with low[t] ≤ EMA20[t] and high[t] ≥ EMA20[t] (the bar touched or crossed the EMA but did not close an entire bar below it), with §4 satisfied at *t*. | SOURCE RULE "retracement in price to the 20 period exponential moving average… When the price touches the 20 period moving average"; the requirement high ≥ EMA is PROPOSED |
| 5.2 Pending entry | Immediately after bar *t* closes, place a **buy stop** at high[t] + 0.10 USD. | SOURCE RULE "put a buy stop above the high of the previous bar"; the 0.10 USD offset is PROPOSED |
| 5.3 Re-arming | If the order is unfilled and a later bar *t+j* (j = 1…4) is itself a valid touch bar (§5.1 with §4), move the buy stop to high[t+j] + 0.10 and restart the expiry clock. The pullback sequence then spans bars *t … t+j*. | PROPOSED ADAPTATION |
| 5.4 Expiry | The pending order expires if unfilled by the close of the 4th M15 bar after the (latest) touch bar, or at 16:00 UTC, whichever is first. | PROPOSED ADAPTATION |
| 5.5 Cancellation | Cancel the pending order if any closed bar in the sequence has close < EMA20 − 0.5 × ATR14 (deep break of the average), or ADX falls below 25, or a position is already open. | PROPOSED ADAPTATION |
| 5.6 Trigger | A buy stop at level L fills on the first M1 bar whose modelled **ask high** (bid high + spread) ≥ L. Fill price = max(L, ask open of that M1 bar) + slippage. | PROPOSED ADAPTATION (execution convention) |
| 5.7 Late entry | No entry after 16:00 UTC; no chasing: if the order was cancelled or expired, the setup is over until a new touch bar appears. | PROPOSED ADAPTATION |
| 5.8 Minimum reward | At order placement, gross reward/risk = (target − entry)/(entry − stop) must be ≥ 1.0 or the setup is skipped and logged as WAIT (RR_TOO_LOW). | PROPOSED ADAPTATION |

## 6. Stop-loss and invalidation

| Rule | Definition | Tag |
|---|---|---|
| Swing low | The lowest low of the pullback sequence (bars *t … t+j* plus any M1 lows observed between the last closed bar and the fill minute). | SOURCE RULE "protective sell stop at the newly formed swing low"; the exact definition is PROPOSED |
| Buffer | Stop = swing low − max(0.30 USD, 0.10 × ATR14[t]). | PROPOSED ADAPTATION |
| Invalidation meaning | The pullback low is broken: the trend continuation hypothesis has failed. | SOURCE rationale |
| Stop fill | Sell stop at S fills on the first M1 bar whose bid low ≤ S at min(S, bid open) − slippage. | PROPOSED ADAPTATION |
| Modification | The stop is never widened. | PROPOSED ADAPTATION |

## 7. Targets and management

| Rule | Definition | Tag |
|---|---|---|
| Target | The recent momentum high = highest high of the 20 closed M15 bars ending at the first touch bar *t*. | SOURCE rationale ("when a security makes a new momentum high and pulls back, it will retest its recent high"); the 20-bar window is PROPOSED |
| Target fill | Sell limit at T fills only if an M1 bid high > T (trade-through by at least one tick). A touched limit is not a fill. | PROPOSED ADAPTATION (conservative convention) |
| Same-bar ambiguity | If stop and target are both reachable within one M1 bar, the **stop is assumed first**. The count of such bars is reported, with the opposite assumption as a sensitivity. | PROPOSED ADAPTATION |
| Trailing stop | "Trail stops as profits grow" is a SOURCE RULE but has no stated method. **UNRESOLVED — not used in v1.0.** | UNRESOLVED |
| Partial exits, breakeven | None. | PROPOSED ADAPTATION |
| Time exit | Market close at 20:50 UTC (§3). | PROPOSED ADAPTATION |

## 8. Costs (research cost model, per ounce)

| Scenario | Spread | Slippage on stop fills (entry and stop-loss) | Commission | Financing |
|---|---|---|---|---|
| Base | 0.25 USD | 0.05 USD per fill | 0 (standard-account assumption) | 0 (no overnight holds) |
| Stress | 0.50 USD | 0.15 USD per fill | 0 | 0 |
| Raw-account | 0.10 USD | 0.05 USD per fill | 0.07 USD/oz round trip (≈ USD 7 per 100-oz lot) | 0 |

Basis: broker "typical spread" figures seen in search snippets on 2026-11-09 (e.g. Pepperstone Standard avg ≈ 0.25, Razor avg ≈ 0.12 + USD 3.50/lot/side). These are **assumptions**, not the user's broker's numbers. Costs are applied once each: spread through ask = bid + spread, slippage only on stop-type fills, commission as a flat per-ounce deduction. Spread widening around news is **not** modelled.

## 9. News exclusions

| Item | Value | Tag |
|---|---|---|
| Primary tested variant | **Filter-free.** Historical high-impact calendar could not be downloaded in this session (BLS, Federal Reserve and calendar hosts are not reachable from the container), so no exact filter was reconstructed. | disclosure |
| Live rule (for screenshots) | No new pending orders from 15 minutes before to 15 minutes after US CPI, NFP (Employment Situation), FOMC statement/press conference, and core PCE; verify times on the day from the official BLS/Federal Reserve schedules or a dated calendar. Cancel pending orders inside the window. Open positions are left to their stop/target (prop-firm rules may require otherwise — see §11). | PROPOSED ADAPTATION |
| Sensitivity variant | Approximate filter: NFP = first Friday of the month 12:30/13:30 UTC; FOMC statement dates from a list of meeting dates recorded in the backtest config, **not verified against federalreserve.gov in this session**. Labelled APPROXIMATE in the report. | PROPOSED ADAPTATION |

## 10. Limits

| Item | Value | Tag |
|---|---|---|
| Concurrent positions | 1 | PROPOSED ADAPTATION |
| Trades per UTC day | max 3 | PROPOSED ADAPTATION |
| Daily/weekly loss limits | **Not set** — depend on the user's account/prop rules (unknown). | UNRESOLVED |
| Risk per trade | Expressed in R only. No monetary sizing until §11 inputs are supplied. | convention |

## 11. Position sizing and account compliance (inputs required before any lot size)

Lot size is **not calculated** until Aayan supplies: account equity and currency; chosen risk budget per trade; broker XAUUSD contract size, tick size/value, min/step/max volume; entry, stop and cost assumptions; existing exposure; and for a prop account the exact firm, account type, current official rules, current drawdown headroom, reset timezone and news/holding restrictions. Sizing formula to be used then: lots = floor_to_step( (risk_budget_after_costs_and_reserve) / (|entry − stop| × contract_size × currency_conversion) ). If minimum volume exceeds the risk budget → WAIT.

## 12. WAIT conditions (any one is sufficient)

1. §4 trend conditions not met at the latest closed M15 bar.
2. No valid touch bar in the current sequence, or the pending order expired/cancelled.
3. Signal outside 07:00–15:45 UTC, or quote/chart older than one M15 bar.
4. Gross reward/risk < 1.0 at the proposed levels.
5. Spread at the time of the decision > 0.60 USD (PROPOSED maximum acceptable spread) or unknown when a live plan is requested.
6. Inside a §9 news window, or news status unknown when a live plan is requested.
7. Price has already traded through the entry level (setup already triggered) or beyond the target.
8. A position is already open, or the daily trade cap is reached.
9. Any chart price that cannot be read reliably.

## 13. Pre-registered test design (frozen with the rules)

| Item | Value |
|---|---|
| Development period | 2021-01-04 → 2024-06-30 (≈ 60 %) |
| Validation period | 2024-07-01 → 2025-08-31 (≈ 20 %) |
| Final test period | 2025-09-01 → 2026-10-30 (≈ 20 %), untouched by any tuning |
| Indicator warm-up | Indicators are computed on the continuous series; the first 200 M15 bars of the dataset are excluded. Splits are applied to signal time, so a trade belongs to the period in which its signal bar closed; positions never span a split boundary by more than one day (intraday). |
| Metrics | trade count, net R total, mean R (expectancy), win rate, avg win/avg loss, profit factor, max drawdown in R and its duration, longest losing streak, exposure (hours in market / total session hours), median holding time, results by session and by direction, by year; sensitivity to cost scenarios and ±1 parameter steps; share of total R from the top 5 trades; bootstrap 90 % interval of mean R (trade-level resampling, independence assumption flagged) |
| Decision rule | **SUPPORTED FOR DEMO** if, with base costs, mean R > 0 in validation **and** in final test, profit factor > 1.10 in both, at least 60 trades in each, the 90 % bootstrap interval for mean R on validation+test combined excludes 0, and removing the 5 best trades from validation+test still leaves mean R > 0. **REJECTED** if mean R ≤ 0 with base costs in validation+test combined and the bootstrap interval's upper bound < +0.10 R, or if the stress-cost mean R < −0.10 R in both out-of-sample periods. Otherwise **INCONCLUSIVE**. |
| Variants to be run and recorded | V0 base; cost stress; raw-account costs; ADX threshold 25 and 35; London-only and New York-only windows; min R:R 1.5; no re-arming; target-first ambiguity convention; approximate news filter. No other variants will be added without logging them. |

## 14. Version control

- v1.0 frozen 2026-11-09. Proposed changes are logged in PROJECT_STATE.md under "Proposed changes (not yet evaluated)" and become v1.1 only after a fresh evaluation on data not used to propose them.
