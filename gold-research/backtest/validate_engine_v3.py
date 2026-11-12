#!/usr/bin/env python3
"""Mechanics validation for engine_v3.py (all V3_* variants). Validates bookkeeping, not profitability.

1. Hand-check: prints, for one variant per family, two trades with the M1 bars around entry and exit so that the fill
   prices, stop/target levels and realised R can be verified by eye.
2. Automated per-trade checks (independent recomputation of levels from the raw M1 data and engine_v2.daily_frame):
   geometry, R arithmetic, entry level / stop / target construction per family, windows and cut-offs, one trade per
   session day (ORB/VB/DC) or max 2 (VW), stop/target reachability on the exit bar, exit-price rules, max-hold rule.
Writes results/VALIDATION_MECHANICS_v3.md
"""
import json, pathlib, sys, numpy as np, pandas as pd
import engine as E, engine_v2 as V2, engine_v3 as V3
HERE = pathlib.Path(__file__).resolve().parent; RES = HERE.parent / "results"
m1 = pd.read_parquet(E.DATA)
daily = V2.daily_frame(m1); dpos = {k: i for i, k in enumerate(daily.index)}
twap, sd = V3.session_twap(m1)
spread, slip, comm = V3.V3_CONFIG["spread"], V3.V3_CONFIG["slippage"], V3.V3_CONFIG["commission_rt"]
m1_t = m1.index.values
m1_day = (m1_t + np.timedelta64(1, "h")).astype("datetime64[D]")
m1_modarr = (m1.index.hour * 60 + m1.index.minute).values
m1_h, m1_l, m1_o = m1.high.values, m1.low.values, m1.open.values
def day_slice(day):
    d = np.datetime64(day); i0 = np.searchsorted(m1_day, d, side="left"); i1 = np.searchsorted(m1_day, d, side="right"); return i0, i1

def load(v):
    cols = ["signal_time", "signal_bar_open", "entry_time", "exit_time"]
    t = pd.read_csv(RES / v / "trades.csv", parse_dates=cols)
    for c in cols:
        if t[c].dt.tz is None: t[c] = t[c].dt.tz_localize("UTC")
    return t

def bars_around(t0, t1, before=2, after=2):
    i0 = m1.index.searchsorted(t0) - before; i1 = m1.index.searchsorted(t1) + after + 1
    return m1.iloc[max(0, i0):i1]

lines = ["# Mechanics validation — engine_v3.py (all V3_* variants)", "", "Validates the simulator's bookkeeping, not profitability. Prices in the data are BID; ask = bid + 0.25; slippage 0.05 on every stop/market fill.", ""]
# ---------------------------------------------------------------- 1. hand checks
lines += ["## 1. Hand-checked trades (M1 bars around entry and exit)", ""]
HAND = {"V3_ORB_L10": [0, "minR"], "V3_VB_03": [2, "minR"], "V3_VW_2s": [1, "minR"], "V3_DC_20_10": [3, "maxR"], "V3_VW_2s_h15": [0]}
for v, picks in HAND.items():
    t = load(v)
    for p in picks:
        idx = int(t.realised_R.idxmin()) if p == "minR" else int(t.realised_R.idxmax()) if p == "maxR" else p
        r = t.iloc[idx]
        keep = [c for c in ["side", "signal_time", "entry_time", "entry_price", "level", "initial_stop", "final_stop", "target", "exit_time", "exit_price", "exit_reason",
                            "planned_risk", "pnl_per_oz", "realised_R", "hold_minutes", "range_high", "range_low", "range", "d1atr", "k", "session_open", "bias", "vwap", "band_sd", "adx", "atr",
                            "dc_exit_long", "dc_exit_short", "stop_capped"] if c in t.columns and not (isinstance(r[c], float) and np.isnan(r[c]))]
        lines += [f"### {v} trade #{idx} ({'min R' if p == 'minR' else 'max R' if p == 'maxR' else 'row ' + str(p)})", "", "```", r[keep].to_string(), "", "M1 bars around entry:",
                  bars_around(r.entry_time, r.entry_time, 3, 2).to_string(), "", "M1 bars around exit:",
                  bars_around(r.exit_time - pd.Timedelta(minutes=1), r.exit_time - pd.Timedelta(minutes=1), 2, 2).to_string() if r.exit_reason == "max_hold" else bars_around(r.exit_time, r.exit_time, 2, 2).to_string(), "```", ""]
        sign = 1 if r.side == "long" else -1
        lines.append(f"Check: pnl = {sign:+d} × ({r.exit_price:.3f} − {r.entry_price:.3f}) − {comm} = {sign * (r.exit_price - r.entry_price) - comm:.3f}; "
                     f"R = {sign * (r.exit_price - r.entry_price) - comm:.3f} / {r.planned_risk:.3f} = {(sign * (r.exit_price - r.entry_price) - comm) / r.planned_risk:+.3f} (recorded {r.realised_R:+.3f})")
        lines.append("")
# ---------------------------------------------------------------- 2. automated checks
lines += ["## 2. Automated per-trade checks", ""]
problems = []; summary_rows = []
def session_open(day):
    """First M1 bar at/after 07:00 UTC of session day `day`."""
    i0, i1 = day_slice(day); mods = m1_modarr[i0:i1]; sel = np.nonzero((mods >= 7 * 60) & (mods < 23 * 60))[0]
    return (m1_o[i0 + sel[0]], m1.index[i0 + sel[0]]) if len(sel) else (np.nan, None)
for v in V3.VARIANTS:
    if not (RES / v / "trades.csv").exists(): continue
    cfg = json.loads((RES / v / "config.json").read_text())["config"]; fam = cfg["family"]
    t = load(v); checks = {}
    def chk(name, ok, info=None):
        checks.setdefault(name, [0, 0]); checks[name][0 if ok else 1] += 1
        if not ok: problems.append((v, name, info))
    orb_s, orb_e, orb_c = E.hhmm(cfg["orb_range_start"]), E.hhmm(cfg["orb_range_end"]), E.hhmm(cfg["orb_cancel"])
    texit = E.hhmm(cfg["time_exit"])
    per_day = t.groupby(t.signal_time.dt.tz_convert(None).add(pd.Timedelta(hours=1)).dt.date).size()
    chk("entries_per_session_day_within_cap", (per_day <= (cfg["vw_max_trades"] if fam == "VW" else 1)).all(), per_day[per_day > 1].head().to_dict())
    for r in t.itertuples():
        sign = 1 if r.side == "long" else -1
        pnl = sign * (r.exit_price - r.entry_price) - comm
        chk("realised_R_arithmetic", abs(pnl / r.planned_risk - r.realised_R) < 1e-9, (r.Index, pnl / r.planned_risk, r.realised_R))
        chk("planned_risk_eq_level_minus_stop", abs(abs(r.level - r.initial_stop) - r.planned_risk) < 1e-9, r.Index)
        geo = (r.initial_stop < r.entry_price) if r.side == "long" else (r.initial_stop > r.entry_price)
        if fam != "DC": geo = geo and ((r.entry_price < r.target) if r.side == "long" else (r.entry_price > r.target))
        chk("geometry_stop_target_vs_entry", geo, (r.Index, r.side, r.initial_stop, r.entry_price, r.target))
        chk("entry_after_signal", r.entry_time >= r.signal_time, r.Index)
        day = (r.entry_time + pd.Timedelta(hours=1)).date(); pdy = daily.iloc[dpos[day] - 1]
        if fam != "DC":
            chk("exit_same_session_day", (r.exit_time - pd.Timedelta(minutes=1 if r.exit_reason == "max_hold" else 0) + pd.Timedelta(hours=1)).date() == day or r.exit_reason == "session_gap_exit", (r.Index, r.exit_reason))
        emod = r.entry_time.hour * 60 + r.entry_time.minute
        # entry fill vs level
        if fam in ("ORB", "VB", "DC"):
            bar = m1.loc[r.entry_time]
            if r.side == "long":
                chk("stop_entry_reachable_and_fill_rule", bar.high + spread >= r.level - 1e-9 and abs(r.entry_price - (max(r.level, bar.open + spread) + slip)) < 1e-9, (r.Index, r.level, r.entry_price))
            else:
                chk("stop_entry_reachable_and_fill_rule", bar.low <= r.level + 1e-9 and abs(r.entry_price - (min(r.level, bar.open) - slip)) < 1e-9, (r.Index, r.level, r.entry_price))
        if fam == "ORB":
            i0, i1 = day_slice(day); sel = (m1_modarr[i0:i1] >= orb_s) & (m1_modarr[i0:i1] < orb_e)
            rh, rl = m1_h[i0:i1][sel].max(), m1_l[i0:i1][sel].min(); rng = rh - rl
            chk("orb_range_from_m1", abs(rh - r.range_high) < 1e-9 and abs(rl - r.range_low) < 1e-9, (r.Index, rh, r.range_high, rl, r.range_low))
            chk("orb_level_is_edge_plus_offset", abs(r.level - (rh + cfg["orb_offset"] if r.side == "long" else rl - cfg["orb_offset"])) < 1e-9, r.Index)
            chk("orb_range_ge_min", rng >= cfg["orb_min_range_d1atr"] * pdy.atr14 - 1e-9, (r.Index, rng, pdy.atr14))
            exp_stop = max(rl, r.level - cfg["orb_stop_cap_d1atr"] * pdy.atr14) if r.side == "long" else min(rh, r.level + cfg["orb_stop_cap_d1atr"] * pdy.atr14)
            chk("orb_stop_opposite_edge_capped", abs(exp_stop - r.initial_stop) < 1e-9, (r.Index, exp_stop, r.initial_stop))
            chk("orb_target_mult_x_range", abs(abs(r.target - r.level) - cfg["orb_target_mult"] * rng) < 1e-9, r.Index)
            chk("orb_entry_in_window", orb_e <= emod < orb_c, (r.Index, emod))
            chk("orb_d1atr_is_previous_day", abs(r.d1atr - pdy.atr14) < 1e-9, r.Index)
        if fam == "VB":
            so, st = session_open(day)
            chk("vb_session_open_is_first_bar_at_or_after_0700", abs(so - r.session_open) < 1e-9, (r.Index, so, r.session_open))
            d = cfg["vb_k"] * pdy.atr14
            chk("vb_level_open_pm_k_atr", abs(r.level - (so + d if r.side == "long" else so - d)) < 1e-9, (r.Index, r.level, so, d))
            chk("vb_stop_is_open", abs(r.initial_stop - so) < 1e-9, r.Index)
            chk("vb_target_1_5x", abs(abs(r.target - r.level) - cfg["vb_target_mult"] * d) < 1e-9, r.Index)
            chk("vb_entry_window", E.hhmm(cfg["vb_open"]) <= emod < E.hhmm(cfg["vb_cancel"]), (r.Index, emod))
            if cfg["vb_bias"] == "sma200":
                chk("vb_bias_from_prev_day_sma200", (r.side == "long") == (pdy.close > pdy.sma200), r.Index)
        if fam == "VW":
            # last M1 bar of the signal M15 bar: the last bar with time < signal_time
            jl = m1.index.searchsorted(r.signal_time) - 1
            v_, s_ = twap[jl], max(sd[jl], cfg["vw_min_band"])
            chk("vw_vwap_and_band_recomputed", abs(v_ - r.vwap) < 1e-9 and abs(s_ - r.band_sd) < 1e-9, (r.Index, v_, r.vwap, s_, r.band_sd))
            beyond = (r.signal_close > v_ + cfg["vw_sigma"] * s_) if r.side == "short" else (r.signal_close < v_ - cfg["vw_sigma"] * s_)
            chk("vw_signal_close_beyond_band", beyond, (r.Index, r.signal_close, v_, s_))
            chk("vw_adx_below_max", r.adx < cfg["vw_adx_max"], (r.Index, r.adx))
            chk("vw_target_is_vwap", abs(r.target - v_) < 1e-9, r.Index)
            chk("vw_entry_is_next_m1_bar", r.entry_time == m1.index[jl + 1], (r.Index, r.entry_time, m1.index[jl + 1]))
            bar = m1.loc[r.entry_time]
            chk("vw_market_fill_rule", abs(r.entry_price - ((bar.open + spread + slip) if r.side == "long" else (bar.open - slip))) < 1e-9, r.Index)
            chk("vw_signal_in_window", E.hhmm(cfg["vw_start"]) <= (r.signal_bar_open.hour * 60 + r.signal_bar_open.minute) <= E.hhmm(cfg["vw_end"]), r.Index)
            a_, b_ = m1.index.searchsorted(r.signal_bar_open), m1.index.searchsorted(r.signal_time)
            exp_stop = (m1_l[a_:b_].min() - cfg["vw_stop_atr"] * r.atr) if r.side == "long" else (m1_h[a_:b_].max() + cfg["vw_stop_atr"] * r.atr)
            chk("vw_stop_1atr_beyond_signal_bar_extreme", abs(exp_stop - r.initial_stop) < 1e-9, (r.Index, exp_stop, r.initial_stop))
        if fam == "DC":
            row = daily.iloc[dpos[day]]
            hh = daily.high.iloc[dpos[day] - cfg["dc_entry_n"]:dpos[day]].max(); ll = daily.low.iloc[dpos[day] - cfg["dc_entry_n"]:dpos[day]].min()
            chk("dc_level_is_prev_N_day_extreme", abs(r.level - (hh if r.side == "long" else ll)) < 1e-9, (r.Index, r.level, hh, ll))
            llx = daily.low.iloc[dpos[day] - cfg["dc_exit_n"]:dpos[day]].min(); hhx = daily.high.iloc[dpos[day] - cfg["dc_exit_n"]:dpos[day]].max()
            exp_stop = max(llx, r.level - cfg["dc_trail_atr"] * pdy.atr14) if r.side == "long" else min(hhx, r.level + cfg["dc_trail_atr"] * pdy.atr14)
            chk("dc_initial_stop_closer_of_exit_channel_and_2atr", abs(exp_stop - r.initial_stop) < 1e-9, (r.Index, exp_stop, r.initial_stop))
            chk("dc_stop_only_ratchets", (r.final_stop >= r.initial_stop - 1e-9) if r.side == "long" else (r.final_stop <= r.initial_stop + 1e-9), r.Index)
            first_bar = m1.index[day_slice(day)[0]].floor("15min")
            chk("dc_signal_is_first_m15_bar_of_entry_day", r.signal_time == first_bar, (r.Index, r.signal_time, first_bar))
        # exits
        if r.exit_reason in ("stop", "trail_stop", "stop_same_minute"):
            bar = m1.loc[r.exit_time]
            if r.side == "long":
                chk("stop_exit_reachable", bar.low <= r.final_stop + 1e-9, (r.Index, bar.low, r.final_stop))
                chk("stop_exit_price_le_stop_minus_slip", r.exit_price <= r.final_stop - slip + 1e-9, (r.Index, r.exit_price, r.final_stop))
            else:
                chk("stop_exit_reachable", bar.high + spread >= r.final_stop - 1e-9, (r.Index, bar.high, r.final_stop))
                chk("stop_exit_price_ge_stop_plus_slip", r.exit_price >= r.final_stop + slip - 1e-9, (r.Index, r.exit_price, r.final_stop))
        elif r.exit_reason == "target":
            bar = m1.loc[r.exit_time]
            chk("target_exit_traded_through", (bar.high > r.target - 1e-6) if r.side == "long" else (bar.low + spread < r.target + 1e-6), (r.Index, bar.high, bar.low, r.target))
            chk("target_exit_price_eq_target", abs(r.exit_price - r.target) < 1e-9, r.Index)
        elif r.exit_reason == "time_exit":
            chk("time_exit_at_or_after_2050", (r.exit_time.hour * 60 + r.exit_time.minute) >= texit, (r.Index, r.exit_time))
            bar = m1.loc[r.exit_time]
            chk("time_exit_price_rule", abs(r.exit_price - ((bar.open - slip) if r.side == "long" else (bar.open + spread + slip))) < 1e-9, r.Index)
        elif r.exit_reason == "max_hold":
            bar = m1.loc[r.exit_time - pd.Timedelta(minutes=1)]
            chk("max_hold_exit_price_is_close_rule", abs(r.exit_price - ((bar.close - slip) if r.side == "long" else (bar.close + spread + slip))) < 1e-9, r.Index)
            chk("max_hold_minutes_eq_config", abs(r.hold_minutes - cfg["max_hold_minutes"]) < 1e-9 or (r.hold_minutes > cfg["max_hold_minutes"] and (bar.name - r.entry_time) >= pd.Timedelta(minutes=cfg["max_hold_minutes"] - 1)), (r.Index, r.hold_minutes))
        elif r.exit_reason == "session_gap_exit":
            chk("session_gap_exit_is_first_bar_of_next_session", (r.exit_time + pd.Timedelta(hours=1)).date() > day, (r.Index, r.exit_time))
        if cfg["max_hold_minutes"] and r.exit_reason not in ("max_hold", "stop_same_minute"):
            chk("hold_le_max_hold_when_not_max_hold_exit", r.hold_minutes <= cfg["max_hold_minutes"], (r.Index, r.hold_minutes, r.exit_reason))
    n_fail = sum(f for _, f in checks.values())
    summary_rows.append((v, len(t), n_fail, t.exit_reason.value_counts().to_dict()))
    lines += [f"### {v} — {len(t)} trades, {n_fail} failed checks", "", "| check | passed | failed |", "|---|---|---|"] + [f"| {k} | {a} | {b} |" for k, (a, b) in checks.items()] + [""]
lines += ["## 3. Summary", "", "| variant | trades | failed checks | exit reasons |", "|---|---|---|---|"] + [f"| {v} | {n} | {f} | {ex} |" for v, n, f, ex in summary_rows] + [""]
if problems:
    lines += ["## 4. Problems", "", "```"] + [str(p) for p in problems[:200]] + ["```", ""]
else:
    lines += ["## 4. Problems", "", "None.", ""]
lines += ["## 5. Known approximations", "",
          "- Data has no volume: the F3 'VWAP' is a time-weighted average of M1 closes (TWAP) from the 23:00 UTC session start.",
          "- Session day = 23:00 → 23:00 UTC (engine_v2.daily_frame); the day label is the calendar date on which the session ends. D1 ATR(14) is a Wilder EWM from the first day of data (early values are rough; all inside the development period).",
          "- The feed has no bar when no tick occurred and has occasional intraday gaps of 10–60 minutes; a stop that falls inside such a gap is filled at the next available open (max(stop, open) + slippage), exactly as in engine.py / engine_v2.py.",
          "- 62 session days end before 20:50 UTC (early closes, feed outages). engine_v3 closes intraday positions at the first bar of the next session day ('session_gap_exit') and cancels pending orders ('CANCEL_session_ended'); engine_v2 lets such positions run into the next day. This is a v3-only correction, noted in VALIDATION_REPORT_v3.md.",
          "- stop_same_minute (fill and stop in the same M1 bar) uses the engine_v2 convention: long exits at the bar low − slippage when the low is below the stop, short at stop + slippage.",
          "- F2 'NY' ORB uses fixed UTC times (13:30–14:00); the NY equity open is 13:30 UTC only during US DST, 14:30 UTC in winter.",
          "- F4 holds overnight and over weekends; an open F4 position at the end of the data is closed at the last bar ('end_of_data', one trade).",
          "- A stop or market order whose first available fill (after a feed gap or a news bar) is already beyond the planned stop or target is NOT taken ('SKIP_gap_fill_past_stop/target', counter gap_fill_skipped). Booking such a fill with the planned geometry produced wrong R signs in the first run (a short filled above its stop, then 'stopped' at a profit). engine_v2 Trigger C has the same exposure in principle; none of its trades hit it.",
          "- 21 US-DST-switch Sundays appear in the feed as a 60-bar pseudo session day (22:00-22:59 UTC); they enter engine_v2.daily_frame (shared, unchanged) as tiny daily bars and slightly depress the D1 ATR / rolling channels around those dates.", ""]
(RES / "VALIDATION_MECHANICS_v3.md").write_text("\n".join(lines))
print("\n".join(lines[-40:]) if problems else "\n".join(l for l in lines if l.startswith("| V3") or l.startswith("###") or l.startswith("## 4") or l == "None."))
print(f"problems: {len(problems)}")
