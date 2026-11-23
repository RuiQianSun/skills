# Insights: provinces_asof_2024-09.csv

Source sha256 `ecc821e173b0`, 249 rows, split seed 20261123 (136 explore / 113 holdout). Generated from `analysis/LEDGER.jsonl`; every figure below cites the ledger entry it came from.

Holdout looks: 11 of a budget of 16.
Data audit at seal: {"duplicate_keys": [], "empty_cells": {"mb": 72, "nb": 4, "nl": 72, "ns": 39, "pe": 72, "sk": 72}, "missing_months": []}.
Fresh window: 2024-10..2026-09 (24 rows, `#37`); 0 sealed rows revised at source.

## Descriptive

| id | kind | status | claim | decision it informs | falsified if | holdout result | goldfish | fresh data |
|---|---|---|---|---|---|---|---|---|
| D1 | seasonality | **refuted** | In every province, Oct+Nov take at least 18% of annual sales and more than Apr+May | Put the larger share of seasonal marketing into the fall changeover, not spring, in all six provinces | share of complete years where all six provinces meet both conditions < 0.80 | `#12` min_fall_minus_spring=-0.015, min_fall_share=0.1806, scored_from=None, share_years_fall_ge_18pct_and_above_spring=0.375, years=8 | `#49` falsified | `#38` 2024-10..2026-09: pending (24 of 36 fresh rows needed) |
| D2 | composition | **established (narrowed)** | The Prairies (MB+SK) are the majority of these six provinces' sales every year | Lead the six-province buying plan with Prairie demand | Prairie share <= 0.5 in any complete year | `#14` prairie_share_max=0.5686, prairie_share_min=0.5364, scored_from=None, years=8 | `#54` survived (narrowed: on annual totals in every complete calendar year; not in every month (2018-11 was 49.6%)) | `#39` 2024-10..2026-09: pending (24 of 36 fresh rows needed) |
| D4 | trend | **refuted** | The Prairie share of six-province sales is rising | Shift the regional buying budget toward the Prairies over time | gain < 1 pp or slope <= 0 | `#16` first3_mean=0.5517, last3_mean=0.5443, scored_from=None, slope_per_year=-0.00227, years=8 | `#53` falsified | `#40` 2024-10..2026-09: pending (24 of 60 fresh rows needed) |
| D3 | comparison | **established (narrowed)** | October takes a larger part of the fall rush in the Prairies than in Atlantic Canada, by at least 2 pp | Land Prairie fall stock earlier than Atlantic stock | share of years < 0.80 or mean gap < 2 pp | `#18` mean_gap_pp=3.57, scored_from=None, share_years_prairie_earlier=1.0, years=8 | `#57` survived (narrowed: the gap averages >= 2 pp and Prairie leads every year, but single-year gaps can be ~1 pp) | `#41` 2024-10..2026-09: pending (24 of 36 fresh rows needed) |

## Diagnostic

| id | kind | status | claim | decision it informs | falsified if | holdout result | goldfish | fresh data |
|---|---|---|---|---|---|---|---|---|
| G1 | attribution | **refuted** | Prairie growth outpaces Atlantic growth, not just Prairie size: Prairie sales grow faster for every endpoint pair 3+ years apart | Prioritise Prairie store expansion over Atlantic | any pair where Atlantic grew as fast or faster | `#20` atlantic_cagr=0.0956, endpoint_pairs=15, prairie_cagr=0.0776, scored_from=None, share_pairs_prairie_faster=0.333 | `#50` falsified | `#42` 2024-10..2026-09: pending (24 of 60 fresh rows needed) |
| G2 | driver | **established (narrowed)** | Prairie and Atlantic sales growth move together strongly, outside the COVID years (expected to fail) | Forecast both regions from one shared demand signal | rho < 0.5 or p >= 0.005 | `#22` n=77, p_circular=0.0002, rho=0.5416, scored_from=None | `#59` survived (narrowed: moderately (rho ~0.54), not strongly) | `#43` 2024-10..2026-09: pending (24 of 60 fresh rows needed) |

## Predictive

| id | kind | status | claim | decision it informs | falsified if | holdout result | goldfish | fresh data |
|---|---|---|---|---|---|---|---|---|
| F1 | forecast | **refuted, REVIVED on fresh data (recheck it)** | Same month last year scaled by trailing 12-month growth forecasts the six-province monthly total within 5% MAPE, at least 10% better than plain same-month-last-year | Use the drift forecast as the regional monthly baseline | MAPE(drift) > 0.05 or relative gain < 10% | `#24` mape_drift=0.0767, mape_naive=0.0865, months=89, relative_gain=0.1128, scored_from=None | `#51` falsified | `#44` 2024-10..2026-09: survived, mape_drift=0.0331, mape_naive=0.0477, months=24, relative_gain=0.307, scored_from=2024-10 |
| F2 | timing | **established** | November outsells October in each Atlantic province at least 75% of years | Default Atlantic fall staffing peak to November | any Atlantic province below 0.75 | `#26` hit_rate_nb=0.875, hit_rate_nl=1.0, hit_rate_ns=1.0, hit_rate_pe=1.0, scored_from=None, years=8 | `#56` survived | `#45` 2024-10..2026-09: pending (24 of 36 fresh rows needed) |
| F3 | forecast | **refuted** | Last year's fall (Oct+Nov) province shares predict this year's fall shares better than last year's annual shares do | Base fall allocation on fall history rather than annual history | mean relative error not lower | `#28` mean_rel_err_annual_share=0.0642, mean_rel_err_fall_share=0.0721, scored_from=None, years=7 | `#52` falsified | `#46` 2024-10..2026-09: pending (24 of 36 fresh rows needed) |

## Prescriptive

| id | kind | status | claim | decision it informs | falsified if | holdout result | goldfish | fresh data |
|---|---|---|---|---|---|---|---|---|
| R1 | policy (rests on F1) | **blocked: rests on F1 (refuted, REVIVED on fresh data (recheck it))** | Ordering fall stock at drift forecast + 5% beats the status quo (last year + 5%) when a shortfall costs 3x an overstock | Replace last-year-plus-buffer fall ordering with drift-plus-buffer | win rate < 0.70 or mean cost not lower | `#30` mean_cost_drift=0.0845, mean_cost_status_quo=0.1131, scored_from=None, win_rate=0.286, years=7 | `#58` falsified | `#47` 2024-10..2026-09: pending (24 of 36 fresh rows needed) |
| R2 | allocation (rests on F3) | **blocked: rests on F3 (refuted)** | Allocating fall stock by last year's fall shares cuts misallocated stock by at least 20% versus annual shares (expected to fail) | Switch fall allocation from annual shares to fall shares | win rate < 0.70 or cut < 20% | `#32` cut=-0.0685, misallocated_annual_share=0.0326, misallocated_fall_share=0.0349, scored_from=None, win_rate=0.571, years=7 | `#55` falsified | `#48` 2024-10..2026-09: pending (24 of 36 fresh rows needed) |

## Coverage

| category | kind | claims | waived |
|---|---|---|---|
| descriptive | level | **not covered** |  |
| descriptive | trend | D4 (refuted) |  |
| descriptive | seasonality | D1 (refuted) |  |
| descriptive | composition | D2 (established (narrowed)) |  |
| descriptive | comparison | D3 (established (narrowed)) |  |
| descriptive | distribution | **not covered** |  |
| descriptive | anomaly | **not covered** |  |
| descriptive | change-point | **not covered** |  |
| diagnostic | attribution | G1 (refuted) |  |
| diagnostic | driver | G2 (established (narrowed)) |  |
| diagnostic | causal |  | no intervention or policy change in these six provinces inside the data window; a provincial winter-tire mandate or tax change would unlock this |
| diagnostic | root-cause |  | the one explore anomaly (2012-09, six-province total) has no second observable in this data that an explanation would predict |
| predictive | forecast | F1 (refuted, REVIVED on fresh data (recheck it)); F3 (refuted) |  |
| predictive | leading-indicator | **not covered** |  |
| predictive | classification | **not covered** |  |
| predictive | timing | F2 (established) |  |
| prescriptive | policy | R1 (blocked: rests on F1 (refuted, REVIVED on fresh data (recheck it))) |  |
| prescriptive | allocation | R2 (blocked: rests on F3 (refuted)) |  |
| prescriptive | trigger |  | no outcome here that a metric-crossing trigger could be scored on; needs stock-out or weather data |

Statuses: **established** = survived holdout, replayed byte-identical, every goldfish agrees. **refuted** = falsified and confirmed the same way. **(narrowed)** = a goldfish found the claim holds only in a narrower reading; quote the narrowed version. **held / BROKE on fresh data** = the frozen test rerun on rows published after the seal. **blocked** = a prescriptive claim whose supporting claim is not established. Anything else is not yet an insight.
