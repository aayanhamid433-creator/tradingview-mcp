# ALT candidate report — "Gold Breakout 15M Strategy [WillyAlgoTrader]" re-implemented and tested

Date: 2026-11-16 (revised the same day after the clock correction). Status: **alternative candidate, descriptive only; not pre-registered, not adopted.** Aayan found this script on TradingView and asked what it does. The rules were read from the author's published source, re-implemented in our simulator, and run on the 2021–2026 research data with the project's cost model and periods. Because the candidate was chosen after seeing its advertised result, every number here is descriptive, not confirmatory.

Written by the original research session (branch `claude/quirky-lovelace-y41dkc`, now merged and deleted). It was produced without sight of the fork's later work (v2–v8) until the end; §6 places it against that work. The project's live state is PROJECT_STATE.md on the fork's `claude/v22-variants` branch, not the copy next to this file.

Plain English: overnight (midnight to 07:00 on the broker's clock) gold usually sits in a narrow band. At 07:00 the strategy puts a buy order at the top of that band and a sell order at the bottom. Whichever side breaks first becomes the day's trade, with a stop 1 % away, no profit target, and a forced close at 20:00. One trade a day, every day.

## 1. Provenance (READ IN FULL)

| Item | Value |
|---|---|
| Script | "Gold Breakout 15M Strategy [WillyAlgoTrader]", TradingView script id HnelYN0A, published 2026-10-12, **open-source** Pine v6 |
| Page | https://www.tradingview.com/script/HnelYN0A-Gold-Breakout-15M-Strategy-WillyAlgoTrader/ (read 2026-11-16) |
| Source | fetched from TradingView's public script endpoint and saved as `alt_gold_bo_15m_source_WillyAlgoTrader.pine` (66 KB, author's copyright; reference only) |
| Author's claimed result | OANDA XAUUSD 15-minute, 2011-01-01 → 2026-10-12, 10,000 USD start, 1 % risk, 1 % stop, commission 0.4 USD per order, **no slippage, no spread**: "approximately +800 %" compounded, "roughly 4,000 trades", "profit factor of about 1.27", "maximum drawdown of about 14 %" |
| Evidence label | **self-reported** (a TradingView tester run anyone can reproduce, but without spread and chosen by the author); no live record |
| Aayan's screenshot | same script on the FOREX.com feed, 2026-08-02 → 2026-11-16, 35,000 USD: +7,740 USD (+22.1 %), 44/70 winners (62.9 %), PF 2.06, max DD 3.38 % |

## 2. Rules as implemented by the author (exact, from source)

1. Broker clock: a fixed timezone (default GMT+3) all year, or "New York + 7h" (GMT+2 in winter, GMT+3 in summer, on the US daylight-saving calendar).
2. Range = highest high and lowest low of all 15-minute bars whose opening hour is ≥ 0 and < 7 (broker time). Reset every broker day. First day of history skipped.
3. From the close of the last range bar, while the next bar opens at ≥ 07:00 and < 20:00: buy stop at Range High and sell stop at Range Low, one-cancels-other, re-placed each bar until filled or the window ends. One trade per broker day (a trade that enters and exits inside one bar still counts).
4. Stop-loss, "% of entry" mode (default 1.0 %): placed from the breakout level (× 0.99 for a long, × 1.01 for a short); at the close of the entry bar re-set once from the actual fill price. Alternative mode: the opposite range boundary.
5. No take-profit. Exit at the stop or at the open of the first bar at or after 20:00 broker time.
6. Size: 1 % of equity at risk divided by the stop distance, capped at 10× leverage, rounded down to the contract step. Optional "prop firm guard" (off by default) closes everything when the estimated intraday drawdown from the day's equity peak reaches 4 %.
7. Author's own caveats, quoted from the page: "The test uses a fixed commission per order and no slippage. Spread is not modeled by the tester. Real trading costs are higher"; "If one candle touches both range boundaries, the tester decides which side was reached first."

On GMT+3 the range is 21:00–04:00 UTC and the trading window 04:00–17:00 UTC; 82 % of fills happen in the first three hours after the window opens (04:00–06:59 UTC).

## 3. Our re-implementation

- `backtest/engine_gbo.py` applies the rules to the HistData M1 bid data with M1 fills: stop entries fill at max(level, open) plus slippage, with ask = bid + spread; the stop is re-anchored to the fill at the first minute of the next 15-minute bar; time exit at the open of the first minute at or after 20:00 broker time (next available bar on early-close days, as the author's script does).
- **Clock correction applied.** The research dataset's index is HistData's stamp + 5 h, and the stamps follow New York local time, so that index is London local time, not UTC (PROJECT_STATE.md on the fork, correction of 2026-11-13; confirmed here by the daily break sitting at 21:58 on that clock in every month and shifting only in the UK/US misalignment weeks). The engine converts the index to true UTC by localising (index − 5 h) as America/New_York. After the correction the break is at 21:00 UTC in winter and 20:00 UTC in summer, where the 17:00 New York close belongs. A first run without the correction (one hour early in summer) gave slightly better numbers (all-years PF 1.21 vs 1.19); it is superseded and not kept.
- One-minute bars that cross both boundaries: 1 case in six years, so the author's "tester decides" ambiguity is immaterial here.
- Commission: the author's 0.4 USD per order is about 0.008 % of notional per round trip at his sizing; variant G0 uses that and no spread to reproduce his conditions. Other variants use the project cost model (base spread 0.25 + 0.05 slippage on stop fills; stress 0.50 + 0.15).
- Not implemented: the equity guard, leverage cap and step rounding (irrelevant when results are in R).

## 4. Results (R = 1 % of the breakout level; periods identical to v1.0 §13; clock-corrected)

| variant | development 2021-01 → 2024-06 | validation 2024-07 → 2025-08 | final test 2025-09 → 2026-10 | validation + test (held-out) | all 2021–2026 |
|---|---|---|---|---|---|
| G0 author-like costs | 891 trades, +0.032 R, PF 1.13, DD −9.8 R | 298, +0.084, PF 1.35 | 287, +0.144, PF 1.46 | 585, +0.113, CI [+0.055, +0.172], PF 1.41, DD −13.2 R | 1,476, +0.064, PF 1.25, DD −13.2 R |
| **G1 base costs** | 893, +0.014, PF 1.05, DD −18.5 R | 298, +0.077, CI [+0.011, +0.144], PF 1.32, DD −7.3 R | 287, +0.140, CI [+0.042, +0.241], PF 1.44, DD −13.1 R | 585, +0.108, CI [+0.049, +0.168], PF 1.39, ex-top-5 +0.077, DD −13.1 R, win 54 % | 1,478, +0.051, CI [+0.019, +0.084], PF 1.19, DD −18.5 R, longest losing streak 11 |
| G2 stress costs | 893, −0.005, PF 0.98, DD −37.5 R (first run; corrected run similar) | 298, +0.067 | 287, +0.133 | 585, +0.100, CI [+0.042, +0.159], PF 1.36 | 1,478, +0.035, PF 1.13 |
| G3 New York + 7h clock, base costs | 893, +0.022, PF 1.08 | 298, +0.072 | 287, +0.155 | 585, +0.113, CI [+0.052, +0.174], PF 1.41, DD −12.2 R | 1,478, +0.059, PF 1.22 |
| G4 stop = opposite range boundary | 894, −0.014, PF 0.98, win 42 % | 298, +0.140 | 287, +0.111 | — | 1,479, +0.044, PF 1.09, DD −58 R |
| G5 both-sides adverse convention | identical to G1 (1 such minute) | | | | |

Cross-checks: G0 gives PF 1.25 on 2021–2026 against the author's 1.27 on 2011–2026; in the screenshot window (2026-08-02 → 2026-10-30, where our data ends) G1 gives 62 trades, 62.9 % winners, PF 1.96 against the screenshot's 62.9 % and 2.06 to 2026-11-16. The transcription is faithful; the differences are feed, window end and spread.

G1 breakdowns, all years: 2021 +0.056 R, 2022 −0.016, 2023 −0.008, 2024 +0.052, 2025 +0.065, 2026 +0.189 (PF 1.61); longs +0.055 (796 trades), shorts +0.047 (682); 14.7 % of trades stop out at −1.01 R, the rest are time exits averaging +0.23 R; about 4.9 trades a week; median hold 11.2 hours; 50 % of trading days positive; worst day −1.96 R, best day +5.06 R; average planned risk in 2026 about 45 USD/oz (1 % of price). Compounding at 1 % risk per trade would have made about +104 % over 2021–2026 (roughly 13 % a year), not the +22 % per quarter in the screenshot, which was an unusually good stretch (2026 is the best year in the sample).

## 5. Reading the numbers honestly

- Against the v1.0 wording (applied after the fact): both held-out periods positive with PF above 1.10 and more than 60 trades; held-out interval excludes zero; still positive without the five best trades; stress costs stay positive. It would pass that wording. But that bar was written for a candidate chosen before any result; this one was chosen because its advertised result looked good, and its defaults were set by an author looking at 2011–2026, which overlaps our "held-out" years. **PROMISING, UNVALIDATED** is the right label.
- Against the stricter rule the fork adopted from v3 onward (max drawdown ≤ 10 R in every period including development, and per-trade R above v2.2): **fails** on the development drawdown (−18.5 R) and on per-trade R (v2.2 held-out +0.98 / +0.19 R per trade on far fewer trades).
- The edge is a small positive drift on trades held to the evening (+0.23 R average) against occasional −1 R stops; development is flat (+0.014 R). It is the same "breakout with stops on both sides, hold to the close" pattern that the fork's own research found to be the only intraday family with a held-out edge, and like that family it leans on the 2024–2026 trending regime.

## 6. Where it sits against the fork's own tested variants (VALIDATION_REPORT_v3, v5, v8)

| variant | rule in one line | development n / mean R / PF / DD | held-out n / mean R / PF / DD | trades per day |
|---|---|---|---|---|
| V3_ORB_L10 (rejected) | 07:00–08:00 London range, target 1.0×range, orders to 11:00 | 540 / +0.002 / 1.00 / −32 R | 330 / ≈ −0.01 / 0.98 / −17 R | 0.5 |
| HL_C_W01 (v5 best) | swing-10 high/low, EMA50 filter, orders 01:00–16:00 London, target 1.5 R, flat 20:50 | 1,017 / +0.006 / 1.01 / −27 R | 666 / +0.141 / 1.37 / −9 R | 1.09 |
| HL_C_W01_RH4 (v8, Pine default) | HL_C_W01 + 4-hour direction filter | ≈ 0.036 / 1.08 / −24.6 R | 431 / +0.188 / 1.50 / −6.3 R | 0.71 |
| **GBO G1 (this report)** | overnight 21:00–04:00 UTC range, OCO stops, 1 % stop, no target, flat 17:00 UTC | 893 / +0.014 / 1.05 / −18.5 R | 585 / +0.108 / 1.39 / −13.1 R | 0.97 |

Reading: the Willy script is a simpler cousin of HL_C_W01, with a wider fixed stop and no target, and it comes out slightly weaker per trade and with a larger held-out drawdown than the fork's best variant, while trading a little more often. It is **not** an improvement on what the fork already has; it is independent confirmation, from a third party's published rules and from Aayan's own TradingView run, that the overnight-range breakout held into the New York afternoon is where gold's intraday edge has been in 2024–2026. Its one genuinely different idea, the 1 % price stop instead of a structure stop, trades a lower win rate on stops for a larger average time-exit gain; G4 shows the structure stop (opposite range edge) is worse here.

## 7. Account notes (Atlas Funded 1-Step 50k, ACCOUNT_RULES.md on the fork)

- Risk per trade: the fork's account simulation set 0.15 % for the breakout family because the 2023 drawdown kills the account at 0.25 %. The same logic applies here: at 0.15 % (75 USD per R) the worst six-year drawdown (−18.5 R) is about −1,400 USD, inside the 6 % trailing floor (3,000 USD); at 0.5 % it would be −4,600 USD and a breach. With a 1 % stop at today's prices (≈ 45 USD/oz) 75 USD of risk is 0.017 lot, which rounds to 0.01 lot (≈ 45 USD risk, 0.09 %). So on this account the strategy trades the minimum lot.
- Daily limit 3 % at 00:00 UTC: the worst single day in six years was −1.96 R; no issue at this size.
- News ±5 min: stop entries can fill inside a release window (e.g. 12:30/13:30 UTC), which forfeits that trade's profit. A gate that cancels the pending orders ±5 min around red-folder events is required before any demo; the author's script has none.
- Holding window 04:00–17:00 UTC never crosses the 00:00 UTC reset or a weekend. Early-close days carry the position into the next session; the same leak the fork fixed in engine_v3 (`session_gap_exit`) should be applied if this engine is ever used for a decision.
- Consistency (best day ≤ 20 % of cycle profit): the best day in six years was +5.06 R against a typical month of about +3 R, so payout lag is possible after a runner day.

## 8. Recommendation

Do not adopt it in place of HL_C_W01_RH4. Record it as independent corroboration of that family and as a reference implementation whose author's and Aayan's own results we can reproduce. If Aayan wants a simpler rule set to run by hand, this one is executable from a chart with no indicators, at the cost of a weaker per-trade edge; it would still need the news gate, the broker-data run and the forward test before any money.

## 9. Files

- backtest/engine_gbo.py (clock-corrected), backtest/analyze_gbo.py
- results_alt_gold_bo/<variant>/{trades.csv, skips.csv, config.json}, results_alt_gold_bo/summary.md, summary.json
- alt_gold_bo_15m_source_WillyAlgoTrader.pine (author's source, reference only)
- Suggested PROJECT_STATE entry on the fork: "P17 — Gold Breakout 15M (WillyAlgoTrader) re-implemented; PROMISING, UNVALIDATED; weaker than HL_C_W01_RH4; independent corroboration of the overnight-range breakout family; not adopted."
