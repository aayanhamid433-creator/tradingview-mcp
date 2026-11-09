#!/usr/bin/env python3
"""Render M15 candlestick charts (EMA20 + ADX/DI panel) that END at a chosen bar, hiding all later candles,
for the chart-reading audit. Writes PNGs plus an answer key (never shown to the reader) in ../chart_audit/.
Sample: 8 bars that are valid v1.0 setups (touch + armed) and 8 that are near-misses (touch but ADX<30, or armed but no touch),
all from the development period, chosen at random with a fixed seed.
"""
import pathlib, json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import engine as E
HERE = pathlib.Path(__file__).resolve().parent; OUT = HERE.parent / "chart_audit"; OUT.mkdir(exist_ok=True)
cfg = dict(E.BASE_CONFIG)
m1 = pd.read_parquet(E.DATA)
m15 = m1.resample("15min", label="left", closed="left").agg(open=("open","first"), high=("high","max"), low=("low","min"), close=("close","last")).dropna()
ind = E.indicators(m15, cfg)
adx = ind.adx.values; thr = cfg["adx_threshold"]
rising_above = (adx > thr) & (adx > np.roll(adx, 1))
rising_recent = pd.Series(rising_above).rolling(cfg["adx_rising_lookback"] + 1, min_periods=1).max().values.astype(bool)
armed = (adx > thr) & rising_recent
touch = (ind.low.values <= ind.ema.values) & (ind.high.values >= ind.ema.values)
mod = ind.index.hour * 60 + ind.index.minute
in_window = (mod >= 7*60) & (mod <= 15*60+45)
dev = (ind.index >= pd.Timestamp("2021-06-01", tz="UTC")) & (ind.index < pd.Timestamp("2024-07-01", tz="UTC"))
rng = np.random.default_rng(7)
setups = np.where(armed & touch & in_window & dev)[0]
near_adx = np.where(touch & ~armed & (adx > 22) & (adx <= 30) & in_window & dev)[0]
near_touch = np.where(armed & ~touch & in_window & dev & (ind.low.values > ind.ema.values))[0]
picks = [(int(i), "setup") for i in rng.choice(setups, 8, replace=False)] + \
        [(int(i), "near_miss_adx") for i in rng.choice(near_adx, 4, replace=False)] + \
        [(int(i), "near_miss_no_touch") for i in rng.choice(near_touch, 4, replace=False)]
rng.shuffle(picks)
key = []
for n, (i, kind) in enumerate(picks, 1):
    w = ind.iloc[i-59:i+1]
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw=dict(height_ratios=[3, 1]))
    x = np.arange(len(w))
    for k, (t, b) in enumerate(w.iterrows()):
        col = "#2ca02c" if b.close >= b.open else "#d62728"
        ax.plot([k, k], [b.low, b.high], color=col, lw=1)
        ax.add_patch(plt.Rectangle((k-0.3, min(b.open, b.close)), 0.6, max(abs(b.close-b.open), 0.01), color=col))
    ax.plot(x, w.ema, color="#1f77b4", lw=1.5, label="EMA 20")
    ax.set_title(f"XAUUSD M15 (UTC) — last closed bar opens {w.index[-1]:%Y-%m-%d %H:%M} UTC — audit chart {n:02d}")
    ax.legend(loc="upper left"); ax.grid(alpha=0.3); ax.set_ylabel("USD/oz (bid)")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%.2f"))
    ax2.plot(x, w.adx, color="black", lw=1.5, label="ADX 14"); ax2.plot(x, w.pdi, color="#2ca02c", lw=1, label="+DI"); ax2.plot(x, w.mdi, color="#d62728", lw=1, label="-DI")
    ax2.axhline(30, color="gray", ls="--", lw=0.8); ax2.legend(loc="upper left", ncol=3); ax2.grid(alpha=0.3)
    ticks = list(range(0, len(w), 8)); ax2.set_xticks(ticks); ax2.set_xticklabels([w.index[k].strftime("%m-%d %H:%M") for k in ticks], rotation=0)
    plt.tight_layout(); fig.savefig(OUT / f"audit_{n:02d}.png", dpi=110); plt.close(fig)
    b = w.iloc[-1]; prev = w.iloc[-2]
    key.append(dict(chart=f"audit_{n:02d}.png", kind=kind, bar_open_utc=str(w.index[-1]), open=round(b.open,2), high=round(b.high,2), low=round(b.low,2), close=round(b.close,2),
                    ema20=round(b.ema,2), adx=round(b.adx,1), adx_prev=round(prev.adx,1), pdi=round(b.pdi,1), mdi=round(b.mdi,1),
                    touch=bool(touch[i]), armed=bool(armed[i]), direction=("long" if b.pdi > b.mdi else "short"),
                    valid_setup=bool(armed[i] and touch[i]),
                    entry_level=round((b.high + 0.10) if b.pdi > b.mdi else (b.low - 0.10), 2),
                    target=round(w.high.iloc[-20:].max() if b.pdi > b.mdi else w.low.iloc[-20:].min(), 2)))
json.dump(key, open(OUT / "ANSWER_KEY_do_not_show_reader.json", "w"), indent=2)
print(json.dumps(key, indent=1)[:1500])
