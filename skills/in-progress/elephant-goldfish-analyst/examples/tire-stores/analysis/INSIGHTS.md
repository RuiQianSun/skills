# Insights: tire_stores.csv

Source sha256 `95c07fd36dab`, 415 rows, split seed 20261123 (249 explore / 166 holdout). Generated from `analysis/LEDGER.jsonl`; every figure below cites the ledger entry it came from.

Holdout looks: 6 (no budget set).

| id | status | claim | decision it informs | falsified if | holdout result | goldfish | fresh data |
|---|---|---|---|---|---|---|---|
| T1 | **established** | January or February is the weakest month of the year for US tire-store sales |  | share of complete years with a Jan/Feb low < 0.80 | `#7` low_months={'1': 4, '2': 7, '4': 1}, share_jan_feb_low=0.917, years=12 | `#20` survived |  |
| T2 | **established** | Summer (Jun-Aug) tire-store sales run at least 8% (log points) above winter (Nov-Feb), after removing trend |  | mean gap < 0.08 or p >= 0.002 | `#9` mean_gap_logpts=0.1186, p_gap_gt_0.08=0.000122, years=13 | `#24` survived |  |
| T3 | **refuted** | Tire-store sales growth tracks growth in vehicle miles driven |  | rho < 0.3 or p >= 0.002 | `#11` n=154, p_circular=0.045, rho=0.2967 | `#21` falsified |  |
| T4 | **refuted** | Tire-store sales growth falls when unemployment rises |  | rho > -0.3 or p >= 0.002 | `#13` n=154, p_circular=0.11, rho=-0.2557 | `#19` falsified |  |
| T5 | **contested** | Tire price inflation (producer prices) shows up as higher nominal tire-store sales growth (expected to fail) |  | rho < 0.3 or p >= 0.002 | `#15` n=154, p_circular=0.0002, rho=0.3737 | `#22` falsified |  |
| T6 | **established** | Last year's same month, scaled by trailing 12-month growth, forecasts monthly tire-store sales within 4% MAPE and beats plain same-month-last-year |  | MAPE(drift) > 0.04 or not better than seasonal naive | `#17` mape_drift=0.0336, mape_naive=0.0491, months=142 | `#23` survived |  |

Statuses: **established** = survived holdout, replayed byte-identical, every goldfish agrees. **refuted** = falsified and confirmed the same way. **(narrowed)** = a goldfish found the claim holds only in a narrower reading; quote the narrowed version. **held / BROKE on fresh data** = the frozen test rerun on rows published after the seal. Anything else is not yet an insight.
