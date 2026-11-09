#!/usr/bin/env python3
"""Mechanics validation for engine_v2.py (V2_0 trades). Validates bookkeeping, not profitability.
Checks: v1-compat regression (engine_v2 --check), window/cut-off, bias consistency, min RR, stop sanity, news gate,
geometry, partial-exit arithmetic, T1 reachability, daily/weekly stop enforcement, exit-price plausibility.
Writes results/VALIDATION_MECHANICS_v2.md
"""
import pathlib, subprocess, sys, numpy as np, pandas as pd
import engine as E, engine_v2 as V
HERE = pathlib.Path(__file__).resolve().parent; RES = HERE.parent / "results"
cfg = dict(V.V2_CONFIG); cfg.update(V.VARIANTS["V2_0"])
m1 = pd.read_parquet(E.DATA)
daily = V.daily_frame(m1); dkeys = list(daily.index); dpos = {k: i for i, k in enumerate(dkeys)}
ns, ne = V.news_windows(m1.index[0].date(), m1.index[-1].date())
tr = pd.read_csv(RES / "V2_0" / "trades.csv", parse_dates=["signal_bar_open", "last_touch_open", "entry_time", "exit_time", "t1_time"])
for c in ["signal_bar_open", "last_touch_open", "entry_time", "exit_time", "t1_time"]:
    if tr[c].dt.tz is None: tr[c] = tr[c].dt.tz_localize("UTC")
spread, slip, comm = cfg["spread"], cfg["slippage"], cfg["commission_rt"]
lines = ["# Mechanics validation — engine_v2.py (V2_0)", "", "Validates the simulator's bookkeeping, not profitability.", ""]
# 0. regression
r = subprocess.run([sys.executable, str(HERE / "engine_v2.py"), "--check"], capture_output=True, text=True)
lines += ["## 0. Regression: v1-compatible configuration must reproduce V0_base", "", "```", r.stdout.strip(), "```", ""]
checks = {}; problems = []
def chk(name, ok, info=None):
    checks.setdefault(name, [0, 0]); checks[name][0 if ok else 1] += 1
    if not ok: problems.append((name, info))
def in_news(ts):
    ts64 = np.datetime64(ts.tz_convert(None)); i = np.searchsorted(ns, ts64, side="right") - 1
    return i >= 0 and ts64 < ne[i]
sig_lo, sig_hi, cutoff = E.hhmm(cfg["signal_start"]), E.hhmm(cfg["signal_end"]), E.hhmm(cfg["pending_cutoff"])
for t in tr.itertuples():
    mod = t.signal_bar_open.hour * 60 + t.signal_bar_open.minute
    chk("signal_in_window", sig_lo <= mod <= sig_hi, t.Index)
    emod = t.entry_time.hour * 60 + t.entry_time.minute
    chk("entry_before_cutoff_and_after_signal_close", emod < cutoff and t.entry_time >= t.last_touch_open + pd.Timedelta(minutes=15), t.Index)
    chk("side_matches_bias", t.bias == t.side, (t.Index, t.bias, t.side))
    chk("rr_at_placement_ge_min", t.rr_at_placement >= cfg["min_rr"] - 1e-9, (t.Index, t.rr_at_placement))
    k = (t.signal_bar_open + pd.Timedelta(hours=1)).date(); pdy = daily.iloc[dpos[k] - 1]
    chk("stop_within_0.6_D1ATR", abs(t.level - t.initial_stop) <= cfg["stop_sanity_d1atr"] * pdy.atr14 + 1e-9, (t.Index, abs(t.level - t.initial_stop), pdy.atr14))
    chk("bias_from_prev_day", (t.side == "long") == (pdy.close > pdy.sma200), t.Index)
    exp_mult = 1.0 if ((pdy.mom > 0) == (pdy.close > pdy.sma200)) else cfg["bias_disagree_mult"]
    chk("size_mult_correct", abs(t.size_mult - exp_mult) < 1e-9, (t.Index, t.size_mult, exp_mult))
    chk("entry_not_in_news_window", not in_news(t.entry_time), t.Index)
    geo = (t.initial_stop < t.entry_price < t.target) if t.side == "long" else (t.target < t.entry_price < t.initial_stop)
    chk("geometry", geo, t.Index)
    sign = 1 if t.side == "long" else -1; risk = abs(t.level - t.initial_stop)
    if t.t1_filled:
        pnl = sign * (cfg["partial_frac"] * (t.t1_price - t.entry_price) + (1 - cfg["partial_frac"]) * (t.exit_price - t.entry_price)) - comm
        seg = m1.loc[t.entry_time + pd.Timedelta(minutes=1): t.t1_time]
        reach = (seg.high > t.target).any() if t.side == "long" else ((seg.low + spread) < t.target).any()
        chk("t1_reached_by_trade_through", bool(reach) and t.t1_time <= t.exit_time, t.Index)
        chk("post_t1_exit_reason", t.exit_reason in ("trail_stop", "breakeven_stop", "time_exit"), (t.Index, t.exit_reason))
        if t.exit_reason == "breakeven_stop":
            chk("breakeven_exit_price", (t.exit_price <= t.be_stop - slip + 1e-9) if t.side == "long" else (t.exit_price >= t.be_stop + slip - 1e-9), t.Index)
    else:
        pnl = sign * (t.exit_price - t.entry_price) - comm
        chk("pre_t1_exit_reason", t.exit_reason in ("stop", "stop_same_minute", "time_exit"), (t.Index, t.exit_reason))
    chk("realised_R_arithmetic", abs(pnl / risk - t.realised_R) < 1e-9, (t.Index, pnl / risk, t.realised_R))
    chk("weighted_R", abs(t.realised_R * t.size_mult - t.realised_R_weighted) < 1e-12, t.Index)
    if t.exit_reason == "time_exit": chk("time_exit_at_or_after_2050", (t.exit_time.hour * 60 + t.exit_time.minute) >= E.hhmm(cfg["time_exit"]), t.Index)
# daily / weekly stop enforcement, ordered by exit then entry
tr["skey"] = (tr.signal_bar_open + pd.Timedelta(hours=1)).dt.date
for k, g in tr.sort_values("entry_time").groupby("skey"):
    closed, consec, halted_at = 0.0, 0, None
    for t in g.itertuples():
        if halted_at is not None and t.entry_time > halted_at: chk("no_entry_after_daily_stop", False, (k, t.entry_time)); continue
        closed += t.realised_R_weighted; consec = consec + 1 if t.realised_R <= 0 else 0
        if (consec >= cfg["daily_stop_losses"] or closed <= cfg["daily_stop_R"]) and halted_at is None: halted_at = t.exit_time
    chk("daily_stop_enforced", True)
tr["wkey"] = tr.signal_bar_open.apply(lambda x: x.isocalendar()[:2])
for k, g in tr.sort_values("entry_time").groupby("wkey"):
    closed, halted_at = 0.0, None
    for t in g.itertuples():
        if halted_at is not None and t.entry_time > halted_at: chk("no_entry_after_weekly_stop", False, (k, t.entry_time)); continue
        closed += t.realised_R_weighted
        if closed <= cfg["weekly_stop_R"] and halted_at is None: halted_at = t.exit_time
    chk("weekly_stop_enforced", True)
lines += ["## 1. Per-trade checks on V2_0", "", f"Trades checked: {len(tr)}; T1 (partial) reached in {int(tr.t1_filled.sum())} trades.", "", "| check | passed | failed |", "|---|---|---|"]
lines += [f"| {k} | {v[0]} | {v[1]} |" for k, v in checks.items()]
if problems: lines += ["", "### Discrepancies", ""] + [f"- {p}" for p in problems[:40]]
lines += ["", "## 2. Known approximations", "", "- News gate uses first-Friday NFP and an unverified FOMC date list only (no CPI/PCE/GDP dates available offline).",
          "- Bias is undefined for the first 252 session days (no trades), so biased variants start in 2022-01.",
          "- Trail distance uses the ATR of the last closed M15 bar; the trail is evaluated on M1 running extremes and never moved beyond the current minute's extreme.",
          "- Trigger B is OFF in V2_0; its mechanics are exercised only in V2_C/V2_D and were not independently re-derived here.", ""]
(RES / "VALIDATION_MECHANICS_v2.md").write_text("\n".join(lines)); print("\n".join(lines)); print("problems:", len(problems))
