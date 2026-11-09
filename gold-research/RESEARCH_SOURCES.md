# RESEARCH_SOURCES — gold trading methods: candidates, evidence labels, citations

Prepared 2026-11-09 for Aayan's XAUUSD intraday research project. All access dates are 2026-11-09.

## How to read the verification tags

| Tag | Meaning |
|---|---|
| **READ IN FULL** | We opened the actual document in this session and quote it directly. |
| **SNIPPET** | Only search-engine excerpts of the cited page were readable in this session (the container's network allowlist blocked the host). The URL is the page the excerpt came from; it should be re-read before being relied on. |
| **UNVERIFIED** | Claim appears in secondary sources only, or could not be checked at all. |
| Evidence labels | *independently substantiated* / *self-reported* / *no usable performance record found*. Follower counts, testimonials and selected screenshots are not evidence. |

Honesty note: because most research hosts were unreachable from the sandbox, four of the six candidate write-ups rest largely on snippets. The selected strategy (Candidate 3, Holy Grail) is the one whose primary rule text we **did** read in full.

## Category separation

| Category | Candidates here | Transferable to intraday XAUUSD CFD? |
|---|---|---|
| Long-term gold investing | none selected (out of scope for intraday; e.g. strategic allocations) | No. |
| Discretionary macro / position trading in gold futures | Turtle system (gold was one of ~20 markets) | Only with large adaptation (daily bars → intraday). |
| Short-term futures pattern trading (all markets, incl. gold) | Crabel ORB, Raschke Holy Grail / Turtle Soup, Fisher ACD | Patterns are generic; none has published gold-specific, cost-inclusive results. |
| Intraday XAUUSD retail methods | ICT | Time windows and the 3-candle gap are mechanical; the rest is discretionary; no performance record. |
| Academic / quantitative intraday gold evidence | PM-fix drift, session seasonality, intraday momentum, ORB study | Testable hypotheses, mostly pre-2015 or non-COMEX data. |

---

## Candidate 1 — The Original Turtle Trading Rules (Richard Dennis / William Eckhardt; published by Curtis Faith)

1. **Market / holding period:** ~20 liquid US futures including COMEX gold; daily bars; holds of weeks to months.
2. **Sources:** "The Original Turtle Trading Rules", OriginalTurtles.org, © 2003, foreword by Curtis Faith — **READ IN FULL** by our research agent from a copy of the PDF in a public GitHub repository (https://github.com/Js-uu/trading, file `turtle-rules.pdf`). Curtis Faith, *Way of the Turtle*, McGraw-Hill, 2007 — **not accessed**. S. Angrist, "Winning Commodity Traders May Be Made, Not Born", *Wall Street Journal*, 5 Sep 1989 — **SNIPPET** (scan at https://www.turtletrader.com/images/wsj_turtle_article.pdf).
3. **Performance evidence:** the PDF states "over the next four years, we earned an average annual compound rate of return of 80%" (program 1984–1988). The 1989 WSJ table is credited to Barclay Trading Group data (a tracker, not an audit); individual Turtle figures circulate on promoter sites. Costs: live accounts, so net of commissions by construction; nothing else specified. Later evidence: Chesapeake Capital (Jerry Parker) is an audited CTA since 1988 but trades its own system, not the literal rules (AutumnGold/IASG listings, **SNIPPET**).
4. **Evidence label: self-reported.** No independent audit of the 1984–88 results was found.
5. **Reproducible rules (exact):** N = 20-day Wilder average of True Range ("N = (19 × PDN + TR) / 20"); unit = 1 % of equity / (N × dollars per point); System 1 entry on a 1-tick break of the 20-day high/low, skipped if the last breakout was a winner (then use the 55-day "Failsafe" breakout); System 2 entry on a 55-day breakout, always taken; add units every ½ N up to 4; stops 2 N from entry (raised ½ N per add); exits at 10-day (S1) / 20-day (S2) opposite extremes, intraday as the level trades; market list includes "Comex: Gold, Silver, Copper". **Missing:** capital split between systems, slippage/commission assumptions, rollover handling.
6. **Suitability:** fully specified and gold-relevant, but a daily-bar, multi-market, low-win-rate trend follower; on one instrument intraday it loses the diversification that made it work, and multi-week CFD holds incur swap. Kept as an alternative (not selected).

## Candidate 2 — Toby Crabel, *Day Trading with Short Term Price Patterns and Opening Range Breakout* (Traders Press, 1990)

1. **Market / holding period:** US futures (S&P, bonds, currencies, gold, crude, beans appear in table headers); day trades from the pit open to the close.
2. **Sources:** the book — **not accessible** (out of print; only unofficial scans, which we did not use as a source). Crabel's precursor articles in *Technical Analysis of Stocks & Commodities* (1988–89), e.g. V.6:9 "Playing the opening range breakout" (https://store.traders.com/-v06-c09-playing-pdf.html) — **SNIPPET** of abstracts only.
3. **Performance evidence:** the book's own pattern statistics (percent of days closing in the breakout direction, gross dollars) on 1978–1987 data, explicitly gross of costs ("when commission and slippage is added profits are reduced dramatically" — **SNIPPET** of an OCR excerpt, wording UNVERIFIED) and without stops. Crabel Capital Management's multi-billion-dollar CTA business (SEC filings cited in agent report, **SNIPPET**) runs different systems and does not validate the book's patterns.
4. **Evidence label: self-reported** (book); the firm's record is independently reported but for other strategies.
5. **Reproducible rules:** ORB = trade on a stop a predetermined amount off the open; "Stretch" = 10-day average of min(High − Open, Open − Low); buy stop at Open + Stretch, sell stop at Open − Stretch; filters NR4, NR7, Inside Day, ID/NR4. **Missing:** exit rule per table, stop, sizing, which "open" for a 24-hour market.
6. **Suitability:** needs an arbitrary session anchor for a 24-hour CFD; very sensitive to spread because the Stretch is small; a 2026 pre-registered futures ORB study (Candidate 6d) reports no cell surviving costs. Not selected.

## Candidate 3 — Linda Bradford Raschke (with Laurence Connors), *Street Smarts* (1995/96) — "Holy Grail" and "Turtle Soup"  ← SELECTED (Holy Grail)

1. **Market / holding period:** generic price patterns presented for any market and timeframe; the 1997 interview examples are daily stock charts; Raschke is a futures and options trader (floor trader from 1981; CTA from 1992; CPO from 2002).
2. **Sources:**
   - Interview by David Vomund, *AIQ Opening Bell Monthly*, Vol. 6 Issue 8, **August 1997**, containing the box "Holy Grail Pattern — Buy rules (sells are reversed)". **READ IN FULL**: https://lindaraschke.net/wp-content/uploads/2026/01/august1997.pdf (hosted on Raschke's own site).
   - Connors & Raschke, *Street Smarts: High Probability Short-Term Trading Strategies*, M. Gordon Publishing, 1995 (Wikipedia gives 1996). **Not accessible** in this session.
   - Wikipedia, "Linda Bradford Raschke" — **READ IN FULL** (https://en.wikipedia.org/wiki/Linda_Bradford_Raschke) for biography only.
   - Turtle Soup rule write-ups: StockCharts (J. de Kempenaer, June 2018) and Traders.com — **SNIPPET** (the StockCharts URL returned 404 when we tried it; the article may have moved).
3. **Performance evidence:** New Market Wizards profile (Schwager, 1992) — an interview, not an audit. Wikipedia (READ IN FULL) states her Granat Fund was "ranking 17th out of approximately 4,500 hedge funds for five-year performance by BarclayHedge in the late 2000s" and that she "retired from institutional roles as a CTA and CPO in 2015"; we found **no primary BarclayHedge table, year, return figures or fee basis** for that ranking. *Street Smarts* reportedly contains Moore Research Center back-tests described by the authors as showing "a market's tendency", not mechanical systems — **SNIPPET**; whether gold was included is **UNVERIFIED**.
4. **Evidence label: self-reported.** Reputation rests on interviews and an unlocated ranking; no independently audited, cost-inclusive return series was found.
5. **Reproducible rules — Holy Grail, quoted verbatim from the 1997 AIQ box (READ IN FULL):**
   > 1. The 14-period ADX must initially be greater than 30 and rising. This is the value to the right of TradingExperts ADX/R indicator.
   > 2. Look for a retracement in price to the 20 period exponential moving average. This will usually be accompanied by a turndown in the ADX.
   > 3. When the price touches the 20 period moving average, put a buy stop above the high of the previous bar.
   > 4. Once filled, enter a protective sell stop at the newly formed swing low. Trail stops as profits grow.

   Rationale, same interview: "This pattern takes advantage of the fact that the odds are very high that when a security makes a new momentum high and pulls back, it will retest its recent high."
   **Missing from the source:** trend-direction test, how a "touch" is defined, how long the buy stop stays valid, the trailing method, a target other than the implied retest, timeframe, costs, sizing. Each gap is filled by a tagged PROPOSED ADAPTATION in GOLD_PLAYBOOK_v1.md.
   **Turtle Soup (SNIPPET-level reconstruction):** new 20-day low today; the prior 20-day low at least four sessions earlier; buy stop 5–10 ticks above the prior low, valid today only; stop one tick under today's low. Not selected (24-hour market makes "today's low" ambiguous; rules only secondhand).
6. **Suitability:** chosen because (a) the rule text is primary-sourced and short, (b) it needs only OHLC data, (c) it is explicitly generic across markets/timeframes, (d) it is simple to encode. Limitations: no gold-specific or cost-inclusive evidence; ADX > 30 regimes are a minority of intraday bars (29 % of M15 bars in our data); the intraday timeframe is our choice, not hers.

## Candidate 4 — Mark B. Fisher, *The Logical Trader* (Wiley, 2002) — ACD method

1. **Market / holding period:** NYMEX/COMEX futures and stocks; intraday A/C trades to multi-day pivot-range bias.
2. **Sources:** the book (ISBN 9780471215516) — **not accessible**; Google Books / Wiley listings and secondary summaries (NexusFi, LuxAlgo, SMB) — **SNIPPET**.
3. **Performance evidence:** none for ACD. Fisher's business was a clearing firm (MBF Clearing Corp). CFTC release 6437-12 (2012 consent order, USD 650,000 civil penalty over customer-fund segregation; no customer losses alleged) — **SNIPPET** (cftc.gov returned 403 to us).
4. **Evidence label: no usable performance record found.**
5. **Reproducible rules (SNIPPET):** opening range of 5–30 minutes; A-up/A-down = OR ± a market-specific "A value" (appendix values not public for gold); time confirmation ≈ half the OR duration; C levels for failed-A reversals; pivot range = (H+L+C)/3 ± |pivot − (H+L)/2|; a rolling "number line" score. **Missing:** gold A/C values, scoring grid, stops, sizing; author states it is not mechanical.
6. **Suitability:** structurally fits a session-anchored gold open but every parameter would be ours. Not selected.

## Candidate 5 — ICT (Michael J. Huddleston)

1. **Market / holding period:** FX, indices, gold; intraday.
2. **Sources:** no written primary text located; the method exists as videos (2016–17 paid lectures; free 2022 YouTube mentorship ending with Episode 41, 2022-06-24; 2023 "Silver Bullet" series). Third-party transcripts (e.g. sozai.app episode transcripts) — **SNIPPET**. Official channels: https://x.com/I_Am_The_ICT, YouTube "The Inner Circle Trader".
3. **Performance evidence:** none verified. A 2016 public "$10k to $1M" demo challenge was not completed (forum reports, **UNVERIFIED**); 2024 Robbins World Cup participation was announced on his X account (2024-01-29 post) and no placing is recorded (**UNVERIFIED**). We could not confirm the "2023 failed live challenge" mentioned in the brief; the documented episodes are 2016 and 2024. Reports of a regulatory investigation are unsupported and are not repeated.
4. **Evidence label: no usable performance record found.**
5. **Testable elements:** kill-zone time windows (London 02:00–05:00 New York time; New York morning windows vary by source), Silver Bullet hours (03:00–04:00, 10:00–11:00, 14:00–15:00 NY), the 3-candle fair value gap ("the upper end of the fair value gap is the low of candle number one, and the lower end is the high of candle number three" — third-party transcript, **SNIPPET**), a sweep of a prior session high/low. **Discretionary:** daily bias, which swing defines a market-structure shift, which liquidity pool is "the draw", order-block validity.
6. **Suitability:** supplies crisp time windows and one mechanical pattern, but no complete rule set and no record. Not selected; the fixed UTC session windows in v1.0 are a project choice, not an ICT rule.

## Candidate 6 — Academic and quantitative evidence on gold's intraday behaviour (all SNIPPET-level: publisher hosts were blocked)

| Paper | Data | Finding | Costs | Testable implication | Caveat |
|---|---|---|---|---|---|
| Caminschi & Heaney (2014), "Fixing a Leaky Fixing", *J. Futures Markets* 34(11) 1003–1039, DOI 10.1002/fut.21636 | COMEX GC futures and GLD, minute data, c. 2007–2012 | Direction of the first minutes of the 15:00 London PM fix predicts the fix outcome, "in some cases exceeding 90 %"; "significant return advantages in the 4 minutes following the start of the fixing" | abstract claims economic returns; details unseen | trade the first-minutes direction at 15:00 London for a few minutes | pre-2015 fixing regime (replaced by the LBMA/ICE auction in March 2015); likely conduct-related; must be re-tested post-2015 |
| Speck (2013), *The Gold Cartel*, Palgrave, chs. 4 and 7 | intraday averages 1986–2012 (book) | gold tended to fall into the London PM fix time; rise in Asian hours | none | long Asia / short London–NY hours | practitioner, not peer-reviewed; manipulation interpretation is the author's |
| Donati & Jung (2019), MSc thesis, Copenhagen Business School, "Gold Price Dynamics Around the Clock" | GC futures | appreciation in eastern hours, depreciation otherwise; Sharpe up to 1.61 before costs, "still show some profitability" after costs | partly | session seasonality | student thesis |
| Hauptfleisch, Putniņš & Lucey (2016), *JFM* 36(6) 564–586 | 17 years intraday | price discovery mostly in New York futures | n/a | none directional | not a return anomaly |
| Gao, Han, Li & Zhou (2018), *JFE* 129(2) 394–414 | SPY 1993–2013 | first half-hour return predicts last half-hour | survives fees per paper | intraday momentum | equities; later checks suggest decay |
| Xu, Bouri, Saeed & Wen (2020), *Resources Policy* 69, 101830 | commodity ETFs incl. GLD | predictability exists; for gold the predictive half-hour is "not necessarily the first" | unseen | ETF-hours only | pattern unstable |
| Ma, Bouri, Xu & Zhou (2025), *Global Finance Journal* 64, 101084 | SHFE gold/silver futures (China) | predictor half-hour changed after night trading began | unseen | China only | not COMEX/spot |
| Fetna (2026), SSRN 7428398, "Opening-Range Breakout Does Not Survive Trading Costs" (working paper) | nine US futures, 1-min, 2010–2026, 225 pre-registered cells | "Zero of 225 cells meet the pre-registered positive bar"; grid gross +USD 1.57M vs −USD 6.49M at USD 25 round trip | yes | negative prior for ORB | not peer-reviewed; gold cell unseen |

**Evidence label for the category:** independently documented hypotheses, none validated for XAUUSD CFD after costs in the post-2015 regime. No peer-reviewed gold ORB test or COMEX intraday-momentum test was found.

---

## Finalist comparison and selection

| Criterion | Holy Grail (Raschke) | Turtle System (Dennis/Faith) | Crabel ORB |
|---|---|---|---|
| Rule clarity | 4 short rules, primary text read in full; gaps are explicit | fully specified, primary text read | partially recoverable, exits/stops unspecified |
| Data needed | OHLC only | daily OHLC | OHLC + a defined "open" |
| Gold relevance | generic pattern; no gold evidence | gold confirmed in portfolio | gold in table headers (unseen) |
| Intraday fit | explicitly timeframe-agnostic | daily-bar system | needs a session anchor; cost-sensitive |
| Simplicity to encode | high | medium | medium |
| **Decision** | **selected for v1.0** | alternative | alternative |

Selection was made on these criteria **before** any backtest was run (see PROJECT_STATE.md timeline). Alternatives are kept separate; no rules were merged.

## Execution facts gathered for the cost model (all SNIPPET-level, re-verify in MT5)

| Broker (page) | Contract | Spread (USD/oz) | Commission | Hours / server time |
|---|---|---|---|---|
| Pepperstone (pepperstone.com/en/markets/commodities/spreads; /en/ways-to-trade/pricing) | 100 oz (3rd-party) | Razor min 0.08 / avg 0.12; Standard min 0.20 / avg 0.25 | Razor USD 3.50 per lot per side | server GMT+2, GMT+3 in US DST |
| IC Markets (cdn.icmarkets.com Commodity-Specification-Sheet.pdf; help centre) | 100 oz | unverified | metals commission by account type | XAUUSD 01:02–23:57 server; triple swap Wednesday |
| FTMO (ftmo.com trading updates 25 Sep 2025, 2 Feb 2026) | 100 oz (3rd-party) | unverified | metals 0.0007 % of notional per side (≈ USD 2.80/side per lot at USD 4,000/oz) | MT5 GMT+2 + DST |
| Exness (get.exness.help article 17854173039388) | 100 oz, min 0.01 lot | unverified (3rd-party ≈ 0.16 standard) | Raw 3.5 / Zero 5.5 USD per lot | server GMT+0; higher margin around the daily break and news |

Other anchors: LBMA Gold Price auctions 10:30 and 15:00 London (lbma.org.uk); COMEX GC settlement window 13:29–13:30 ET (CME); BLS releases (NFP, CPI) 08:30 ET (bls.gov schedules); FOMC statement 14:00 ET, press conference 14:30 ET. DST misalignment weeks (London vs New York): 2025: 9–30 Mar and 26 Oct–2 Nov; 2026: 8–29 Mar and 25 Oct–1 Nov (timeanddate.com / TSX notices, **SNIPPET**).

Prop-firm rule types seen (FTMO, The5ers, FundedNext official pages, **SNIPPET**): daily loss limits defined on balance or equity with a firm-specific reset time (e.g. midnight Prague for FTMO); maximum loss static or end-of-day trailing; news restrictions such as no executions within 2 minutes of listed releases on funded accounts; weekend-holding and minimum-trading-day rules; consistency rules on some one-step products. These change often and must be verified for Aayan's exact firm and account type before any compliance statement.

## Data source

HistData.com FAQ (**READ IN FULL**, https://www.histdata.com/f-a-q/): "The timezone of all data is: Eastern Standard Time (EST) time-zone WITHOUT Day Light Savings adjustments"; bar prices "are based on the tick Bid price"; volume removed because forex volume "is not aggregated". Dataset details in data/DATA_AUDIT.md.

## Full source list (URLs as cited above; access date 2026-11-09)

- https://lindaraschke.net/wp-content/uploads/2026/01/august1997.pdf (READ IN FULL)
- https://en.wikipedia.org/wiki/Linda_Bradford_Raschke (READ IN FULL)
- https://github.com/Js-uu/trading — turtle-rules.pdf (READ IN FULL by agent)
- https://www.histdata.com/f-a-q/ (READ IN FULL)
- https://www.turtletrader.com/images/wsj_turtle_article.pdf (SNIPPET)
- https://store.traders.com/-v06-c09-playing-pdf.html (SNIPPET)
- https://books.google.com/books/about/The_Logical_Trader.html?id=4xFo6Pnb6JsC (SNIPPET)
- https://www.cftc.gov/PressRoom/PressReleases/6437-12 (SNIPPET; 403 to us)
- https://x.com/I_Am_The_ICT/status/1752023744241930570 (SNIPPET)
- https://onlinelibrary.wiley.com/doi/abs/10.1002/fut.21636 (SNIPPET)
- https://link.springer.com/chapter/10.1057/9781137286437_7 (SNIPPET)
- https://research.cbs.dk/en/studentProjects/gold-price-dynamics-around-the-clock/ (SNIPPET)
- https://www.sciencedirect.com/science/article/abs/pii/S0304405X18301351 (SNIPPET)
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7428398 (SNIPPET)
- https://pepperstone.com/en/markets/commodities/spreads (SNIPPET); https://pepperstone.com/en/ways-to-trade/pricing/ (SNIPPET)
- https://cdn.icmarkets.com/uploads/Commodity-Specification-Sheet.pdf (SNIPPET)
- https://ftmo.com/en/blog/trading-updates/trading-update-25-sep-2025/ (SNIPPET); https://ftmo.com/en/trading-objectives/ (SNIPPET); https://ftmo.com/en/faq/can-i-trade-news/ (SNIPPET)
- https://get.exness.help/hc/en-us/articles/17854173039388-Commodities (SNIPPET)
- https://www.bls.gov/schedule/news_release/empsit.htm ; https://www.bls.gov/schedule/news_release/cpi.htm ; https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm (official schedules; not fetched in this session)
- https://www.lbma.org.uk/prices-and-data/lbma-gold-price/lbma-gold-price (SNIPPET)
- https://www.timeanddate.com/time/change/usa/new-york?year=2025 (SNIPPET)
