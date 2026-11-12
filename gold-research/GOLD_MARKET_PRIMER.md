# GOLD MARKET PRIMER — what you need to know to trade XAUUSD intraday, in plain words

Written 2026-11-12 for Aayan from the project's research (RESEARCH_SOURCES.md, RESEARCH_SOURCES_v2_ADDENDUM.md, research_notes/, results/DATA_FACTS.md) plus this week's trading. Where a number comes from our own six years of data it says so. Where it comes from a source read only as a search snippet it should be re-checked before being repeated to anyone else.

## 1. What XAUUSD actually is

- **Spot gold priced in US dollars per troy ounce.** Your broker's "XAUUSD" is a CFD (contract for difference): you never own metal, you hold a contract that tracks the spot price. 1.00 lot is 100 ounces at most brokers (FOREX.com's TradingView pages show 10-ounce lots on some regions, so check the symbol specification). At 4,000 USD, one lot is 400,000 USD of exposure and every 1 USD move is 100 USD.
- **The price is made elsewhere.** The real market is COMEX futures in New York and the London bullion market (OTC). Your CFD price is the broker's copy of those, with a spread added. Academic work finds New York futures lead price discovery most of the time.
- **Leverage.** Regulated brokers allow 1:20 on gold (5 % margin). That is why a 1-lot position on a 50,000 account used 40 % of your margin on Tuesday.

## 2. What moves gold (the big drivers)

In rough order of importance for a trader on a weeks-to-months view:

1. **Real interest rates.** Gold pays nothing. When the return on safe bonds *after inflation* rises, gold loses its appeal; when it falls, gold gains. This is the driver behind "hot CPI → Fed hike bets → gold falls", which is exactly what happened on 10 November. The relationship is well documented but it weakened in 2022–2025 (central-bank buying overrode it), so it is a bias, not a law.
2. **The US dollar.** Gold is priced in dollars, so a stronger dollar usually means a weaker gold price. Same caveat: contemporaneous, not predictive.
3. **Central-bank and ETF demand.** Central banks have been net buyers for years; ETF flows swing with retail and institutional sentiment. These show up as multi-month trends, not intraday moves.
4. **Fear.** Wars, bank failures, sanctions, political shocks push gold up fast. These are unscheduled, which is why a stop loss is the only protection.
5. **Positioning.** When speculators are very long (CFTC Commitments of Traders report), gold is vulnerable to sharp drops as they unwind. Evidence says positioning *follows* price more than it leads it; only extremes carry weak signal.

For an intraday trader the practical summary is: the daily trend already contains all of the above. That is why the system reads the 200-day average and does not try to forecast the Fed.

## 3. The daily rhythm (all times UTC; shift US times by one hour in summer)

| Time (UTC, winter) | What happens | What it means for you |
|---|---|---|
| 23:00 | Market reopens after the daily break (Sunday: week opens) | spreads wide for 10–20 min; weekend gaps median 1.5 USD, 90th percentile 16 USD, 36 USD in 2025–26 |
| 23:00–07:00 | Asia (Tokyo, Shanghai, Singapore) | quietest hours; spreads 30–50 % wider than London; our data shows a small positive drift (+5 bps/day) but it is not tradable after costs |
| 07:00–08:00 | London opens | volatility picks up; the system's window opens at 07:00 |
| 10:30 | LBMA morning auction (London "fix") | volatility marker, no directional edge since 2015 |
| 12:30–13:30 | New York arrives; **13:30 is US data time** (08:30 ET) | CPI, NFP, GDP, PCE, retail sales land here; 90 % of the reaction is inside 90 seconds; spreads 1–5 USD for a minute |
| 13:20 | COMEX pit open (08:20 ET) | volume jumps |
| 13:00–16:59 | London/New York overlap | **the best hours**: tightest spreads, biggest ranges (1.2–1.75× the day's median 15-minute range in our data) |
| 15:00 | LBMA afternoon auction | volatility marker |
| 15:45 | the system's last signal bar | nothing new after this |
| 19:00 | FOMC statement days (14:00 ET), press conference 19:30 | the biggest scheduled event; reaction continues beyond 5 minutes, stronger on dovish surprises |
| 18:30 | COMEX settlement window (13:30 ET) | — |
| 20:50 | the system is flat | — |
| 21:00/22:00 | daily break (17:00 ET) | spreads 1–3 USD, stops do not execute, swap charged; never hold unstopped through it |

## 4. The calendar you must know

Red-folder US releases, the ones that move gold most (times UTC in winter, one hour earlier in US summer):

| Release | When | Time |
|---|---|---|
| CPI (inflation) | monthly, around the 10th–15th | 13:30 |
| Nonfarm payrolls (jobs) | first Friday of the month | 13:30 |
| FOMC statement | 8 meetings a year (next: 9 Dec 2026) | 19:00, press conference 19:30 |
| PCE (the Fed's inflation measure) | end of month | 13:30 |
| GDP | end of month, three estimates per quarter | 13:30 |
| Retail sales, ISM, jobless claims | monthly / Thursdays | 13:30, 15:00 |

Check Forex Factory each morning. The account rules deduct profit on any trade opened or closed within 5 minutes of a red-folder event, so the script's blackout list must match the calendar.

## 5. How big moves are (from our data, HistData M1, 2021–2026)

| Measure | 2021–2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| Median daily range | 21–23 USD | 31 | 51 | 99 |
| Median 15-minute bar range | 1.6–1.9 | 2.4 | 4.5 | 8.3 |
| Annualised volatility | 13–15 % | 15 % | 19 % | 29 % |

Gold in 2026 moves four times as much in dollars as in 2023. Every stop, target and lot size must scale with ATR, never be a fixed number of dollars. A "normal" 2026 day is 100 USD; Tuesday's 100 USD drop was one ATR, not a crash.

After a day down 2 % or more that closes near its low, the next session took out the low 90 % of the time in our data, yet closed higher half the time. New low, then chop, is the base case after a big down day.

## 6. The regime right now (12 November 2026)

- Gold peaked at 5,414 on 28 January 2026 and is about 28 % lower.
- Price is roughly 500 USD below the 200-day average (≈ 4,450) and below the 50-day. The trend is down. The system allows shorts only.
- Catalyst this week: October CPI printed hot (0.4 % vs 0.3 %) and the market now prices a Fed hike in December. Rising rate expectations are the textbook gold negative.
- Silver fell too but bounced far harder (73 % of its drop recovered versus 25 % for gold before both rolled over again): a sign that metals bounces can be violent even inside a downtrend.

## 7. Who the "experts" are, and what to take from them

- **Trend followers** (Turtles, Hurst/Ooi/Pedersen, Faber): the only evidence that survives a century and costs. Take: trade with the 200-day, size by volatility, cut losses.
- **Raschke's Holy Grail**: ADX above 30, pullback to the 20 EMA, enter on the break. Our core trigger.
- **Tudor Jones, Kovner, Seykota, Brandt**: the risk rules. Never average a loser, 1 % or less per trade, cut size when losing, stop at pattern invalidation.
- **Druckenmiller, Soros, Dalio**: macro gold bets on real rates and the dollar. Not intraday; useful as context only.
- **Paulson**: lost 71 % in 2013 holding a thesis with no stop. The cautionary tale.
- **ICT, "smart money", order blocks, scalping bots**: no verified record; the one controlled test of order blocks found them equal to random levels.

## 8. What a good day looks like with this system

1. 06:30 UTC: read the calendar, note red-folder times, open MT5 and TradingView on 15m with the script.
2. 07:00: window opens. The monitor says the direction for the day and whether the trend is armed.
3. A touch bar appears in the trend direction: the banner turns orange with the exact order. Place it in MT5 with the stop and target it shows. Lot size from the monitor.
4. Filled: banner green. Do nothing until it says take half, move the stop, or you are out.
5. 15:45: no new orders. 16:00: pending orders cancelled. 20:50: flat.
6. Journal row logged (I do this), one line in your own words about how you felt.

Most days end at step 2 or 3 with no trade. That is the system working, not failing.

## 9. Glossary

- **Stop order (buy stop / sell stop)**: an order that triggers only if price reaches the level. "Sell stop 3,945" = sell automatically if price falls to 3,945.
- **Stop loss**: the price at which you accept the trade is wrong and exit. Always in the terminal, never in your head.
- **Take profit / target**: the price where you take money off the table. We take half there and trail the rest.
- **R**: your planned risk on one trade, in money. A +2 R trade made twice what you risked. Expectancy is average R per trade.
- **ADX**: trend strength, 0–100. Above 30 is strong. +DI/−DI tell you which side is pushing.
- **EMA20**: the average of the last 20 closes, weighted to recent ones. Where pullbacks tend to end in a trend.
- **ATR**: average bar range. The ruler for stops and sizes.
- **Spread**: the gap between buy and sell price; your cost on every trade. 0.25–0.40 USD normally, 1–5 USD around news and the daily break.
- **Swap/rollover**: the daily financing charge for holding past the break.
- **Drawdown**: the fall from your account's peak. Your prop rules measure it on equity, including open profit.
- **Profit factor**: total wins divided by total losses. Above 1 is profitable; our system tests around 1.2–1.7 depending on period and mode.
