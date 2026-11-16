#!/usr/bin/env python3
"""Metrics and pre-registered decision for the engine_v3.py strategy families (results/V3_*).
Reuses analyze.metrics (mean R, PF, max DD in R, 90 % bootstrap CI, win rate, median hold) and analyze.PERIODS.
Adds trades per month. Writes results/summary_v3.md and results/summary_v3.json.

Decision rule (pre-registered in the brief, 2026-11-12): a variant PASSES if
  mean R > 0 AND PF > 1.10 in BOTH validation and final test; n >= 60 in each; max DD <= 10 R in every period
  (development, validation, final test); AND better per-trade AND total R than v2.2 (V2_K_confirm) in both periods
  (validation 17 trades, +0.978 R, total +16.6 R, PF 3.01; final test 26 trades, +0.191 R, total +5.0 R, PF 1.49).
"""
import json, pathlib, numpy as np, pandas as pd
import analyze as A, engine_v3 as V3
HERE = pathlib.Path(__file__).resolve().parent; RES = HERE.parent / "results"
P = A.PERIODS
V22 = {"validation": dict(n=17, mean_R=0.978, total_R=16.6, profit_factor=3.01), "final_test": dict(n=26, mean_R=0.191, total_R=5.0, profit_factor=1.49), "max_dd": -7.1}

def months(a, b): return (pd.Timestamp(b) - pd.Timestamp(a)).days / 30.4375

def load(v):
    t = pd.read_csv(RES / v / "trades.csv", parse_dates=["signal_time", "signal_bar_open", "entry_time", "exit_time"])
    for c in ["signal_time", "signal_bar_open", "entry_time", "exit_time"]:
        if t[c].dt.tz is None: t[c] = t[c].dt.tz_localize("UTC")
    t["period"] = "none"
    for name, (a, b) in P.items():
        m = (t.signal_bar_open >= pd.Timestamp(a, tz="UTC")) & (t.signal_bar_open < pd.Timestamp(b, tz="UTC")); t.loc[m, "period"] = name
    return t

def met(t, a, b):
    m = A.metrics(t, a, b)
    m["trades_per_month"] = m.get("n", 0) / months(a, b)
    if m.get("n"):
        m["first_trade"] = str(t.signal_time.min().date()); m["last_trade"] = str(t.signal_time.max().date())
    return m

HDR = ["| period | trades | trades/month | mean R | 90% CI mean R | win rate | PF | total R | max DD (R) | longest losing streak | median hold (min) |",
       "|---|---|---|---|---|---|---|---|---|---|---|"]
def row(label, m):
    if not m.get("n"): return f"| {label} | 0 | 0.0 | – | – | – | – | – | – | – | – |"
    ci = m["boot_ci90"]; pf = "inf" if m["profit_factor"] == float("inf") else f"{m['profit_factor']:.2f}"
    return (f"| {label} | {m['n']} | {m['trades_per_month']:.1f} | {m['mean_R']:+.3f} | [{ci[0]:+.3f}, {ci[1]:+.3f}] | {m['win_rate']*100:.1f}% | {pf} | "
            f"{m['total_R']:+.1f} | {m['max_drawdown_R']:.1f} | {m['longest_losing_streak']} | {m['median_hold_min']:.0f} |")

def decide(per):
    val, tst, dev = per["validation"], per["final_test"], per["development"]
    g = lambda m, k, d=0.0: m.get(k, d) if m.get("n") else d
    cond = dict(
        n_val_ge60=g(val, "n", 0) >= 60, n_test_ge60=g(tst, "n", 0) >= 60,
        meanR_pos_both=g(val, "mean_R") > 0 and g(tst, "mean_R") > 0,
        pf_gt_1_10_both=g(val, "profit_factor") > 1.10 and g(tst, "profit_factor") > 1.10,
        maxDD_le_10R_all_periods=all(g(m, "max_drawdown_R", 0) >= -10.0 for m in (dev, val, tst)),
        beats_v22_meanR_both=g(val, "mean_R") > V22["validation"]["mean_R"] and g(tst, "mean_R") > V22["final_test"]["mean_R"],
        beats_v22_totalR_both=g(val, "total_R") > V22["validation"]["total_R"] and g(tst, "total_R") > V22["final_test"]["total_R"],
    )
    return dict(passes=all(cond.values()), conditions=cond,
                oos_positive_both=cond["meanR_pos_both"] and cond["pf_gt_1_10_both"])

def main():
    variants = [v for v in V3.VARIANTS if (RES / v / "trades.csv").exists()]
    out = {"decision_rule": "mean R > 0 and PF > 1.10 in both validation and final test; n >= 60 in each; max DD <= 10 R in every period; mean R and total R above v2.2 (V2_K_confirm) in both periods", "v22_reference": V22, "variants": {}}
    md = ["# Backtest results — v3 alternative strategy families (pre-registered variants)", "",
          "R = planned risk (entry level to initial stop; for market orders, fill to initial stop). Realised R includes spread 0.25, slippage 0.05 per fill, commission 0. "
          "Periods by signal time: development 2021-01-04→2024-07-01 (41.9 months), validation 2024-07-01→2025-09-01 (14.0 months), final test 2025-09-01→2026-11-01 (14.0 months).", "",
          "Reference v2.2 (V2_K_confirm): validation 17 trades, +0.978 R/trade, +16.6 R, PF 3.01; final test 26 trades, +0.191 R, +5.0 R, PF 1.49; max DD −7.1 R.", ""]
    overview = ["## Overview (per variant: n / mean R / PF / max DD per period; verdict against the pre-registered rule)", "",
                "| variant | family | development n / mean R / PF / max DD | validation n / mean R / PF / max DD | final test n / mean R / PF / max DD | OOS trades/month | passes rule? | conditions failed |", "|---|---|---|---|---|---|---|---|"]
    sections = []
    for v in variants:
        t = load(v); cfg = json.loads((RES / v / "config.json").read_text())
        res = {"family": cfg["config"]["family"], "n": int(len(t)), "counters": cfg.get("counters"), "periods": {}}
        sec = [f"## {v} ({res['family']}; `{json.dumps(V3.VARIANTS[v])}`)", ""] + HDR
        for name, (a, b) in P.items():
            m = met(t[t.period == name], a, b); res["periods"][name] = m; sec.append(row(f"{name} {a}→{b}", m))
        oos = t[t.period.isin(["validation", "final_test"])]
        m = met(oos, P["validation"][0], P["final_test"][1]); res["periods"]["validation+final_test"] = m; sec.append(row("validation+final_test", m))
        m = met(t, P["development"][0], P["final_test"][1]); res["periods"]["all"] = m; sec.append(row("all (reference)", m))
        sec.append("")
        sec += ["Exit reasons (all periods): " + ", ".join(f"{k} {n}" for k, n in t.exit_reason.value_counts().items()), ""]
        if len(oos):
            sec += ["By side (validation + final test):", ""] + [HDR[0].replace("period", "side"), HDR[1]] + [row(s, met(g, P["validation"][0], P["final_test"][1])) for s, g in oos.groupby("side")] + [""]
        res["decision"] = decide(res["periods"]); out["variants"][v] = res
        def cell(m): return f"{m['n']} / {m['mean_R']:+.3f} / {('inf' if m['profit_factor'] == float('inf') else f'{m['profit_factor']:.2f}')} / {m['max_drawdown_R']:.1f}" if m.get("n") else "0 / – / – / –"
        pr = res["periods"]; failed = [k for k, ok in res["decision"]["conditions"].items() if not ok]
        overview.append(f"| {v} | {res['family']} | {cell(pr['development'])} | {cell(pr['validation'])} | {cell(pr['final_test'])} | {pr['validation+final_test']['trades_per_month']:.1f} | "
                        f"{'**YES**' if res['decision']['passes'] else 'no'} | {', '.join(failed) if failed else '–'} |")
        sections += sec
    # per-family verdicts
    fam_lines = ["## Verdict per family", "", "| family | variants | any passes the rule? | positive OOS (mean R > 0 and PF > 1.10 in both held-out periods) | notes |", "|---|---|---|---|---|"]
    fams = {}
    for v, r in out["variants"].items(): fams.setdefault(r["family"], []).append(v)
    out["families"] = {}
    for f, vs in fams.items():
        anyp = any(out["variants"][v]["decision"]["passes"] for v in vs)
        pos = [v for v in vs if out["variants"][v]["decision"]["oos_positive_both"]]
        out["families"][f] = dict(variants=vs, any_passes=anyp, oos_positive=pos)
        fam_lines.append(f"| {f} | {len(vs)} | {'YES' if anyp else 'no'} | {', '.join(pos) if pos else 'none'} | {'overnight holding; not account-compatible as is' if f == 'DC' else ''} |")
    # 15-minute hold twins
    h15 = ["## 15-minute maximum hold vs unconstrained twin (validation + final test)", "", "| twin | unconstrained n / mean R / PF / total R / max DD | h15 n / mean R / PF / total R / max DD | h15 exits |", "|---|---|---|---|"]
    for a, b in [("V3_ORB_L10", "V3_ORB_L10_h15"), ("V3_VB_03", "V3_VB_03_h15"), ("V3_VW_2s", "V3_VW_2s_h15")]:
        if a in out["variants"] and b in out["variants"]:
            ma, mb = out["variants"][a]["periods"]["validation+final_test"], out["variants"][b]["periods"]["validation+final_test"]
            f = lambda m: f"{m['n']} / {m['mean_R']:+.3f} / {m['profit_factor']:.2f} / {m['total_R']:+.1f} / {m['max_drawdown_R']:.1f}"
            tb = load(b); ex = tb[tb.period.isin(["validation", "final_test"])].exit_reason.value_counts().to_dict()
            h15.append(f"| {a} → {b} | {f(ma)} | {f(mb)} | {ex} |")
    md += overview + [""] + fam_lines + [""] + h15 + [""] + sections
    (RES / "summary_v3.md").write_text("\n".join(md)); (RES / "summary_v3.json").write_text(json.dumps(out, indent=2, default=str))
    print("\n".join(overview + [""] + fam_lines + [""] + h15))

if __name__ == "__main__":
    main()
