# Insights: canada_tire_stores.csv

Source sha256 `2ec999c5a4e7`, 273 rows, split seed 20261123 (150 explore / 123 holdout). Generated from `analysis/LEDGER.jsonl`; every figure below cites the ledger entry it came from.

Holdout looks: 5 (no budget set).

## Untyped

| id | kind | status | claim | decision it informs | falsified if | holdout result | goldfish | fresh data |
|---|---|---|---|---|---|---|---|---|
| K1 |  | **refuted** | November is the peak sales month of the year for Canadian tire stores |  | share of complete years peaking in Nov < 0.80 | `#6` peak_months={'10': 4, '11': 5}, share_nov_peak=0.556, years=9 | `#16` falsified |  |
| K2 |  | **established** | Canada's fall changeover (Oct-Nov) runs at least 15% (log points) above summer (Jun-Aug), after removing trend |  | mean gap < 0.15 or p >= 0.002 | `#8` mean_gap_logpts=0.2181, min_gap=0.174, p_gap_gt_0.15=0.00195, years=9 | `#19` survived |  |
| K3 |  | **established** | Quebec's spring tire peak is sharper than Ontario's: April takes a larger share of Quebec's annual sales |  | share of years with Quebec April share > Ontario's < 0.80 | `#10` mean_apr_share_on=0.0868, mean_apr_share_qc=0.0962, share_qc_gt_on=1.0, years=9 | `#17` survived |  |
| K4 |  | **established** | Same month last year, scaled by trailing 12-month growth, forecasts Canadian monthly tire-store sales within 7% MAPE and beats plain same-month-last-year |  | MAPE(drift) > 0.07 or not better than seasonal naive | `#12` mape_drift=0.0616, mape_naive=0.0735, months=99 | `#20` survived |  |
| K5 |  | **established** | Alberta peaks in October, ahead of the rest of Canada, in at least half of years (risky: explore was a 6-6 split) |  | share of complete years with an Oct peak in Alberta < 0.50 | `#14` peak_months={'10': 6, '11': 2, '5': 1}, share_oct_peak=0.667, years=9 | `#18` survived |  |

## Coverage

| category | kind | claims | waived |
|---|---|---|---|
| descriptive | level | **not covered** |  |
| descriptive | trend | **not covered** |  |
| descriptive | seasonality | **not covered** |  |
| descriptive | composition | **not covered** |  |
| descriptive | comparison | **not covered** |  |
| descriptive | distribution | **not covered** |  |
| descriptive | anomaly | **not covered** |  |
| descriptive | change-point | **not covered** |  |
| diagnostic | attribution | **not covered** |  |
| diagnostic | driver | **not covered** |  |
| diagnostic | causal | **not covered** |  |
| diagnostic | root-cause | **not covered** |  |
| predictive | forecast | **not covered** |  |
| predictive | leading-indicator | **not covered** |  |
| predictive | classification | **not covered** |  |
| predictive | timing | **not covered** |  |
| prescriptive | policy | **not covered** |  |
| prescriptive | allocation | **not covered** |  |
| prescriptive | trigger | **not covered** |  |

Untyped claims (registered before types existed): K1, K2, K3, K4, K5.

Statuses: **established** = survived holdout, replayed byte-identical, every goldfish agrees. **refuted** = falsified and confirmed the same way. **(narrowed)** = a goldfish found the claim holds only in a narrower reading; quote the narrowed version. **held / BROKE on fresh data** = the frozen test rerun on rows published after the seal. **blocked** = a prescriptive claim whose supporting claim is not established. Anything else is not yet an insight.
