# CHART_SUBMISSION_TEMPLATE (template — copy, fill, and send with your screenshots)

Minimum package for a v1.0 (Holy Grail, M15) read. H4 and M5 are optional context for this method; **M15 is the decision chart**.

```
Symbol and feed:          XAUUSD on <broker name>, MT5 server time <GMT+2/+3/0>
Screenshots attached:     [ ] M15 with EMA 20 and ADX(14)/+DI/−DI visible   (REQUIRED)
                          [ ] H1 (context)   [ ] H4 (optional)   [ ] M5 (optional)
Each chart shows:         symbol, timeframe, price axis, time axis, at least 60 bars; the still-forming candle is identifiable
Chart capture time:       YYYY-MM-DD HH:MM  (timezone: America/Toronto / UTC / server)
Current quote:            bid ____.__  ask ____.__  at HH:MM:SS (timezone) → spread ____ USD
Last CLOSED M15 bar:      open time ____  O ____ H ____ L ____ C ____   (type the numbers; do not make me read them off pixels)
EMA20 at that bar:        ____      ADX14: ____  (previous bar ____)   +DI ____  −DI ____
Highest high / lowest low of the last 20 closed M15 bars: ____ / ____
News check:               next high-impact US release (CPI/NFP/FOMC/PCE) at ____ (timezone), source: ____
Account (only if sizing requested): equity ____ currency ____; risk budget per trade ____; existing positions/pending exposure ____
Broker symbol spec (only if sizing requested): contract size ____ oz; tick size ____; min/step/max volume ____/____/____
Prop account (only if compliance requested): firm ____; account type ____; daily loss rule ____; max loss rule ____; reset time ____; news/holding rules ____; current headroom ____
```

What you get back: the fixed response block from the master prompt (DECISION / USE STATUS / … / Journal setup ID). Until the strategy is validated, every plan is labelled **UNVALIDATED DEMO**. A plan is conditional on its trigger; it is not a filled order.

Freshness rule (v1.0): a chart older than one closed M15 bar (15 minutes) at analysis time is stale → WAIT until an updated capture arrives.
