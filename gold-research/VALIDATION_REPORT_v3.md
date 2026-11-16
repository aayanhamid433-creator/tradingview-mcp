# VALIDATION REPORT v3 — alternative strategy families on XAUUSD M1 (sixth look at the same data)

Date: 2026-11-12 (UTC). Engine: `backtest/engine_v3.py` (imports `engine.py` for costs/indicators and `engine_v2.py` for the session-day frame). Metrics: `backtest/analyze_v3.py` (reuses `analyze.metrics` and the fixed period splits). Mechanics: `backtest/validate_engine_v3.py` → `results/VALIDATION_MECHANICS_v3.md` (0 failed checks on 13,500 trades; one trade per family hand-checked against the M1 bars). Raw results: `results/V3_*/trades.csv`, `results/summary_v3.md`, `results/summary_v3.json`.

**Question.** Does any strategy family other than the EMA20 pullback (v1.0 / v2.2) show a positive, cost-adjusted, out-of-sample edge with more trades per month than v2.2, on the same data, costs, session day and 20:50 UTC time exit?

**Answer in one line: no. None of the 16 pre-registered variants passes the pre-registered rule; three are positive out of sample but fail it on sample size, drawdown or the v2.2 comparison, and one of those holds overnight.**

## 1. Method

Same HistData XAUUSD M1 bid data (2021-01-04 → 2026-10-30), resampled to M15 for decisions (closed bars only) and simulated on M1 for fills, with the engine_v2 fill mechanics copied as they are: ask = bid + 0.25, slippage 0.05 on every stop and market fill, commission 0, stop-first when stop and target are hit in the same minute, same-minute stop after a fill booked as `stop_same_minute`, time exit at the first M1 bar ≥ 20:50 UTC at the bar open, session day 23:00 → 23:00 UTC (`engine_v2.daily_frame`), all daily quantities (D1 ATR14, SMA200, Donchian channels) taken from the previous completed session day, trailing distances from the last closed bar / previous day. No partial exits and no news gate (each family has its own full exit). R = P&L per oz including costs ÷ planned risk (entry level to initial stop; for market orders, fill to initial stop). Periods are the fixed ones (development 2021-01-04 → 2024-07-01, validation 2024-07-01 → 2025-09-01, final test 2025-09-01 → 2026-11-01), assigned by signal time. All 16 variants were written into `engine_v3.py` before the first run; after the first run two mechanics bugs were fixed (§6) and everything was re-run unchanged; nothing was added or tuned after results were seen.

## 2. Pre-registered variants (frozen before the first run)

| family | variant | rule |
|---|---|---|
| F1 ORB | V3_ORB_L10 | range = high/low of the 07:00–07:59 UTC M15 bars; buy stop range high + 0.10, sell stop range low − 0.10 placed at 08:00, OCO, cancelled 11:00; stop = opposite edge, distance capped at 0.6 × D1 ATR; skip day if range < 0.15 × D1 ATR; target 1.0 × range; one trade per session day |
| F1 ORB | V3_ORB_L15 | as above, target 1.5 × range |
| F1 ORB | V3_ORB_NY10 / V3_ORB_NY15 | range 13:30–13:59 UTC, orders from 14:00, cancel 16:00, target 1.0 × / 1.5 × range |
| F2 VB | V3_VB_03 / V3_VB_05 | at the first M1 bar ≥ 07:00 UTC: buy stop open + k × D1 ATR, sell stop open − k × D1 ATR (k = 0.3 / 0.5), OCO, cancel 16:00; stop = the open; target 1.5 × stop distance; one trade per day |
| F2 VB | V3_VB_03_bias / V3_VB_05_bias | as above, long only when the previous session-day close > SMA200, short only when below (engine_v2 bias) |
| F3 VW | V3_VW_2s / V3_VW_25s / V3_VW_2s_adx15 | session "VWAP" (no volume in the data → **time-weighted average of M1 closes from 23:00 UTC**), band ±s × running population std of (close − VWAP) within the session, minimum 1 USD; signal = M15 close beyond the band and ADX14(M15) < 20 (< 15 for the adx15 variant), window 07:00–15:45; market order on the next M1 bar towards VWAP; stop 1 × ATR14(M15) beyond the signal bar's extreme; target = VWAP at signal time; max 2 trades per day; s = 2.0 / 2.5 / 2.0 |
| F4 DC | V3_DC_20_10 / V3_DC_55_20 | buy stop at the 20- (55-) day high, sell stop at the 20- (55-) day low of the previous completed session days, standing all day while flat, re-placed each session start; exit = the closer of the 10- (20-) day low/high and a 2 × D1 ATR Chandelier trail from the running extreme, ratchet only; no time exit; held overnight and over weekends; one position at a time, at most one entry per day |
| 15-min hold | V3_ORB_L10_h15 / V3_VB_03_h15 / V3_VW_2s_h15 | the first variant of each intraday family with `max_hold_minutes = 15`: if neither stop nor target has hit, the position is closed at the close of the M1 bar that closes 15 minutes after the open of the fill minute, at bid close − 0.05 (long) or bid close + 0.25 + 0.05 (short). Added by the coordinator before the first run; F4 exempt |

**Decision rule (pre-registered):** a variant passes if mean R > 0 AND PF > 1.10 in BOTH validation and final test, with at least 60 trades in each, max drawdown ≤ 10 R in every period (development, validation, final test), AND a higher mean R and a higher total R than v2.2 (V2_K_confirm) in both periods. v2.2 reference: validation 17 trades, +0.978 R/trade, +16.6 R, PF 3.01; final test 26 trades, +0.191 R/trade, +5.0 R, PF 1.49; max DD −7.1 R.

## 3. Results

Per variant and period: trades / mean R / PF / max drawdown (R). "cost" = spread + slippage as a share of planned risk (mean over all trades, the friction every trade pays). Full tables with 90 % bootstrap CIs, win rates, total R, losing streaks and median holds are in `results/summary_v3.md`.

| variant | rule | development n / mean R / PF / DD | validation n / mean R / PF / DD | final test n / mean R / PF / DD | OOS trades / month | cost (R) | passes? |
|---|---|---|---|---|---|---|---|
| V3_ORB_L10 | London range 07:00–08:00, target 1.0×range | 540 / +0.002 / 1.00 / -31.8 | 177 / -0.002 / 1.00 / -13.1 | 153 / -0.026 / 0.95 / -17.0 | 11.8 | 0.055 | no |
| V3_ORB_L15 | London range, target 1.5×range | 540 / -0.039 / 0.94 / -49.5 | 177 / +0.005 / 1.01 / -14.8 | 153 / -0.009 / 0.98 / -18.3 | 11.8 | 0.055 | no |
| V3_ORB_NY10 | range 13:30–14:00 UTC, cancel 16:00, target 1.0× | 666 / -0.009 / 0.98 / -31.2 | 206 / +0.054 / 1.13 / -7.5 | 171 / +0.014 / 1.03 / -18.4 | 13.5 | 0.046 | no |
| V3_ORB_NY15 | range 13:30–14:00 UTC, target 1.5× | 668 / +0.018 / 1.04 / -27.3 | 206 / +0.100 / 1.22 / -7.5 | 171 / +0.040 / 1.08 / -24.5 | 13.5 | 0.046 | no |
| V3_ORB_L10_h15 | V3_ORB_L10 + 15-min max hold | 540 / -0.048 / 0.69 / -29.9 | 177 / -0.039 / 0.70 / -8.4 | 153 / +0.003 / 1.02 / -6.9 | 11.8 | 0.055 | no |
| V3_VB_03 | k = 0.3, both sides | 805 / -0.067 / 0.88 / -79.9 | 269 / -0.074 / 0.86 / -35.8 | 243 / -0.044 / 0.91 / -21.0 | 18.3 | 0.038 | no |
| V3_VB_05 | k = 0.5, both sides | 495 / -0.037 / 0.90 / -29.8 | 162 / +0.002 / 1.01 / -8.8 | 120 / +0.145 / 1.53 / -6.0 | 10.1 | 0.024 | no |
| V3_VB_03_bias | k = 0.3, SMA200 side only | 369 / -0.133 / 0.77 / -55.2 | 156 / +0.052 / 1.11 / -13.7 | 139 / -0.071 / 0.86 / -21.1 | 10.5 | 0.037 | no |
| V3_VB_05_bias | k = 0.5, SMA200 side only | 188 / +0.003 / 1.01 / -12.2 | 88 / +0.130 / 1.51 / -6.5 | 62 / +0.137 / 1.52 / -3.7 | 5.4 | 0.023 | no |
| V3_VB_03_h15 | V3_VB_03 + 15-min max hold | 805 / -0.053 / 0.69 / -45.8 | 269 / -0.043 / 0.72 / -16.5 | 243 / -0.056 / 0.66 / -14.7 | 18.3 | 0.038 | no |
| V3_VW_2s | ±2σ, ADX < 20 | 818 / -0.177 / 0.74 / -155.0 | 256 / -0.155 / 0.77 / -47.6 | 217 / -0.106 / 0.84 / -31.6 | 16.9 | 0.108 | no |
| V3_VW_25s | ±2.5σ, ADX < 20 | 614 / -0.156 / 0.78 / -110.5 | 190 / -0.153 / 0.78 / -42.4 | 159 / -0.096 / 0.86 / -23.8 | 12.5 | 0.105 | no |
| V3_VW_2s_adx15 | ±2σ, ADX < 15 | 288 / -0.237 / 0.65 / -72.7 | 80 / -0.278 / 0.61 / -23.0 | 85 / -0.097 / 0.85 / -13.1 | 5.9 | 0.112 | no |
| V3_VW_2s_h15 | V3_VW_2s + 15-min max hold | 904 / -0.152 / 0.54 / -139.5 | 283 / -0.101 / 0.66 / -30.5 | 252 / -0.004 / 0.99 / -13.0 | 19.1 | 0.109 | no |
| V3_DC_20_10 | entry 20-day, exit 10-day / 2×ATR | 52 / +0.157 / 1.46 / -3.8 | 16 / +0.703 / 3.01 / -3.2 | 13 / +0.713 / 3.05 / -2.2 | 1.0 | 0.006 | no |
| V3_DC_55_20 | entry 55-day, exit 20-day / 2×ATR | 25 / +0.439 / 3.03 / -2.8 | 8 / +1.660 / 11.25 / -0.8 | 9 / +0.655 / 4.12 / -1.0 | 0.6 | 0.006 | no |

Conditions failed, by variant (from `summary_v3.json`):

- ORB (all five): mean R or PF not positive in both held-out periods except V3_ORB_NY15 (PF 1.08 in the final test, below 1.10); max DD −13 to −50 R in development for every ORB variant; none approaches v2.2 per trade.
- VB: V3_VB_05_bias is the only variant positive in both held-out periods (88 / 62 trades, +0.130 / +0.137 R, PF 1.51 / 1.52, total +11.4 / +8.5 R). It fails on development drawdown (−12.2 R, development mean R +0.003, PF 1.01), on per-trade R against v2.2 in both periods, and on total R in validation (+11.4 vs +16.6). Its final-test total (+8.5 R on 62 trades) does beat v2.2's +5.0 R on 26. The bias layer trades from 2021-10 only (SMA200 warm-up), so its development row covers 2021-10 → 2024-06.
- VW (all four): negative in every period; the 90 % CI of the OOS mean excludes zero on the wrong side for 2s and 25s. Rejected outright.
- DC: positive in every period with tiny drawdowns (-3.8 / -3.2 / -2.2 R for 20/10) but 16 and 13 trades in the held-out periods (about one per month) against a 60-trade minimum, and it holds for a median of 11 days. V3_DC_55_20 has 8 and 9 held-out trades; its numbers (+1.66 R, PF 11) are what eight trades in a one-directional gold year look like, not evidence.

## 4. Verdict per family

| family | verdict | reason |
|---|---|---|
| F1 opening-range breakout | **rejected** | mean R within ±0.1 of zero in every period and variant; the London range is a coin flip after costs (PF 0.94–1.01); the New York range is slightly positive out of sample (NY15: +0.100 / +0.040 R) but PF 1.08 in the final test and development DD −27 R; at 0.06 R of cost per trade the edge, if any, is smaller than the friction |
| F2 volatility breakout | **rejected as a family; one variant inconclusive** | three of four variants negative or flat; V3_VB_05_bias is positive in both held-out periods on 150 trades (OOS +0.133 R, CI [+0.030, +0.238], PF 1.52, DD −6.5 R, 5.4 trades/month) but flat in development (+0.003 R, DD −12.2 R) and below v2.2 per trade in both periods. Same pattern as every "works out of sample, not in development" result in this project (V6, V2_J): a 2024–2026 trend artefact until proven otherwise. It does not add trades: 5.4 per month vs v2.2's 1.2–1.9, but 74 % of its OOS trades are 20:50 time exits, i.e. it is a daily-bias trend hold wearing a breakout entry |
| F3 session-VWAP mean reversion | **rejected** | −0.10 to −0.28 R per trade in every period and variant, 32 % win rate; with no volume the "VWAP" is a TWAP, and the 2–4 USD stops cost 0.1 R per trade in spread alone; gold's intraday moves beyond ±2σ of a running mean continue more often than they revert at this horizon |
| F4 daily Donchian | **inconclusive, and not usable on this account as specified** | positive in all three periods (+0.157 / +0.703 / +0.713 R, PF 1.5–3.0, DD ≤ 3.8 R) but 13–16 held-out trades per period, one trade a month, 10-day median hold, overnight and weekend exposure: the 6 % trailing floor, the 3 % daily limit measured at 00:00 UTC and the Atlas Protector (2 % floating) all bite on a position that gaps against it over a weekend; the stop distances (median 56 USD) mean 0.5 % risk = 0.04–0.05 lots, which is fine, but a gap through the stop is unbounded. It cannot pass a 60-trades-per-period rule in any realistic test window |

**Nothing passes.** The pre-registered answer to the question is: on this data, no tested family produces a positive, cost-adjusted, out-of-sample edge with more trades per month than v2.2 and a drawdown the account can carry. The two positive signals (VB_05_bias, DC) are both "trade with the daily trend and hold" in disguise and both rest on the 2024–2026 bull run; they are not intraday edges and they were not positive in 2021–2024.

## 5. 15-minute maximum hold vs the unconstrained twin

| pair | period | unconstrained n / mean R / total R / PF / DD | h15 n / mean R / total R / PF / DD |
|---|---|---|---|
| V3_ORB_L10 vs V3_ORB_L10_h15 | development | 540 / +0.002 / +1.2 / 1.00 / -31.8 | 540 / -0.048 / -26.0 / 0.69 / -29.9 |
| V3_ORB_L10 vs V3_ORB_L10_h15 | validation | 177 / -0.002 / -0.3 / 1.00 / -13.1 | 177 / -0.039 / -7.0 / 0.70 / -8.4 |
| V3_ORB_L10 vs V3_ORB_L10_h15 | final_test | 153 / -0.026 / -4.0 / 0.95 / -17.0 | 153 / +0.003 / +0.4 / 1.02 / -6.9 |
| V3_VB_03 vs V3_VB_03_h15 | development | 805 / -0.067 / -53.9 / 0.88 / -79.9 | 805 / -0.053 / -42.9 / 0.69 / -45.8 |
| V3_VB_03 vs V3_VB_03_h15 | validation | 269 / -0.074 / -19.9 / 0.86 / -35.8 | 269 / -0.043 / -11.5 / 0.72 / -16.5 |
| V3_VB_03 vs V3_VB_03_h15 | final_test | 243 / -0.044 / -10.6 / 0.91 / -21.0 | 243 / -0.056 / -13.7 / 0.66 / -14.7 |
| V3_VW_2s vs V3_VW_2s_h15 | development | 818 / -0.177 / -144.7 / 0.74 / -155.0 | 904 / -0.152 / -137.3 / 0.54 / -139.5 |
| V3_VW_2s vs V3_VW_2s_h15 | validation | 256 / -0.155 / -39.7 / 0.77 / -47.6 | 283 / -0.101 / -28.6 / 0.66 / -30.5 |
| V3_VW_2s vs V3_VW_2s_h15 | final_test | 217 / -0.106 / -23.0 / 0.84 / -31.6 | 252 / -0.004 / -0.9 / 0.99 / -13.0 |

A 15-minute hold turns every intraday family into a bet on the first quarter-hour after the fill: 96–98 % of ORB and VB trades and 84 % of VW trades end as `max_hold` exits, so the realised R per trade shrinks to a fraction of the planned risk (median |R| 0.19 for ORB and VB, 0.31 for VW) while the fixed cost of 0.35 USD per round trip stays the same. For ORB and VB the result is a worse profit factor (ORB OOS 0.97 → 0.84, VB 0.89 → 0.69): breakouts that would have run to the 1.0–1.5 × target are cut at +0.1 R, while the cost is paid in full, so mean R stays slightly negative and nothing is gained except a smaller drawdown in R (which is only a smaller bet, not a better one). For VW the 15-minute cut reduces the loss per trade (OOS −0.133 → −0.055 R, final test −0.004 R) because it truncates the losing continuation moves before the 1-ATR stop, and it frees the 2-per-day slots so there are more trades (535 vs 473); the family is still negative in validation (−0.101 R, PF 0.66) and the final-test figure is zero within the CI. Under the account's rule that trades held under 3 minutes lose their profit, a 15-minute cap is allowed, but on this data it does not create an edge for any family; it only changes how fast the same non-edge is paid for.

## 6. Bugs found and fixed before the final run (all variants re-run; no parameters changed)

1. **Intraday positions leaking across session days.** 62 session days end before 20:50 UTC (early closes, feed outages, e.g. a four-hour gap on 2023-06-28). The engine_v2-style time exit (`minute ≥ 20:50`) never fires on those days and the position lived into the next day until its stop or target hit. v3 now closes intraday positions and cancels pending orders at the first bar of the next session day (`session_gap_exit`, `CANCEL_session_ended`, 9–16 cases per variant). engine_v2 still has this leak; it is noted here, not fixed there (out of scope; it affects v2 results only on those days).
2. **Gap fills beyond the planned stop or target.** On a feed gap or a news bar the first available print can be beyond the planned stop (a VW short filled 0.6 USD above its stop, then "stopped" at stop + slippage for a +0.9 R profit) or beyond the target (ten ORB/VB entries). v3 now does not take such an order (`SKIP_gap_fill_past_stop/target`, 0–4 cases per variant). engine_v2 Trigger C has the same exposure in principle; none of its trades hit it.
3. Validator only: the target check needed a 1e-6 tolerance (float noise on `level + range`), and the Donchian signal-time check had to accept the three session days whose first bar is 22:00 or 00:00 rather than 23:00 UTC.

## 7. Caveats

- **Sixth look at the same data.** The periods are the same as in every previous pass and the families were chosen knowing what v1/v2 did on this data. Pre-registration protects against tuning within this pass, not against the selection of what to test. The clean evidence remains the forward test.
- **No volume**: the F3 "VWAP" is a TWAP. Real VWAP bands would differ, probably not in sign.
- **Approximate daily boundary**: the 23:00 UTC session day and the fixed-EST feed produce 21 one-hour pseudo days on US DST-switch Sundays that enter the shared daily frame (D1 ATR, SMA200, channels) as tiny bars. The "NY" ORB uses 13:30 UTC all year; that is the NY equity open only during US DST.
- **Data gaps**: minutes without a tick are absent; a stop inside a gap fills at the next open (same as v1/v2). 20 VB and 9 VW trades are same-minute stop-outs on news bars (no news gate in v3 by design); the worst single trade is −4.1 R (VW, NFP 2024-02-02).
- **Overnight holding (F4)** is outside the account's current rules (ACCOUNT_RULES.md: Protector 2 % floating, daily limit from 00:00 UTC equity, trailing 6 % on equity including open P&L); nothing here changes the flat-by-night habit.
- Sample sizes: at σ ≈ 1.0–1.4 R per trade, a 0.05 R edge needs > 1,000 trades to separate from zero at 90 %; the ORB/VB/VW variants have 150–270 trades per held-out period, enough to reject a 0.2 R edge (which they do) and not enough to see a 0.05 R one, which would be eaten by the first widening of the spread anyway.

## 8. Files

- `backtest/engine_v3.py` (new), `backtest/analyze_v3.py` (new), `backtest/validate_engine_v3.py` (new)
- `results/V3_*/trades.csv`, `skips.csv`, `config.json` (16 variants), `results/summary_v3.md`, `results/summary_v3.json`, `results/VALIDATION_MECHANICS_v3.md`
- No file from v1/v2 (`engine.py`, `engine_v2.py`, `analyze_v2.py`, `results/V0_*`, `results/V2_*`) was modified.
