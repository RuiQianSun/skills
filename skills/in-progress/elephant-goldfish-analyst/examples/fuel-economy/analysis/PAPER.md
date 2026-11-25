# What Drives US Vehicle Fuel Economy, 2012 to 2025

*Generated from the evidence ledger `analysis/LEDGER.jsonl` (head `268450fe9ad3c34c`, 43 entries, chain intact). Every number below cites the ledger entry it came from as `#n`. To check this paper, run `python3 ledger.py audit`, which re-executes every result.*

## Abstract

We registered 7 claims before testing them on held-out data, across 4 insight categories. 7 were established, 0 refuted, and 0 remain open (contested, blocked or untested).

Established findings:

- **D1** (descriptive/composition): Among non-hybrid configurations of 2.0 L or less, at least 60% are turbocharged in every model year
- **D2** (descriptive/distribution): 30+ mpg configurations stay a niche: under 20% of each model year's configurations, and not rising by more than 1 pp a year *Narrowed to: under 20% each year with a fitted trend near 0.75 pp a year, but single years rise faster (+2.3 pp 2024 to 2025).*
- **D3** (descriptive/comparison): Like for like (same class and engine-size band, non-hybrid), front-wheel drive gets at least 1 mpg more than all-wheel drive every year, 1.5 on average
- **G1** (diagnostic/driver): Within a vehicle class, non-hybrid MPG moves strongly with engine displacement (association, not cause) *Narrowed to: holds exactly at the 80% bar (12 of 15 classes): clearly for cars and standard SUVs and pickups, not for small 4WD SUVs, small 4WD pickups or small station wagons.*
- **G2** (diagnostic/attribution): Falling fuel consumption comes more from configurations improving within each class than from the configuration mix shifting between classes *Narrowed to: within-class improvement drove the whole net decline despite an adverse mix (+0.13 gal/100 mi), not two components both reducing consumption.*
- **F1** (predictive/forecast): From specs alone, a model trained on model years up to two years earlier predicts the combined MPG of never-before-seen configurations within 2.0 mpg on average, and beats a similar-spec median
- **P1b** (prescriptive/policy): Flagging new configurations the model predicts at 30+ mpg as low-rolling-resistance tire targets creates value (+5 or more a year) and beats both status-quo rules on payoff

## 1. Data

- Source: `vehicles_2012_2025.csv`, sha256 `27ee2704cb0d46c4`, 16285 rows, 19 columns.
- Split (`#0`): ordered by year, seed 20261123; 9754 rows for exploration, 6531 sealed for confirmation (exploration up to 2019).
- Data audit before sealing: {"duplicate_keys": [], "empty_cells": {}}.

### 1.1 Variables (`#3`, confirmed by the user (domain owner for this demo), 2026-11-25)

| role | columns | meaning |
|---|---|---|
| exclude | city_mpg, highway_mpg, co2_g_per_mile, annual_fuel_cost, barrels_per_year, five_year_savings | unusable or leaky: recorded after the outcome, a duplicate of the target, or junk (city_mpg: a component of the target; highway_mpg: a component of the target; co2_g_per_mile: calculated from MPG; annual_fuel_cost: calculated from MPG; barrels_per_year: calculated from MPG; five_year_savings: calculated from MPG) |
| feature | make, vclass, drive, transmission, cylinders, displ, turbo, supercharger, hybrid, fuel | independent variable: a candidate explanation or predictor |
| key | id | an identifier; never a predictor |
| segment | vclass, make | a grouping used to slice results (can also be a feature) |
| target | comb_mpg | dependent variable: the outcome the analysis explains or predicts |
| time | year | the order key for time series |

Rows are vehicle configurations, not sales; every configuration counts once regardless of how many were sold.

## 2. Methods

Each claim was written down with its kill criterion and the decision it informs, reviewed by a critic agent that saw no data, and frozen (its test script hashed) before its single look at the sealed holdout. Registration required the test to pass a lint for future-peeking and leaky code, a smoke run on exploration data, and a mutation gate: on copies of the data with the claimed pattern destroyed, the test had to report falsified at least 4 times in 5. Results were replayed byte-for-byte, then replicated by independent agents who saw only the claim and the holdout and wrote their own method. Prescriptive claims count only if the claim they rest on is established.

- Holdout looks used: 7 of a budget of 12.
- Claims registered: 7; attempts refused by the gates: 1 (together, the multiple-comparisons count; thresholds were set per claim at registration).
- Replicating agents: goldfish-D1-sonnet, goldfish-D2, goldfish-D3-sonnet, goldfish-F1-sonnet, goldfish-G1-sonnet, goldfish-G2, goldfish-P1b.
- Stage log: `#13` close descriptive; `#25` close diagnostic; `#33` close predictive; `#40` close prescriptive.

## 3. Results

### 3.1 Descriptive

#### D1: Among non-hybrid configurations of 2.0 L or less, at least 60% are turbocharged in every model year

- **Status: established.** Type descriptive/composition.
- Decision it informs: Treat small turbo engines as the mainstream configuration when planning fitments.
- Pre-registered (`#4`): predicted small-engine turbo share >= 0.60 each year; falsified if any model year below 0.60. Test `analysis/tests/D1.py` sha `16f31714262f`.
- Gates: smoke run on exploration data falsified; mutant permute:turbo killed 5/5 (uninformative).
- Holdout result (`#7`): **survived**, by_year={'2020': 0.757, '2021': 0.776, '2022': 0.784, '2023': 0.826, '2024': 0.822, '2025': 0.797}, min_share=0.7567, years=6. Replay `#8` byte-identical.
- Replication by goldfish-D1-sonnet (`#14`): survived (agrees); method: per-year share of turbo==1 among hybrid==0 & displ<=2.0, compared directly to 0.60; bootstrap CI for context; by_year={'2020': {'boot95': [0.7112, 0.7995], 'n': 374, 'share': 0.7567, 'share_incl_supercharger': 0.7567, 'turbo': 283}, '2021': {'boot95': [0.7328, 0.819], 'n': 348, 'share': 0.7759, 'share_incl_supercharger': 0.7759, 'turbo': 270}, '2022': {'boot95': [0.7378, 0.8262], 'n': 328, 'share': 0.7835, 'share_incl_supercharger': 0.7835, 'turbo': 257}, '2023': {'boot95': [0.7805, 0.8676], 'n': 287, 'share': 0.8258, 'share_incl_supercharger': 0.8258, 'turbo': 237}, '2024': {'boot95': [0.7671, 0.8721], 'n': 219, 'share': 0.8219, 'share_incl_supercharger': 0.8219, 'turbo': 180}, '2025': {'boot95': [0.738, 0.8556], 'n': 187, 'share': 0.7968, 'share_incl_supercharger': 0.7968, 'turbo': 149}}, min_share=0.7567, years_below_060=[]. Reviewer note: read 2.0 L or less as displ <= 2.0 inclusive; unweighted configurations

#### D2: 30+ mpg configurations stay a niche: under 20% of each model year's configurations, and not rising by more than 1 pp a year

- **Status: established (narrowed).** Type descriptive/distribution.
- Decision it informs: Size the high-MPG fitment line as a niche, not a mainstream line.
- Pre-registered (`#5`): predicted share < 0.20 every year, fitted slope <= 1 pp/yr; falsified if any year >= 0.20, or slope > 1 pp/yr. Test `analysis/tests/D2.py` sha `ab495087b3bd`.
- Gates: smoke run on exploration data survived; no mutant: a share of the marginal distribution; no structure to destroy.
- Holdout result (`#9`): **survived**, max_share=0.1632, slope_pp_per_year=0.748, years=6. Replay `#10` byte-identical.
- Replication by goldfish-D2 (`#15`): survived (agrees); method: per-year share of configs with comb_mpg>=30; max-share check vs 20%; OLS slope of yearly share on year (pp/yr) vs 1 pp, with count-weighted slope and within-year bootstrap 95% CI as sensitivity; bootstrap_frac_slope_gt_1pp=0.162, bootstrap_slope_ci95_pp=[0.225, 1.26], last2_year_change_pp=2.3, max_share_pct=16.32, n_by_year={'2020': 1171, '2021': 1180, '2022': 1183, '2023': 1137, '2024': 984, '2025': 876}, ols_slope_pp_per_year=0.748, share_pct_by_year={'2020': 12.3, '2021': 12.03, '2022': 12.85, '2023': 12.93, '2024': 14.02, '2025': 16.32}, weighted_slope_pp_per_year=0.713, years=[2020, 2021, 2022, 2023, 2024, 2025]. Reviewer note: read 'not rising by more than 1 pp a year' as the fitted trend; year by year it fails Narrowed: under 20% each year with a fitted trend near 0.75 pp a year, but single years rise faster (+2.3 pp 2024 to 2025).

#### D3: Like for like (same class and engine-size band, non-hybrid), front-wheel drive gets at least 1 mpg more than all-wheel drive every year, 1.5 on average

- **Status: established.** Type descriptive/comparison.
- Decision it informs: Quote a like-for-like AWD penalty, not the raw gap, in fitment guidance.
- Pre-registered (`#6`): predicted median stratum gap >= 1 every year, mean >= 1.5; falsified if any year below 1 mpg, or mean below 1.5. Test `analysis/tests/D3.py` sha `84cc1714f953`.
- Gates: smoke run on exploration data survived; mutant permute:drive killed 5/5.
- Holdout result (`#11`): **survived**, mean_gap=3.458, min_gap=2.5, years=6. Replay `#12` byte-identical.
- Replication by goldfish-D3-sonnet (`#16`): survived (agrees); method: non-hybrid FWD vs AWD only; strata = vclass x displ band (8 bands) x year; per-year gap = weighted mean of FWD-AWD cell mean differences, weight=min(nF,nA); within-year bootstrap (300) 90% intervals; avg_gap=3.932, avg_gap_boot_p5=3.619, boot90_hi=[4.257, 4.28, 4.641, 5.069, 4.849, 5.749], boot90_lo=[2.964, 2.969, 3.227, 3.247, 3.09, 3.678], cell_median_gap_by_year={'2020': 2.25, '2021': 2.421, '2022': 3.686, '2023': 3.482, '2024': 4.042, '2025': 4.417}, cells_by_year={'2020': 17, '2021': 12, '2022': 10, '2023': 10, '2024': 11, '2025': 9}, gap_by_year={'2020': 3.526, '2021': 3.491, '2022': 3.776, '2023': 4.071, '2024': 3.943, '2025': 4.786}. Reviewer note: chose 8 displacement bands and a count-weighted cell mean; AWD = the All-Wheel Drive label only


### 3.2 Diagnostic

#### G1: Within a vehicle class, non-hybrid MPG moves strongly with engine displacement (association, not cause)

- **Status: established (narrowed).** Type diagnostic/driver.
- Decision it informs: Use engine size, not class alone, when estimating a new vehicle's MPG.
- Pre-registered (`#17`): predicted Spearman rho(displ, comb_mpg) <= -0.6 in at least 80% of classes with 50+ non-hybrid configurations; falsified if fewer than 80% of such classes at rho <= -0.6. Test `analysis/tests/G1.py` sha `558d7e98cb28`.
- Gates: smoke run on exploration data survived; mutant permute:comb_mpg killed 5/5.
- Holdout result (`#19`): **survived**, classes=15, share_rho_le_minus_0_6=0.8, weakest={'Small Pickup Trucks 4WD': -0.58, 'Small Sport Utility Vehicle 4WD': -0.55, 'Small Station Wagons': -0.312}. Replay `#20` byte-identical.
- Replication by goldfish-G1-sonnet (`#26`): survived (agrees); method: Spearman rho(displ, comb_mpg) per vclass among hybrid==0, classes n>=50; strong = rho<=-0.6; survive if >=80% strong; fraction_strong=0.8, n_classes=15, n_strong=12, per_class={'Compact Cars': {'n': 454, 'rho': -0.822}, 'Large Cars': {'n': 334, 'rho': -0.909}, 'Midsize Cars': {'n': 632, 'rho': -0.776}, 'Minicompact Cars': {'n': 239, 'rho': -0.884}, 'Small Pickup Trucks 4WD': {'n': 74, 'rho': -0.58}, 'Small Sport Utility Vehicle 2WD': {'n': 393, 'rho': -0.642}, 'Small Sport Utility Vehicle 4WD': {'n': 861, 'rho': -0.55}, 'Small Station Wagons': {'n': 89, 'rho': -0.312}, 'Special Purpose Vehicle 2WD': {'n': 83, 'rho': -0.659}, 'Standard Pickup Trucks 2WD': {'n': 177, 'rho': -0.794}, 'Standard Pickup Trucks 4WD': {'n': 392, 'rho': -0.634}, 'Standard Sport Utility Vehicle 2WD': {'n': 237, 'rho': -0.9}, 'Standard Sport Utility Vehicle 4WD': {'n': 583, 'rho': -0.753}, 'Subcompact Cars': {'n': 494, 'rho': -0.88}, 'Two Seaters': {'n': 375, 'rho': -0.872}}. Narrowed: holds exactly at the 80% bar (12 of 15 classes): clearly for cars and standard SUVs and pickups, not for small 4WD SUVs, small 4WD pickups or small station wagons.

#### G2: Falling fuel consumption comes more from configurations improving within each class than from the configuration mix shifting between classes

- **Status: established (narrowed).** Type diagnostic/attribution.
- Decision it informs: Track efficiency gains class by class rather than as a fleet-mix story.
- Pre-registered (`#18`): predicted midpoint shift-share on gal/100 mi: within-class cut >= 0.1 and larger than the mix term; within-class negative in all but at most one adjacent-year pair; falsified if within-class cut < 0.1 gal/100 mi, or smaller than mix, or two or more adjacent pairs going the wrong way. Test `analysis/tests/G2.py` sha `b5ce031180ed`.
- Gates: smoke run on exploration data survived; mutant permute:year killed 5/5.
- Holdout result (`#21`): **survived**, adjacent_pairs_improving=5/5, first=2020, last=2025, mix_gal_per_100mi=0.1149, within_gal_per_100mi=-0.194. Replay `#22` byte-identical.
- Replication by goldfish-G2 (`#27`): survived (agrees); method: symmetric (midpoint-weight) shift-share of mean gallons/100mi across vclass, first vs last model year, plus each adjacent-year pair; entry/exit classes split out; 1000x within-year bootstrap for CIs; adjacent_pairs={'2020-2021': {'entry_exit': 0.0, 'mix': 0.068, 'total': 0.0564, 'within': -0.0116}, '2021-2022': {'entry_exit': 0.0, 'mix': 0.0419, 'total': 0.0113, 'within': -0.0305}, '2022-2023': {'entry_exit': -0.0103, 'mix': 0.0109, 'total': 0.0003, 'within': -0.0003}, '2023-2024': {'entry_exit': -0.0, 'mix': 0.0214, 'total': -0.0433, 'within': -0.0647}, '2024-2025': {'entry_exit': 0.0, 'mix': -0.0101, 'total': -0.1039, 'within': -0.0938}}, entry_exit_change=-0.0104, fail_pairs=False, fail_within_smaller_than_mix=False, fail_within_under_0.1=False, max_consecutive_wrong_way=0, mean_gpm_first=4.5891, mean_gpm_last=4.5099, mix_change=0.1252, mix_ci95=[0.0617, 0.2091], n_pairs_within_wrong_way=0, total_change=-0.0791, within_change=-0.194, within_ci95=[-0.2768, -0.1013], years=[2020, 2025]. Narrowed: within-class improvement drove the whole net decline despite an adverse mix (+0.13 gal/100 mi), not two components both reducing consumption.


### 3.3 Predictive

#### F1: From specs alone, a model trained on model years up to two years earlier predicts the combined MPG of never-before-seen configurations within 2.0 mpg on average, and beats a similar-spec median

- **Status: established.** Type predictive/forecast.
- Decision it informs: Estimate MPG for new configurations from specs before EPA ratings are published.
- Pre-registered (`#28`): predicted mean MAE <= 2.0, no year above 2.5, and MAE <= 0.85 x the similar-spec baseline in every year; falsified if mean MAE > 2.0, any year > 2.5, or any year above 0.85 x baseline. Test `analysis/tests/F1.py` sha `8feb0f9c2b8f`.
- Gates: smoke run on exploration data survived; mutant permute:comb_mpg killed 5/5.
- Holdout result (`#29`): **survived**, by_year={'2022': {'baseline': 2.21, 'mae': 1.68, 'new_configs': 140}, '2023': {'baseline': 3.26, 'mae': 1.93, 'new_configs': 109}, '2024': {'baseline': 3.12, 'mae': 1.81, 'new_configs': 90}, '2025': {'baseline': 3.39, 'mae': 2.19, 'new_configs': 90}}, mean_mae=1.9, years=4. Replay `#30` byte-identical.
- Replication by goldfish-F1-sonnet (`#41`): survived (agrees); method: HistGradientBoosting on one-hot specs, train years<=Y-2, test = year-Y configs whose full spec tuple not seen in any year<Y; baseline median by class/cyl/turbo/hybrid/drive with coarser fallback; avg_mae=1.8035941688563417, per_year={'2022': {'base_mae': 2.3892857142857142, 'mae': 1.5971127697550762, 'n': 140, 'ratio': 0.6684477960110932}, '2023': {'base_mae': 3.091743119266055, 'mae': 1.9665341221843247, 'n': 109, 'ratio': 0.6360599979765323}, '2024': {'base_mae': 3.2944444444444443, 'mae': 1.628408415727839, 'n': 90, 'ratio': 0.4942892324300354}, '2025': {'base_mae': 3.172222222222222, 'mae': 2.022321367758127, 'n': 90, 'ratio': 0.6375093628659595}}. Reviewer note: read 'never seen' as absent from every year before Y; baseline falls back to coarser medians when a group is empty; only 4 test years, and 2023 and 2025 sit near 2.0


### 3.4 Prescriptive

#### P1b: Flagging new configurations the model predicts at 30+ mpg as low-rolling-resistance tire targets creates value (+5 or more a year) and beats both status-quo rules on payoff

- **Status: established.** Type prescriptive/policy, rests on F1.
- Decision it informs: Use the model's 30+ mpg flag to choose LRR fitment targets for new configurations.
- Pre-registered (`#37`): predicted payoff (+1 correct target, -1 wrong target) >= 5 in >= 75% of years, total above both rules, and above both in >= 75% of years; falsified if payoff < 5 in more than a quarter of years, total not above both rules, or wins in < 75% of years. Test `analysis/tests/P1b.py` sha `0c5f7e04fd2f`.
- Gates: smoke run on exploration data survived; mutant permute:comb_mpg killed 5/5.
- Holdout result (`#38`): **survived**, share_years_payoff_ge_5=0.75, total_payoff={'hybrid_or_small_car': -102, 'hybrids_only': -101, 'model': 31}, win_rate=1.0, years=4. Replay `#39` byte-identical.
- Replication by goldfish-P1b (`#42`): survived (agrees); method: Expanding-window by year: HistGradientBoostingRegressor (native categoricals) on 10 spec columns trained on years <= Y-2; test on year-Y configs whose full 10-field spec never appeared in any earlier year; flag pred>=30; +1/-1 payoff vs real comb_mpg>=30; rules applied to same novel set; car/wagon = vclass containing 'Cars' or 'Wagons'.; frac_years_beats_both=1.0, frac_years_payoff_ge5=1.0, per_year=[{'beats_both': True, 'hybrid_or_small_car': -36, 'hybrids_only': -37, 'model': 7, 'n_flag': 11, 'n_novel': 140, 'year': 2022}, {'beats_both': True, 'hybrid_or_small_car': -26, 'hybrids_only': -24, 'model': 10, 'n_flag': 14, 'n_novel': 109, 'year': 2023}, {'beats_both': True, 'hybrid_or_small_car': -27, 'hybrids_only': -27, 'model': 6, 'n_flag': 10, 'n_novel': 90, 'year': 2024}, {'beats_both': True, 'hybrid_or_small_car': -13, 'hybrids_only': -13, 'model': 5, 'n_flag': 5, 'n_novel': 90, 'year': 2025}], sensitivity_novel_vs_training_window_only={'frac_years_beats_both': 1.0, 'frac_years_payoff_ge5': 1.0, 'per_year': [{'beats_both': True, 'hybrid_or_small_car': -61, 'hybrids_only': -60, 'model': 17, 'n_flag': 25, 'n_novel': 308, 'year': 2022}, {'beats_both': True, 'hybrid_or_small_car': -55, 'hybrids_only': -54, 'model': 19, 'n_flag': 23, 'n_novel': 243, 'year': 2023}, {'beats_both': True, 'hybrid_or_small_car': -50, 'hybrids_only': -48, 'model': 18, 'n_flag': 22, 'n_novel': 183, 'year': 2024}, {'beats_both': True, 'hybrid_or_small_car': -47, 'hybrids_only': -47, 'model': 10, 'n_flag': 12, 'n_novel': 181, 'year': 2025}], 'totals': {'hybrid_or_small_car': -213, 'hybrids_only': -209, 'model': 64}, 'verdict': 'survived'}, test_years=[2022, 2023, 2024, 2025], totals={'hybrid_or_small_car': -102, 'hybrids_only': -101, 'model': 28}. Reviewer note: test years 2022 to 2025 only; 2025 sits exactly at the +5 payoff bar, so one more miss would break it; holds under both readings of 'never seen before'

## 4. Threats to validity

- Not testable with this data: diagnostic/causal: no intervention or natural experiment in the data; turbo adoption, CAFE and class mix move together
- Not testable with this data: diagnostic/root-cause: no anomaly found in exploration that needed explaining
- Not testable with this data: predictive/leading-indicator: cross-sectional specs; no series that leads another
- Not testable with this data: predictive/timing: no events to time in annual configuration data
- Not testable with this data: prescriptive/allocation: no volumes or budgets to allocate
- Not testable with this data: prescriptive/trigger: no time-varying metric to trigger on
- Descriptive kinds left open at close (`#13`): level, trend, seasonality, anomaly, change-point. level, trend, seasonality, anomaly and change-point left open: this demo keeps two to three claims per stage; seasonality does not apply to annual model-year data
- Predictive kinds left open at close (`#33`): classification. classification is covered inside P1's 30 mpg flag rather than as a separate claim
- D1 already failed on exploration data before registration, so its mutation gate says nothing.
- Refused at registration (`#36`, mutation gate): P1, "Flagging new configurations the model predicts at 30+ mpg as low-rolling-resistance tire targets beats both status-quo rules (hybrids only; hybrid or small non-turbo car) on payoff". the test has no teeth against permute:comb_mpg: it falsified only 0 of 5 mutants. Tighten the test or the threshold, or pick a mutant that really destroys what the claim asserts
- Analyst notes: see `NOTES.md`.

## 5. Peer review

- Critic review before testing: `analysis/reviews/descriptive.md`.
- Critic review before testing: `analysis/reviews/diagnostic.md`.
- Critic review before testing: `analysis/reviews/predictive.md`.

## Appendix A. Reproduce

```bash
python3 ledger.py verify
```

```bash
python3 ledger.py audit
```

`audit` re-runs every frozen test and every replication against the sealed data and checks each output is byte-identical to the recorded one. It changes nothing and writes `AUDIT.md`.

## Appendix B. Ledger index

| # | entry | claim | hash |
|---|---|---|---|
| 0 | init |  | `e112a382d01d` |
| 1 | profile |  | `f331a9d1c049` |
| 2 | profile |  | `c51dc5e89239` |
| 3 | schema |  | `540f6f8b5d04` |
| 4 | register | D1 | `2cbd5386eeca` |
| 5 | register | D2 | `50ae45e65842` |
| 6 | register | D3 | `3dd2724b40dc` |
| 7 | run | D1 | `d10c0f541a39` |
| 8 | replay | D1 | `7ac35f32fa6e` |
| 9 | run | D2 | `dcf5f3f79446` |
| 10 | replay | D2 | `e8c235b106e2` |
| 11 | run | D3 | `1b896175558f` |
| 12 | replay | D3 | `af407d9afdfc` |
| 13 | close | descriptive | `eb23cf019db0` |
| 14 | goldfish | D1 | `2b4d0217bfe1` |
| 15 | goldfish | D2 | `aeda536ba9af` |
| 16 | goldfish | D3 | `e3788f9fbf53` |
| 17 | register | G1 | `cd9f6667a046` |
| 18 | register | G2 | `a53435808860` |
| 19 | run | G1 | `87fda74ff84b` |
| 20 | replay | G1 | `655013623175` |
| 21 | run | G2 | `aa90982cfffd` |
| 22 | replay | G2 | `321c21f951dd` |
| 23 | waive |  | `f16a50534ceb` |
| 24 | waive |  | `17a2c4afb32e` |
| 25 | close | diagnostic | `5e715a417df1` |
| 26 | goldfish | G1 | `1ce34afccc62` |
| 27 | goldfish | G2 | `e6c3f352d60d` |
| 28 | register | F1 | `379ad73b00e4` |
| 29 | run | F1 | `e76d78cb0b97` |
| 30 | replay | F1 | `32b7b109e5cd` |
| 31 | waive |  | `bb268b301b6b` |
| 32 | waive |  | `3adfcd67d8b7` |
| 33 | close | predictive | `61c63035d762` |
| 34 | waive |  | `db5d11c59df3` |
| 35 | waive |  | `3e10680c08e8` |
| 36 | refused | P1 | `b56aad0e13ad` |
| 37 | register | P1b | `650f382cba61` |
| 38 | run | P1b | `2b80a6e7d91f` |
| 39 | replay | P1b | `942db650806f` |
| 40 | close | prescriptive | `35e9098e91da` |
| 41 | goldfish | F1 | `f426a84e1cf7` |
| 42 | goldfish | P1b | `268450fe9ad3` |
