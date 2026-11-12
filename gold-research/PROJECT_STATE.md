# PROJECT_STATE — Gold trading research (Aayan)

Last updated: 2026-11-09 (UTC). Current strategy version: **v1.0** (frozen, baseline). Candidate: **v2.0 CANDIDATE** (GOLD_PLAYBOOK_v2_CANDIDATE.md). Validation status: v1.0 **INCONCLUSIVE**; v2.0 backtest on HistData **INCONCLUSIVE** (VALIDATION_REPORT_v2.md; contaminated by design, can only reject layers: Trigger B, momentum vote and the widened window are rejected). Use status for any chart analysis: **UNVALIDATED DEMO**.

## Timeline of this session (for audit of ordering)
1. 00:11 UTC — tool check; market-data hosts blocked; environment allowlist created and approved; web research delegated to four agents.
2. 00:17 — HistData M1 download (2021-01 → 2026-10) and UTC dataset build; data audit written.
3. 00:26 — primary source for the Holy Grail (AIQ Opening Bell, Aug 1997) read in full; strategy selected on rule clarity / data / relevance / simplicity.
4. 00:30 — **GOLD_PLAYBOOK_v1.md frozen** (rules, parameters, costs, splits, verdict criteria, variant list).
5. 00:32 — engine written; mechanics validator found 27 stop-placement mismatches (intermediate-bar lows ignored); engine fixed; re-validated 477/477.
6. 00:33 — all 11 variants run; analysis produced; verdict INCONCLUSIVE.
7. 00:35 — chart-reading audit (16 charts) run by a separate model instance and scored.
8. 00:40 — reports written; committed to branch `claude/quirky-lovelace-y41dkc` (merged to main as PR #1).
9. 04:20–06:40 — second research pass (four agents: macro traders, quantitative evidence, intraday retail methods, risk rules; interrupted once by a usage limit); results/DATA_FACTS.md computed; **GOLD_PLAYBOOK_v2_CANDIDATE.md written** with pre-registered ablation variants; RESEARCH_SOURCES_v2_ADDENDUM.md and research_notes/ added (PR #3).
10. 17:00–17:30 — engine_v2.py written and regression-checked (v1-compat = V0_base exactly); all V2 variants run; mechanics validated (116/116, 0 problems); VALIDATION_REPORT_v2.md: **INCONCLUSIVE**; Trigger B, momentum vote and the 16:45 window rejected.

## Completed work and files (all under `gold-research/`)
| Deliverable | File | Status |
|---|---|---|
| 1 Research sources | RESEARCH_SOURCES.md | complete; most citations snippet-level (hosts blocked), Holy Grail primary text read in full |
| 2 Playbook | GOLD_PLAYBOOK_v1.md | complete, frozen |
| 3 Validation report | VALIDATION_REPORT.md | complete for this data; NOT RUN items listed inside |
| 4 Backtest implementation | backtest/*.py, README.md (run instructions), results/ | complete and reproducible |
| 5 Trade journal | journal/GOLD_TRADE_JOURNAL.csv | schema + one TEMPLATE row (delete before use); no real entries yet |
| 6 Chart submission template | CHART_SUBMISSION_TEMPLATE.md | complete (template) |
| 7 Project state | this file | — |
| extra | FORWARD_TEST_PROTOCOL.md, data/DATA_AUDIT.md, results/VALIDATION_MECHANICS.md, chart_audit/CHART_AUDIT_RESULTS.md | complete |
| 8 v2.0 candidate | GOLD_PLAYBOOK_v2_CANDIDATE.md, RESEARCH_SOURCES_v2_ADDENDUM.md, research_notes/*.md, results/DATA_FACTS.md (backtest/data_facts.py) | written |
| 9 v2.0 backtest | backtest/engine_v2.py (+ analyze_v2.py, validate_engine_v2.py), results/V2_*/, results/summary_v2.md, VALIDATION_MECHANICS_v2.md, VALIDATION_REPORT_v2.md | run; 0 mechanics problems; v1-compat regression exact; verdict INCONCLUSIVE |

## Blockers / missing inputs (one list)
1. Broker and symbol confirmation (MT5 server timezone, XAUUSD spec screenshot).
2. Broker M1 export 2021 → today with spread column (see VALIDATION_REPORT.md §9 for the exact request).
3. Historical high-impact news calendar 2021–2026 (CPI, NFP, FOMC, PCE dates and times).
4. For sizing: ~~equity, currency~~ (50,000 USD account, 2026-11-12), risk budget per trade (playbook default 0.5 % = 250 USD unless Aayan sets otherwise), existing exposure (status of the 2026-11-10 short still unreported).
5. ~~For prop compliance: firm, account type, current official rules, headroom, reset timezone.~~ **Resolved 2026-11-12:** Atlas Funded 1-Step Access Funded 50k; rules and derived sizing in ACCOUNT_RULES.md (daily 3 % of 00:00 UTC equity, trailing 6 % of peak equity, Protector 2 % floating, news ±5 min, consistency 20 %). Still missing: broker M1 export with spread, symbol spec screenshot.

## Proposed changes (NOT yet evaluated — do not trade)
| id | proposal | reason | how it will be tested |
|---|---|---|---|
| P1 | restrict signals to 12:00–15:45 UTC (New York morning) | V6 was the only variant positive in both held-out periods (+0.494 R mean, 87 trades) but negative in development and selected after the fact | evaluate as v1.1 only on broker data and the forward test, never on the same HistData periods |
| P2 | raise minimum reward/risk to 1.5 | V7 slightly better and fewer trades; not significant | same as P1 |
| P3 | replace constant spread with time-of-day spread from broker data | realism | after broker export |
| P4 | add DST-aware session windows | London/New York local times shift by one hour for part of the year | after broker export |
| P6 | **v2.1** = v2.0 minus Trigger B, minus momentum vote, window 07:00–15:45 | on HistData this is V2_I-like: 55 OOS trades, +0.414 R, PF 1.93, max DD −7.7 R, CI [+0.030, +0.851]; but it is the third look at the same data and rests on 2025 runners | first clean test = broker export and the paper trade; never re-tuned on HistData |
| P5 | v2.0 CANDIDATE: L1 daily bias (SMA200 + 12-1 momentum), news gate, min RR 1.5, 50 % partial at T1 + 3×ATR Chandelier trail, 0.5 % risk with Turtle drawdown scaling, three-strike / −2 R daily / −4 R weekly stops, Trigger B breakout OFF | Aayan asked for the documented gold methods to be combined; each element is a switchable layer with its own evidence label | pre-registered variants V2-A…V2-I in GOLD_PLAYBOOK_v2_CANDIDATE.md §11; paper trade per §12; recommended engine extension per §13 (HistData result is contaminated for P1/P2/bias and can only reject layers) |

## Exact next action
**For v2.0/v2.1:** backtest done (see VALIDATION_REPORT_v2.md). Next: start the paper trade of **v2.1** (P6) per FORWARD_TEST_PROTOCOL.md + GOLD_PLAYBOOK_v2_CANDIDATE.md §12 on the broker you will trade, logging layer tokens in every journal row.

**For v1.0 (unchanged):** Export XAUUSD M1 (with spread) from the MT5 terminal you will trade, note the server's UTC offset in winter and summer, and send it with the symbol-specification screenshot. The next step is then: `python3 backtest/engine.py --all --data <your_file.parquet>` after converting the export with a small loader (to be added when the format is known), followed by a fresh verdict under the same pre-registered rule.

## Working rules carried forward
- Chart responses use the fixed block from the master prompt; USE STATUS = UNVALIDATED DEMO until this file says otherwise.
- Levels come from typed numbers in CHART_SUBMISSION_TEMPLATE.md; pixel reads are approximate.
- No lot sizes and no compliance statements without the §11 inputs.
- **Bias must be computed, never inferred (correction 2026-11-10 17:30 UTC).** Journal rows GOLD-20261109-0001/0004 and GOLD-20261110-0001/0002 state or imply a LONG daily bias "inferred, not typed". That was wrong: on the research data the 200-day SMA was ≈ 4,490 at 2026-10-30 (≈ 4,455 projected to 2026-11-10) with price ≈ 4,020, i.e. ~10 % below; the 2026 high close was 5,414 (2026-01-28). The correct v2.1 bias on 2026-11-09/10 is **SHORT**. Rows are left unedited per the journal rule; this note is the correction. From now on the bias line in every analysis must cite the SMA200 value from data (results/DATA_FACTS.md method or a typed value from the chart).
- Every chart analysis is logged automatically to journal/GOLD_TRADE_JOURNAL.csv (one row per screenshot, WAIT included, setup_id GOLD-YYYYMMDD-NNNN) and pushed directly to main, no branch or PR; no analysis without a journal row (rule set by Aayan, 2026-11-09).
