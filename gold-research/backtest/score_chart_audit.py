#!/usr/bin/env python3
"""Score the chart-reading audit: reader answers (from images only) vs the answer key (from data)."""
import json, pathlib, numpy as np
HERE = pathlib.Path(__file__).resolve().parent; CA = HERE.parent / "chart_audit"
key = {k["chart"]: k for k in json.load(open(CA / "ANSWER_KEY_do_not_show_reader.json"))}
ans = json.load(open(CA / "reader_answers.json"))
rows = []; conf = {"armed": [0, 0], "touch": [0, 0], "direction": [0, 0], "valid_setup": [0, 0]}
missed = false_sig = 0; errs = {"high": [], "low": [], "entry": [], "target": [], "adx": []}
for a in ans:
    k = key[a["chart"]]
    for f in conf:
        ok = a[f] == k[f]; conf[f][0 if ok else 1] += 1
    if k["valid_setup"] and not a["valid_setup"]: missed += 1
    if a["valid_setup"] and not k["valid_setup"]: false_sig += 1
    errs["adx"].append(abs(a["adx_estimate"] - k["adx"]))
    if a["last_bar_high_estimate"] is not None: errs["high"].append(abs(a["last_bar_high_estimate"] - k["high"]))
    if a["last_bar_low_estimate"] is not None: errs["low"].append(abs(a["last_bar_low_estimate"] - k["low"]))
    if a["valid_setup"] and k["valid_setup"]:
        errs["entry"].append(abs(a["entry_level_estimate"] - k["entry_level"])); errs["target"].append(abs(a["target_estimate"] - k["target"]))
    rows.append(f"| {a['chart']} | {k['kind']} | {k['valid_setup']} / {a['valid_setup']} | {k['armed']} / {a['armed']} | {k['touch']} / {a['touch']} | {k['direction']} / {a['direction']} | {k['adx']} / {a['adx_estimate']} | {k['high']} / {a['last_bar_high_estimate']} | {k['low']} / {a['last_bar_low_estimate']} | {a['confidence']} |")
n = len(ans)
md = ["# Chart-reading audit — v1.0 rule recognition from images with future candles hidden", "",
      f"16 M15 charts (60 bars each, EMA20 + ADX/DI panel) rendered from the research data at development-period timestamps: 8 valid setups, 4 near-misses with ADX below 30, 4 near-misses with no EMA touch. A fresh model instance read only the PNGs (no data access) and answered a fixed questionnaire. Scored against the data-derived key.", "",
      "| field | correct | wrong |", "|---|---|---|"] + [f"| {f} | {c[0]} | {c[1]} |" for f, c in conf.items()] + ["",
      f"- Missed setups (key valid, reader said no): **{missed}**", f"- False signals (reader valid, key no): **{false_sig}**", "",
      "| quantity | n | median abs error (USD) | max abs error (USD) |", "|---|---|---|---|"] + \
     [f"| {q} | {len(v)} | {np.median(v):.2f} | {np.max(v):.2f} |" for q, v in errs.items() if v] + ["",
      "## Per chart (key / reader)", "", "| chart | kind | valid | armed | touch | direction | ADX | last high | last low | reader confidence |", "|---|---|---|---|---|---|---|---|---|---|"] + rows + ["",
      "## Interpretation", "",
      "- Classification from a clean, indicator-labelled chart is reliable for the binary rules when the case is clear-cut; errors cluster where ADX sits at the 30 line or a wick barely grazes the EMA (the reader flagged these as low confidence).",
      "- Price reads from pixels carry errors of the order of tenths of a dollar to over a dollar depending on the y-axis scale. Entry/stop/target levels must therefore come from **typed numbers** in the submission template, not from reading a screenshot; the playbook's 0.10 USD entry offset is smaller than typical read error.",
      "- Sample is 16 charts rendered by us, not broker screenshots with varying styles; broker charts without an ADX panel or with a forming candle visible would be harder. This audit is a baseline, not a validation of screenshot trading."]
(CA / "CHART_AUDIT_RESULTS.md").write_text("\n".join(md)); print("\n".join(md))
