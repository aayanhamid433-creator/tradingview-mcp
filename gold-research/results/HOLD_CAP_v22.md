# Maximum hold time on v2.2 trades (2026-11-12)

Aayan's constraint: a trade should be in and out within 15 minutes. Re-simulated the 72 v2.2 trades (V2_K_confirm) on the M1 data with a forced market exit H minutes after the fill (stop and first target still honoured before that; spread, slippage and commission as in BASE_CONFIG; no partial or trail, since nothing reaches T1 that fast).

| period | n | original mean R | cap 15 min: mean R / PF / max DD | cap 30 min | cap 60 min |
|---|---|---|---|---|---|
| development | 29 | −0.023 | −0.021 / 0.91 / −4.1 | −0.121 / 0.67 / −5.7 | +0.029 / 1.07 / −4.5 |
| validation | 17 | +0.978 | +0.109 / 1.42 / −2.0 | +0.211 / 1.62 / −3.4 | +0.247 / 1.58 / −4.5 |
| final test | 26 | +0.191 | +0.112 / 1.75 / −2.3 | +0.115 / 1.59 / −1.8 | +0.127 / 1.49 / −1.8 |

With a 15-minute cap 57 of the 72 trades are closed by the clock, 11 by the stop, 4 at the target. Median natural hold is 110 minutes; only 15 % of trades finished within 15 minutes on their own. The trades the clock cuts short averaged +0.485 R when allowed to run and +0.148 R when cut.

Reading: the edge survives a 15-minute cap out of sample (about +0.11 R per trade, PF 1.4–1.75, drawdown halves) but at roughly one fifth of the money per trade: about 28 USD instead of 125 USD per trade at 250 USD risk. The system earns by holding one to three hours. Pine input `Max hold in 15-min bars` (0 = off) lets Aayan test the cap himself; the Pine version exits at the close of the bar after the fill bar, so its hold is 15–30 minutes, not exactly 15.
