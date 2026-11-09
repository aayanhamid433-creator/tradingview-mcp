# PROJECT_STATE — Gold trading research (Aayan)

Last updated: 2026-11-09 (UTC). Current strategy version: **v1.0** (frozen). Validation status: **INCONCLUSIVE** (not supported for demo, not rejected). Use status for any chart analysis: **UNVALIDATED DEMO**.

## Timeline of this session (for audit of ordering)
1. 00:11 UTC — tool check; market-data hosts blocked; environment allowlist created and approved; web research delegated to four agents.
2. 00:17 — HistData M1 download (2021-01 → 2026-10) and UTC dataset build; data audit written.
3. 00:26 — primary source for the Holy Grail (AIQ Opening Bell, Aug 1997) read in full; strategy selected on rule clarity / data / relevance / simplicity.
4. 00:30 — **GOLD_PLAYBOOK_v1.md frozen** (rules, parameters, costs, splits, verdict criteria, variant list).
5. 00:32 — engine written; mechanics validator found 27 stop-placement mismatches (intermediate-bar lows ignored); engine fixed; re-validated 477/477.
6. 00:33 — all 11 variants run; analysis produced; verdict INCONCLUSIVE.
7. 00:35 — chart-reading audit (16 charts) run by a separate model instance and scored.
8. 00:40 — reports written; committed to branch `claude/quirky-lovelace-y41dkc`.

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

## Blockers / missing inputs (one list)
1. Broker and symbol confirmation (MT5 server timezone, XAUUSD spec screenshot).
2. Broker M1 export 2021 → today with spread column (see VALIDATION_REPORT.md §9 for the exact request).
3. Historical high-impact news calendar 2021–2026 (CPI, NFP, FOMC, PCE dates and times).
4. For sizing: equity, currency, risk budget per trade, existing exposure.
5. For prop compliance: firm, account type, current official rules, headroom, reset timezone.

## Proposed changes (NOT yet evaluated — do not trade)
| id | proposal | reason | how it will be tested |
|---|---|---|---|
| P1 | restrict signals to 12:00–15:45 UTC (New York morning) | V6 was the only variant positive in both held-out periods (+0.494 R mean, 87 trades) but negative in development and selected after the fact | evaluate as v1.1 only on broker data and the forward test, never on the same HistData periods |
| P2 | raise minimum reward/risk to 1.5 | V7 slightly better and fewer trades; not significant | same as P1 |
| P3 | replace constant spread with time-of-day spread from broker data | realism | after broker export |
| P4 | add DST-aware session windows | London/New York local times shift by one hour for part of the year | after broker export |

## Exact next action
Export XAUUSD M1 (with spread) from the MT5 terminal you will trade, note the server's UTC offset in winter and summer, and send it with the symbol-specification screenshot. The next step is then: `python3 backtest/engine.py --all --data <your_file.parquet>` after converting the export with a small loader (to be added when the format is known), followed by a fresh verdict under the same pre-registered rule.

## Working rules carried forward
- Chart responses use the fixed block from the master prompt; USE STATUS = UNVALIDATED DEMO until this file says otherwise.
- Levels come from typed numbers in CHART_SUBMISSION_TEMPLATE.md; pixel reads are approximate.
- No lot sizes and no compliance statements without the §11 inputs.
- Every chart analysis is logged automatically to journal/GOLD_TRADE_JOURNAL.csv (one row per screenshot, WAIT included, setup_id GOLD-YYYYMMDD-NNNN) and pushed directly to main, no branch or PR; no analysis without a journal row (rule set by Aayan, 2026-11-09).
