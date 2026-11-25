# Insights: vehicles_2012_2025.csv

Source sha256 `27ee2704cb0d`, 16285 rows, split seed 20261123 (9754 explore / 6531 holdout). Generated from `analysis/LEDGER.jsonl`; every figure below cites the ledger entry it came from.

Holdout looks: 10 of a budget of 12.
Data audit at seal: {"duplicate_keys": [], "empty_cells": {}}.

## Descriptive

| id | kind | status | claim | decision it informs | falsified if | holdout result | goldfish | fresh data |
|---|---|---|---|---|---|---|---|---|
| D1 | composition | **established** | Among non-hybrid configurations of 2.0 L or less, at least 60% are turbocharged in every model year | Treat small turbo engines as the mainstream configuration when planning fitments | any model year below 0.60 | `#7` by_year={'2020': 0.757, '2021': 0.776, '2022': 0.784, '2023': 0.826, '2024': 0.822, '2025': 0.797}, min_share=0.7567, scored_from=None, years=6 | `#14` survived |  |
| D2 | distribution | **established (narrowed)** | 30+ mpg configurations stay a niche: under 20% of each model year's configurations, and not rising by more than 1 pp a year | Size the high-MPG fitment line as a niche, not a mainstream line | any year >= 0.20, or slope > 1 pp/yr | `#9` max_share=0.1632, scored_from=None, slope_pp_per_year=0.748, years=6 | `#15` survived (narrowed: under 20% each year with a fitted trend near 0.75 pp a year, but single years rise faster (+2.3 pp 2024 to 2025)) |  |
| D3 | comparison | **established** | Like for like (same class and engine-size band, non-hybrid), front-wheel drive gets at least 1 mpg more than all-wheel drive every year, 1.5 on average | Quote a like-for-like AWD penalty, not the raw gap, in fitment guidance | any year below 1 mpg, or mean below 1.5 | `#11` mean_gap=3.458, min_gap=2.5, scored_from=None, years=6 | `#16` survived |  |

## Diagnostic

| id | kind | status | claim | decision it informs | falsified if | holdout result | goldfish | fresh data |
|---|---|---|---|---|---|---|---|---|
| G1 | driver | **established (narrowed)** | Within a vehicle class, non-hybrid MPG moves strongly with engine displacement (association, not cause) | Use engine size, not class alone, when estimating a new vehicle's MPG | fewer than 80% of such classes at rho <= -0.6 | `#19` classes=15, scored_from=None, share_rho_le_minus_0_6=0.8, weakest={'Small Pickup Trucks 4WD': -0.58, 'Small Sport Utility Vehicle 4WD': -0.55, 'Small Station Wagons': -0.312} | `#26` survived (narrowed: holds exactly at the 80% bar (12 of 15 classes): clearly for cars and standard SUVs and pickups, not for small 4WD SUVs, small 4WD pickups or small station wagons) |  |
| G2 | attribution | **established (narrowed)** | Falling fuel consumption comes more from configurations improving within each class than from the configuration mix shifting between classes | Track efficiency gains class by class rather than as a fleet-mix story | within-class cut < 0.1 gal/100 mi, or smaller than mix, or two or more adjacent pairs going the wrong way | `#21` adjacent_pairs_improving=5/5, first=2020, last=2025, mix_gal_per_100mi=0.1149, scored_from=None, within_gal_per_100mi=-0.194 | `#27` survived (narrowed: within-class improvement drove the whole net decline despite an adverse mix (+0.13 gal/100 mi), not two components both reducing consumption) |  |
| G2r | attribution | **refuted** | Among non-hybrid configurations alone, falling fuel consumption still comes more from within-class improvement than from the class mix | Credit efficiency gains to engine improvement, not only to hybrid substitution, when forecasting tire mix | within-class cut < 0.1, smaller than mix, or two or more adjacent pairs the wrong way | `#46` adjacent_pairs_improving=3/5, first=2020, last=2025, mix_gal_per_100mi=0.1131, scored_from=2020, within_gal_per_100mi=-0.0565 | `#59` falsified |  |

## Predictive

| id | kind | status | claim | decision it informs | falsified if | holdout result | goldfish | fresh data |
|---|---|---|---|---|---|---|---|---|
| F1 | forecast | **established** | From specs alone, a model trained on model years up to two years earlier predicts the combined MPG of never-before-seen configurations within 2.0 mpg on average, and beats a similar-spec median | Estimate MPG for new configurations from specs before EPA ratings are published | mean MAE > 2.0, any year > 2.5, or any year above 0.85 x baseline | `#29` by_year={'2022': {'baseline': 2.21, 'mae': 1.68, 'new_configs': 140}, '2023': {'baseline': 3.26, 'mae': 1.93, 'new_configs': 109}, '2024': {'baseline': 3.12, 'mae': 1.81, 'new_configs': 90}, '2025': {'baseline': 3.39, 'mae': 2.19, 'new_configs': 90}}, mean_mae=1.9, scored_from=None, years=4 | `#41` survived |  |
| F1r | forecast | **refuted** | Trained on every model year up to two years earlier, without make as a predictor, a spec model predicts the combined MPG of never-before-seen configurations within 2.0 mpg on average and beats a similar-spec median | Estimate MPG for new configurations from specs before EPA ratings are published | mean MAE > 2.0, any year > 2.5, or any year above 0.85 x baseline | `#51` by_year={'2020': {'baseline': 3.14, 'mae': 2.43, 'new_configs': 108}, '2021': {'baseline': 3.14, 'mae': 2.04, 'new_configs': 141}, '2022': {'baseline': 2.34, 'mae': 1.88, 'new_configs': 131}, '2023': {'baseline': 3.34, 'mae': 2.34, 'new_configs': 100}, '2024': {'baseline': 3.25, 'mae': 1.74, 'new_configs': 89}, '2025': {'baseline': 3.18, 'mae': 2.15, 'new_configs': 89}}, mean_mae=2.095, scored_from=2020, years=6 | `#60` falsified |  |

## Prescriptive

| id | kind | status | claim | decision it informs | falsified if | holdout result | goldfish | fresh data |
|---|---|---|---|---|---|---|---|---|
| P1b | policy (rests on F1) | **established** | Flagging new configurations the model predicts at 30+ mpg as low-rolling-resistance tire targets creates value (+5 or more a year) and beats both status-quo rules on payoff | Use the model's 30+ mpg flag to choose LRR fitment targets for new configurations | payoff < 5 in more than a quarter of years, total not above both rules, or wins in < 75% of years | `#38` scored_from=None, share_years_payoff_ge_5=0.75, total_payoff={'hybrid_or_small_car': -102, 'hybrids_only': -101, 'model': 31}, win_rate=1.0, years=4 | `#42` survived |  |
| P1r | policy (rests on F1r) | **blocked: rests on F1r (refuted)** | Using the full-history model, flagging never-before-seen configurations predicted at 30+ mpg as LRR tire targets earns a positive payoff in most years, beats flagging nothing and both status-quo rules, and stays positive at cutoffs of 29 and 31 mpg | Use the model's 30+ mpg flag to choose LRR fitment targets for new configurations | any of those fails | `#56` by_year={'2020': {'cut29': 16, 'cut30': 12, 'cut31': 10, 'flagged': 16, 'hybrid_or_small_car': 5, 'hybrids_only': -5}, '2021': {'cut29': 8, 'cut30': 5, 'cut31': 6, 'flagged': 9, 'hybrid_or_small_car': -25, 'hybrids_only': -27}, '2022': {'cut29': 7, 'cut30': 8, 'cut31': 5, 'flagged': 10, 'hybrid_or_small_car': -36, 'hybrids_only': -37}, '2023': {'cut29': 11, 'cut30': 11, 'cut31': 10, 'flagged': 15, 'hybrid_or_small_car': -26, 'hybrids_only': -24}, '2024': {'cut29': 8, 'cut30': 8, 'cut31': 9, 'flagged': 12, 'hybrid_or_small_car': -27, 'hybrids_only': -27}, '2025': {'cut29': 4, 'cut30': 4, 'cut31': 5, 'flagged': 6, 'hybrid_or_small_car': -13, 'hybrids_only': -13}}, scored_from=2020, totals={'cut29': 54, 'cut30': 48, 'cut31': 45, 'flagged': 68, 'hybrid_or_small_car': -122, 'hybrids_only': -133}, years=6 | `#61` survived |  |

## Coverage

| category | kind | claims | waived |
|---|---|---|---|
| descriptive | level | **not covered** |  |
| descriptive | trend | **not covered** |  |
| descriptive | seasonality | **not covered** |  |
| descriptive | composition | D1 (established) |  |
| descriptive | comparison | D3 (established) |  |
| descriptive | distribution | D2 (established (narrowed)) |  |
| descriptive | anomaly | **not covered** |  |
| descriptive | change-point | **not covered** |  |
| diagnostic | attribution | G2 (established (narrowed)); G2r (refuted) |  |
| diagnostic | driver | G1 (established (narrowed)) |  |
| diagnostic | causal |  | no intervention or natural experiment in the data; turbo adoption, CAFE and class mix move together |
| diagnostic | root-cause |  | no anomaly found in exploration that needed explaining |
| predictive | forecast | F1 (established); F1r (refuted) |  |
| predictive | leading-indicator |  | cross-sectional specs; no series that leads another |
| predictive | classification | **not covered** |  |
| predictive | timing |  | no events to time in annual configuration data |
| prescriptive | policy | P1b (established); P1r (blocked: rests on F1r (refuted)) |  |
| prescriptive | allocation |  | no volumes or budgets to allocate |
| prescriptive | trigger |  | no time-varying metric to trigger on |

Statuses: **established** = survived holdout, replayed byte-identical, every goldfish agrees. **refuted** = falsified and confirmed the same way. **(narrowed)** = a goldfish found the claim holds only in a narrower reading; quote the narrowed version. **held / BROKE on fresh data** = the frozen test rerun on rows published after the seal. **blocked** = a prescriptive claim whose supporting claim is not established. Anything else is not yet an insight.
