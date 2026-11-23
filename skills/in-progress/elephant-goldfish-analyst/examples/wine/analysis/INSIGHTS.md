# Insights: wine.csv

Source sha256 `a31b59070b81`, 178 rows, split seed 20261123 (89 explore / 89 holdout). Generated from `analysis/LEDGER.jsonl`; every figure below cites the ledger entry it came from.

| id | status | claim | falsified if | holdout result | goldfish |
|---|---|---|---|---|---|
| H1 | **established** | Flavanoids fall strictly by cultivar: 0 > 1 > 2 | order breaks, or either adjacent p >= 0.001 | `#4` median_0=2.82, median_1=1.97, median_2=0.66, p_0gt1=1.58e-09, p_1gt2=4.53e-09 | `#10` survived |
| H2 | **established** | Proline and color intensity alone identify the cultivar | CV accuracy < 0.85 | `#6` chance=0.4719, cv_accuracy=0.9105, fold_min=0.8333 | `#11` survived |
| H3 | **contested** | Cultivar 0 is at least 0.5 %vol more alcoholic than cultivar 2 (expected to fail) | median diff < 0.5 or p >= 0.001 | `#8` median_diff=0.825, p_0gt2=1.9e-05 | `#12` falsified |
| H3b | **refuted** | Cultivar 0 is at least 0.5 %vol more alcoholic than cultivar 2 (H3 corrected: p now tests shift > 0.5, not shift > 0) | median diff < 0.5 or p for a shift beyond 0.5 >= 0.001 | `#14` median_diff=0.825, p_shift_gt_0.5=0.127 | `#16` falsified |

Statuses: **established** = survived holdout, replayed byte-identical, every goldfish agrees. **refuted** = falsified and confirmed the same way. Anything else is not yet an insight.
