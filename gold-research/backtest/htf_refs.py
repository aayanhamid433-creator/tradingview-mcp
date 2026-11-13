#!/usr/bin/env python3
"""htf_refs.py — direction references from bigger timeframes, per M1 bar, without look-ahead.

For each M1 bar the state of a reference is taken from the last bar of that timeframe that CLOSED BEFORE the bar of
that timeframe which contains the M1 bar. This is what TradingView returns on a lower-timeframe chart for
request.security(sym, tf, expr[1], lookahead=barmerge.lookahead_on).

  m15 / h1 / h4 : close > EMA50 and EMA50 > EMA50 four bars earlier (up); close < EMA50 and EMA50 falling (down)
  d1            : previous session-day close above (up) / below (down) its 200-day simple average

Bars are built from the M1 bars that exist (dataset clock = London time). H1 bars start on the clock hour. H4 bars start
at 22:00, 02:00, 06:00, 10:00, 14:00, 18:00 London time (TradingView builds forex 4-hour bars from the 17:00 New York
session start). The session day runs 23:00 -> 23:00 as in every engine.
"""
import numpy as np


def _bars(tmin, C, slot):
    gs = np.flatnonzero(np.r_[True, slot[1:] != slot[:-1]]); ge = np.r_[gs[1:], len(slot)]
    cl = C[ge - 1]
    gidx = np.cumsum(np.r_[True, slot[1:] != slot[:-1]]) - 1
    return cl, gidx


def _ema(x, length):
    out = np.empty(len(x)); out[0] = x[0]; a = 2.0 / (length + 1.0)
    for q in range(1, len(x)): out[q] = out[q - 1] + a * (x[q] - out[q - 1])
    return out


def ema_state(tmin, C, slot, length=50, slope_bars=4, warmup=200):
    """(up, dn) per M1 index for an EMA-trend reference on the bars defined by `slot`."""
    cl, gidx = _bars(tmin, C, slot)
    e = _ema(cl, length)
    e4 = np.r_[np.full(slope_bars, np.nan), e[:-slope_bars]]
    up_bar = (cl > e) & (e > e4); dn_bar = (cl < e) & (e < e4)
    prev = gidx - 1; ok = prev >= warmup
    p = np.maximum(prev, 0)
    return np.where(ok, up_bar[p], False), np.where(ok, dn_bar[p], False)


def d1_state(tmin, C, length=200):
    """(up, dn) per M1 index: previous session-day close vs its SMA(length)."""
    sday = (tmin + 60) // 1440
    cl, gidx = _bars(tmin, C, sday)
    cs = np.cumsum(np.r_[0.0, cl])
    sma = np.full(len(cl), np.nan)
    sma[length - 1:] = (cs[length:] - cs[:-length]) / length
    up_bar = cl > sma; dn_bar = cl < sma                       # NaN compares False: no state before `length` days exist
    prev = gidx - 1; ok = prev >= 0
    p = np.maximum(prev, 0)
    return np.where(ok, up_bar[p], False), np.where(ok, dn_bar[p], False)


def all_refs(tmin, C):
    """{'m15': (up, dn), 'h1': ..., 'h4': ..., 'd1': ...} per M1 index."""
    return {
        "m15": ema_state(tmin, C, tmin // 15),
        "h1": ema_state(tmin, C, tmin // 60),
        "h4": ema_state(tmin, C, (tmin + 120) // 240),
        "d1": d1_state(tmin, C),
    }
