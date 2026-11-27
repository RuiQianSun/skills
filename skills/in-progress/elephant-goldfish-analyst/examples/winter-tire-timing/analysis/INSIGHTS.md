# Insights: changeover_by_province.csv

Source sha256 `126324338ae5`, 160 rows, split seed 20261123 (80 explore / 80 holdout). Generated from `analysis/LEDGER.jsonl`; every figure below cites the ledger entry it came from.

Holdout looks: 7 of a budget of 12.
Data audit at seal: {"duplicate_keys": [], "empty_cells": {"first_snow_day": 39}}.

## Descriptive

| id | kind | status | claim | decision it informs | falsified if | holdout result | goldfish | fresh data |
|---|---|---|---|---|---|---|---|---|
| D1 | distribution | **falsified (no goldfish yet)** | Year-to-year swings in how much of the fall rush lands in October are material: the October share's standard deviation is at least 2 points in at least 6 of 10 provinces | Keep fall staffing and stock plans flexible between October and November rather than fixed by date | fewer than 6 provinces | `#4` provinces_sd_ge_2pp=5, scored_from=2018, sd_by_province={'ab': 0.0215, 'bc': 0.0318, 'mb': 0.0248, 'nb': 0.0222, 'nl': 0.0178, 'ns': 0.0152, 'on': 0.0202, 'pe': 0.0142, 'qc': 0.0186, 'sk': 0.0165} |  |  |

## Diagnostic

| id | kind | status | claim | decision it informs | falsified if | holdout result | goldfish | fresh data |
|---|---|---|---|---|---|---|---|---|
| G1 | driver | **survived (no goldfish yet)** | Within a province, a colder October moves with a larger share of the fall rush landing in October (association, judged after the season) | In post-season reviews, attribute October/November swings to October weather before blaming execution | any condition fails | `#11` p_within_perm=0.0005, provinces_same_sign=10, rho=-0.5293, rho_without_2020=-0.5426, scored_from=2018 |  |  |
| G2 | driver | **falsified (no goldfish yet)** | The 7 C crossing date adds timing information beyond October temperature (the 7 C rule as a trigger; expected to fail) | Use the 7 C crossing date as the trigger to pull staffing forward | partial correlation above -0.2 | `#13` n=80, partial_rho_given_oct_temp=0.1657, scored_from=2018 |  |  |
| G3 | driver | **falsified (no goldfish yet)** | Within a province, a warmer March moves with a larger share of the spring swap landing in April (association) | Expect April-heavy spring demand after warm Marches | any condition fails | `#21` p_within_perm=0.018, provinces_same_sign=9, rho=0.249, rho_without_2020=0.324, scored_from=2018 |  |  |

## Predictive

| id | kind | status | claim | decision it informs | falsified if | holdout result | goldfish | fresh data |
|---|---|---|---|---|---|---|---|---|
| F1 | leading-indicator | **falsified (no goldfish yet)** | By April 1, March temperature plus each province's history predicts the April share of the spring swap at least 10% and 0.2 points better than the province's historical average | Use March temperature to set the April/May split of spring staffing and stock | either condition fails in either version | `#26` all={'gain_pp': 0.15, 'mae_baseline': 0.02634, 'mae_model': 0.02484, 'rel_gain': 0.057, 'years': 8}, no2020={'gain_pp': 0.169, 'mae_baseline': 0.023, 'mae_model': 0.02131, 'rel_gain': 0.0734, 'years': 7}, scored_from=2018 |  |  |
| F2 | leading-indicator | **falsified (no goldfish yet)** | September temperature predicts the October share of the fall rush at least 10% better than the province's historical average (expected to fail) | Use September weather to pre-plan the October/November split | MAE above 0.9 x baseline | `#28` mae_baseline=0.02088, mae_model=0.02164, scored_from=2018, years=8 |  |  |

## Prescriptive

| id | kind | status | claim | decision it informs | falsified if | holdout result | goldfish | fresh data |
|---|---|---|---|---|---|---|---|---|
| P1 | allocation (rests on F1) | **blocked: rests on F1 (falsified (no goldfish yet))** | Splitting spring capacity between April and May by the March-temperature forecast, instead of each province's average split, cuts the cost of misallocation (under-planning April costs 2x over-planning) by at least 5% and wins in at least 60% of province-years | Adopt the March-temperature rule for the April/May split | either fails in either version | `#35` all={'cost_cut': 0.0817, 'province_years': 80, 'win_rate': 0.6}, no2020={'cost_cut': 0.1033, 'province_years': 70, 'win_rate': 0.571}, scored_from=2018 |  |  |

## Coverage

| category | kind | claims | waived |
|---|---|---|---|
| descriptive | level |  | levels, trends and peak months were covered in earlier runs on these tables; this run is about timing |
| descriptive | trend |  | levels, trends and peak months were covered in earlier runs on these tables; this run is about timing |
| descriptive | seasonality |  | levels, trends and peak months were covered in earlier runs on these tables; this run is about timing |
| descriptive | composition |  | levels, trends and peak months were covered in earlier runs on these tables; this run is about timing |
| descriptive | comparison |  | levels, trends and peak months were covered in earlier runs on these tables; this run is about timing |
| descriptive | distribution | D1 (falsified (no goldfish yet)) | levels, trends and peak months were covered in earlier runs on these tables; this run is about timing |
| descriptive | anomaly |  | levels, trends and peak months were covered in earlier runs on these tables; this run is about timing |
| descriptive | change-point |  | levels, trends and peak months were covered in earlier runs on these tables; this run is about timing |
| diagnostic | attribution |  | the target is a share of two months; there are no components to attribute |
| diagnostic | driver | G1 (survived (no goldfish yet)); G2 (falsified (no goldfish yet)); G3 (falsified (no goldfish yet)) |  |
| diagnostic | causal |  | no policy change inside 2010 to 2025; Quebec's mandate predates the data, so it cannot be studied as an intervention |
| diagnostic | root-cause |  | no anomaly under study |
| predictive | forecast |  | covered by the leading-indicator claims |
| predictive | leading-indicator | F1 (falsified (no goldfish yet)); F2 (falsified (no goldfish yet)) |  |
| predictive | classification |  | no class outcome in a province-year share |
| predictive | timing |  | monthly sales cannot time the rush within a month |
| prescriptive | policy |  | covered by the allocation claim |
| prescriptive | allocation | P1 (blocked: rests on F1 (falsified (no goldfish yet))) |  |
| prescriptive | trigger |  | the 7 C trigger was tested as G2 and adds nothing beyond October temperature |

Statuses: **established** = survived holdout, replayed byte-identical, every goldfish agrees. **refuted** = falsified and confirmed the same way. **(narrowed)** = a goldfish found the claim holds only in a narrower reading; quote the narrowed version. **held / BROKE on fresh data** = the frozen test rerun on rows published after the seal. **blocked** = a prescriptive claim whose supporting claim is not established. **seed-sensitive** = the verdict changes with the random seed (`seeds`), so it is not a finding. Anything else is not yet an insight.
