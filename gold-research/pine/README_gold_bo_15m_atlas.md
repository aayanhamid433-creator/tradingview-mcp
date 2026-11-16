# gold_bo_15m_atlas.pine — Atlas edition of "Gold Breakout 15M Strategy [WillyAlgoTrader]"

Derivative of the open-source TradingView script by WillyAlgoTrader (script HnelYN0A, published 2026-10-12). His breakout, sizing, dashboard and alert code is unchanged; every modification is marked `[ATLAS]` in the source. Status: tester and demo only.

What was added
1. News gate: typed list of release times (UTC), ±5 minutes by default. No pending entry while the next bar overlaps a window; the 20:00 time exit waits until the window has passed. Stop-loss fills inside a window cannot be avoided (Atlas deducts profit, losses stay).
2. Account guard, Atlas Funded 1-Step defaults: daily loss vs 00:00 UTC equity (no new trades at 2 %, close everything at 2.5 %, firm breach 3 %); trailing floor 6 % below peak equity (no new trades within 500 USD, close within 200 USD); Protector (close at −700 USD floating, firm at −1,000); consistency (best day ≤ 20 % of cycle profit) and inactivity (30 days) warnings; ACCOUNT CHECK table bottom-right with a verdict.
3. Defaults: initial capital 50,000; risk per trade 1.0 % (Aayan's choice; 0.15 % is the level the account simulation found survives the 2023 drawdown); max leverage 2.

How to use
1. TradingView → Pine Editor → paste the file → Add to chart (XAUUSD, 15-minute, regular candles).
2. Settings: Broker Time Mode / Timezone = your MT5 server clock (FOREX.com-style servers are "New York + 7h"); keep Range 00:00–07:00 and Close 20:00 unless you are testing something else.
3. Type the next weeks' red-folder events into "Release times, UTC"; Pine cannot download a calendar.
4. Check "Payout cycle start" and the account inputs against your Atlas dashboard; the firm can change terms with 7 days' notice.
5. Strategy Tester shows the backtest; the research re-run with realistic costs is in ../ALT_GOLD_BO_15M_REPORT.md (PROMISING, UNVALIDATED). The tester does not model spread.

Not compiled here: this file was written without access to a Pine compiler. If the editor reports an error, paste the message and line.
