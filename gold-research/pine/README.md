# pine/ — TradingView strategy for self-backtesting v2.2

`gold_v21.pine` (strategy title "Gold v2.2"; the file name is historical) is one script that does four jobs (the fourth, the account guard, is described at the end): backtest engine for the Strategy Tester, simple on-chart guidance (instruction label, red risk box, green reward box, five-row table), and `alert()` messages for live or demo use (Create Alert → this script → "Any alert() function call": new setup, move stop order, filled, target hit, move stop, cancel, exit). It implements GOLD_PLAYBOOK_v2_CANDIDATE.md in its v2.1 form (trend-pullback trigger only, SMA200 daily bias, no momentum vote, 07:00–15:45 UTC window) with the sizing from ACCOUNT_RULES.md. Pine Script v6, strategy type, overlay.

## Setup in TradingView

1. Chart: XAUUSD (FOREX.com), **15-minute**. Pine Editor → paste the file → "Add to chart".
2. The script sets margin to 5 % (1:20). Without it TradingView requires 100 % cash per position and refuses every order, which shows up as "no trades". Strategy Tester → Settings → Properties: initial capital 50000, base currency USD, commission **0.15 per contract** (this stands in for the ~0.30 USD/oz spread the strategy cannot see), slippage **5 ticks** (0.05 USD), order size "from script". Turn on "Use bar magnifier" if your plan has it (fills then use 1-minute data inside each 15-minute bar; without it, same-bar stop/target order is TradingView's guess).
3. Quantity is in ounces. 100 oz = 1.00 lot. `Quantity step` input: 1 for whole ounces.
4. The daily bias needs 200 daily bars of history. The first trades appear about ten months after the start of your data.

## How to read the result honestly

- Compare the three periods **separately** (Properties → date range): 2021-01-04 → 2024-06-30, 2024-07-01 → 2025-08-31, 2025-09-01 → today. The decision rule in GOLD_PLAYBOOK_v2_CANDIDATE.md §11 needs mean R > 0 and profit factor > 1.10 in **both** held-out periods, at least 60 trades in each, and must beat v1.0.
- Count trades. Fewer than about 240 trades cannot distinguish a 0.1 R edge from zero (ACCOUNT_RULES.md / playbook §8.6). Three months of data proves nothing either way.
- Every input you change is a new variant. Write down what you changed and why **before** looking at the result, and never keep a change because it improved the all-period equity curve. Keep it only if it improves the held-out periods and you can say why it should.
- TradingView's FOREX.com XAUUSD history differs from the HistData research set (different feed, different daily boundary). Numbers will not match results/summary_v2.md exactly. Direction and magnitude should be similar; if they are not, that is information.

## What the script does on each 15-minute bar

| Step | Rule |
|---|---|
| Bias | previous daily close above its 200-day SMA → longs only; below → shorts only (`useBias` off = both) |
| Armed | ADX(14) > 30 now and ADX rose above 30 within the last 10 bars; +DI vs −DI gives direction |
| Touch | bar low ≤ EMA20 ≤ bar high, bar opens between 07:00 and 15:45 UTC |
| Order | stop order 0.10 beyond the touch bar's extreme; re-armed on later touch bars; expires after 4 bars, at 16:00 UTC, on a deep break of the EMA (0.5 ATR), or if ADX < 25 |
| Stop | swing extreme of the pullback bars ± max(0.30, 0.10 × ATR14) — **15-minute lows only; the research engine also used 1-minute lows** |
| Target | 20-bar extreme at the first touch bar, capped at the prior-day high/low if more than 1 ATR beyond it |
| Filter | reward/risk at placement ≥ 1.5; stop distance ≤ 0.6 × daily ATR |
| Size | equity × 0.5 % ÷ stop distance, in ounces, capped at 50 % margin use and 2.0 lots (added 2026-11-12 after the TradingView backtest showed margin calls: tight 15-minute stops produced 2-lot positions) |
| Exit | 50 % at target, stop to entry ± 0.10, remainder trails at highest high − 3 × ATR; everything flat at the 20:45 UTC bar (fills at 20:45; the research rule was 20:50) |
| Stops | day halts after 3 consecutive losses or −2 R closed; week halts at −4 R; max 3 entries per session day (23:00–23:00 UTC) |
| News | no calendar access. Use the manual blackout inputs on red-folder days, or accept that the backtest trades through news (the research engine's approximate gate changed nothing) |

## Known differences from the research engine (backtest/engine_v2.py)

- Stop placement uses 15-minute lows between first touch and fill, not 1-minute lows → stops slightly tighter in some trades.
- Forced flat at 20:45 instead of 20:50 UTC.
- Daily bars are TradingView's (exchange day) rather than the 23:00 UTC session day used in the research.
- Fill prices are TradingView's (one price series, no bid/ask); commission input stands in for spread.
- The script has not been compiled here; if the Pine editor reports an error, paste it back and it will be fixed.

## MODE input (added 2026-11-12)

| Mode | What changes | Out-of-sample on HistData (results/summary_v2.md) |
|---|---|---|
| v2.2 (close confirmation) | **default**; touch bar must close on the trend side of EMA20 | 43 trades, +0.502 R, PF 2.17, max DD −5.2 R |
| Strict (v2.1) | no confirmation | 55 trades, +0.414 R, PF 1.93 |
| v2.2 New York only | signals 12:00–15:45 UTC only | 21 trades, +1.03 R, PF 5.2, but negative in development; small sample |
| More trades: no daily bias | both directions | 158 trades, +0.179 R, PF 1.28 |
| More trades: reward/risk 1.0 | min RR 1.0 | 110 trades, +0.205 R, PF 1.45 |
| Most trades: no bias + RR 1.0 | both | not run in the research; expect the most trades and the least edge per trade |

More trades always meant less edge per trade in the research. None of the modes produces a trade every day; the loosest is roughly one every two sessions. A forced daily trade was tested on 2026-11-12 (VALIDATION_REPORT_v2.md §8): the forced trades lost on average and the drawdown would close the account, so there is no daily mode. The "more trades" modes are also incompatible with the 6 % trailing floor (ACCOUNT_RULES.md, risk budget decision); they stay in the script for backtesting only.

## News blackout list (added 2026-11-12)

The `Red-folder events` input holds UTC date-times (comma separated). No new order is placed, and any pending order is cancelled, on a bar that overlaps ±5 minutes of an event. The defaults cover the next weeks (CPI, NFP, FOMC, PCE/GDP days as known on 2026-11-12) and **must be verified and extended from Forex Factory every week**; times move one hour earlier in US summer time. Open positions are not closed by the gate: the account's rule only deducts profit on trades opened or closed inside the window.

## Account guard (added 2026-11-12): "powered by Claude", inside TradingView

Pine Script cannot call the internet, so it cannot call Claude or any AI model. What it can do is run the same checks Claude runs on every chart review, as code, on every bar. The `Account guard` input group holds the Atlas Funded numbers from ACCOUNT_RULES.md; the bottom-right **ACCOUNT CHECK** table shows each one with a colour and a final verdict. It never predicts direction.

| Row | What it measures | Green / orange / red |
|---|---|---|
| TODAY'S LOSS | equity now vs equity at 00:00 UTC, open P&L included (firm: 3 % = breach) | new trades stop at 2 % (1,000 USD); everything is closed at 2.5 % |
| TRAILING FLOOR | highest equity so far × 0.94 (firm: 6 % trailing) | new trades stop within 500 USD of the floor; everything is closed within 200 USD |
| FLOATING P&L | open profit or loss (firm Protector: −1,000 USD = positions closed, payout split halved) | everything is closed at −700 USD |
| NEWS | minutes to the next event in the red-folder list; red while in the ±5-minute blackout | orange inside one hour |
| CONSISTENCY | best UTC day's closed profit as % of closed profit since `Payout cycle start` (firm: max 20 %) | orange above 20 %: payout will be delayed, not a breach |
| INACTIVITY | days since the last fill (firm: 30 days = breach) | orange from 20 days, red from 25 |
| VERDICT | OK TO TAKE THE NEXT SETUP / NO NEW TRADES: reason / CLOSE EVERYTHING: reason | |

When the guard halts, pending orders are cancelled, no new setup is placed, the top banner says why, and an alert fires once (`ACCOUNT GUARD: no new trades (...)`). When it says close, the script closes its own backtest position at the next bar open and the alert `ACCOUNT GUARD: CLOSE EVERYTHING IN MT5 NOW (...)` fires; in live use you still close the MT5 position yourself.

Limits to know: equity is read at bar closes, so intrabar peaks and the exact 00:00 UTC equity are approximations (the firm uses tick equity); the script only sees its own trades, not discretionary ones in MT5; the 3-minute minimum hold cannot be enforced on 15-minute bars (a stop hit in the entry bar is a loss anyway, and losses are not deducted). In a multi-year backtest the trailing floor behaves like the real account: once equity falls 6 % from its peak the guard stops trading for good, which is what would have happened to the account. Turn `Account guard on` off to see the raw strategy through a drawdown, and on to see whether the account would have survived.

## Review fixes (2026-11-12, after an independent three-lens code review)

- **Protective orders from the fill tick.** The stop and the first target are now attached to the entry order itself (`strategy.exit(..., from_entry=...)` issued together with `strategy.entry`), so they are live during the bar in which the entry fills. Before, they were only placed at the close of the fill bar, which let a reversal bar run past the stop and executed the stop at the next open. Expect more exits at the planned stop price and more T1 fills than in earlier runs.
- **Consecutive losses are counted per trade,** not per exit leg (the T1 leg and the remainder are two rows in the List of Trades). The three-loss daily halt no longer trips after two losers.
- **Alerts accumulate within a bar** (`cancel | new setup`), so a cancel is never overwritten by a new order message.
- **Force flat** default is now the 20:30 bar, so the close order fills at 20:45 UTC, five minutes before the research engine's 20:50 and well before the daily feed break. On-chart texts are built from the inputs.
- **Max hold:** 1 = close at the end of the fill bar (within 15 minutes), 2 = within 30 minutes.
- The script stops with an error on any chart other than 15 minutes; the news-list parser tolerates a blank list; the box drawings are guarded against missing values and the reward box disappears after T1.
- Not changed, and documented here: the research bias used an additional 12-1 momentum vote with half size on disagreement (the script uses SMA200 only); the research engine checked the news window at the bar close while the script blocks any bar overlapping the window; the engine's Monday gap gate is absent; the daily SMA200 needs 200 daily bars of history, so the first trades appear about ten months into any backtest window.

## EVERY DAY mode (added 2026-11-12 at Aayan's request; tested and rejected in VALIDATION_REPORT_v2.md §8)

MODE "EVERY DAY: v2.2 + forced trade at 13:30 UTC (tested: loses)". Normal v2.2 pullback setups all day; if no entry has happened by the bar that opens at 13:30 UTC, a market order in the direction of the daily bias (DI direction when the bias filter is off; skipped when the bias is undefined), stop 1.5 × ATR14, half off at 1.5 × that distance, remainder on the usual breakeven and trail, flat at 20:45. It fires on the first bar from 13:30 where every gate passes, so on a listed news day it fires one bar later; it never fires on a pullback-setup bar, after the daily or weekly stop, under the account guard, or more than once a day. A "DAILY TRADE skipped: reason" alert explains a missed day. Research numbers for the forced trades: −0.03 to −0.12 R per trade, 40–87 R drawdown, about 60 % losing days. The account guard halts the mode when the drawdown approaches the firm's floor.
