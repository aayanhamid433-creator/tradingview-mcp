# pine/ — TradingView strategy for self-backtesting v2.1

`gold_v21.pine` is one script that does three jobs: backtest engine for the Strategy Tester, simple on-chart guidance (instruction label, red risk box, green reward box, five-row table), and `alert()` messages for live or demo use (Create Alert → this script → "Any alert() function call": new setup, move stop order, filled, target hit, move stop, cancel, exit). It implements GOLD_PLAYBOOK_v2_CANDIDATE.md in its v2.1 form (trend-pullback trigger only, SMA200 daily bias, no momentum vote, 07:00–15:45 UTC window) with the sizing from ACCOUNT_RULES.md. Pine Script v6, strategy type, overlay.

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
| Size | equity × 0.5 % ÷ stop distance, in ounces |
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
| Strict (v2.1) | default | 61 trades, +0.339 R, PF 1.74 |
| More trades: no daily bias | both directions | 158 trades, +0.179 R, PF 1.28 |
| More trades: reward/risk 1.0 | min RR 1.0 | 110 trades, +0.205 R, PF 1.45 |
| Most trades: no bias + RR 1.0 | both | not run in the research; expect the most trades and the least edge per trade |

More trades always meant less edge per trade in the research. None of the modes produces a trade every day; the loosest is roughly one every two sessions.

## News blackout list (added 2026-11-12)

The `Red-folder events` input holds UTC date-times (comma separated). No new order is placed, and any pending order is cancelled, on a bar that overlaps ±5 minutes of an event. The defaults cover the next weeks (CPI, NFP, FOMC, PCE/GDP days as known on 2026-11-12) and **must be verified and extended from Forex Factory every week**; times move one hour earlier in US summer time. Open positions are not closed by the gate: the account's rule only deducts profit on trades opened or closed inside the window.
