# Notes on this run

- Source: FRED series MRTSSM4413USN (sales), PCU326211326211 (tire PPI), TRFVOLUSM227NFWA (miles), GASREGW (gas, monthly mean), UNRATE. Pulled 2026-11-23. US data, not Canadian: the US peak is summer, and Canadian winter-tire changeover seasonality will differ.
- Known data defect, disclosed rather than patched: FRED has no UNRATE for 2025-10, and the merge dropped that whole row. In the holdout, the YoY lags in T3 to T6 for 2025-11 onward span 13 months, not 12 (about 10 of 154 rows). The T1 and T6 goldfish noticed the gap and excluded it; their verdicts match the elephant's.
- T5 is contested: the elephant's circular-shift null gave p = 0.0002, while the goldfish's autocorrelation-preserving surrogates gave p = 0.042 (and an effective-n correction p = 0.006). The correlation (rho 0.37) is real but rests on one episode, the 2021 to 2022 inflation spike. Not an insight.
