#!/usr/bin/env python3
"""Compute pre-registered metrics for every variant in ../results and write summary.md / summary.json.
Periods (GOLD_PLAYBOOK_v1.md §13): development 2021-01-04..2024-06-30, validation 2024-07-01..2025-08-31, final test 2025-09-01..2026-10-30.
"""
import json, pathlib, numpy as np, pandas as pd
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE.parent / "results"
PERIODS = {"development": ("2021-01-04", "2024-07-01"), "validation": ("2024-07-01", "2025-09-01"), "final_test": ("2025-09-01", "2026-11-01")}
SESSION_HOURS_PER_DAY = (20*60+50 - 7*60) / 60.0
rng = np.random.default_rng(20261109)

def load(variant):
    p = RES / variant / "trades.csv"
    t = pd.read_csv(p, parse_dates=["signal_bar_open", "entry_time", "exit_time"])
    for c in ["signal_bar_open", "entry_time", "exit_time"]:
        if t[c].dt.tz is None: t[c] = t[c].dt.tz_localize("UTC")
    t["period"] = "none"
    for name, (a, b) in PERIODS.items():
        m = (t.signal_bar_open >= pd.Timestamp(a, tz="UTC")) & (t.signal_bar_open < pd.Timestamp(b, tz="UTC"))
        t.loc[m, "period"] = name
    t["year"] = t.signal_bar_open.dt.year
    return t

def metrics(t: pd.DataFrame, start=None, end=None):
    r = t.realised_R.values
    n = len(r)
    if n == 0: return dict(n=0)
    wins = r[r > 0]; losses = r[r <= 0]
    cum = np.cumsum(r); peak = np.maximum.accumulate(cum); dd = cum - peak
    mdd = float(dd.min()) if n else 0.0
    # drawdown duration: longest stretch (in trades and days) below a prior peak
    longest, cur, start_i, dd_days = 0, 0, None, 0
    for k in range(n):
        if dd[k] < 0:
            cur += 1; start_i = start_i if start_i is not None else k
        else:
            if cur > longest:
                longest = cur; dd_days = (t.exit_time.iloc[k] - t.entry_time.iloc[start_i]).total_seconds() / 86400
            cur, start_i = 0, None
    if cur > longest:
        longest = cur; dd_days = (t.exit_time.iloc[-1] - t.entry_time.iloc[start_i]).total_seconds() / 86400
    streak = best = 0
    for x in r:
        streak = streak + 1 if x <= 0 else 0; best = max(best, streak)
    days = ((pd.Timestamp(end, tz="UTC") - pd.Timestamp(start, tz="UTC")).days * 5 / 7) if start else t.signal_bar_open.dt.date.nunique()
    exposure = t.hold_minutes.sum() / 60 / (days * SESSION_HOURS_PER_DAY) if days else np.nan
    top5 = np.sort(r)[-5:].sum() if n >= 5 else r.sum()
    boot = rng.choice(r, size=(10000, n), replace=True).mean(axis=1) if n >= 10 else np.array([np.nan])
    return dict(n=n, total_R=float(r.sum()), mean_R=float(r.mean()), median_R=float(np.median(r)),
                win_rate=float((r > 0).mean()), avg_win_R=float(wins.mean()) if len(wins) else 0.0,
                avg_loss_R=float(losses.mean()) if len(losses) else 0.0,
                profit_factor=float(wins.sum() / abs(losses.sum())) if len(losses) and losses.sum() != 0 else float("inf"),
                max_drawdown_R=mdd, longest_dd_trades=int(longest), longest_dd_days=float(dd_days), longest_losing_streak=int(best),
                exposure_share=float(exposure), median_hold_min=float(t.hold_minutes.median()), mean_hold_min=float(t.hold_minutes.mean()),
                top5_R=float(top5), mean_R_ex_top5=float(np.sort(r)[:-5].mean()) if n > 5 else np.nan,
                boot_ci90=[float(np.nanpercentile(boot, 5)), float(np.nanpercentile(boot, 95))],
                exits=t.exit_reason.value_counts().to_dict())

def fmt(m):
    if m.get("n", 0) == 0: return "| 0 | – | – | – | – | – | – | – | – | – |"
    ci = m["boot_ci90"]
    pf = "inf" if m["profit_factor"] == float("inf") else f"{m['profit_factor']:.2f}"
    return (f"| {m['n']} | {m['total_R']:+.1f} | {m['mean_R']:+.3f} | [{ci[0]:+.3f}, {ci[1]:+.3f}] | {m['win_rate']*100:.1f}% | "
            f"{m['avg_win_R']:+.2f} / {m['avg_loss_R']:+.2f} | {pf} | {m['max_drawdown_R']:.1f} | {m['longest_losing_streak']} | {m['median_hold_min']:.0f} |")

HDR = "| trades | total R | mean R (expectancy) | 90% bootstrap CI of mean R | win rate | avg win / avg loss (R) | profit factor | max DD (R) | longest losing streak | median hold (min) |\n|---|---|---|---|---|---|---|---|---|---|"

def main():
    variants = sorted([p.name for p in RES.iterdir() if (p / "trades.csv").exists()], key=lambda s: int(s.split("_")[0][1:]))
    out = {}; md = ["# Backtest results — GOLD_PLAYBOOK v1.0 (all pre-registered variants)", "",
                    "R = planned risk from the entry stop level to the initial stop-loss. Realised R includes spread, slippage and commission per the variant's cost model.", ""]
    for v in variants:
        t = load(v); cfg = json.loads((RES / v / "config.json").read_text())
        skips = pd.read_csv(RES / v / "skips.csv") if (RES / v / "skips.csv").stat().st_size > 5 else pd.DataFrame()
        res = {"config": cfg["config"], "ambiguous_m1_bars": cfg["ambiguous_bars"], "periods": {}}
        md += [f"## {v}", "", f"Config differences from base: `{json.dumps({k: cfg['config'][k] for k in cfg['config'] if k in __import__('engine').VARIANTS[v]})}`; ambiguous stop/target M1 bars: {cfg['ambiguous_bars']}", "",
               "| period | dates |" + HDR[1:], ]
        md[-1] = "| period | dates " + HDR.split("\n")[0] + "\n" + "|---|---" + HDR.split("\n")[1]
        for name, (a, b) in PERIODS.items():
            m = metrics(t[t.period == name], a, b); res["periods"][name] = m
            md.append(f"| {name} | {a} → {b} " + fmt(m))
        oos = t[t.period.isin(["validation", "final_test"])]
        m = metrics(oos, PERIODS["validation"][0], PERIODS["final_test"][1]); res["periods"]["validation+final_test"] = m
        md.append(f"| validation+final_test | {PERIODS['validation'][0]} → {PERIODS['final_test'][1]} " + fmt(m))
        m = metrics(t, PERIODS["development"][0], PERIODS["final_test"][1]); res["periods"]["all"] = m
        md.append(f"| all (for reference only) | {PERIODS['development'][0]} → {PERIODS['final_test'][1]} " + fmt(m))
        md.append("")
        if v == "V0_base":
            # breakdowns on out-of-sample
            md += ["### V0 breakdowns (validation + final test combined, out-of-sample)", ""]
            for col in ["session", "side", "year", "exit_reason"]:
                md += [f"**By {col}**", "", "| " + col + " " + HDR.split("\n")[0], "|---" + HDR.split("\n")[1]]
                for k, g in oos.groupby(col):
                    md.append(f"| {k} " + fmt(metrics(g)))
                md.append("")
            md += ["**By year (all periods, for reference)**", "", "| year " + HDR.split("\n")[0], "|---" + HDR.split("\n")[1]]
            for k, g in t.groupby("year"): md.append(f"| {k} " + fmt(metrics(g)))
            md.append("")
            md += ["**Top-5 dependence (validation + final test)**", "",
                   f"- Total R: {m_oos['total_R']:+.1f}; R from the 5 best trades: {m_oos['top5_R']:+.1f}; mean R excluding the 5 best: {m_oos['mean_R_ex_top5']:+.3f}" if (m_oos := res['periods']['validation+final_test']).get('n') else "- n/a", ""]
            md += ["**Exposure and holding (out-of-sample)**", "", f"- Share of session hours with an open position: {m_oos['exposure_share']*100:.1f}%; median hold {m_oos['median_hold_min']:.0f} min; mean hold {m_oos['mean_hold_min']:.0f} min", ""]
            if len(skips):
                md += ["**Skipped / cancelled setups (all periods)**", "", "| reason | count |", "|---|---|"]
                md += [f"| {k} | {n} |" for k, n in skips.reason.value_counts().items()]
                md.append("")
            res["skips"] = skips.reason.value_counts().to_dict() if len(skips) else {}
        out[v] = res
    # pre-registered decision for V0
    v0 = out["V0_base"]["periods"]; val, tst, oos = v0["validation"], v0["final_test"], v0["validation+final_test"]
    stress = out.get("V1_cost_stress", {}).get("periods", {})
    supported = (val.get("n", 0) >= 60 and tst.get("n", 0) >= 60 and val["mean_R"] > 0 and tst["mean_R"] > 0 and val["profit_factor"] > 1.10 and tst["profit_factor"] > 1.10
                 and oos["boot_ci90"][0] > 0 and oos["mean_R_ex_top5"] > 0)
    rejected = (oos["mean_R"] <= 0 and oos["boot_ci90"][1] < 0.10) or (stress and stress["validation"].get("mean_R", 0) < -0.10 and stress["final_test"].get("mean_R", 0) < -0.10)
    verdict = "SUPPORTED FOR DEMO" if supported else ("REJECTED" if rejected else "INCONCLUSIVE")
    out["verdict"] = dict(verdict=verdict, supported_rule_met=supported, rejected_rule_met=bool(rejected))
    md = md[:3] + [f"**Pre-registered verdict for V0_base: {verdict}** (criteria in GOLD_PLAYBOOK_v1.md §13).", ""] + md[3:]
    (RES / "summary.md").write_text("\n".join(md)); (RES / "summary.json").write_text(json.dumps(out, indent=2, default=str))
    print("\n".join(md[:60])); print("VERDICT:", verdict)

if __name__ == "__main__":
    main()
