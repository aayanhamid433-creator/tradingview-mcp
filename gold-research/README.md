# gold-research — XAUUSD intraday strategy research (Holy Grail v1.0)

Research and decision-support artefacts for Aayan's gold trading project. Nothing here places orders.

| Read this first | Purpose |
|---|---|
| PROJECT_STATE.md | current version, status, blockers, next action |
| GOLD_MARKET_PRIMER.md | plain-language guide to the gold market, its calendar, its drivers and this system's day |
| GOLD_PLAYBOOK_v1.md | frozen v1.0 rules with SOURCE / PROPOSED / UNRESOLVED tags (baseline) |
| GOLD_PLAYBOOK_v2_CANDIDATE.md | v2.0 candidate: layered combination of documented gold methods, UNTESTED, with pre-registered ablations |
| VALIDATION_REPORT.md | v1.0: what was tested, results, verdict (INCONCLUSIVE), limitations |
| VALIDATION_REPORT_v2.md | v2.0 candidate backtest: cross-variant table, layer decisions, verdict (INCONCLUSIVE), v2.1 proposal |
| RESEARCH_SOURCES.md | six candidate methods, evidence labels, citations |
| RESEARCH_SOURCES_v2_ADDENDUM.md | traders, quantitative evidence, intraday methods and risk rules behind v2.0 (raw notes in research_notes/) |
| results/DATA_FACTS.md | volatility by session/year, session drift, regime and gap statistics from the research data |
| CHART_SUBMISSION_TEMPLATE.md | what to send with screenshots |
| FORWARD_TEST_PROTOCOL.md | demo protocol (not started) |
| journal/GOLD_TRADE_JOURNAL.csv | journal schema |

## Reproduce the backtest

```bash
cd gold-research
pip install -r requirements.txt
python3 backtest/fetch_histdata.py --start 2021-01 --end 2026-10 --out data/raw   # ~25 MB from HistData.com
python3 backtest/build_dataset.py        # -> data/xauusd_m1_utc.parquet + data/DATA_AUDIT.md
python3 backtest/engine.py --all         # -> results/<variant>/trades.csv, skips.csv, config.json
python3 backtest/validate_engine.py      # -> results/VALIDATION_MECHANICS.md (simulator checks)
python3 backtest/analyze.py              # -> results/summary.md, summary.json (metrics + verdict)
python3 backtest/make_audit_charts.py && python3 backtest/score_chart_audit.py   # chart-reading audit
python3 backtest/data_facts.py           # -> results/DATA_FACTS.md (descriptive statistics)
python3 backtest/engine_v2.py --check    # regression: v1-compatible v2 engine must equal V0_base
python3 backtest/engine_v2.py --all      # -> results/V2_*/ (v2.0 candidate and ablations)
python3 backtest/validate_engine_v2.py   # -> results/VALIDATION_MECHANICS_v2.md
python3 backtest/analyze_v2.py           # -> results/summary_v2.md, summary_v2.json
```

Raw zips and the parquet are not committed (see .gitignore); trade-level results are.

Data: HistData.com free M1 bid bars (EST without DST → converted to UTC). Not a broker feed; see data/DATA_AUDIT.md and VALIDATION_REPORT.md §2.
