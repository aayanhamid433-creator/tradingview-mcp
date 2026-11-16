#!/usr/bin/env python3
"""Metrics for the ALT candidate (Gold Breakout 15M re-implementation) using the same metric code as analyze.py.
Adds: the screenshot window (2026-08-02 .. 2026-10-30, the last date in our data), yearly breakdown, side breakdown,
and a compounded-equity figure at 1% risk per trade (product of 1 + 0.01*R)."""
import json, pathlib, numpy as np, pandas as pd
import analyze as A
HERE = pathlib.Path(__file__).resolve().parent; RES = HERE.parent / "results_alt_gold_bo"
WINDOWS = dict(A.PERIODS); WINDOWS["screenshot_window_2026-08-02_to_2026-10-30"] = ("2026-08-02", "2026-10-31")
WINDOWS["all_2021-2026"] = ("2021-01-04", "2026-11-01")
def load(v):
    t = pd.read_csv(RES / v / "trades.csv", parse_dates=["entry_time", "exit_time", "signal_bar_open"])
    for c in ["entry_time", "exit_time", "signal_bar_open"]:
        if t[c].dt.tz is None: t[c] = t[c].dt.tz_localize("UTC")
    t["year"] = t.entry_time.dt.year; return t
def sel(t, a, b): return t[(t.entry_time >= pd.Timestamp(a, tz="UTC")) & (t.entry_time < pd.Timestamp(b, tz="UTC"))]
def fmt(m):
    if m.get("n", 0) == 0: return "| 0 | – | – | – | – | – | – | – | – |"
    ci = m["boot_ci90"]; comp = m.get("compounded", float("nan"))
    return (f"| {m['n']} | {m['total_R']:+.1f} | {m['mean_R']:+.3f} | [{ci[0]:+.3f}, {ci[1]:+.3f}] | {m['win_rate']*100:.1f}% | {m['profit_factor']:.2f} | {m['max_drawdown_R']:.1f} | {m['longest_losing_streak']} | {comp:+.1f}% |")
HDR = "| trades | total R | mean R | 90% bootstrap CI | win rate | profit factor | max DD (R) | longest losing streak | compounded at 1% risk |\n|---|---|---|---|---|---|---|---|---|"
def met(t, a=None, b=None):
    m = A.metrics(t, a, b)
    if m.get("n"): m["compounded"] = float((np.prod(1 + 0.01 * t.realised_R.values) - 1) * 100)
    return m
md = ["# ALT candidate results — Gold Breakout 15M (WillyAlgoTrader) re-implemented on HistData M1 2021–2026 (clock-corrected: index converted from New York local stamps to true UTC)", "",
      "R = planned risk = 1% of the breakout level (SL 1% of entry). Costs per variant. Periods identical to GOLD_PLAYBOOK v1.0 §13. NOT a pre-registered test of our own: this candidate was selected after seeing the author's published result, so treat every number as descriptive.", ""]
out = {}
for v in sorted(p.name for p in RES.iterdir() if (p / "trades.csv").exists()):
    t = load(v); cfg = json.loads((RES / v / "config.json").read_text()); out[v] = {"config": cfg["config"], "periods": {}}
    md += [f"## {v}", "", f"`{json.dumps({k: cfg['config'][k] for k in ('clock','sl_mode','spread','slippage','commission_frac_rt','both_sides_rule')})}`; minutes crossing both boundaries: {cfg['both_sides_minutes']}", "",
           "| window | dates " + HDR.split("\n")[0], "|---|---" + HDR.split("\n")[1]]
    for name, (a, b) in WINDOWS.items():
        m = met(sel(t, a, b), a, b); out[v]["periods"][name] = m; md.append(f"| {name} | {a} → {b} " + fmt(m))
    md.append("")
    if v == "G1_base_costs":
        md += ["### G1 breakdowns", "", "**By year**", "", "| year " + HDR.split("\n")[0], "|---" + HDR.split("\n")[1]]
        for y, g in t.groupby("year"): md.append(f"| {y} " + fmt(met(g)))
        md += ["", "**By side (all years)**", "", "| side " + HDR.split("\n")[0], "|---" + HDR.split("\n")[1]]
        for s, g in t.groupby("side"): md.append(f"| {s} " + fmt(met(g)))
        md += ["", "**By exit reason (all years)**", "", "| exit " + HDR.split("\n")[0], "|---" + HDR.split("\n")[1]]
        for s, g in t.groupby("exit_reason"): md.append(f"| {s} " + fmt(met(g)))
        oos = sel(t, "2024-07-01", "2026-11-01"); mo = met(oos)
        md += ["", f"**Top-5 dependence (2024-07 → 2026-10):** total {mo['total_R']:+.1f} R, best 5 trades {mo['top5_R']:+.1f} R, mean R excluding best 5 {mo['mean_R_ex_top5']:+.3f}", ""]
(RES / "summary.md").write_text("\n".join(md)); (RES / "summary.json").write_text(json.dumps(out, indent=2, default=str))
print("\n".join(md))
