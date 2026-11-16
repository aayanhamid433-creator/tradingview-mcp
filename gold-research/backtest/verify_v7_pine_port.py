"""Re-derive the Gold Quick Pine signals with pandas operations that mirror the Pine expressions line by line
(chart-bar series, x[1] = shift on the chart's own bars, request.security("15", x[1], lookahead_on) = value of the
previous existing 15-minute bar), and compare with the research engine's signal arrays."""
import sys, math
sys.path.insert(0, "/home/user/tradingview-mcp/gold-research/backtest")
import numpy as np, pandas as pd
import engine_v6_mtf as V6, engine_v7_quick as Q

m1 = pd.read_parquet(V6.DATA)
D = V6.prepare(m1); D["ltf15"] = V6.ltf_arrays(D["tmin"], D["H"], D["L"], D["C"], 15)

def chart(tf):
    """chart bars of tf minutes built from the M1 bars that exist (what a tf-minute chart shows)"""
    t = D["tmin"]; slot = t // tf
    df = pd.DataFrame(dict(slot=slot, o=D["O"], h=D["H"], l=D["L"], c=D["C"], t=t))
    g = df.groupby("slot", sort=True)
    b = pd.DataFrame(dict(open=g.o.first(), high=g.h.max(), low=g.l.min(), close=g.c.last(), last_m1=g.t.last()))
    b["time"] = b.index * tf                       # bar open, minutes since epoch
    return b.reset_index(drop=True)

def ctx15(bars):
    """[c15, e15, e15b, a15] as request.security(..., "15", [close[1], ema[1], ema[5], atr[1]], lookahead_on) returns them"""
    b15 = chart(15)
    c = b15.close
    ema = c.ewm(alpha=2 / 51.0, adjust=False).mean()
    pc = c.shift(1).fillna(c.iloc[0])
    tr = np.maximum(b15.high - b15.low, np.maximum((b15.high - pc).abs(), (b15.low - pc).abs()))
    atr = tr.ewm(alpha=1 / 14.0, adjust=False).mean(); atr.iloc[:14] = np.nan
    f = pd.DataFrame(dict(time=b15.time, c15=c.shift(1), e15=ema.shift(1), e15b=ema.shift(5), a15=atr.shift(1)))
    slot15 = (bars.time // 15) * 15
    return f.set_index("time").reindex(slot15.values).reset_index(drop=True)

def pine_signals(tf, mode, brk_min=5, w=5, k=2.0, need_trend=False, pb_len=20, warm=200):
    b = chart(tf); x = ctx15(b)
    trend_up = x.c15.notna() & x.e15b.notna() & (x.c15 > x.e15) & (x.e15 > x.e15b)
    trend_dn = x.c15.notna() & x.e15b.notna() & (x.c15 < x.e15) & (x.e15 < x.e15b)
    if mode == "burst":
        wb = max(1, int(w / tf))
        mv = b.close - b.close.shift(wb)
        cont = (b.time - b.time.shift(wb)) == w
        z = mv / (x.a15 * math.sqrt(w / 15.0))
        up = cont & (z >= k) & ((not need_trend) | trend_up); dn = cont & (z <= -k) & ((not need_trend) | trend_dn)
    elif mode == "brk":
        kb = max(1, int(brk_min / tf))
        hh = b.high.rolling(kb).max().shift(1); ll = b.low.rolling(kb).min().shift(1)
        cont = (b.time - b.time.shift(kb)) == kb * tf
        up = cont & trend_up & (b.close > hh); dn = cont & trend_dn & (b.close < ll)
    else:
        ema = b.close.ewm(alpha=2 / (pb_len + 1.0), adjust=False).mean()
        ql = (b.low <= ema) & (b.close > ema); qs = (b.high >= ema) & (b.close < ema)
        up = ql & ~ql.shift(1, fill_value=False) & trend_up; dn = qs & ~qs.shift(1, fill_value=False) & trend_dn
    if mode != "pb":
        up = up & ~up.shift(1, fill_value=False); dn = dn & ~dn.shift(1, fill_value=False)
    modc = (b.time + tf) % 1440
    in_win = (modc >= 420) & (modc < 960) & x.a15.notna()
    # the research engine ignores the first 200 fifteen-minute bars; apply the same warm-up for the comparison only
    b15 = chart(15); first_ok = b15.time.iloc[warm + 1]
    in_win &= (b.time // 15) * 15 >= first_ok
    sig = np.where(up & in_win, 1, np.where(dn & in_win, -1, 0))
    return b, sig, x

def compare(name, tf, mode, **kw):
    cfg = dict(Q.BASE); cfg.update(Q.VARIANTS[name])
    eng, dist = Q.signals(cfg, D); eng = np.asarray(eng)
    b, sig, x = pine_signals(tf, mode, **kw)
    # engine signals are per M1 index (signal at that M1 bar's close); map chart bars to the M1 index of their last minute
    idx = pd.Series(np.arange(len(D["tmin"])), index=D["tmin"]).reindex(b.last_m1.values).to_numpy()
    mine = np.zeros(len(eng), dtype=int); mine[idx] = sig
    a = set(np.flatnonzero(eng != 0)); c = set(np.flatnonzero(mine != 0))
    both = a & c; same_dir = sum(1 for i in both if eng[i] == mine[i])
    dd = np.asarray(dist, dtype=float)[idx]; da = x.a15.to_numpy()
    okd = np.isfinite(dd) & np.isfinite(da)
    print(f"{name:18s} tf={tf}m engine={len(a):6d} pine-form={len(c):6d} common={len(both):6d} same direction={same_dir:6d} "
          f"only engine={len(a - c):5d} only pine-form={len(c - a):5d} | stop distance max abs diff={np.max(np.abs(dd[okd] - da[okd])):.2e}")
    return a, c, eng, mine

import sys as _s
if "--tf5" in _s.argv:
    compare("QS5_BURST5_H5", 5, "burst", w=5)
    compare("QS5_TREND_BRK_H5", 5, "brk")
    compare("QS5_TREND_PB_H5", 5, "pb")
else:
    compare("QS_TREND_BRK_H5", 1, "brk")
    compare("QS_BURST5_H5", 1, "burst", w=5)
    compare("QS_BURST5_H5_T", 1, "burst", w=5, need_trend=True)
    compare("QS_BURST15_H15", 1, "burst", w=15)
    compare("QS_TREND_PB_H15", 5, "pb")
