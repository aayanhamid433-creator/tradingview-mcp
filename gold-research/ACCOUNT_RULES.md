# ACCOUNT_RULES — Atlas Funded "1-Step Access Funded" 50k account (effective 2026-11-12)

Source: the trader agreement supplied by Aayan on 2026-11-12 (personal identifiers deliberately omitted here). Verify against the dashboard before relying on any number; firms change terms with 7 days' notice (§17).

## Hard constraints (breach = account closed, §7.1)

| Rule | Definition | Number on 50,000 USD |
|---|---|---|
| Maximum daily drawdown (§4.2) | 3 % below **equity at 00:00 UTC**, open positions included; set once per day, not raised by intraday profit | 1,500 USD below the 00:00 UTC equity |
| Maximum trailing drawdown (§4.1) | 6 % below the **highest equity ever reached**, open profit included; ratchets up, never down | floor starts at 47,000; a new equity peak P moves it to 0.94 × P permanently |
| Atlas Protector (§4.5) | net floating loss of all open positions ≥ 2 % of **initial** balance → all positions auto-closed. First trigger: profit split cut from 100 % to 50 % for the life of the account. Second trigger: breach | 1,000 USD net open loss |
| Inactivity (§4.11) | no new trade for 30 days → breach | one trade every 30 days |
| Prohibited practices (§5) | cross-firm hedging, latency/tick scalping, account sharing, overload, exploits | — |

## Soft constraints (profit deducted or payout delayed, no breach)

| Rule | Definition | Playbook consequence |
|---|---|---|
| News (§4.6) | profit of any trade **opened or closed** within ±5 min of a red-folder event (Forex Factory, any currency) is deducted; losses stay | L0 news gate widened from ±3 to **±5 min**; no manual exits inside the window; prefer not to hold a take-profit that is likely to fill inside it |
| Short trades (§4.7) | profit of trades held < 3 min deducted | no scalping; stop_same_minute exits are losses anyway |
| Consistency (§4.4) | best Trading Day ≤ 20 % of cycle profit, else payout delayed until profits even out | a +2.4 R runner day (≈ +600 USD at 0.5 % risk) needs ≥ 3,000 USD cycle profit before payout; expect payout lag with a system that earns on few big days |
| Minimum trading days (§4.3) | 3 UTC days with ≥ 0.5 % (250 USD) closed profit before first payout | needs three separate ≥ +1 R days |
| Margin (§4.10) | used margin ≥ 80 % of total → positions closed, profits deducted | ≈ 2 lots of gold at 1:20; never relevant at playbook size |
| Payout timing (§6.2) | first after 28 days, then every 14 days (7 with add-on) | — |

## Sizing on this account (v2.1 L6, now with real inputs)

- Risk per trade: 0.5 % of equity = **250 USD** (multiplier 1.0).
- Gold: 1.00 lot = 100 oz → 100 USD per 1.00 USD of price. **lots = 250 ÷ (stop distance USD × 100)**, rounded down to 0.01.
- Examples: 5 USD stop → 0.50 lot; 10 USD → 0.25; 20 USD → 0.12; 30 USD → 0.08.
- Daily stop −2 R = −500 USD (one third of the daily limit). Weekly stop −4 R = −1,000 USD.
- Atlas Protector sits at 4 R of floating loss; a stopped trade cannot reach it, a gap or an unstopped trade can. **Every position carries a hard stop in the terminal from the moment it is filled.**
- Trailing drawdown on equity means open profit must be banked: the 50 % partial at T1 stays mandatory.

## Changes to GOLD_PLAYBOOK_v2_CANDIDATE.md L0 for this account (recorded here, applied in v2.1)

1. Gate 0.3: news window **±5 min** around red-folder events in any currency (was ±3 min, US releases only).
2. New gate 0.9: no position without a terminal stop; max floating loss across all positions < 1,000 USD at all times (Protector buffer).
3. New gate 0.10: if no setup has fired for 25 days, open and hold (> 3 min) a 0.01-lot trade in the bias direction to satisfy §4.11, logged as INACTIVITY_KEEPALIVE.
4. Reporting: track best-day share of cycle profit (consistency rule) in the monthly review.

## What this week would have looked like under these rules

- 2026-11-10 discretionary short, 1.00 lot, no stop: at −870 USD floating it was **130 USD from the first Protector trigger** (−1,000), which would have halved the payout split permanently. A 10 USD adverse move from entry does that at 1.00 lot. Playbook size for that trade (stop ~25 USD above entry) was 0.10 lot.

## Risk budget decision (Aayan, 2026-11-12): 0.5 % to 1 % per trade

Checked against the 6 % trailing floor using the worst drawdown each candidate produced in the research (results/summary_v2.md, weighted R, development period unless noted). The guard in gold_v21.pine stops new trades 500 USD above the floor, so the usable drawdown is about 5 %.

| Candidate | Worst drawdown | at 0.5 % | at 0.75 % | at 1 % |
|---|---|---|---|---|
| v2.2 close confirmation (V2_K) | −7.1 R (dev); −5.2 R (test) | −3.6 % survives | −5.3 % halted by guard, 350 USD from breach | −7.1 % **breach** |
| More trades: no daily bias (V2_A) | −25.7 R (dev); −22.2 R (test) | −12.9 % **breach** | breach | breach |

Decision: **0.5 % (250 USD) on v2.2**. 1 % is not survivable on this account with the drawdowns already seen; 0.75 % survives only because the guard halts first. The "more trades" modes are not compatible with a 6 % trailing floor at any risk above 0.2 %, so they are off the table for this account whatever their total R. Reviewed again after 60 forward-test trades.
