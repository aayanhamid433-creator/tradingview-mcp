#!/usr/bin/env python3
"""ALTERNATIVE CANDIDATE (kept separate from GOLD_PLAYBOOK v1.0): re-implementation of
"Gold Breakout 15M Strategy [WillyAlgoTrader]" (open-source Pine v6, TradingView script HnelYN0A,
published 2026-10-12; source saved as ../alt_gold_bo_15m_source_WillyAlgoTrader.pine).

Rules (from the author's description and source, defaults):
  * Broker clock: fixed GMT+3 all year (option: New York + 7h, DST-aware).
  * Range = highest high / lowest low of bars whose opening hour is in [0, 7) broker time; resets each broker day;
    first day of history skipped.
  * From the first bar opening at/after 07:00 until the bar before 20:00: buy stop at Range High and sell stop at
    Range Low, one-cancels-other. One trade per broker day.
  * Stop-loss: % of entry (1.0%). Placed from the breakout level; re-set once from the fill price at the close of
    the entry bar. Alternative mode: opposite range boundary. No take-profit.
  * Exit: stop-loss or forced close at the open of the first bar at/after 20:00 broker time.
  * Size: 1% of equity at risk (R = 1% of price). We report in R, so sizing only matters for commission per oz.
Fills are simulated on M1 bars with the same conventions as engine.py (ask = bid + spread; stop fills at
max(level, open) + slippage; a bar that crosses both boundaries is resolved to the side nearer the bar's open and counted).
Usage: python3 engine_gbo.py --all
"""
import argparse, json, pathlib, datetime as dt
import numpy as np, pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "xauusd_m1_utc.parquet"
RESULTS = HERE.parent / "results_alt_gold_bo"  # clock-corrected run (true UTC); the earlier London-clock run is in results_alt_gold_bo_londonclock

BASE = dict(clock_fix=True, clock="fixed_gmt3", range_from=0, range_to=7, close_hour=20, sl_mode="pct", sl_pct=1.0,
            spread=0.25, slippage=0.05, commission_frac_rt=0.0, both_sides_rule="nearer_open")
VARIANTS = {
    "G0_author_like": dict(spread=0.0, slippage=0.0, commission_frac_rt=0.00008),   # 0.4 USD/order at 10k equity, 1% risk
    "G1_base_costs": {},
    "G2_cost_stress": dict(spread=0.50, slippage=0.15),
    "G3_ny7_clock": dict(clock="ny_plus_7"),
    "G4_sl_range_boundary": dict(sl_mode="range"),
    "G5_both_sides_adverse": dict(both_sides_rule="adverse"),
}

def us_dst_active_np(days):
    out = np.zeros(len(days), dtype=bool)
    for i, d in enumerate(days):
        d = pd.Timestamp(d).date()
        mar = dt.date(d.year, 3, 1); start = mar + dt.timedelta(days=(6 - mar.weekday()) % 7 + 7)
        nov = dt.date(d.year, 11, 1); end = nov + dt.timedelta(days=(6 - nov.weekday()) % 7)
        out[i] = start <= d < end
    return out

def broker_time(idx_utc, clock):
    naive = idx_utc.tz_convert("UTC").tz_localize(None)
    if clock == "fixed_gmt3":
        return naive + pd.Timedelta(hours=3)
    # New York + 7h: NY local time + 7h  == UTC-5+7 = UTC+2 (winter), UTC-4+7 = UTC+3 (summer)
    ny = idx_utc.tz_convert("America/New_York").tz_localize(None)
    return ny + pd.Timedelta(hours=7)

def true_utc_index(idx_parquet):
    """Clock correction (PROJECT_STATE.md, 2026-11-13): the parquet index is HistData's stamp + 5h, and the stamps follow
    New York local time (EST/EDT), so (index - 5h) is New York local time. Localize as America/New_York and convert to UTC."""
    ny_local = idx_parquet.tz_convert("UTC").tz_localize(None) - pd.Timedelta(hours=5)
    return ny_local.tz_localize("America/New_York", ambiguous="NaT", nonexistent="shift_forward").tz_convert("UTC")

def run(cfg, m1, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    if cfg.get("clock_fix", True):
        fixed = true_utc_index(m1.index)
        keep = ~fixed.isna()
        m1 = m1[keep].copy(); m1.index = fixed[keep]
    bt = broker_time(m1.index, cfg["clock"])
    o, h, l, c = (m1[k].values for k in ("open", "high", "low", "close"))
    hour = bt.hour.values; minute = bt.minute.values; day = bt.normalize().values
    spread, slip = cfg["spread"], cfg["slippage"]
    days = np.unique(day)
    # index boundaries per day
    day_start = np.searchsorted(day, days, side="left"); day_end = np.searchsorted(day, days, side="right")
    trades, skips = [], []; both_sides = 0
    for di in range(1, len(days)):  # first day skipped (as in the script)
        a, b = day_start[di], day_end[di]
        hr = hour[a:b]
        rmask = (hr >= cfg["range_from"]) & (hr < cfg["range_to"])
        if not rmask.any(): skips.append((str(days[di])[:10], "no_range_bars")); continue
        RH = h[a:b][rmask].max(); RL = l[a:b][rmask].min()
        if not RH > RL: skips.append((str(days[di])[:10], "degenerate_range")); continue
        if cfg["sl_mode"] == "pct":
            slL0 = round(RH * (1 - cfg["sl_pct"] / 100), 2); slS0 = round(RL * (1 + cfg["sl_pct"] / 100), 2)
        else:
            slL0, slS0 = RL, RH
        wmask = (hr >= cfg["range_to"]) & (hr < cfg["close_hour"])
        widx = np.where(wmask)[0]
        if len(widx) == 0: skips.append((str(days[di])[:10], "no_window_bars")); continue
        pos = None; entry_bar15 = None
        for k in widx:
            j = a + k
            bo, bh, bl = o[j], h[j], l[j]; ao, ah, al = bo + spread, bh + spread, bl + spread
            if pos is None:
                long_hit = ah >= RH; short_hit = bl <= RL
                if long_hit and short_hit:
                    both_sides += 1
                    if cfg["both_sides_rule"] == "nearer_open":
                        side = "long" if abs(ao - RH) <= abs(bo - RL) else "short"
                    else:  # adverse: pick the side that will be stopped if possible, else nearer open
                        side = "long" if abs(ao - RH) > abs(bo - RL) else "short"
                elif long_hit: side = "long"
                elif short_hit: side = "short"
                else: continue
                if side == "long":
                    fill = max(RH, ao) + slip; stop = slL0; level = RH
                else:
                    fill = min(RL, bo) - slip; stop = slS0; level = RL
                pos = dict(side=side, level=level, entry_time=m1.index[j], entry_price=fill, stop_initial=stop, stop=stop,
                           range_high=RH, range_low=RL, both_sides=bool(long_hit and short_hit))
                entry_bar15 = (hour[j], minute[j] // 15)
                # same-minute stop check (conservative)
                if (side == "long" and bl <= stop) or (side == "short" and ah >= stop):
                    px = (stop - slip) if side == "long" else (stop + slip)
                    pos.update(exit_time=m1.index[j], exit_price=px, exit_reason="stop_same_minute"); trades.append(pos); pos = None
                continue
            # position open: re-anchor stop at the close of the entry M15 bar (first minute of a later M15 bar)
            if (hour[j], minute[j] // 15) != entry_bar15 and not pos.get("reanchored") and cfg["sl_mode"] == "pct":
                pos["stop"] = round(pos["entry_price"] * (1 - cfg["sl_pct"] / 100), 2) if pos["side"] == "long" else round(pos["entry_price"] * (1 + cfg["sl_pct"] / 100), 2)
                pos["reanchored"] = True
            if pos["side"] == "long" and bl <= pos["stop"]:
                pos.update(exit_time=m1.index[j], exit_price=min(pos["stop"], bo) - slip, exit_reason="stop"); trades.append(pos); pos = None; break
            if pos["side"] == "short" and ah >= pos["stop"]:
                pos.update(exit_time=m1.index[j], exit_price=max(pos["stop"], ao) + slip, exit_reason="stop"); trades.append(pos); pos = None; break
        if pos is not None:
            # time exit: open of the first bar at/after close_hour on this broker day (or the next available bar)
            later = np.where(hour[a:b] >= cfg["close_hour"])[0]
            j = a + later[0] if len(later) else b  # fall through to the next day's first bar if the feed has a gap
            if j >= len(o): j = len(o) - 1
            px = (o[j] - slip) if pos["side"] == "long" else (o[j] + spread + slip)
            pos.update(exit_time=m1.index[j], exit_price=px, exit_reason="time_exit"); trades.append(pos); pos = None
    tr = pd.DataFrame(trades)
    if len(tr):
        tr["planned_risk"] = (tr.level - tr.stop_initial).abs()
        sign = np.where(tr.side == "long", 1.0, -1.0)
        comm = cfg["commission_frac_rt"] * tr.entry_price
        tr["pnl_per_oz"] = sign * (tr.exit_price - tr.entry_price) - comm
        tr["realised_R"] = tr.pnl_per_oz / tr.planned_risk
        tr["hold_minutes"] = (pd.to_datetime(tr.exit_time) - pd.to_datetime(tr.entry_time)).dt.total_seconds() / 60
        tr["signal_bar_open"] = tr.entry_time  # for analyze.py compatibility (period assignment by entry time)
        tr["session"] = np.where(pd.to_datetime(tr.entry_time).dt.hour < 12, "before_12UTC", "after_12UTC")
    tr.to_csv(out_dir / "trades.csv", index=False)
    pd.DataFrame(skips, columns=["day", "reason"]).to_csv(out_dir / "skips.csv", index=False)
    meta = dict(config=cfg, n_trades=int(len(tr)), both_sides_minutes=both_sides, ambiguous_bars=both_sides,
                run_time_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    (out_dir / "config.json").write_text(json.dumps(meta, indent=2, default=str))
    return tr, meta

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--variant"); ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    m1 = pd.read_parquet(DATA)
    for name in (list(VARIANTS) if a.all else [a.variant or "G1_base_costs"]):
        cfg = dict(BASE); cfg.update(VARIANTS[name]); cfg["variant"] = name
        tr, meta = run(cfg, m1, RESULTS / name)
        print(f"{name}: trades={len(tr)} both_sides_minutes={meta['both_sides_minutes']}" + (f" meanR={tr.realised_R.mean():+.3f} win={(tr.realised_R>0).mean():.3f} PF={tr.realised_R[tr.realised_R>0].sum()/abs(tr.realised_R[tr.realised_R<=0].sum()):.2f}" if len(tr) else ""))

if __name__ == "__main__":
    main()
