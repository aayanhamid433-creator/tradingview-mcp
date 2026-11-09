# GOLD_PLAYBOOK v2.0 CANDIDATE — layered combination of documented gold methods, intraday XAUUSD

**Status:** CANDIDATE, written 2026-11-09. **UNTESTED.** Not a replacement for v1.0 (which stays frozen in GOLD_PLAYBOOK_v1.md). **Use status for any chart analysis: UNVALIDATED DEMO.**
**Owner:** Aayan. **Prepared by:** Claude (research assistant). **Validation plan:** paper trade per FORWARD_TEST_PROTOCOL.md with the additions in §12, and (recommended) a backtest with the existing engine before or alongside it (§13).

## 0. What this is, and the honest warning

Aayan asked for the methods of the best-documented gold traders to be combined into one system. The research (RESEARCH_SOURCES.md, RESEARCH_SOURCES_v2_ADDENDUM.md, research_notes/) found that:

- The famous names (Tudor Jones, Druckenmiller, Soros, Paulson, Dalio, Brandt, Williams) trade gold on **weeks-to-years** horizons. What transfers to intraday is their **bias filters and risk discipline**, not entries.
- The only rule sets with multi-decade, cost-inclusive evidence are **trend following** (12-month momentum, 200-day / 10-month moving average), and that evidence is at portfolio level, weak in commodities after 2010, and never published for gold alone.
- The intraday retail methods (London breakout, COMEX opening range, VWAP, order blocks, scalping) have **no independently substantiated gold record**. The one careful out-of-sample test of the gold session breakout (288 variants, 18 years, costs) found no edge beyond gold's uptrend. The one controlled test of order blocks found them indistinguishable from random levels.
- The risk rules (1 % risk, never average losers, cut size in drawdown, daily stop) are the most consistently stated element across every documented trader and are the part most worth copying.

So combining "everything" would stack untested entries on top of each other. Instead, v2.0 is built as **layers**: each borrowed idea is one switchable module with its own source tag and evidence label, so that the paper trade and backtest can tell which layers help and which are dead weight. The default build switches on every layer that has at least some evidence or a clear risk rationale; layers with evidence **against** them are included only as pre-registered ablation variants (§11), not in the default.

Tags: **SOURCE RULE** (stated by the cited source) / **PROPOSED ADAPTATION** (ours) / **UNRESOLVED** (not specified, not used). Evidence labels per RESEARCH_SOURCES.md: *independently substantiated* / *self-reported* / *no usable performance record found*.

## 1. Architecture

```
L0 Execution gates   -> may I trade at all right now?   (spread, time, news, daily/weekly stops)
L1 Daily bias        -> which direction is allowed, at what size?   (200-day SMA + 12-1 momentum)
L2 Session map       -> where are the reference levels today?   (Asian range, prior day H/L, 20-bar extremes)
L3 Setup trigger     -> is there a setup?   (A: trend pullback = v1.0 Holy Grail; B: range breakout, ablation only)
L4 Entry and stop    -> exact order levels   (stop entry beyond trigger bar; stop beyond swing + buffer)
L5 Targets and exits -> how the trade ends   (first target = retest; remainder = ATR trail; time exit)
L6 Risk and sizing   -> how much   (fixed-fraction R, drawdown scaling, three-strike stop, caps)
L7 Weekly context    -> logged, not acted on   (COT index, real yields / DXY, seasonality)
```

A trade happens only when L0 passes, L1 allows the direction, L3 fires, L4 gives a reward/risk at or above the minimum, and L6 has budget. Everything else is logging.

## 2. Instrument, data and timeframes (unchanged from v1.0 unless stated)

| Item | Value | Tag |
|---|---|---|
| Instrument | XAUUSD CFD on MT5; broker **unconfirmed**. Aayan's charts are FOREX.com Gold Spot/USD. FOREX.com regional pages show 1 lot = 10 oz, min 1 lot, margin from 5 % (UK/IE/AU), spread "from 0.10" with measured averages ≈ 0.30 (third-party). Verify in the MT5 symbol specification. | assumption (SNIPPET sources) |
| Decision timeframe | M15 closed bars for L3/L4; D1 closed bars for L1; M1 for fills and L0 checks. | PROPOSED ADAPTATION |
| Timezone | UTC for all rules. Session day = 23:00 UTC to 22:00 UTC (matches the feed's daily break). | convention |
| Research data | HistData M1 bid 2021-01 → 2026-10 (data/DATA_AUDIT.md); facts in results/DATA_FACTS.md. | assumption |

## 3. L0 — Execution gates (any failed gate = WAIT; nothing below is a signal)

| Gate | Rule | Source / evidence |
|---|---|---|
| 0.1 Entry window | New orders only when the M15 signal bar closes between **07:00 and 16:45 UTC**. Pending orders cancelled at **17:00 UTC**. | PROPOSED ADAPTATION. Widened from v1.0 (15:45) to include the 16:00 UTC hour: DATA_FACTS §3 shows 13:00–16:59 UTC carries the highest M15 ranges (1.2–1.75× the day median) and third-party spread logs show the London/NY overlap as the tightest spreads (SNIPPET). |
| 0.2 Forced flat | Close any position at market on the first M1 bar at or after **20:50 UTC**. No positions through the 21:00–23:00 UTC break (spreads reported at 1.2–2.8 USD for 5–20 min; stops do not execute during the break). | v1.0 rule kept; break-spread figures *self-reported* third-party logs |
| 0.3 News blackout | No new orders, and cancel pending orders, from **3 min before to 3 min after** US 08:30 ET releases (NFP, CPI, PCE, GDP advance, retail sales) and from **5 min before to 15 min after** the FOMC statement (14:00 ET) and through the press conference start (14:30 ET). Open positions keep their stop and target. | PROPOSED ADAPTATION. Basis: bulk of gold's reaction completes within ~90 s (Smales & Yang 2015, SNIPPET), 08:30 releases have the largest effect (Elder, Miao & Ramchander 2012, SNIPPET), FTMO funded accounts forbid activity ±2 min (SNIPPET). Window is set wider than the evidence to cover spread widening (1–5 USD for 30–90 s reported). |
| 0.4 Spread gate | No entry if the live spread > **0.60 USD** (v1.0) or unknown. Log the spread on every decision. | PROPOSED ADAPTATION |
| 0.5 Daily stop | Stop trading for the session day after **3 consecutive losing trades** or when the day's closed P&L reaches **−2 R**, whichever first. | PROPOSED ADAPTATION. "Three strikes" is a folk rule with no primary source or test; Tudor Jones' "decrease your trading volume when you are trading poorly" (*Market Wizards*, reprint SNIPPET) is the stated principle. Chosen so one bad day cannot breach a 5 % prop daily limit at 0.5 % risk. |
| 0.6 Weekly stop | Stop for the week at **−4 R** closed. | PROPOSED ADAPTATION (no source; sized from §9 streak math) |
| 0.7 Monday open | No entries before **08:00 UTC on Monday** if the weekend gap exceeds 1 × daily ATR(14). | PROPOSED ADAPTATION. DATA_FACTS §6: median |gap| 1.5 USD but 90th percentile 15.7 USD, 36 USD in 2025–26. |
| 0.8 Trade cap | Max **3 entries per session day**, max **1 open position**. | v1.0 |

## 4. L1 — Daily bias (direction allowed and size multiplier)

Computed once per session day from the previous **closed D1 bar** (23:00–22:00 UTC day).

| Rule | Definition | Source / evidence |
|---|---|---|
| 1.1 Trend state | TREND_UP if close > SMA200(close); TREND_DOWN if close < SMA200. | SOURCE RULE (Tudor Jones: "My metric for everything I look at is the 200-day moving average of closing prices", Robbins 2014, reprint SNIPPET). Evidence: conditional returns only (SentimenTrader: gold ≈ 12 %/yr above vs ≈ 2 % below since 1975, SNIPPET; DATA_FACTS §5: +7.9 bps/day t 2.1 above vs +3.0 bps t 0.5 below, 2021–26). *Self-reported / descriptive; no cost-inclusive gold test.* |
| 1.2 Momentum vote | MOM_UP if close(t−21 days) / close(t−252 days) − 1 > 0; else MOM_DOWN. (12-month return skipping the latest month.) | SOURCE RULE (Moskowitz, Ooi & Pedersen 2012; Hurst, Ooi & Pedersen 2017, SNIPPET). Evidence: *independently substantiated at portfolio level* (Sharpe ≈ 0.8 over 1880–2013 net of costs and fees), gold-only number never published, weak in commodities 2010–2020 (Clare et al. replication Sharpe −0.13, SNIPPET). |
| 1.3 Allowed direction | TREND_UP → long setups only. TREND_DOWN → short setups only. | PROPOSED ADAPTATION |
| 1.4 Size multiplier | 1.0 if the momentum vote agrees with the trend state; **0.5** if it disagrees. | PROPOSED ADAPTATION |
| 1.5 Flip handling | A bias change applies from the next session day; it never closes an open trade (L5 does). | PROPOSED ADAPTATION |
| Disclosure | 2021–2026 was a strong uptrend (gold ≈ 1,800 → 4,500): 77 % of days were above SMA200, so any long-bias filter looks good in this sample. The bias layer is the first ablation to run (§11, V2-A). | — |

## 5. L2 — Session map (reference levels; computed, not traded directly)

| Level | Definition | Used by |
|---|---|---|
| Asian range | High and low of M1 bars from **23:00 to 07:00 UTC** (fixed window; the most common definition in the breakout literature, SNIPPET). | Trigger B (ablation), §12 logging |
| Prior-day H/L | High/low of the previous session day. | §12 logging; Trigger A target cap (5.2) |
| Momentum extreme | Highest high (longs) / lowest low (shorts) of the 20 closed M15 bars ending at the first touch bar. | Trigger A target (v1.0) |
| M15 ATR(14) | Wilder, on closed M15 bars. Median 7.05 USD in 2025–26 (DATA_FACTS §2). | Buffers, trail |
| D1 ATR(14) | Wilder, on session-day bars. Median 107 USD in 2026 (DATA_FACTS §1). | Gate 0.7, sanity cap on stop distance (6.4) |

## 6. L3/L4 — Setup, entry and stop

### Trigger A — trend pullback (default ON; this is v1.0 §4–§6 unchanged except where marked)

| Step | Rule | Tag |
|---|---|---|
| A.1 Armed | ADX(14) > 30 at the signal bar and some bar in the last 10 with ADX > 30 and rising; +DI > −DI for longs, −DI > +DI for shorts. | SOURCE RULE (Raschke 1997, READ IN FULL) + v1.0 PROPOSED details |
| A.2 Touch bar | Closed M15 bar with low ≤ EMA20 ≤ high (long case; mirrored for shorts). | SOURCE RULE + PROPOSED |
| A.3 Direction gate | **New in v2.0:** the setup direction must equal the L1 allowed direction. | PROPOSED ADAPTATION |
| A.4 Entry | Buy stop at high[touch bar] + 0.10 USD; re-arm on later valid touch bars (up to 4); expire after 4 bars or at 17:00 UTC; cancel on deep break (close < EMA20 − 0.5 × ATR14) or ADX < 25. | v1.0 |
| A.5 Stop | Swing low of the pullback sequence (bars from first touch through the fill minute, M1 lows included) − max(0.30 USD, 0.10 × ATR14). | v1.0 (SOURCE RULE "protective sell stop at the newly formed swing low"; Brandt's "Last Day Rule" places the stop just beyond the extreme of the breakout bar, which is the same construction, SNIPPET) |
| A.6 Minimum reward/risk | Gross (first target − entry)/(entry − stop) ≥ **1.5** at placement. | PROPOSED ADAPTATION. **Changed from v1.0's 1.0**: this is proposal P2 in PROJECT_STATE.md (V7 was slightly better out of sample, not significant). Tudor Jones' stated 5:1 (Robbins 2014, SNIPPET) is not reachable with a retest target intraday; 1.5 is the compromise and is an ablation (V2-E). |
| A.7 Stop-distance sanity | If (entry − stop) > 0.6 × D1 ATR(14), skip (WAIT: STOP_TOO_WIDE). | PROPOSED ADAPTATION (keeps one M15 setup from carrying a swing-sized risk on gap days) |

### Trigger B — session breakout (default **OFF**; ablation variant V2-C only)

| Step | Rule | Tag |
|---|---|---|
| B.1 Window | First closed M15 bar between 07:00 and 10:45 UTC that closes outside the Asian range, in the L1 direction, with ADX(14) > 20. | PROPOSED ADAPTATION (London/Asian-range breakout folklore, no author; Crabel ORB and Turtle breakouts are the published ancestors, SNIPPET) |
| B.2 Entry | Stop order at the breakout bar's extreme + 0.10 USD; valid for 2 bars. | PROPOSED |
| B.3 Stop | Opposite side of the Asian range + buffer, capped at 2 × ATR14(M15) (Turtle 2N analogue). | PROPOSED |
| B.4 Target | 1 × Asian-range height from the breakout level; then L5 trail. | PROPOSED |
| Why OFF by default | The most careful retail test (288 variants, gold 2008–2026, costs, in/out-of-sample: 14 of 288 profitable in both halves vs ≈ 15 expected by chance) found **no edge** beyond long beta (SNIPPET). It is kept as a pre-registered variant so the paper trade can log the setups without trading them. | disclosure |

## 7. L5 — Targets and exits

| Rule | Definition | Source / evidence |
|---|---|---|
| 5.1 First target (T1) | The momentum extreme (highest high of the 20 closed M15 bars ending at the first touch bar). Fill requires a trade-through (M1 bid high > T1). | SOURCE rationale (Raschke: "it will retest its recent high", READ IN FULL); v1.0 convention |
| 5.2 Target cap | If T1 is beyond the prior-day high (longs) by more than 1 × ATR14(M15), T1 = prior-day high. | PROPOSED ADAPTATION (no source; avoids targets in air on gap days) |
| 5.3 Partial exit | At T1 close **50 %** of the position and move the stop on the remainder to **entry + 0.10 USD** (breakeven plus costs). | PROPOSED ADAPTATION. Brandt's "popcorn trade" rule (take partial profit / tighten once a target is approached so a winner does not round-trip, *Diary of a Professional Commodity Trader* 2011, SNIPPET); Shannon's AVWAP method scales 1/3 at 1R (SNIPPET). No published test of partial exits on gold. |
| 5.4 Trail on remainder | Chandelier: stop = highest high since entry − **3 × ATR14(M15)**, ratcheted up only, never beyond the current M15 bar's low. | SOURCE RULE (LeBeau's Chandelier exit, 3 × ATR, SNIPPET; Raschke's "trail stops as profits grow" names no method). *No published comparison of exit methods found.* |
| 5.5 Time exit | 20:50 UTC market close of anything open. | v1.0 |
| 5.6 Same-minute ambiguity | Stop assumed first. | v1.0 |
| 5.7 Never | Never widen a stop. Never add to a losing position. | SOURCE RULE (Tudor Jones "Don't ever average losers", *Market Wizards* reprint SNIPPET; Seykota "cut losses", SNIPPET) |
| R accounting | R is defined on the **initial** stop. A trade that hits T1 then stops at breakeven realises ≈ +0.5 × RR_T1 R. | convention |

## 8. L6 — Risk and sizing

| Rule | Definition | Source / evidence |
|---|---|---|
| 6.1 Risk per trade | **0.5 %** of account equity per trade at size multiplier 1.0 (0.25 % at 0.5). | PROPOSED ADAPTATION within the documented range: Brandt ≤ 1 % (own tweet thread, SNIPPET); Kovner "1 to 2 percent" and "cut it at least in half" (*Market Wizards* reprint, SNIPPET); Turtle unit = 1 % per N with a 2N stop (Faith 2003, SNIPPET). Half of the common 1 % because a single instrument has no diversification. |
| 6.2 Size formula | lots = floor_to_step( equity × risk% × multiplier ÷ (|entry − stop| × contract_oz × fx) ). If min lot exceeds the budget → WAIT. | Tharp percent-risk model (SNIPPET) = playbook v1.0 §11 |
| 6.3 Drawdown scaling | For every **10 % peak-to-trough drawdown** in equity, compute size as if equity were **20 % smaller**; restore when a new equity high is made. | SOURCE RULE (Turtle recovery rule, SNIPPET; Tudor Jones "when I am trading poorly, I keep reducing my position size", reprint SNIPPET) |
| 6.4 Hard caps | Max 1 open position; max 3 entries/day; daily −2 R; weekly −4 R; FTMO-style 5 %/10 % limits respected with ≥ 50 % headroom. | §3 + prop-firm figures (SNIPPET; verify on the firm's page) |
| 6.5 Monetary sizing | Still **not produced** until the §11 inputs of v1.0 are supplied (equity, currency, contract spec, prop rules). | unchanged |
| 6.6 What sizing cannot do | None of these rules creates an edge. With σ ≈ 1.2 R per trade, a true 0.1 R expectancy needs ≈ 240 trades (90 % one-sided) to ≈ 550 trades (95 % two-sided) to be distinguishable from zero (n = (z·σ/μ)²). At a 40 % win rate, an 8-loss streak has ≈ 75 % probability within 200 trades. Size so that −10 R is survivable. | arithmetic (risk note §6) |

## 9. L7 — Weekly context (logged every Monday; **no automatic rule in v2.0**)

| Input | Definition | Why logged, not acted on |
|---|---|---|
| COT index | (commercial net − 3-year min)/(3-year max − min) × 100 from the CFTC gold report. | Williams' 75/25 thresholds (book, SNIPPET; threshold variants unresolved). Academic evidence: net positions **follow** returns; only extremes show weak forecasting value in gold (Mutafoglu et al. 2012, SNIPPET). *Candidate rule for v2.1:* no new longs when managed-money net long > 90th percentile. |
| Real yield / dollar | Direction of 10-y TIPS yield and DXY over the past week. | Druckenmiller/Soros logic ("gold trades off interest rates", SNIPPET). Evidence is contemporaneous only; the relationship weakened 2022–2025 (Chicago Fed 2021, WGC, SNIPPET). |
| Seasonality | Month and weekday. | Baur's autumn effect **reversed** out of sample (Potrykus & Augustynowicz 2024, SNIPPET); weekday effects pre-2011 only. Logged to test, not to trade. |
| Macro calendar | This week's 08:30 ET and FOMC dates/times from BLS and the Federal Reserve. | Feeds gate 0.3 |

## 10. What was deliberately left out (and why)

| Idea | Reason |
|---|---|
| ICT order blocks / fair value gaps / "smart money" | Only controlled test: order blocks ≈ random levels (1,854 zones, SNIPPET). No reproducible break-of-structure definition. |
| VWAP / anchored VWAP | No volume on CFD gold (tick volume only); no cost-inclusive test. May be logged as a reference line later. |
| M1/M5 EMA/RSI scalping | Every published result is gross of costs; with a 0.25–0.35 USD spread and sub-2 USD targets the edge is negative by arithmetic. |
| London PM fix drift | Pre-2015 effect; not documented as persisting after the LBMA auction reform (Crain & Hoelscher, SNIPPET). |
| Discretionary macro sizing ("go for the jugular") | Druckenmiller's concentration advice is for conviction macro bets with audited-fund risk control; the opposite of what a single-instrument intraday account needs. |
| Paulson-style thesis without price invalidation | −71 % in 2013 (self-reported via press). Negative example. |
| Grid / martingale / "verified" EAs | Typical 30–60 % max drawdown and survivorship bias; benchmark of what to avoid. |

## 11. Pre-registered variants (frozen with this document; nothing else may be added without logging)

| id | change from the default build | question it answers |
|---|---|---|
| **V2.0** | default: L0–L6 as above, Trigger A only | the combination |
| V1.0 | the frozen v1.0 engine | baseline (already run: mean R +0.076 out of sample, INCONCLUSIVE) |
| V2-A | no L1 bias (both directions, multiplier 1.0) | is the bias layer beta or edge? |
| V2-B | L1 trend state only (no momentum vote / multiplier) | is the second vote worth anything? |
| V2-C | Trigger B ON, Trigger A OFF | does the breakout add anything on its own? |
| V2-D | Trigger A + Trigger B both ON | combination of triggers |
| V2-E | min RR 1.0 instead of 1.5 | P2 proposal |
| V2-F | v1.0 exits (single target, no partial, no trail) | does the partial + trail help? |
| V2-G | no daily/weekly stop, no three-strike | do the behavioural stops cost expectancy? |
| V2-H | cost stress (spread 0.50, slippage 0.15) | cost sensitivity |
| V2-I | signal window 07:00–15:45 (v1.0 window) | does the extra hour matter? |

**Decision rule (same thresholds as v1.0 §13, plus one):** v2.0 is SUPPORTED FOR DEMO only if it meets every v1.0 §13 condition **and** beats v1.0 on validation+test combined in both mean R and profit factor. If v2.0 and v1.0 tie within the bootstrap interval, the **simpler** (v1.0) wins. REJECTED and INCONCLUSIVE as in v1.0. The development/validation/test split is unchanged, but note that proposals P1/P2 and the bias layer were formed after seeing v1.0's results on this data, so a v2.0 backtest on HistData is **contaminated** for those elements; only broker data not yet seen and the forward test are clean.

## 12. Paper-trade additions (on top of FORWARD_TEST_PROTOCOL.md)

1. Every setup row in journal/GOLD_TRADE_JOURNAL.csv records the layer states in `matched_rules` as tokens, e.g. `BIAS=LONG;MOM=+;MULT=1.0;SESS=NY;TRIG=A;RR=1.8;ASIA=4105.2-4131.0;SPREAD=0.28;NEWS=clear`, so that every ablation in §11 can be recomputed from the journal afterwards. WAIT rows record which gate failed.
2. Trigger B setups are **logged as WAIT (TRIG_B_OFF)** with their would-be entry/stop/target, so V2-C can be scored without trading it.
3. Minimum sample before any conclusion: 60 decided setups and 40 filled trades (protocol), but §8.6 means three months of paper trading **cannot** establish the edge; it establishes execution quality, spread reality, and rule adherence. Say so in every monthly review.
4. Weekly: record L7 inputs. Monthly: compute mean R, PF, max DD, by trigger, by session, by bias state, and compare with v1.0's out-of-sample distribution.
5. No rule changes during the observation period. Proposals go to PROJECT_STATE.md.

## 13. Recommended next step before or alongside the paper trade

The engine (backtest/engine.py) already implements L0 (partly), L3-A, L4, L5.1, L5.5–5.7 and the cost model. Adding L1 (SMA200 / 12-1 momentum from the D1 resample), gate 0.3 (approximate calendar), the 0.5 % drawdown-scaled sizing in R terms, the partial-exit + Chandelier trail, the daily/weekly stops and Trigger B is a bounded change, and all §11 variants can then be run in minutes on the same data with the same validator. That costs nothing and prevents three months of paper trading a dead configuration. The contamination caveat in §11 still applies, so the backtest cannot "pass" v2.0; it can only **reject** layers that clearly hurt.

## 14. Chart-submission additions for a v2.0 read

In addition to CHART_SUBMISSION_TEMPLATE.md: previous D1 close, SMA200 value, close 21 and 252 trading days ago (or state the 12-1 return sign), Asian range high/low (23:00–07:00 UTC), prior-day high/low, D1 ATR(14), live spread, this week's release times. Pixel reads remain approximate (chart_audit/).

## 15. Version control

- v1.0 stays frozen and remains the baseline.
- v2.0 CANDIDATE is frozen as written here on 2026-11-09 for the purpose of the §11 tests. Changes become v2.1 only after a logged evaluation.
- Evidence tags in this file were assigned from search snippets for most sources (hosts were unreachable from the sandbox); re-read any primary source before quoting it to a third party.
