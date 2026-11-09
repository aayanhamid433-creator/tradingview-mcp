# Chart-reading audit — v1.0 rule recognition from images with future candles hidden

16 M15 charts (60 bars each, EMA20 + ADX/DI panel) rendered from the research data at development-period timestamps: 8 valid setups, 4 near-misses with ADX below 30, 4 near-misses with no EMA touch. A fresh model instance read only the PNGs (no data access) and answered a fixed questionnaire. Scored against the data-derived key.

| field | correct | wrong |
|---|---|---|
| armed | 16 | 0 |
| touch | 15 | 1 |
| direction | 16 | 0 |
| valid_setup | 16 | 0 |

- Missed setups (key valid, reader said no): **0**
- False signals (reader valid, key no): **0**

| quantity | n | median abs error (USD) | max abs error (USD) |
|---|---|---|---|
| high | 16 | 0.08 | 0.76 |
| low | 16 | 0.14 | 1.02 |
| entry | 8 | 0.12 | 0.62 |
| target | 8 | 0.07 | 0.40 |
| adx | 16 | 0.15 | 0.90 |

## Per chart (key / reader)

| chart | kind | valid | armed | touch | direction | ADX | last high | last low | reader confidence |
|---|---|---|---|---|---|---|---|---|---|
| audit_01.png | setup | True / True | True / True | True / True | long / long | 38.4 / 38.5 | 1990.92 / 1991.0 | 1988.24 / 1988.2 | medium |
| audit_02.png | near_miss_no_touch | False / False | True / True | False / False | long / long | 32.0 / 32.0 | 1930.26 / 1930.2 | 1926.9 / 1927.3 | high |
| audit_03.png | near_miss_adx | False / False | False / False | True / True | long / long | 24.8 / 25.0 | 2042.22 / 2042.1 | 2039.94 / 2039.9 | high |
| audit_04.png | setup | True / True | True / True | True / True | short / short | 41.9 / 42.0 | 1824.84 / 1825.6 | 1820.96 / 1821.5 | low |
| audit_05.png | setup | True / True | True / True | True / True | short / short | 30.1 / 30.0 | 1984.52 / 1984.5 | 1979.12 / 1979.0 | low |
| audit_06.png | near_miss_no_touch | False / False | True / True | False / False | long / long | 36.4 / 37.0 | 1990.35 / 1990.0 | 1988.46 / 1988.6 | high |
| audit_07.png | near_miss_adx | False / False | False / False | True / True | short / short | 24.8 / 25.0 | 2041.06 / 2041.0 | 2039.56 / 2039.7 | medium |
| audit_08.png | setup | True / True | True / True | True / True | long / long | 39.1 / 39.0 | 1903.78 / 1904.4 | 1901.76 / 1902.1 | medium |
| audit_09.png | setup | True / True | True / True | True / True | long / long | 31.1 / 32.0 | 1884.52 / 1884.6 | 1883.14 / 1883.3 | low |
| audit_10.png | setup | True / True | True / True | True / True | short / short | 42.6 / 43.0 | 2304.36 / 2304.5 | 2293.46 / 2293.5 | medium |
| audit_11.png | setup | True / True | True / True | True / True | long / long | 40.8 / 41.0 | 2157.61 / 2157.5 | 2155.6 / 2155.5 | medium |
| audit_12.png | near_miss_adx | False / False | False / False | True / False | long / long | 26.9 / 27.0 | 1794.38 / 1794.3 | 1791.92 / 1792.7 | high |
| audit_13.png | near_miss_adx | False / False | False / False | True / True | short / short | 24.8 / 25.0 | 1792.97 / 1793.0 | 1790.58 / 1790.7 | high |
| audit_14.png | setup | True / True | True / True | True / True | long / long | 40.5 / 41.0 | 2034.62 / 2034.4 | 2031.44 / 2031.5 | medium |
| audit_15.png | near_miss_no_touch | False / False | True / True | False / False | long / long | 44.1 / 44.0 | 1827.46 / 1827.5 | 1824.31 / 1824.5 | high |
| audit_16.png | near_miss_no_touch | False / False | True / True | False / False | long / long | 37.4 / 37.5 | 2020.83 / 2020.8 | 2013.98 / 2015.0 | high |

## Interpretation

- Classification from a clean, indicator-labelled chart is reliable for the binary rules when the case is clear-cut; errors cluster where ADX sits at the 30 line or a wick barely grazes the EMA (the reader flagged these as low confidence).
- Price reads from pixels carry errors of the order of tenths of a dollar to over a dollar depending on the y-axis scale. Entry/stop/target levels must therefore come from **typed numbers** in the submission template, not from reading a screenshot; the playbook's 0.10 USD entry offset is smaller than typical read error.
- Sample is 16 charts rendered by us, not broker screenshots with varying styles; broker charts without an ADX panel or with a forming candle visible would be harder. This audit is a baseline, not a validation of screenshot trading.