# gold-research — XAUUSD intraday strategy research (Holy Grail v1.0)

Research and decision-support artefacts for Aayan's gold trading project. Nothing here places orders.

| Read this first | Purpose |
|---|---|
| PROJECT_STATE.md | current version, status, blockers, next action |
| GOLD_PLAYBOOK_v1.md | frozen rules with SOURCE / PROPOSED / UNRESOLVED tags |
| VALIDATION_REPORT.md | what was tested, results, verdict (INCONCLUSIVE), limitations |
| RESEARCH_SOURCES.md | six candidate methods, evidence labels, citations |
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
```

Raw zips and the parquet are not committed (see .gitignore); trade-level results are.

Data: HistData.com free M1 bid bars (EST without DST → converted to UTC). Not a broker feed; see data/DATA_AUDIT.md and VALIDATION_REPORT.md §2.
