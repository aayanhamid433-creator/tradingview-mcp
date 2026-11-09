# RESEARCH_SOURCES v2 ADDENDUM — gold traders, quantitative evidence, intraday methods, risk rules

Prepared 2026-11-09 for GOLD_PLAYBOOK_v2_CANDIDATE.md. Extends RESEARCH_SOURCES.md (same tags: READ IN FULL / SNIPPET / UNVERIFIED; evidence labels *independently substantiated* / *self-reported* / *no usable performance record found*). Full agent notes with every URL are in research_notes/2026-11-09_{macro,quant,intraday,risk}.md.

**Access disclosure:** from the sandbox only Wikipedia, GitHub and a few forums could be fetched in full. Everything else below rests on search-result snippets of the named page and must be re-read before being quoted to a third party.

## A. Documented traders and what transfers

| Trader | Gold vehicle / horizon | Reproducible rule(s) | Gold performance evidence | Used in v2.0 as |
|---|---|---|---|---|
| Paul Tudor Jones | Futures; 1–2 year themes (2019 "favorite trade", 2020 inflation letter) | 200-day MA of closes as the filter for "everything"; ~5:1 reward/risk screen; "don't ever average losers"; cut size when trading poorly (*Market Wizards* 1989; Robbins 2014; all reprint SNIPPET) | Fund audited in aggregate; **gold-specific: none** | L1 trend state (SMA200); L5.7; L6.3 |
| Stanley Druckenmiller | GLD, Barrick, GDX; quarters to 2 years (13F) | None numeric; gold "trades off interest rates"; concentration when convinced | ~30 %/yr record *self-reported*; 13F timing (2015 buy, Nov-2016 sell, 2020 hold) regulated | L7 real-yield/DXY context only |
| George Soros | GLD, calls, Barrick; quarters | None ("ultimate bubble" = may go higher) | 13F timing; sold ~6 months before the 2011 top | L7 context only |
| John Paulson | Miners/GLD; years | Thesis only, no invalidation | *Self-reported* via press: 2013 ≈ −71 % | negative example (§10) |
| Ray Dalio | 5–15 % allocation | None for timing | none (allocation) | not used |
| Peter Brandt | GC/GLD; days–months; classical patterns | ≤ 1 % risk per trade (own thread); stop just beyond the breakout bar extreme ("Last Day Rule"); pattern-height target; anti-"popcorn" partial exits (*Diary*, 2011) | 41.6 %/yr claim *self-reported*, attestation disputed; no gold sub-record | L4 stop construction; L5.3 partial; L6.1 risk |
| Larry Williams | Futures swing, 2–5 days | COT index = (commercial net − 3-yr min)/(range) × 100, bullish > 75 / bearish < 25 (thresholds vary); %R timing; seasonals | 1987 contest account *independently substantiated* (+11,376 %); NFA record shows client losses the same quarter; gold P&L none | L7 COT index, logged |
| Rogers, Schiff | Physical, permanent long | None | None | not used |

## B. Quantitative evidence by layer

| Layer in v2.0 | Source (SNIPPET unless noted) | Finding | Label / caveat |
|---|---|---|---|
| L1 momentum vote | Moskowitz, Ooi & Pedersen 2012 *JFE*; Hurst, Ooi & Pedersen 2017 *JPM* | 12-month sign, 1-month hold, vol-scaled; portfolio Sharpe ≈ 0.8–1.0, positive every decade 1880–2013, net of costs/fees | *independently substantiated* at portfolio level; gold-only Sharpe never published; commodities weak 2010–2020 (Clare et al. 2014 replication Sharpe −0.13) |
| L1 trend state | Faber 2007 (10-month SMA); SentimenTrader conditional returns; Szakmary et al. 2010 *JBF* | 10-month SMA cuts drawdown; weakest on commodities; gold ≈ 12 %/yr above vs ≈ 2 % below 200-day since 1975 | descriptive, no costs; golden-cross tests exist only for equities |
| L7 real price / yields | Erb & Harvey 2013 *FAJ*; Chicago Fed Letter 464 (2021); WGC GRAM | real gold price mean-reverts over decades; real-yield elasticity contemporaneous and weaker since 2022 | no daily/weekly predictive power shown |
| L7 seasonality | Baur 2013 *RIBAF*; Potrykus & Augustynowicz 2024 | Sept/Nov effect 1980–2010; **reversed** 2010–2022 | logged only |
| L7 COT | Sanders, Irwin & Merrin 2009; Wang 2003; Mutafoglu, Tokat & Tokat 2012 *Resources Policy* (gold) | positions follow returns; only extremes weakly predictive | logged only; candidate v2.1 extreme filter |
| L0 news gate | Elder, Miao & Ramchander 2012 *JBF*; Cai, Cheung & Wong 2001 *JFM*; Smales & Yang 2015 *IRFA*; Awartani, Hussain & Virk 2024 *IRFA* | 08:30 ET releases largest; reaction mostly within 90 s; wider spreads around releases; post-FOMC adjustment lasts beyond 5 min, stronger for easing surprises | avoidance window justified; drift magnitude unquantified |
| L0 fix times | Crain & Hoelscher (Missouri State WP) | no return difference around the fix after the 2015 auction reform | PM-fix drift not assumed |
| L2 session structure | Batten et al. 2017; Hauptfleisch, Putniņš & Lucey 2016 *JFM*; Yu, Lee & Shih 2016 | strong intraday periodicity; NY futures lead price discovery; London highest mean return to 2011 | volatility/liquidity facts, not drift |
| L2 own data | results/DATA_FACTS.md (computed) | 13:00–16:59 UTC M15 ranges 1.2–1.75× day median; Asia session drift +5.2 bps/day (t 3.3) 2021–26; weekend |gap| median 1.5 USD, 90th pct 15.7 (36 in 2025–26); M15 ATR14 median 7.05 USD 2025–26 | descriptive; uptrend sample |
| Trigger B | mql5 blog 777728 (288 variants, gold 2008–2026, costs, in/out-of-sample); mql5 777540 (3.7 yrs, PF 1.37); Backtrex EUR/USD H1 (−28 %) | careful OOS test: 14/288 profitable both halves ≈ chance; apparent gains = long beta | *self-reported*; OFF by default |
| Excluded: order blocks | TradingView OB statistics script (1,854 zones, placebo-controlled); Backtrex GBP/USD OB (PF 0.83) | no difference from random levels | *self-reported*, consistent negative |
| Excluded: scalping | github Sandyyy123 (gross), TradingView Gold Spread Algo (47k trades, ≈ 0.02 USD/trade before commissions) | positive gross, ≈ zero/negative net | arithmetic against sub-2 USD targets |
| Excluded: VWAP | Shannon AVWAP summaries; mql5 session-anchored VWAP | rules exist; no cost-inclusive gold test; no true volume on CFD | reference line at most |

## C. Risk rules with their provenance

| Rule | Formula / statement | Source status |
|---|---|---|
| Percent risk (Tharp) | size = equity × risk % ÷ |entry − stop| ; results in R multiples; expectancy = mean R | book summaries SNIPPET; ≤ 1 % "widely attributed" |
| Turtle N | unit = 1 % equity ÷ (N × $/pt), N = 20-day ATR; stop 2N; −10 % DD → trade as if 20 % smaller | Faith 2003 via SNIPPET; Wikipedia Dennis page READ IN FULL confirms size cuts in losing periods |
| Kovner | "Undertrade, undertrade, undertrade … cut it at least in half"; novices should risk 1–2 % | *Market Wizards* reprint SNIPPET |
| Seykota | "Cut losses. Ride winners. Keep bets small." | reprint SNIPPET |
| Kelly / half-Kelly | f* = p − q/b; half-Kelly keeps ≈ 75 % of growth; 2× Kelly → zero growth | Wikipedia READ IN FULL; MacLean-Thorp-Ziemba SNIPPET |
| Optimal f | f maximising Π(1 + f·t_i/L); full f drawdowns > 50 %; "half f" | Vince via SNIPPET |
| Chandelier exit | highest high since entry − 3 × ATR(22) | LeBeau via SNIPPET; no published exit comparison found |
| Prop limits | FTMO 5 % daily / 10 % max; The5ers 5/10; FundedNext 5/10 and 3 % open risk; 2-min news rule on FTMO funded Standard accounts | third-party SNIPPET; verify on official pages |
| Sample size | n = (z·σ/μ)²; σ 1.2 R, μ 0.1 R → 237 (90 % one-sided) / 390 / 553 trades | Wikipedia READ IN FULL (formula) |
| Loss streaks | P(≥ k consecutive losses in n) by recursion; win 40 %, k 8, n 200 → 0.75 | arithmetic |
| Leverage caps | ESMA and ASIC 20:1 on gold (5 % margin); US retail CFDs not offered | SNIPPET (regulators' pages unreachable) |

## D. Execution facts (all SNIPPET; verify in MT5)

- FOREX.com Gold Spot/USD: 1 lot = 10 oz, min 1 lot, margin from 5 % (UK/IE/AU; 22 % shown on the Canada page), rollover after 5 pm ET, spread "from 0.10", measured average ≈ 0.30; separate 7-day gold CFD trades weekends.
- Session spreads (third-party MT5 logs): Asia ≈ 30–50 % wider than London/NY; overlap 13:00–16:00 UTC tightest; rollover 21:00/22:00 UTC spreads 1.2–2.8 USD for 5–20 min; NFP/CPI 1–5 USD for 30–90 s.
- "Pip" on gold means 0.01 USD at some brokers and 0.10 at others; always convert to USD/oz.

## E. Base rates worth remembering

- FTMO: XAUUSD is its most traded symbol; third-party estimates put challenge pass rates near 14 % and ever-paid near 7 %. Popularity is not evidence of edge.
- "Verified" Myfxbook/MQL5 gold systems: verification covers history integrity, not strategy quality; typical max drawdowns 30–60 %, frequent grid/martingale structure, survivorship bias.
