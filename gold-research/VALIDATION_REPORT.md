# VALIDATION_REPORT — GOLD_PLAYBOOK v1.0 ("Holy Grail" intraday adaptation, XAUUSD)

Report date: 2026-11-09. Strategy version: **v1.0** (frozen 00:30 UTC, before any result was inspected).
**Pre-registered verdict: INCONCLUSIVE.** Not SUPPORTED FOR DEMO, not REJECTED. Reasons in §6.

Plain English: we tested one fully written-down rule set on about six years of 1-minute gold data. Out of sample it made money in the first held-out period and lost a little in the second; the uncertainty band around the average trade still includes zero. One pre-registered variant (New York session only) looks much better, but it is one of ten variants looked at after the fact, so it is a hypothesis for the next version, not a result.

---

## 1. What was actually run (and what was not)

| Stage | Status |
|---|---|
| Data download and audit | RUN — HistData.com M1, 2021-01-04 → 2026-10-30 (data/DATA_AUDIT.md) |
| Rule freeze before results | DONE — GOLD_PLAYBOOK_v1.md |
| Simulator mechanics validation | RUN — results/VALIDATION_MECHANICS.md (independent indicator recomputation, P&L arithmetic, every trade re-derived from raw M1 data: 477/477 pass; one engine bug found and fixed before any result was used) |
| Backtest of v1.0 and 10 pre-registered variants | RUN — results/summary.md, results/<variant>/trades.csv |
| Exact news filter | **NOT RUN** — historical BLS/Fed calendars were not downloadable from the sandbox; an approximate NFP/FOMC variant was run and is labelled APPROXIMATE |
| Broker-feed backtest (Aayan's MT5 data) | **NOT RUN** — no broker export yet (request in §9) |
| Chart-reading audit (hidden future candles) | RUN — chart_audit/CHART_AUDIT_RESULTS.md |
| Forward test on demo | **NOT STARTED** — protocol written (FORWARD_TEST_PROTOCOL.md) |
| Monetary sizing / prop-rule compliance | **NOT RUN** — inputs not supplied (playbook §11) |

## 2. Data audit (summary; full table in data/DATA_AUDIT.md)

| Item | Value |
|---|---|
| Source | HistData.com, MetaTrader-format 1-minute bars for XAUUSD (free generic feed) |
| Why this feed | the only free multi-year M1 gold source reachable from the sandbox; **not** the broker Aayan will trade |
| Price basis | BID only (HistData FAQ). Ask modelled as bid + constant spread |
| Timezone | EST without DST per HistData FAQ; converted to UTC with a fixed +5 h |
| Range | 2021-01-03 23:00 → 2026-10-30 20:58 UTC; 2,020,438 bars; 1,504 duplicate timestamps removed; 0 OHLC inconsistencies |
| Structure | daily break ≈ 21:58–23:00 UTC every day (1,078 occurrences); 296 weekend gaps; 682 other gaps > 60 min, mostly holidays and early closes |
| Missing | ask/spread, volume, broker holiday calendar, broker-specific break times |
| Resolution use | M1 drives fills; M15 drives signals; M1 bars remove most stop-vs-target ambiguity (0 ambiguous minutes occurred across all variants) |

Differences from a live XAUUSD CFD: spread varies (widening at the daily break and around news is not modelled); the broker's daily break in summer is at ~21:00 UTC, one hour earlier than this feed's; prices of different liquidity providers differ by tens of cents at times.

## 3. Test design (pre-registered, GOLD_PLAYBOOK_v1.md §13)

| Period | Dates | Purpose |
|---|---|---|
| Development | 2021-01-04 → 2024-06-30 | the only period that could have informed design (in practice the rules were fixed from the source before any run) |
| Validation | 2024-07-01 → 2025-08-31 | first held-out check |
| Final test | 2025-09-01 → 2026-10-30 | untouched by any tuning |

Costs base case: spread 0.25 USD/oz, 0.05 USD slippage on stop-type fills, no commission. Signals on closed M15 bars; fills on later M1 bars; stop assumed first when both are reachable in one minute; limit targets need a trade-through.

R = planned risk from the entry stop level to the initial stop-loss, in USD per ounce. A stopped trade realises about −1.02 R because of slippage; gaps could make it worse.

## 4. Results — V0 base (per period)

| period | trades | total R | mean R | 90 % bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest DD (trades / days) | longest losing streak | exposure* | median / mean hold (min) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| development | 254 | −21.1 | −0.083 | [−0.213, +0.048] | 37.8 % | +1.47 / −1.03 | 0.87 | −36.5 | 206 / 1026 | 8 | 2.9 % | 49 / 86 |
| validation | 107 | +22.2 | +0.208 | [+0.001, +0.422] | 48.6 % | +1.51 / −1.03 | 1.39 | −11.0 | 44 / 171 | 6 | 3.1 % | 52 / 74 |
| final test | 116 | −5.4 | −0.046 | [−0.253, +0.165] | 36.2 % | +1.65 / −1.01 | 0.93 | −22.7 | 61 / 223 | 8 | 4.5 % | 60 / 99 |
| validation + final test | 223 | +16.9 | +0.076 | [−0.070, +0.227] | 42.2 % | +1.58 / −1.02 | 1.13 | −22.7 | 61 / 223 | 8 | 3.8 % | 56 / 87 |

\*exposure = hours with an open position ÷ hours in the 07:00–20:50 UTC window on weekdays.

Exit mix out of sample: 129 stops, 90 targets, 4 time exits. Development period for reference: 153 / 88 / 13.

**Dependence on a few trades (validation + final test):** total +16.9 R, of which the 5 best trades contribute +16.3 R; mean R excluding the 5 best is +0.002. The out-of-sample result is therefore essentially break-even once the best handful of trades is removed.

**By session (out of sample):** London (signal 07:00–11:59 UTC) 146 trades, mean −0.070 R, PF 0.89; New York (12:00–15:45 UTC) 77 trades, mean +0.351 R, CI [+0.107, +0.605], PF 1.76.
**By direction:** long 93 trades, mean +0.120 R; short 130 trades, mean +0.044 R.
**By year:** 2021 +0.152, 2022 −0.054, 2023 −0.149, 2024 −0.099, 2025 +0.122, 2026 (to Oct) −0.041 mean R.

Skipped and cancelled setups (all periods): reward/risk below 1.0 at placement 1,177; deep break of the EMA cancelled 221; cut-off time 30; daily cap 6; other 11. In other words, most touches are rejected because the recent high is too close to the entry.

## 5. Sensitivity (all pre-registered variants; mean R and profit factor)

| variant | what changes | development | validation | final test | validation + test |
|---|---|---|---|---|---|
| V0 base | — | −0.083 / 0.87 (254) | +0.208 / 1.39 (107) | −0.046 / 0.93 (116) | +0.076 / 1.13 (223) |
| V1 cost stress | spread 0.50, slippage 0.15 | −0.262 / 0.64 | +0.079 / 1.14 | −0.112 / 0.83 | −0.020 / 0.97 |
| V2 raw account | spread 0.10 + 0.07 commission | −0.061 / 0.90 | +0.252 / 1.49 | −0.045 / 0.93 | +0.097 / 1.17 |
| V3 ADX > 25 | looser trend filter | −0.062 / 0.90 (458) | −0.014 / 0.98 (191) | −0.041 / 0.93 (202) | −0.028 / 0.95 |
| V4 ADX > 35 | stricter trend filter | 0.000 / 1.00 (139) | +0.250 / 1.48 (63) | −0.228 / 0.69 (65) | +0.007 / 1.01 |
| V5 London only | signals 07:00–11:45 | +0.008 / 1.01 | +0.125 / 1.22 | −0.398 / 0.49 | −0.140 / 0.79 |
| V6 New York only | signals 12:00–15:45 | −0.220 / 0.66 (112) | +0.450 / 2.07 (39) | +0.530 / 2.20 (48) | +0.494 / 2.14 (87), CI [+0.248, +0.749] |
| V7 min R:R 1.5 | fewer, larger targets | −0.059 / 0.91 | +0.275 / 1.47 | +0.002 / 1.00 | +0.112 / 1.18 |
| V8 no re-arming | single entry level per touch | −0.078 / 0.87 | +0.181 / 1.35 | −0.033 / 0.95 | +0.075 / 1.13 |
| V9 target-first ambiguity | opposite same-minute convention | identical to V0 | identical | identical | identical (0 ambiguous minutes) |
| V10 approximate news filter | NFP first-Friday + unverified FOMC list | identical to V0 | identical | identical | identical (only 4 signals fell in windows) |

Reading the table: cost sensitivity is large (stress costs erase the out-of-sample edge); the ADX threshold does not rescue the system; the New York-only window is the only variant positive in every out-of-sample period, but it was **negative in development** (mean −0.220 R), it was chosen from ten variants after seeing results, and its 87 out-of-sample trades are few. It is recorded as the leading proposal for v1.1 and nothing more.

## 6. Verdict against the pre-registered rule

SUPPORTED FOR DEMO required all of: ≥ 60 trades in each held-out period (met: 107 and 116); mean R > 0 in both (not met: final test −0.046); PF > 1.10 in both (not met: 0.93); 90 % bootstrap CI for mean R on validation + test excluding zero (not met: [−0.070, +0.227]); positive mean R after removing the 5 best trades (not met: +0.002, effectively zero).
REJECTED required mean R ≤ 0 out of sample with CI upper bound < +0.10 R (not met: mean +0.076, upper bound +0.227), or stress-cost mean R < −0.10 R in both held-out periods (not met: +0.079 and −0.112).
Therefore **INCONCLUSIVE**. Historical support for live profitability has **not** been shown. Nothing here is a claim that the system makes money.

## 7. Statistical uncertainty and caveats

- Bootstrap intervals resample trades independently; intraday gold trades cluster in volatile days, so true uncertainty is wider than shown.
- Ten variants were examined; with that many looks, one variant with a CI excluding zero is expected to appear by chance alone about half the time at the 90 % level.
- The simulator uses a constant spread. Spread widening at the London open, around US data and after the daily break would lower every number.
- Bid-only data: long-side fills are approximations.
- Fixed UTC windows ignore DST shifts of the London/New York sessions.
- On US holidays with early closes, the 20:50 UTC time exit cannot execute until the next bar (the feed resumes at 23:00 UTC); 17 time exits in total were affected at most.
- The development period is not a true "in-sample" since no tuning was done; it is reported for transparency and is itself negative.

## 8. Chart-reading audit (separate from the numerical backtest)

A fresh model instance classified 16 rendered M15 charts (future candles hidden; 8 valid setups, 8 near-misses) from the images alone. Results: armed 16/16, touch 15/16, direction 16/16, valid-setup 16/16; 0 missed setups, 0 false signals; median price-read error 0.08 USD (high) and 0.14 USD (low), maximum 1.02 USD. The one touch error was a wick within ~0.8 USD of the EMA on a wide y-axis. Conclusion: binary rule recognition is reliable on clean charts with an ADX panel; **price levels must be typed, not read from pixels**. Broker screenshots in varied styles have not been tested. Details: chart_audit/CHART_AUDIT_RESULTS.md.

## 9. What is needed to move from INCONCLUSIVE

1. **Broker data export** (highest value): from Aayan's MT5, export XAUUSD M1 bars for 2021-01-01 → today with columns date, time, open, high, low, close, tick volume, spread (MT5 "Export bars" from the Symbols window, or a script that writes `CopyRates` output); state the server timezone offset in winter and summer; add the symbol specification screenshot (contract size, digits, min/step volume, trading hours, swap, commission). Re-running `engine.py` on that file is the next validation step.
2. **Historical high-impact calendar** (dates/times of CPI, NFP, FOMC, PCE 2021–2026) to replace the approximate filter.
3. **Decision on v1.1 proposals** (PROJECT_STATE.md), to be evaluated only on data the proposals did not see, i.e. the broker feed and the forward test.

## 10. Files

- backtest/fetch_histdata.py, build_dataset.py, engine.py, validate_engine.py, analyze.py, make_audit_charts.py, score_chart_audit.py
- results/summary.md, results/summary.json, results/VALIDATION_MECHANICS.md, results/<variant>/{trades.csv, skips.csv, config.json}
- data/DATA_AUDIT.md (raw zips and the parquet are reproducible with the fetch/build scripts and are not committed)
- chart_audit/*.png, reader_answers.json, CHART_AUDIT_RESULTS.md
