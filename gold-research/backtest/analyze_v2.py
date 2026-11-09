#!/usr/bin/env python3
"""Metrics and pre-registered decision for GOLD_PLAYBOOK_v2_CANDIDATE.md variants (results/V2_*).
R is weighted by size_mult (what the account experiences); unweighted mean R is also reported.
Writes results/summary_v2.md and results/summary_v2.json. Decision rule: playbook v2 §11 (v1.0 §13 thresholds + must beat V0_base).
"""
import json, pathlib, numpy as np, pandas as pd
import analyze as A
HERE = pathlib.Path(__file__).resolve().parent; RES = HERE.parent / "results"
P = A.PERIODS

def load(v):
    t = pd.read_csv(RES / v / "trades.csv", parse_dates=["signal_bar_open", "entry_time", "exit_time"])
    for c in ["signal_bar_open", "entry_time", "exit_time"]:
        if t[c].dt.tz is None: t[c] = t[c].dt.tz_localize("UTC")
    if "realised_R_weighted" not in t: t["realised_R_weighted"] = t["realised_R"]; t["size_mult"] = 1.0; t["trig"] = "A"; t["bias"] = "both"
    t["period"] = "none"
    for name, (a, b) in P.items():
        m = (t.signal_bar_open >= pd.Timestamp(a, tz="UTC")) & (t.signal_bar_open < pd.Timestamp(b, tz="UTC")); t.loc[m, "period"] = name
    t["year"] = t.signal_bar_open.dt.year
    return t

def met(t, a=None, b=None):
    w = t.copy(); w["realised_R_unw"] = w["realised_R"]; w["realised_R"] = w["realised_R_weighted"]
    m = A.metrics(w, a, b)
    if m.get("n"): m["mean_R_unweighted"] = float(w.realised_R_unw.mean())
    return m

def row(label, m):
    if not m.get("n"): return f"| {label} | 0 | – | – | – | – | – | – | – | – | – |"
    ci = m["boot_ci90"]; pf = "inf" if m["profit_factor"] == float("inf") else f"{m['profit_factor']:.2f}"
    return (f"| {label} | {m['n']} | {m['total_R']:+.1f} | {m['mean_R']:+.3f} | {m.get('mean_R_unweighted', m['mean_R']):+.3f} | [{ci[0]:+.3f}, {ci[1]:+.3f}] | "
            f"{m['win_rate']*100:.1f}% | {pf} | {m['max_drawdown_R']:.1f} | {m['longest_losing_streak']} | {m['median_hold_min']:.0f} |")
HDR = ["| period | trades | total R (weighted) | mean R (weighted) | mean R (unweighted) | 90% CI mean R | win rate | PF | max DD (R) | longest losing streak | median hold (min) |", "|---|---|---|---|---|---|---|---|---|---|---|"]

def main():
    import engine_v2 as V2
    variants = ["V0_base"] + [v for v in V2.VARIANTS if v != "V2_v1compat" and (RES / v / "trades.csv").exists()]
    out = {}; md = ["# Backtest results — GOLD_PLAYBOOK v2.0 CANDIDATE (pre-registered variants) vs v1.0 baseline", "",
                    "R = initial planned risk. Weighted R = R × size_mult (0.5 when the momentum vote disagrees with the SMA200 trend state). Costs per variant config.", "",
                    "**Coverage note:** the bias layer needs 200 (SMA) / 252 (momentum) session days of warm-up, so biased variants trade from about 2022-01; their development-period rows cover 2022-01 → 2024-06 while V0_base and V2_A cover 2021-01 → 2024-06.", ""]
    for v in variants:
        t = load(v); cfg = json.loads((RES / v / "config.json").read_text())
        res = {"periods": {}, "n": int(len(t)), "ambiguous_m1_bars": cfg.get("ambiguous_bars")}
        md += [f"## {v}", ""] + HDR
        for name, (a, b) in P.items():
            m = met(t[t.period == name], a, b); res["periods"][name] = m; md.append(row(f"{name} {a}→{b}", m))
        oos = t[t.period.isin(["validation", "final_test"])]
        m = met(oos, P["validation"][0], P["final_test"][1]); res["periods"]["validation+final_test"] = m; md.append(row("validation+final_test", m))
        m = met(t, P["development"][0], P["final_test"][1]); res["periods"]["all"] = m; md.append(row("all (reference)", m))
        md.append("")
        if v in ("V2_0", "V2_A_nobias"):
            md += [f"### {v} breakdowns (validation + final test)", ""]
            for col in ["trig", "bias", "size_mult", "session", "side", "exit_reason", "year"]:
                if col not in oos or oos[col].nunique() < 2 and col != "exit_reason": continue
                md += [f"**By {col}**", ""] + [HDR[0].replace("period", col), HDR[1]]
                for kk, g in oos.groupby(col): md.append(row(str(kk), met(g)))
                md.append("")
            sk = pd.read_csv(RES / v / "skips.csv") if (RES / v / "skips.csv").stat().st_size > 5 else pd.DataFrame()
            if len(sk):
                md += ["**Skipped / cancelled setups (all periods)**", "", "| reason | count |", "|---|---|"] + [f"| {k} | {n} |" for k, n in sk.reason.value_counts().items()] + [""]
                res["skips"] = sk.reason.value_counts().to_dict()
            if "t1_filled" in oos: res["t1_hit_share_oos"] = float(oos.t1_filled.mean())
        out[v] = res
    # ---- decision for V2_0 (playbook v2 §11): v1.0 §13 thresholds AND beat V0_base on OOS mean R and PF
    v2 = out["V2_0"]["periods"]; v0 = out["V0_base"]["periods"]
    val, tst, oos = v2["validation"], v2["final_test"], v2["validation+final_test"]; oos0 = v0["validation+final_test"]
    stress = out.get("V2_H_coststress", {}).get("periods", {})
    cond = dict(n_val_ge60=val.get("n", 0) >= 60, n_test_ge60=tst.get("n", 0) >= 60,
                meanR_pos_both=val.get("mean_R", 0) > 0 and tst.get("mean_R", 0) > 0,
                pf_gt_1_10_both=val.get("profit_factor", 0) > 1.10 and tst.get("profit_factor", 0) > 1.10,
                ci_excludes_zero=oos.get("boot_ci90", [0, 0])[0] > 0, ex_top5_pos=(oos.get("mean_R_ex_top5") or 0) > 0,
                beats_v1_meanR=oos.get("mean_R", 0) > oos0["mean_R"], beats_v1_pf=oos.get("profit_factor", 0) > oos0["profit_factor"])
    supported = all(cond.values())
    rejected = (oos.get("mean_R", 0) <= 0 and oos.get("boot_ci90", [0, 0])[1] < 0.10) or (bool(stress) and stress["validation"].get("mean_R", 0) < -0.10 and stress["final_test"].get("mean_R", 0) < -0.10)
    verdict = "SUPPORTED FOR DEMO" if supported else ("REJECTED" if rejected else "INCONCLUSIVE")
    out["verdict_V2_0"] = dict(verdict=verdict, conditions=cond, rejected_rule_met=bool(rejected))
    md = md[:5] + [f"**Pre-registered verdict for V2_0: {verdict}** (criteria: GOLD_PLAYBOOK_v2_CANDIDATE.md §11). Conditions: " + ", ".join(f"{k}={'yes' if v else 'no'}" for k, v in cond.items()) + ".", "",
                   "**Contamination disclosure:** the bias layer, min RR 1.5 and the exits were chosen after seeing v1.0's results on this same data; this run can reject layers but cannot support v2.0 (see playbook v2 §11).", ""] + md[5:]
    (RES / "summary_v2.md").write_text("\n".join(md)); (RES / "summary_v2.json").write_text(json.dumps(out, indent=2, default=str))
    print("\n".join(md[:40])); print("VERDICT V2_0:", verdict)

if __name__ == "__main__":
    main()
