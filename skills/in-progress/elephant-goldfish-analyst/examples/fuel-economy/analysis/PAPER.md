# What Drives US Vehicle Fuel Economy, 2020 to 2025

*Generated from the evidence ledger `analysis/LEDGER.jsonl` (head `e8055e44389087cb`, 89 entries, chain intact). Every number below cites the ledger entry it came from as `#n`. To check this paper, run `python3 ledger.py audit`, which re-executes every result.*

## Abstract

All findings below are about year 2020 to 2025, the period sealed before analysis; earlier periods were used only to form hypotheses. We registered 11 claims before testing them on held-out data, across 4 insight categories. 4 stand as established, 3 were refuted, 3 were superseded by later tests, and 1 is open (contested, blocked, seed-sensitive or untested).

Established without qualification:

- **D1** (descriptive/composition): Among non-hybrid configurations of 2.0 L or less, at least 60% are turbocharged in every model year
- **D3** (descriptive/comparison): Like for like (same class and engine-size band, non-hybrid), front-wheel drive gets at least 1 mpg more than all-wheel drive every year, 1.5 on average

Established only with qualifications (read these before acting):

- **D2** (descriptive/distribution): 30+ mpg configurations stay a niche: under 20% of each model year's configurations, and not rising by more than 1 pp a year *holds only as narrowed by its tester: under 20% each year with a fitted trend near 0.75 pp a year, but single years rise faster (+2.3 pp 2024 to 2025).*
- **G1** (diagnostic/driver): Within a vehicle class, non-hybrid MPG moves strongly with engine displacement (association, not cause) *holds only as narrowed by its tester: holds exactly at the 80% bar (12 of 15 classes): clearly for cars and standard SUVs and pickups, not for small 4WD SUVs, small 4WD pickups or small station wagons.*

Superseded by later tests (do not act on these as worded):

- **G2** (passed its own test): Falling fuel consumption comes more from configurations improving within each class than from the configuration mix shifting between classes *superseded by G2r (refuted): among non-hybrids the within-class gain is smaller than the mix effect, so G2's within-class improvement is mostly hybrid substitution; decision withdrawn: efficiency gains cannot be tracked class by class as engine improvement: most of the within-class gain was hybrids replacing non-hybrids (G2r).*
- **F1** (passed its own test): From specs alone, a model trained on model years up to two years earlier predicts the combined MPG of never-before-seen configurations within 2.0 mpg on average, and beats a similar-spec median *superseded by F1h (refuted): F1 was scored on 2022 to 2025 with a short training history; with the full history (F1h) and without make (F1r) the 2.0 mpg bar fails; superseded by F1r (refuted): the same test without make as a predictor also fails the 2.0 mpg bar.*
- **P1b** (passed its own test): Flagging new configurations the model predicts at 30+ mpg as low-rolling-resistance tire targets creates value (+5 or more a year) and beats both status-quo rules on payoff *superseded by P1r (blocked: rests on F1r (refuted)): P1r adds the flag-nothing comparator, cutoff sensitivity and the full history.*

Not established:

- **G2r**: refuted. Among non-hybrid configurations alone, falling fuel consumption still comes more from within-class improvement than from the class mix
- **F1r**: refuted. Trained on every model year up to two years earlier, without make as a predictor, a spec model predicts the combined MPG of never-before-seen configurations within 2.0 mpg on average and beats a similar-spec median
- **P1r**: blocked: rests on F1r (refuted). Using the full-history model, flagging never-before-seen configurations predicted at 30+ mpg as LRR tire targets earns a positive payoff in most years, beats flagging nothing and both status-quo rules, and stays positive at cutoffs of 29 and 31 mpg *verdict flips with the random seed.*
- **F1h**: refuted. With the full 2012 onward history (make kept as a predictor), a spec model trained on years up to two years earlier predicts never-before-seen configurations within 2.0 mpg on average and beats a similar-spec median

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

- Holdout looks used: 11 of a budget of 12.
- Claims registered: 11; attempts refused by the gates: 1 (together, the multiple-comparisons count; thresholds were set per claim at registration).
- Replicating agents: goldfish-D1-sonnet, goldfish-D2, goldfish-D3-sonnet, goldfish-F1-sonnet, goldfish-F1h-sonnet, goldfish-F1r, goldfish-G1-sonnet, goldfish-G2, goldfish-G2r-sonnet, goldfish-P1b, goldfish-P1r-sonnet.
- Seed check: 11 claims rerun under several seeds; unstable: P1r.
- Stage log: `#13` close descriptive; `#25` close diagnostic; `#33` close predictive; `#40` close prescriptive; `#44` reopen diagnostic (referee-1: separate engine improvement from hybrid substitution in G2); `#48` close diagnostic; `#49` reopen predictive (referee-1: use the full history and drop make as a predictor); `#53` close predictive; `#54` reopen prescriptive (referee-1: compare with flag-nothing, test cutoff sensitivity, use full history); `#58` close prescriptive; `#74` reopen predictive (referee-2: separate F1r's two changes; test full history alone, keeping make); `#78` close predictive.

## 3. Results

### 3.1 Descriptive

#### D1: Among non-hybrid configurations of 2.0 L or less, at least 60% are turbocharged in every model year

- **Status: established.** Type descriptive/composition.
- Decision it informs: Treat small turbo engines as the mainstream configuration when planning fitments.
- Pre-registered (`#4`): predicted small-engine turbo share >= 0.60 each year; falsified if any model year below 0.60. Test `analysis/tests/D1.py` sha `16f31714262f`.
- Scope: tested on year 2020 to 2025 only (the sealed holdout, without earlier history).
- Reviewed before registration by the critic: `analysis/reviews/descriptive.md`.
- Seed check (`#62`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: survived/survived/survived/survived; goldfish-D1-sonnet: survived/survived/survived/survived.
- Gates: smoke run on exploration data falsified; mutant permute:turbo killed 5/5 (uninformative).
- Holdout result (`#7`): **survived**, by_year={'2020': 0.757, '2021': 0.776, '2022': 0.784, '2023': 0.826, '2024': 0.822, '2025': 0.797}, min_share=0.7567, years=6. Replay `#8` byte-identical.
- Replication by goldfish-D1-sonnet (`#14`): survived (agrees); method: per-year share of turbo==1 among hybrid==0 & displ<=2.0, compared directly to 0.60; bootstrap CI for context; by_year={'2020': {'boot95': [0.7112, 0.7995], 'n': 374, 'share': 0.7567, 'share_incl_supercharger': 0.7567, 'turbo': 283}, '2021': {'boot95': [0.7328, 0.819], 'n': 348, 'share': 0.7759, 'share_incl_supercharger': 0.7759, 'turbo': 270}, '2022': {'boot95': [0.7378, 0.8262], 'n': 328, 'share': 0.7835, 'share_incl_supercharger': 0.7835, 'turbo': 257}, '2023': {'boot95': [0.7805, 0.8676], 'n': 287, 'share': 0.8258, 'share_incl_supercharger': 0.8258, 'turbo': 237}, '2024': {'boot95': [0.7671, 0.8721], 'n': 219, 'share': 0.8219, 'share_incl_supercharger': 0.8219, 'turbo': 180}, '2025': {'boot95': [0.738, 0.8556], 'n': 187, 'share': 0.7968, 'share_incl_supercharger': 0.7968, 'turbo': 149}}, min_share=0.7567, years_below_060=[]. Tester's note: read 2.0 L or less as displ <= 2.0 inclusive; unweighted configurations.

#### D2: 30+ mpg configurations stay a niche: under 20% of each model year's configurations, and not rising by more than 1 pp a year

- **Status: established (narrowed).** Type descriptive/distribution.
- Decision it informs: Size the high-MPG fitment line as a niche, not a mainstream line.
- Pre-registered (`#5`): predicted share < 0.20 every year, fitted slope <= 1 pp/yr; falsified if any year >= 0.20, or slope > 1 pp/yr. Test `analysis/tests/D2.py` sha `ab495087b3bd`.
- Scope: tested on year 2020 to 2025 only (the sealed holdout, without earlier history).
- Reviewed before registration by the critic: `analysis/reviews/descriptive.md`.
- Seed check (`#63`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: survived/survived/survived/survived; goldfish-D2: survived/survived/survived/survived.
- Gates: smoke run on exploration data survived; no mutant: a share of the marginal distribution; no structure to destroy.
- Holdout result (`#9`): **survived**, max_share=0.1632, slope_pp_per_year=0.748, years=6. Replay `#10` byte-identical.
- Replication by goldfish-D2 (`#15`): survived (agrees); method: per-year share of configs with comb_mpg>=30; max-share check vs 20%; OLS slope of yearly share on year (pp/yr) vs 1 pp, with count-weighted slope and within-year bootstrap 95% CI as sensitivity; bootstrap_frac_slope_gt_1pp=0.162, bootstrap_slope_ci95_pp=[0.225, 1.26], last2_year_change_pp=2.3, max_share_pct=16.32, n_by_year={'2020': 1171, '2021': 1180, '2022': 1183, '2023': 1137, '2024': 984, '2025': 876}, ols_slope_pp_per_year=0.748, share_pct_by_year={'2020': 12.3, '2021': 12.03, '2022': 12.85, '2023': 12.93, '2024': 14.02, '2025': 16.32}, weighted_slope_pp_per_year=0.713, years=[2020, 2021, 2022, 2023, 2024, 2025]. Tester's note: read 'not rising by more than 1 pp a year' as the fitted trend; year by year it fails. Narrowed (the tester's words): under 20% each year with a fitted trend near 0.75 pp a year, but single years rise faster (+2.3 pp 2024 to 2025).

#### D3: Like for like (same class and engine-size band, non-hybrid), front-wheel drive gets at least 1 mpg more than all-wheel drive every year, 1.5 on average

- **Status: established.** Type descriptive/comparison.
- Decision it informs: Quote a like-for-like AWD penalty, not the raw gap, in fitment guidance.
- Pre-registered (`#6`): predicted median stratum gap >= 1 every year, mean >= 1.5; falsified if any year below 1 mpg, or mean below 1.5. Test `analysis/tests/D3.py` sha `84cc1714f953`.
- Scope: tested on year 2020 to 2025 only (the sealed holdout, without earlier history).
- Reviewed before registration by the critic: `analysis/reviews/descriptive.md`.
- Seed check (`#64`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: survived/survived/survived/survived; goldfish-D3-sonnet: survived/survived/survived/survived.
- Gates: smoke run on exploration data survived; mutant permute:drive killed 5/5.
- Holdout result (`#11`): **survived**, mean_gap=3.458, min_gap=2.5, years=6. Replay `#12` byte-identical.
- Replication by goldfish-D3-sonnet (`#16`): survived (agrees); method: non-hybrid FWD vs AWD only; strata = vclass x displ band (8 bands) x year; per-year gap = weighted mean of FWD-AWD cell mean differences, weight=min(nF,nA); within-year bootstrap (300) 90% intervals; avg_gap=3.932, avg_gap_boot_p5=3.619, boot90_hi=[4.257, 4.28, 4.641, 5.069, 4.849, 5.749], boot90_lo=[2.964, 2.969, 3.227, 3.247, 3.09, 3.678], cell_median_gap_by_year={'2020': 2.25, '2021': 2.421, '2022': 3.686, '2023': 3.482, '2024': 4.042, '2025': 4.417}, cells_by_year={'2020': 17, '2021': 12, '2022': 10, '2023': 10, '2024': 11, '2025': 9}, gap_by_year={'2020': 3.526, '2021': 3.491, '2022': 3.776, '2023': 4.071, '2024': 3.943, '2025': 4.786}. Tester's note: chose 8 displacement bands and a count-weighted cell mean; AWD = the All-Wheel Drive label only.


### 3.2 Diagnostic

#### G1: Within a vehicle class, non-hybrid MPG moves strongly with engine displacement (association, not cause)

- **Status: established (narrowed).** Type diagnostic/driver.
- Decision it informs: Use engine size, not class alone, when estimating a new vehicle's MPG.
- Pre-registered (`#17`): predicted Spearman rho(displ, comb_mpg) <= -0.6 in at least 80% of classes with 50+ non-hybrid configurations; falsified if fewer than 80% of such classes at rho <= -0.6. Test `analysis/tests/G1.py` sha `558d7e98cb28`.
- Scope: tested on year 2020 to 2025 only (the sealed holdout, without earlier history).
- Reviewed before registration by the critic: `analysis/reviews/diagnostic.md`.
- Seed check (`#65`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: survived/survived/survived/survived; goldfish-G1-sonnet: survived/survived/survived/survived.
- Gates: smoke run on exploration data survived; mutant permute:comb_mpg killed 5/5.
- Holdout result (`#19`): **survived**, classes=15, share_rho_le_minus_0_6=0.8, weakest={'Small Pickup Trucks 4WD': -0.58, 'Small Sport Utility Vehicle 4WD': -0.55, 'Small Station Wagons': -0.312}. Replay `#20` byte-identical.
- Replication by goldfish-G1-sonnet (`#26`): survived (agrees); method: Spearman rho(displ, comb_mpg) per vclass among hybrid==0, classes n>=50; strong = rho<=-0.6; survive if >=80% strong; fraction_strong=0.8, n_classes=15, n_strong=12, per_class={'Compact Cars': {'n': 454, 'rho': -0.822}, 'Large Cars': {'n': 334, 'rho': -0.909}, 'Midsize Cars': {'n': 632, 'rho': -0.776}, 'Minicompact Cars': {'n': 239, 'rho': -0.884}, 'Small Pickup Trucks 4WD': {'n': 74, 'rho': -0.58}, 'Small Sport Utility Vehicle 2WD': {'n': 393, 'rho': -0.642}, 'Small Sport Utility Vehicle 4WD': {'n': 861, 'rho': -0.55}, 'Small Station Wagons': {'n': 89, 'rho': -0.312}, 'Special Purpose Vehicle 2WD': {'n': 83, 'rho': -0.659}, 'Standard Pickup Trucks 2WD': {'n': 177, 'rho': -0.794}, 'Standard Pickup Trucks 4WD': {'n': 392, 'rho': -0.634}, 'Standard Sport Utility Vehicle 2WD': {'n': 237, 'rho': -0.9}, 'Standard Sport Utility Vehicle 4WD': {'n': 583, 'rho': -0.753}, 'Subcompact Cars': {'n': 494, 'rho': -0.88}, 'Two Seaters': {'n': 375, 'rho': -0.872}}. Narrowed (the tester's words): holds exactly at the 80% bar (12 of 15 classes): clearly for cars and standard SUVs and pickups, not for small 4WD SUVs, small 4WD pickups or small station wagons.

#### G2: Falling fuel consumption comes more from configurations improving within each class than from the configuration mix shifting between classes

- **Status: established (narrowed).** Type diagnostic/attribution.
- Decision it informs: Track efficiency gains class by class rather than as a fleet-mix story.
- Pre-registered (`#18`): predicted midpoint shift-share on gal/100 mi: within-class cut >= 0.1 and larger than the mix term; within-class negative in all but at most one adjacent-year pair; falsified if within-class cut < 0.1 gal/100 mi, or smaller than mix, or two or more adjacent pairs going the wrong way. Test `analysis/tests/G2.py` sha `b5ce031180ed`.
- Scope: tested on year 2020 to 2025 only (the sealed holdout, without earlier history).
- **Note:** superseded by G2r (refuted): among non-hybrids the within-class gain is smaller than the mix effect, so G2's within-class improvement is mostly hybrid substitution.
- **Note:** decision withdrawn: efficiency gains cannot be tracked class by class as engine improvement: most of the within-class gain was hybrids replacing non-hybrids (G2r).
- Reviewed before registration by the critic: `analysis/reviews/diagnostic.md`.
- Seed check (`#66`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: survived/survived/survived/survived; goldfish-G2: survived/survived/survived/survived.
- Gates: smoke run on exploration data survived; mutant permute:year killed 5/5.
- Holdout result (`#21`): **survived**, adjacent_pairs_improving=5/5, first=2020, last=2025, mix_gal_per_100mi=0.1149, within_gal_per_100mi=-0.194. Replay `#22` byte-identical.
- Replication by goldfish-G2 (`#27`): survived (agrees); method: symmetric (midpoint-weight) shift-share of mean gallons/100mi across vclass, first vs last model year, plus each adjacent-year pair; entry/exit classes split out; 1000x within-year bootstrap for CIs; adjacent_pairs={'2020-2021': {'entry_exit': 0.0, 'mix': 0.068, 'total': 0.0564, 'within': -0.0116}, '2021-2022': {'entry_exit': 0.0, 'mix': 0.0419, 'total': 0.0113, 'within': -0.0305}, '2022-2023': {'entry_exit': -0.0103, 'mix': 0.0109, 'total': 0.0003, 'within': -0.0003}, '2023-2024': {'entry_exit': -0.0, 'mix': 0.0214, 'total': -0.0433, 'within': -0.0647}, '2024-2025': {'entry_exit': 0.0, 'mix': -0.0101, 'total': -0.1039, 'within': -0.0938}}, entry_exit_change=-0.0104, fail_pairs=False, fail_within_smaller_than_mix=False, fail_within_under_0.1=False, max_consecutive_wrong_way=0, mean_gpm_first=4.5891, mean_gpm_last=4.5099, mix_change=0.1252, mix_ci95=[0.0617, 0.2091], n_pairs_within_wrong_way=0, total_change=-0.0791, within_change=-0.194, within_ci95=[-0.2768, -0.1013], years=[2020, 2025]. Narrowed (the tester's words): within-class improvement drove the whole net decline despite an adverse mix (+0.13 gal/100 mi), not two components both reducing consumption.

#### G2r: Among non-hybrid configurations alone, falling fuel consumption still comes more from within-class improvement than from the class mix

- **Status: refuted.** Type diagnostic/attribution.
- Decision it informs: Credit efficiency gains to engine improvement, not only to hybrid substitution, when forecasting tire mix.
- Pre-registered (`#45`): predicted non-hybrid midpoint shift-share on gal/100 mi: within-class cut >= 0.1, larger than mix, wrong way in at most one adjacent pair; falsified if within-class cut < 0.1, smaller than mix, or two or more adjacent pairs the wrong way. Test `analysis/tests/G2r.py` sha `418e454076be`.
- Scope: scored on year 2020 to 2025 (the sealed holdout), with earlier rows available as history.
- Reviewed before registration by a referee report (no pre-test critic saw this exact wording): `analysis/reviews/referee-1.md`.
- Seed check (`#69`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: falsified/falsified/falsified/falsified; goldfish-G2r-sonnet: falsified/falsified/falsified/falsified.
- Gates: smoke run on exploration data survived; mutant permute:year killed 5/5.
- Holdout result (`#46`): **falsified**, adjacent_pairs_improving=3/5, first=2020, last=2025, mix_gal_per_100mi=0.1131, within_gal_per_100mi=-0.0565. Replay `#47` byte-identical.
- Replication by goldfish-G2r-sonnet (`#59`): falsified (agrees); method: midpoint (Shapley) shift-share over vclass, non-hybrid, mean of 100/comb_mpg per config; first vs last scored year; adjacent-year within change sign count; check_sum=0.05652664842538721, first_year=2020, last_year=2025, mix=0.1130712599853673, n_wrong=2, total_change=0.056526648425387904, within=-0.056544611559980085, within_by_pair={'2020': 0.014, '2021': -0.0173, '2022': 0.0168, '2023': -0.03, '2024': -0.0565}, wrong_consecutive=False, wrong_direction_pairs=[2020, 2022]. Tester's note: non-hybrid consumption rose slightly (+0.057 gal/100 mi); midpoint weighting; two non-consecutive adjacent pairs went the wrong way.


### 3.3 Predictive

#### F1: From specs alone, a model trained on model years up to two years earlier predicts the combined MPG of never-before-seen configurations within 2.0 mpg on average, and beats a similar-spec median

- **Status: established.** Type predictive/forecast.
- Decision it informs: Estimate MPG for new configurations from specs before EPA ratings are published.
- Pre-registered (`#28`): predicted mean MAE <= 2.0, no year above 2.5, and MAE <= 0.85 x the similar-spec baseline in every year; falsified if mean MAE > 2.0, any year > 2.5, or any year above 0.85 x baseline. Test `analysis/tests/F1.py` sha `8feb0f9c2b8f`.
- Scope: tested on year 2020 to 2025 only (the sealed holdout, without earlier history).
- **Note:** superseded by F1h (refuted): F1 was scored on 2022 to 2025 with a short training history; with the full history (F1h) and without make (F1r) the 2.0 mpg bar fails.
- **Note:** superseded by F1r (refuted): the same test without make as a predictor also fails the 2.0 mpg bar.
- Reviewed before registration by the critic: `analysis/reviews/predictive.md`.
- Seed check (`#67`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: survived/survived/survived/survived; goldfish-F1-sonnet: survived/survived/survived/survived.
- Gates: smoke run on exploration data survived; mutant permute:comb_mpg killed 5/5.
- Holdout result (`#29`): **survived**, by_year={'2022': {'baseline': 2.21, 'mae': 1.68, 'new_configs': 140}, '2023': {'baseline': 3.26, 'mae': 1.93, 'new_configs': 109}, '2024': {'baseline': 3.12, 'mae': 1.81, 'new_configs': 90}, '2025': {'baseline': 3.39, 'mae': 2.19, 'new_configs': 90}}, mean_mae=1.9, years=4. Replay `#30` byte-identical.
- Replication by goldfish-F1-sonnet (`#41`): survived (agrees); method: HistGradientBoosting on one-hot specs, train years<=Y-2, test = year-Y configs whose full spec tuple not seen in any year<Y; baseline median by class/cyl/turbo/hybrid/drive with coarser fallback; avg_mae=1.8035941688563417, per_year={'2022': {'base_mae': 2.3892857142857142, 'mae': 1.5971127697550762, 'n': 140, 'ratio': 0.6684477960110932}, '2023': {'base_mae': 3.091743119266055, 'mae': 1.9665341221843247, 'n': 109, 'ratio': 0.6360599979765323}, '2024': {'base_mae': 3.2944444444444443, 'mae': 1.628408415727839, 'n': 90, 'ratio': 0.4942892324300354}, '2025': {'base_mae': 3.172222222222222, 'mae': 2.022321367758127, 'n': 90, 'ratio': 0.6375093628659595}}. Tester's note: read 'never seen' as absent from every year before Y; baseline falls back to coarser medians when a group is empty; only 4 test years, and 2023 and 2025 sit near 2.0.

#### F1r: Trained on every model year up to two years earlier, without make as a predictor, a spec model predicts the combined MPG of never-before-seen configurations within 2.0 mpg on average and beats a similar-spec median

- **Status: refuted.** Type predictive/forecast.
- Decision it informs: Estimate MPG for new configurations from specs before EPA ratings are published.
- Pre-registered (`#50`): predicted mean MAE <= 2.0, no year above 2.5, MAE <= 0.85 x baseline every year; falsified if mean MAE > 2.0, any year > 2.5, or any year above 0.85 x baseline. Test `analysis/tests/F1r.py` sha `19ed559ecf52`.
- Scope: scored on year 2020 to 2025 (the sealed holdout), with earlier rows available as history.
- Reviewed before registration by a referee report (no pre-test critic saw this exact wording): `analysis/reviews/referee-1.md`.
- Seed check (`#70`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: falsified/falsified/falsified/falsified; goldfish-F1r: falsified/falsified/falsified/falsified.
- Gates: smoke run on exploration data survived; mutant permute:comb_mpg killed 5/5.
- Holdout result (`#51`): **falsified**, by_year={'2020': {'baseline': 3.14, 'mae': 2.43, 'new_configs': 108}, '2021': {'baseline': 3.14, 'mae': 2.04, 'new_configs': 141}, '2022': {'baseline': 2.34, 'mae': 1.88, 'new_configs': 131}, '2023': {'baseline': 3.34, 'mae': 2.34, 'new_configs': 100}, '2024': {'baseline': 3.25, 'mae': 1.74, 'new_configs': 89}, '2025': {'baseline': 3.18, 'mae': 2.15, 'new_configs': 89}}, mean_mae=2.095, years=6. Replay `#52` byte-identical.
- Replication by goldfish-F1r (`#60`): falsified (agrees); method: per-year walk-forward HistGradientBoosting (L1 loss on log mpg, native categoricals) on 9 spec columns, no make; train years <= Y-2; test = year-Y rows whose make+spec key never appeared in any earlier year; baseline = median comb_mpg of training rows with same vclass/cylinders/turbo/hybrid/drive (coarser fallback when group empty); avg_mae=2.043, failed_conditions=['average MAE > 2.0'], max_ratio_to_baseline=0.791, max_year_mae=2.429, per_year={'2020': {'baseline_fallbacks': 22, 'baseline_mae': 3.069, 'mae': 2.429, 'n': 108, 'ratio': 0.791}, '2021': {'baseline_fallbacks': 43, 'baseline_mae': 3.443, 'mae': 2.09, 'n': 141, 'ratio': 0.607}, '2022': {'baseline_fallbacks': 25, 'baseline_mae': 2.817, 'mae': 1.537, 'n': 131, 'ratio': 0.546}, '2023': {'baseline_fallbacks': 13, 'baseline_mae': 3.23, 'mae': 2.276, 'n': 100, 'ratio': 0.705}, '2024': {'baseline_fallbacks': 23, 'baseline_mae': 3.191, 'mae': 1.687, 'n': 89, 'ratio': 0.529}, '2025': {'baseline_fallbacks': 19, 'baseline_mae': 2.955, 'mae': 2.239, 'n': 89, 'ratio': 0.758}}, seed=20261123. Tester's note: borderline: average MAE 2.045 against 2.0 (2.065 with SEED=2); baseline fell back to coarser groups when empty; every year still beat the baseline.

#### F1h: With the full 2012 onward history (make kept as a predictor), a spec model trained on years up to two years earlier predicts never-before-seen configurations within 2.0 mpg on average and beats a similar-spec median

- **Status: refuted.** Type predictive/forecast.
- Decision it informs: Estimate MPG for new configurations from specs before EPA ratings are published.
- Pre-registered (`#75`): predicted mean MAE <= 2.0, no year above 2.5, MAE <= 0.85 x baseline every year; falsified if mean MAE > 2.0, any year > 2.5, or any year above 0.85 x baseline. Test `analysis/tests/F1.py` sha `8feb0f9c2b8f`.
- Scope: scored on year 2020 to 2025 (the sealed holdout), with earlier rows available as history.
- Reviewed before registration by a referee report (no pre-test critic saw this exact wording): `analysis/reviews/referee-2.md`.
- Seed check (`#85`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: falsified/falsified/falsified/falsified; goldfish-F1h-sonnet: falsified/falsified/falsified/falsified.
- Gates: smoke run on exploration data survived; mutant permute:comb_mpg killed 5/5.
- Holdout result (`#76`): **falsified**, by_year={'2020': {'baseline': 3.14, 'mae': 2.4, 'new_configs': 108}, '2021': {'baseline': 3.14, 'mae': 2.0, 'new_configs': 141}, '2022': {'baseline': 2.34, 'mae': 1.74, 'new_configs': 131}, '2023': {'baseline': 3.34, 'mae': 2.21, 'new_configs': 100}, '2024': {'baseline': 3.25, 'mae': 1.87, 'new_configs': 89}, '2025': {'baseline': 3.18, 'mae': 2.26, 'new_configs': 89}}, mean_mae=2.079, years=6. Replay `#77` byte-identical.
- Replication by goldfish-F1h-sonnet (`#84`): falsified (agrees); method: HistGradientBoosting (categorical specs), train years<=Y-2, test = year-Y rows with spec unseen in any year<Y; baseline median by vclass/cylinders/turbo/hybrid/drive from same training years; avg_mae=2.089377526645454, max_mae=2.2980077562042394, max_ratio=0.7532165027922848, per_year={'2020': {'base_mae': 3.050925925925926, 'mae': 2.2980077562042394, 'n': 108, 'ratio': 0.7532165027922848}, '2021': {'base_mae': 3.3439716312056738, 'mae': 2.1562240266898574, 'n': 141, 'ratio': 0.6448093059666381}, '2022': {'base_mae': 2.8244274809160306, 'mae': 1.721654675211065, 'n': 131, 'ratio': 0.6095588174395933}, '2023': {'base_mae': 3.23, 'mae': 2.275424878223277, 'n': 100, 'ratio': 0.704465906570674}, '2024': {'base_mae': 3.191011235955056, 'mae': 1.992562074763242, 'n': 89, 'ratio': 0.6244296642743963}, '2025': {'base_mae': 2.797752808988764, 'mae': 2.0923917487810453, 'n': 89, 'ratio': 0.747882994544229}}. Tester's note: one untuned model; 'never appeared' read as absent from all years before Y; baseline falls back to coarser groups when a cell is empty.


### 3.4 Prescriptive

#### P1b: Flagging new configurations the model predicts at 30+ mpg as low-rolling-resistance tire targets creates value (+5 or more a year) and beats both status-quo rules on payoff

- **Status: established.** Type prescriptive/policy, rests on F1.
- Decision it informs: Use the model's 30+ mpg flag to choose LRR fitment targets for new configurations.
- Pre-registered (`#37`): predicted payoff (+1 correct target, -1 wrong target) >= 5 in >= 75% of years, total above both rules, and above both in >= 75% of years; falsified if payoff < 5 in more than a quarter of years, total not above both rules, or wins in < 75% of years. Test `analysis/tests/P1b.py` sha `0c5f7e04fd2f`.
- Scope: tested on year 2020 to 2025 only (the sealed holdout, without earlier history).
- **Note:** superseded by P1r (blocked: rests on F1r (refuted)): P1r adds the flag-nothing comparator, cutoff sensitivity and the full history.
- Reviewed before registration by the critic: `analysis/reviews/predictive.md`.
- Seed check (`#68`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: survived/survived/survived/survived; goldfish-P1b: survived/survived/survived/survived.
- Gates: smoke run on exploration data survived; mutant permute:comb_mpg killed 5/5.
- Holdout result (`#38`): **survived**, share_years_payoff_ge_5=0.75, total_payoff={'hybrid_or_small_car': -102, 'hybrids_only': -101, 'model': 31}, win_rate=1.0, years=4. Replay `#39` byte-identical.
- Replication by goldfish-P1b (`#42`): survived (agrees); method: Expanding-window by year: HistGradientBoostingRegressor (native categoricals) on 10 spec columns trained on years <= Y-2; test on year-Y configs whose full 10-field spec never appeared in any earlier year; flag pred>=30; +1/-1 payoff vs real comb_mpg>=30; rules applied to same novel set; car/wagon = vclass containing 'Cars' or 'Wagons'.; frac_years_beats_both=1.0, frac_years_payoff_ge5=1.0, per_year=[{'beats_both': True, 'hybrid_or_small_car': -36, 'hybrids_only': -37, 'model': 7, 'n_flag': 11, 'n_novel': 140, 'year': 2022}, {'beats_both': True, 'hybrid_or_small_car': -26, 'hybrids_only': -24, 'model': 10, 'n_flag': 14, 'n_novel': 109, 'year': 2023}, {'beats_both': True, 'hybrid_or_small_car': -27, 'hybrids_only': -27, 'model': 6, 'n_flag': 10, 'n_novel': 90, 'year': 2024}, {'beats_both': True, 'hybrid_or_small_car': -13, 'hybrids_only': -13, 'model': 5, 'n_flag': 5, 'n_novel': 90, 'year': 2025}], sensitivity_novel_vs_training_window_only={'frac_years_beats_both': 1.0, 'frac_years_payoff_ge5': 1.0, 'per_year': [{'beats_both': True, 'hybrid_or_small_car': -61, 'hybrids_only': -60, 'model': 17, 'n_flag': 25, 'n_novel': 308, 'year': 2022}, {'beats_both': True, 'hybrid_or_small_car': -55, 'hybrids_only': -54, 'model': 19, 'n_flag': 23, 'n_novel': 243, 'year': 2023}, {'beats_both': True, 'hybrid_or_small_car': -50, 'hybrids_only': -48, 'model': 18, 'n_flag': 22, 'n_novel': 183, 'year': 2024}, {'beats_both': True, 'hybrid_or_small_car': -47, 'hybrids_only': -47, 'model': 10, 'n_flag': 12, 'n_novel': 181, 'year': 2025}], 'totals': {'hybrid_or_small_car': -213, 'hybrids_only': -209, 'model': 64}, 'verdict': 'survived'}, test_years=[2022, 2023, 2024, 2025], totals={'hybrid_or_small_car': -102, 'hybrids_only': -101, 'model': 28}. Tester's note: test years 2022 to 2025 only; 2025 sits exactly at the +5 payoff bar, so one more miss would break it; holds under both readings of 'never seen before'.

#### P1r: Using the full-history model, flagging never-before-seen configurations predicted at 30+ mpg as LRR tire targets earns a positive payoff in most years, beats flagging nothing and both status-quo rules, and stays positive at cutoffs of 29 and 31 mpg

- **Status: blocked: rests on F1r (refuted).** Type prescriptive/policy, rests on F1r.
- Decision it informs: Use the model's 30+ mpg flag to choose LRR fitment targets for new configurations.
- Pre-registered (`#55`): predicted payoff > 0 in >= 75% of years and >= 5 in >= 75%; total positive at 29 and 31; total above both rules; falsified if any of those fails. Test `analysis/tests/P1r.py` sha `7eea78c1bf70`.
- Scope: scored on year 2020 to 2025 (the sealed holdout), with earlier rows available as history.
- **Note:** verdict flips with the random seed.
- Reviewed before registration by a referee report (no pre-test critic saw this exact wording): `analysis/reviews/referee-1.md`.
- Seed check (`#71`, seeds [20261123, 20261124, 20261125, 1]): UNSTABLE; elephant: survived/survived/survived/survived; goldfish-P1r-sonnet: survived/survived/survived/falsified.
- Gates: smoke run on exploration data survived; mutant permute:comb_mpg killed 5/5.
- Holdout result (`#56`): **survived**, by_year={'2020': {'cut29': 16, 'cut30': 12, 'cut31': 10, 'flagged': 16, 'hybrid_or_small_car': 5, 'hybrids_only': -5}, '2021': {'cut29': 8, 'cut30': 5, 'cut31': 6, 'flagged': 9, 'hybrid_or_small_car': -25, 'hybrids_only': -27}, '2022': {'cut29': 7, 'cut30': 8, 'cut31': 5, 'flagged': 10, 'hybrid_or_small_car': -36, 'hybrids_only': -37}, '2023': {'cut29': 11, 'cut30': 11, 'cut31': 10, 'flagged': 15, 'hybrid_or_small_car': -26, 'hybrids_only': -24}, '2024': {'cut29': 8, 'cut30': 8, 'cut31': 9, 'flagged': 12, 'hybrid_or_small_car': -27, 'hybrids_only': -27}, '2025': {'cut29': 4, 'cut30': 4, 'cut31': 5, 'flagged': 6, 'hybrid_or_small_car': -13, 'hybrids_only': -13}}, totals={'cut29': 54, 'cut30': 48, 'cut31': 45, 'flagged': 68, 'hybrid_or_small_car': -122, 'hybrids_only': -133}, years=6. Replay `#57` byte-identical.
- Replication by goldfish-P1r-sonnet (`#61`): survived (agrees); method: HistGradientBoosting on specs excl make, trained on years<=Y-2; flag year-Y rows whose full spec incl make unseen in any earlier year; cutoff applied to both prediction and real mpg; conditions={'beats_hybrid_or_small': True, 'beats_hybrids_only': True, 'cut29_positive': True, 'cut31_positive': True, 'ge5_75pct': True, 'positive_75pct': True}, per_year={'2020': {'flagged': 16, 'hcw': 5, 'hyb': -5, 'm29': 16, 'm30': 14, 'm31': 11, 'n_new': 108}, '2021': {'flagged': 8, 'hcw': -25, 'hyb': -27, 'm29': 6, 'm30': 2, 'm31': 2, 'n_new': 141}, '2022': {'flagged': 9, 'hcw': -36, 'hyb': -37, 'm29': 7, 'm30': 5, 'm31': 3, 'n_new': 131}, '2023': {'flagged': 16, 'hcw': -26, 'hyb': -24, 'm29': 10, 'm30': 12, 'm31': 8, 'n_new': 100}, '2024': {'flagged': 8, 'hcw': -27, 'hyb': -27, 'm29': 8, 'm30': 8, 'm31': 5, 'n_new': 89}, '2025': {'flagged': 5, 'hcw': -13, 'hyb': -13, 'm29': 5, 'm30': 5, 'm31': 5, 'n_new': 89}}, totals={'hcw': -122, 'hyb': -133, 'm29': 52, 'm30': 46, 'm31': 34}, years=[2020, 2021, 2022, 2023, 2024, 2025], years_ge5=5, years_positive=6. Tester's note: positive payoff in 6 of 6 years but +5 or more in only 4 of 6 (2021 +2, 2025 +3); moved the real-mpg threshold with the 29 and 31 cutoffs.

## 4. Threats to validity

- Not testable with this data: diagnostic/causal: no intervention or natural experiment in the data; turbo adoption, CAFE and class mix move together
- Not testable with this data: diagnostic/root-cause: no anomaly found in exploration that needed explaining
- Not testable with this data: predictive/leading-indicator: cross-sectional specs; no series that leads another
- Not testable with this data: predictive/timing: no events to time in annual configuration data
- Not testable with this data: prescriptive/allocation: no volumes or budgets to allocate
- Not testable with this data: prescriptive/trigger: no time-varying metric to trigger on
- Descriptive kinds left open at close (`#13`): level, trend, seasonality, anomaly, change-point. level, trend, seasonality, anomaly and change-point left open: this demo keeps two to three claims per stage; seasonality does not apply to annual model-year data
- Predictive kinds left open at close (`#33`): classification. classification is covered inside P1's 30 mpg flag rather than as a separate claim
- Predictive kinds left open at close (`#53`): classification. classification is covered inside the 30 mpg flag of the prescriptive claims
- Predictive kinds left open at close (`#78`): classification. classification is covered inside the 30 mpg flag of the prescriptive claims
- D1 already failed on exploration data before registration, so its mutation gate says nothing.
- P1r is blocked: rests on F1r (refuted).
- Refused at registration (`#36`, mutation gate): P1, "Flagging new configurations the model predicts at 30+ mpg as low-rolling-resistance tire targets beats both status-quo rules (hybrids only; hybrid or small non-turbo car) on payoff". the test has no teeth against permute:comb_mpg: it falsified only 0 of 5 mutants. Tighten the test or the threshold, or pick a mutant that really destroys what the claim asserts
- The diagnostic stage was reopened (`#44`): referee-1: separate engine improvement from hybrid substitution in G2.
- The predictive stage was reopened (`#49`): referee-1: use the full history and drop make as a predictor.
- The prescriptive stage was reopened (`#54`): referee-1: compare with flag-nothing, test cutoff sensitivity, use full history.
- The predictive stage was reopened (`#74`): referee-2: separate F1r's two changes; test full history alone, keeping make.
- D2 holds only in its tester's narrower reading (`#15`): under 20% each year with a fitted trend near 0.75 pp a year, but single years rise faster (+2.3 pp 2024 to 2025)
- G1 holds only in its tester's narrower reading (`#26`): holds exactly at the 80% bar (12 of 15 classes): clearly for cars and standard SUVs and pickups, not for small 4WD SUVs, small 4WD pickups or small station wagons
- G2 holds only in its tester's narrower reading (`#27`): within-class improvement drove the whole net decline despite an adverse mix (+0.13 gal/100 mi), not two components both reducing consumption
- Sample: electric, plug-in hybrid and gaseous-fuel vehicles are excluded, so every finding is about gasoline, diesel and conventional hybrid configurations.
- Data: EPA fueleconomy.gov `vehicles.csv` (downloaded 2026-11-25), model years 2012 to 2025; electric, plug-in hybrid and gaseous-fuel vehicles dropped because their combined MPG measures something else. Rows are configurations, not sales: a niche trim counts as much as a best-seller, so no finding here is about market share.
- Split: by model year as a panel (`--panel`): 2012 to 2019 explored, 2020 to 2025 sealed. Predictive and prescriptive tests train only on years up to Y-2 and score only configurations whose spec never appeared before, following the critic's horizon review.
- Roles were confirmed by the user at the checkpoint, including excluding six columns computed from MPG.
- The first P1 draft was refused by the mutation gate (on data with MPG shuffled it still "beat" the status quo by flagging nothing, because both status-quo rules lose money). The refusal is in the ledger; P1b adds a "creates value" condition.
- D1 is about recent years, so it already failed on 2012 to 2019 exploration data and its mutation check is uninformative; the paper flags this.
- Revision round after referee-1 (major revisions): G2r (non-hybrid attribution) refuted, F1r (full history, no make) refuted narrowly, P1r (flag-nothing comparator, cutoff sensitivity) survived its own test but is seed-sensitive and blocked. See `analysis/reviews/response-1.md`.
- Limitations not addressed: no sales weighting, no deduplication of carried-over configurations, no error breakdown near 30 mpg, no D3 band-width sensitivity, no partial correlations for G1, no intervals in registered tests.
- Correction to response 1: it said P1r's tester failed P1r. The tester's recorded result (at the workspace seed) is survived; the tester's prose described a check at seed 1, where the verdict flips. The seed check records this, and P1r is reported as seed-sensitive.
- F1h (full history, make kept) also misses the 2.0 mpg bar (mean 2.08). Correction (referee 3): this is not because F1 was scored on fewer, easier years; on the same 2022 to 2025 years F1h still averages 2.02 against F1's 1.90. The difference comes from the longer training history and the stricter 'never seen before' test set. The forecast beat the similar-spec baseline in every year; no looser bar was registered.
- G1 and D2 pass at or near their bars and hold only as narrowed by their testers.
- D3 holds for car and wagon classes only: EPA splits SUV, pickup and minivan classes by drive, so all-wheel-drive SUVs were never compared like for like, and 4-wheel and part-time 4WD were not compared at all. Quote the penalty for cars and wagons only.
- D2 is about all configurations in each year. Among newly introduced configurations, the referee's unregistered check found the 30+ mpg share reached 22.3% in 2025, so "stay a niche" does not hold for new configurations, which is what fitment decisions use.
- G2's "mostly hybrid substitution" is an inference from two decompositions on different populations, not a registered test.
- G1 is fragile even as narrowed: the referee's bootstrap reached the 80% bar about 74% of the time (90% on deduplicated configurations).

## 5. Peer review

- Critic review before testing: `analysis/reviews/descriptive.md`.
- Critic review before testing: `analysis/reviews/diagnostic.md`.
- Critic review before testing: `analysis/reviews/predictive.md`.
- Referee report by referee-1 (`#43`): **major-revisions**. `analysis/reviews/referee-1.md`.
  - Response (`#72`): `analysis/reviews/response-1.md`.
- Referee report by referee-2 (`#73`): **major-revisions**. `analysis/reviews/referee-2.md`.
  - Response (`#86`): `analysis/reviews/response-2.md`.
- Referee report by referee-3 (`#87`): **minor-revisions**. `analysis/reviews/referee-3.md`.
  - Response (`#88`): `analysis/reviews/response-3.md`.

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
| 43 | referee |  | `7020a54a352e` |
| 44 | reopen | diagnostic | `736d161ffe58` |
| 45 | register | G2r | `0f5d18176778` |
| 46 | run | G2r | `5633b9fd8fa6` |
| 47 | replay | G2r | `add10007bef5` |
| 48 | close | diagnostic | `de4e5700c35e` |
| 49 | reopen | predictive | `f47534ff93d3` |
| 50 | register | F1r | `4c6bc8fcbe78` |
| 51 | run | F1r | `7b66299960f9` |
| 52 | replay | F1r | `1e5e13570159` |
| 53 | close | predictive | `d06bdfbd2e9a` |
| 54 | reopen | prescriptive | `c2afe1e7495b` |
| 55 | register | P1r | `98f4885a4039` |
| 56 | run | P1r | `263ed7a4ce9a` |
| 57 | replay | P1r | `ddd04e3bd311` |
| 58 | close | prescriptive | `05f386d26718` |
| 59 | goldfish | G2r | `0e661ca9ed88` |
| 60 | goldfish | F1r | `0626887b17a8` |
| 61 | goldfish | P1r | `43a4b8add951` |
| 62 | seeds | D1 | `35d7d6f09bea` |
| 63 | seeds | D2 | `62ebeeb67dcc` |
| 64 | seeds | D3 | `72e5706d59c9` |
| 65 | seeds | G1 | `6e49904bc51a` |
| 66 | seeds | G2 | `5aeb56bae40d` |
| 67 | seeds | F1 | `fd7f79689e2a` |
| 68 | seeds | P1b | `6963d13d40b2` |
| 69 | seeds | G2r | `84f4a43f8849` |
| 70 | seeds | F1r | `58fca9ea812f` |
| 71 | seeds | P1r | `5e485e46011b` |
| 72 | response |  | `f37362f6bac9` |
| 73 | referee |  | `27dbb160b6e2` |
| 74 | reopen | predictive | `7f986f6c8e27` |
| 75 | register | F1h | `4883b4b66963` |
| 76 | run | F1h | `9e8fb2bde901` |
| 77 | replay | F1h | `3fbd338e8346` |
| 78 | close | predictive | `4d0ae84a6efd` |
| 79 | supersede | F1 | `478501a7c473` |
| 80 | supersede | F1 | `7519c1a3ab4d` |
| 81 | supersede | P1b | `8366d21a9e88` |
| 82 | supersede | G2 | `b1fec2c0987f` |
| 83 | withdraw | G2 | `363ae68f7b70` |
| 84 | goldfish | F1h | `da8edc6fffae` |
| 85 | seeds | F1h | `b2446f6beba0` |
| 86 | response |  | `75b42640cd1e` |
| 87 | referee |  | `91df761b5a13` |
| 88 | response |  | `e8055e443890` |
