# Winter-Tire Timing in Canada, 2018 to 2025

*Generated from the evidence ledger `analysis/LEDGER.jsonl` (head `ca86a5603b2de71f`, 54 entries, chain intact). Every number below cites the ledger entry it came from as `#n`. To check this paper, run `python3 ledger.py audit`, which re-executes every result.*

## Abstract

All findings below are about year 2018 to 2025, the period sealed before analysis; earlier periods were used only to form hypotheses. We registered 7 claims before testing them on held-out data, across 4 insight categories. 1 stand as established, 5 were refuted, 0 were superseded by later tests, and 1 is open (contested, blocked, seed-sensitive or untested).

Established without qualification:

- **G1** (diagnostic/driver): Within a province, a colder October moves with a larger share of the fall rush landing in October (association, judged after the season)

Not established:

- **D1**: refuted. Year-to-year swings in how much of the fall rush lands in October are material: the October share's standard deviation is at least 2 points in at least 6 of 10 provinces
- **G2**: refuted. The 7 C crossing date adds timing information beyond October temperature (the 7 C rule as a trigger; expected to fail)
- **G3**: refuted (narrowed). Within a province, a warmer March moves with a larger share of the spring swap landing in April (association)
- **F1**: refuted. By April 1, March temperature plus each province's history predicts the April share of the spring swap at least 10% and 0.2 points better than the province's historical average
- **F2**: refuted. September temperature predicts the October share of the fall rush at least 10% better than the province's historical average (expected to fail)
- **P1**: blocked: rests on F1 (refuted). Splitting spring capacity between April and May by the March-temperature forecast, instead of each province's average split, cuts the cost of misallocation (under-planning April costs 2x over-planning) by at least 5% and wins in at least 60% of province-years

## 1. Data

- Source: `changeover_by_province.csv`, sha256 `126324338ae5082c`, 160 rows, 16 columns.
- Split (`#0`): ordered by year, seed 20261123; 80 rows for exploration, 80 sealed for confirmation (exploration up to 2017).
- Data audit before sealing: {"duplicate_keys": [], "empty_cells": {"first_snow_day": 39}}.

### 1.1 Variables (`#2`, confirmed by the user (domain owner), 2026-11-27)

| role | columns | meaning |
|---|---|---|
| exclude | apr_sales, may_sales, oct_sales, nov_sales, fall_days_with_weather | unusable or leaky: recorded after the outcome, a duplicate of the target, or junk (apr_sales: ingredient of apr_share; may_sales: ingredient of apr_share; oct_sales: ingredient of oct_share; nov_sales: ingredient of oct_share; fall_days_with_weather: data-quality count) |
| feature | fall_7c_day, first_snow_day, sep_mean_temp, oct_mean_temp, spring_7c_day, mar_mean_temp, apr_mean_temp, province | independent variable: a candidate explanation or predictor |
| segment | province | a grouping used to slice results (can also be a feature) |
| target | oct_share, apr_share | dependent variable: the outcome the analysis explains or predicts |
| time | year | the order key for time series |

One row per province per year. Weather is one city per province (St. John's, Charlottetown, Halifax, Moncton, Montreal, Toronto, Winnipeg, Regina, Calgary, Vancouver); sales are the whole province (NAICS 4413, unadjusted).

## 2. Methods

Each claim was written down with its kill criterion and the decision it informs, reviewed by a critic agent that saw no data, and frozen (its test script hashed) before its single look at the sealed holdout. Registration required the test to pass a lint for future-peeking and leaky code, a smoke run on exploration data, and a mutation gate: on copies of the data with the claimed pattern destroyed, the test had to report falsified at least 4 times in 5. Results were replayed byte-for-byte, then replicated by independent agents who saw only the claim and the holdout and wrote their own method. Prescriptive claims count only if the claim they rest on is established.

- Holdout looks used: 7 of a budget of 12.
- Claims registered: 7; attempts refused by the gates: 1 (together, the multiple-comparisons count; thresholds were set per claim at registration).
- Replicating agents: goldfish-D1, goldfish-F1-sonnet, goldfish-F2, goldfish-G1-sonnet, goldfish-G2, goldfish-G3-sonnet, goldfish-P1-sonnet.
- Seed check: 7 claims rerun under several seeds; all stable.
- Stage log: `#7` close descriptive; `#18` close diagnostic; `#19` reopen diagnostic (G3 was refused by a mutation-gate bug: permute skipped rows with any blank cell, leaving 17 true rows in every mutant; fixed in ledger.py); `#23` close diagnostic; `#33` close predictive; `#39` close prescriptive.

## 3. Results

### 3.1 Descriptive

#### D1: Year-to-year swings in how much of the fall rush lands in October are material: the October share's standard deviation is at least 2 points in at least 6 of 10 provinces

- **Status: refuted.** Type descriptive/distribution.
- Decision it informs: Keep fall staffing and stock plans flexible between October and November rather than fixed by date.
- Pre-registered (`#3`): predicted SD of oct_share >= 0.02 in >= 6 provinces; falsified if fewer than 6 provinces. Test `analysis/tests/D1.py` sha `d25c069535f4`.
- Scope: scored on year 2018 to 2025 (the sealed holdout), with earlier rows available as history.
- Reviewed before registration by the critic: `analysis/reviews/critic.md`.
- Seed check (`#47`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: falsified/falsified/falsified/falsified; goldfish-D1: falsified/falsified/falsified/falsified.
- Gates: smoke run on exploration data survived; no mutant: a spread statistic of each province's own series; no structure to destroy.
- Holdout result (`#4`): **falsified**, provinces_sd_ge_2pp=5, sd_by_province={'ab': 0.0215, 'bc': 0.0318, 'mb': 0.0248, 'nb': 0.0222, 'nl': 0.0178, 'ns': 0.0152, 'on': 0.0202, 'pe': 0.0142, 'qc': 0.0186, 'sk': 0.0165}. Replay `#5` byte-identical.
- Replication by goldfish-D1 (`#42`): falsified (agrees); method: per-province sample SD (ddof=1) of oct_share over scored years; count provinces with SD >= 0.02, need >= 6; n_provinces=10, n_years_per_province={'ab': 8, 'bc': 8, 'mb': 8, 'nb': 8, 'nl': 8, 'ns': 8, 'on': 8, 'pe': 8, 'qc': 8, 'sk': 8}, provinces_meeting_threshold_population=4, provinces_meeting_threshold_sample=5, sd_population={'ab': 0.02015, 'bc': 0.02978, 'mb': 0.02324, 'nb': 0.0208, 'nl': 0.01664, 'ns': 0.01417, 'on': 0.01885, 'pe': 0.01329, 'qc': 0.01736, 'sk': 0.01544}, sd_sample={'ab': 0.02154, 'bc': 0.03183, 'mb': 0.02484, 'nb': 0.02224, 'nl': 0.01779, 'ns': 0.01515, 'on': 0.02016, 'pe': 0.0142, 'qc': 0.01855, 'sk': 0.0165}, years_scored=[2018, 2025]. Tester's note: sample standard deviation; Alberta and Ontario sit right at 0.02; the population version gives 4 provinces.


### 3.2 Diagnostic

#### G1: Within a province, a colder October moves with a larger share of the fall rush landing in October (association, judged after the season)

- **Status: established.** Type diagnostic/driver.
- Decision it informs: In post-season reviews, attribute October/November swings to October weather before blaming execution.
- Pre-registered (`#8`): predicted detrended within-province Spearman <= -0.25, within-province permutation p < 0.01, same sign in >= 6 provinces, holds without 2020; falsified if any condition fails. Test `analysis/tests/G1.py` sha `d9b01c377f13`.
- Scope: scored on year 2018 to 2025 (the sealed holdout), with earlier rows available as history.
- Reviewed before registration by the critic: `analysis/reviews/critic.md`.
- Seed check (`#48`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: survived/survived/survived/survived; goldfish-G1-sonnet: survived/survived/survived/survived.
- Gates: smoke run on exploration data survived; mutant permute:oct_mean_temp killed 4/5.
- Holdout result (`#11`): **survived**, p_within_perm=0.0005, provinces_same_sign=10, rho=-0.5293, rho_without_2020=-0.5426. Replay `#12` byte-identical.
- Replication by goldfish-G1-sonnet (`#43`): survived (agrees); method: per-province linear detrend (fit on all years), pooled Spearman on year>=SCORE_FROM residuals, within-province permutation test (5000, one-sided), per-province Spearman, leave-2020-out; n_negative_provinces=9, n_provinces=10, n_rows=80, per_province={'ab': -0.857, 'bc': -0.857, 'mb': -0.786, 'nb': -0.81, 'nl': -0.31, 'ns': -0.333, 'on': -0.571, 'pe': 0.357, 'qc': -0.81, 'sk': -0.405}, perm_p=0.0002, perm_p_no2020=0.0002, pooled_spearman=-0.647, pooled_spearman_no2020=-0.619. Tester's note: detrend fitted on all years with only 2018 onward scored, which gives a stronger result (-0.65, 9 of 10 provinces; PEI goes the other way); within-province permutation.

#### G2: The 7 C crossing date adds timing information beyond October temperature (the 7 C rule as a trigger; expected to fail)

- **Status: refuted.** Type diagnostic/driver.
- Decision it informs: Use the 7 C crossing date as the trigger to pull staffing forward.
- Pre-registered (`#9`): predicted partial Spearman of fall_7c_day with oct_share, given oct_mean_temp, <= -0.2; falsified if partial correlation above -0.2. Test `analysis/tests/G2.py` sha `4b0594b7abdb`.
- Scope: scored on year 2018 to 2025 (the sealed holdout), with earlier rows available as history.
- Reviewed before registration by the critic: `analysis/reviews/critic.md`.
- Seed check (`#49`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: falsified/falsified/falsified/falsified; goldfish-G2: falsified/falsified/falsified/falsified.
- Gates: smoke run on exploration data falsified; mutant permute:fall_7c_day killed 3/5 (uninformative).
- Holdout result (`#13`): **falsified**, n=80, partial_rho_given_oct_temp=0.1657. Replay `#14` byte-identical.
- Replication by goldfish-G2 (`#46`): falsified (agrees); method: per-province linear (mean+trend) detrend of oct_share, fall_7c_day, oct_mean_temp fit on all years; partial Spearman (rank-residual) of fall_7c_day vs oct_share controlling oct_mean_temp on scored rows; province-cluster bootstrap CI, within-province permutation p; boot_ci95=[0.01, 0.267], detrended_spearman_no_control=-0.2628, n_provinces=10, n_scored=80, partial_spearman=0.1461, perm_p_one_sided=0.9095, sens_detrend_history_only=0.1024, sens_detrend_scored_only=0.1657, threshold=-0.2. Tester's note: alone, the 7 C date tracks the October share (rho -0.26), but given October temperature it adds nothing (partial +0.15, CI 0.01 to 0.27), under three detrending choices.

#### G3: Within a province, a warmer March moves with a larger share of the spring swap landing in April (association)

- **Status: refuted (narrowed).** Type diagnostic/driver.
- Decision it informs: Expect April-heavy spring demand after warm Marches.
- Pre-registered (`#20`): predicted detrended within-province Spearman >= 0.25, permutation p < 0.01, same sign in >= 6 provinces, holds without 2020; falsified if any condition fails. Test `analysis/tests/G3.py` sha `7726b75d33a9`.
- Scope: scored on year 2018 to 2025 (the sealed holdout), with earlier rows available as history.
- Reviewed before registration by the critic: `analysis/reviews/critic.md`.
- Seed check (`#50`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: falsified/falsified/falsified/falsified; goldfish-G3-sonnet: falsified/falsified/falsified/falsified.
- Gates: smoke run on exploration data survived; mutant permute:mar_mean_temp killed 5/5.
- Holdout result (`#21`): **falsified**, p_within_perm=0.018, provinces_same_sign=9, rho=0.249, rho_without_2020=0.324. Replay `#22` byte-identical.
- Replication by goldfish-G3-sonnet (`#44`): falsified (agrees); method: per-province demean+linear detrend within scored window, pooled Spearman, within-province permutation test (10000, one-sided), per-province signs, drop-2020; n_positive_provinces=9, n_provinces=10, n_rows=80, per_province={'ab': 0.238, 'bc': 0.452, 'mb': 0.238, 'nb': 0.238, 'nl': 0.381, 'ns': 0.048, 'on': 0.167, 'pe': 0.643, 'qc': -0.238, 'sk': 0.429}, perm_p=0.0162, pooled_spearman=0.249, pooled_spearman_no2020=0.3147. Tester's note: missed 0.25 by 0.001 and p = 0.016; detrend fitted on the scored window only. Narrowed (the tester's words): a loose directional pattern (9 of 10 provinces positive, 0.32 without 2020), not the stated strength.


### 3.3 Predictive

#### F1: By April 1, March temperature plus each province's history predicts the April share of the spring swap at least 10% and 0.2 points better than the province's historical average

- **Status: refuted.** Type predictive/leading-indicator.
- Decision it informs: Use March temperature to set the April/May split of spring staffing and stock.
- Pre-registered (`#24`): predicted expanding-window MAE at least 10% and 0.2 points below the province-average baseline, with and without 2020; falsified if either condition fails in either version. Test `analysis/tests/F1.py` sha `b8b1bea3bef5`.
- Scope: scored on year 2018 to 2025 (the sealed holdout), with earlier rows available as history.
- Reviewed before registration by the critic: `analysis/reviews/critic.md`.
- Seed check (`#51`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: falsified/falsified/falsified/falsified; goldfish-F1-sonnet: falsified/falsified/falsified/falsified.
- Gates: smoke run on exploration data survived; mutant permute:mar_mean_temp killed 5/5.
- Holdout result (`#26`): **falsified**, all={'gain_pp': 0.15, 'mae_baseline': 0.02634, 'mae_model': 0.02484, 'rel_gain': 0.057, 'years': 8}, no2020={'gain_pp': 0.169, 'mae_baseline': 0.023, 'mae_model': 0.02131, 'rel_gain': 0.0734, 'years': 7}. Replay `#27` byte-identical.
- Replication by goldfish-F1-sonnet (`#40`): falsified (agrees); method: expanding-window; baseline=province mean apr_share of prior years; model=province mean + pooled slope on within-province March temp anomaly (fit on prior years only); 2020 excluded from both training and scoring in the leave-out version; all_years={'abs_gain_pts': 0.1501, 'mae_base_pts': 2.6343, 'mae_model_pts': 2.4842, 'n': 80, 'rel_gain_pct': 5.7}, leave_out_2020={'abs_gain_pts': 0.1688, 'mae_base_pts': 2.3002, 'mae_model_pts': 2.1313, 'n': 70, 'rel_gain_pct': 7.34}. Tester's note: province mean plus a pooled slope on the March anomaly; 2020 dropped from training and scoring; one model form only.

#### F2: September temperature predicts the October share of the fall rush at least 10% better than the province's historical average (expected to fail)

- **Status: refuted.** Type predictive/leading-indicator.
- Decision it informs: Use September weather to pre-plan the October/November split.
- Pre-registered (`#25`): predicted expanding-window MAE <= 0.9 x province-average baseline; falsified if MAE above 0.9 x baseline. Test `analysis/tests/F2.py` sha `aae388b701a5`.
- Scope: scored on year 2018 to 2025 (the sealed holdout), with earlier rows available as history.
- Reviewed before registration by the critic: `analysis/reviews/critic.md`.
- Seed check (`#52`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: falsified/falsified/falsified/falsified; goldfish-F2: falsified/falsified/falsified/falsified.
- Gates: smoke run on exploration data falsified; mutant permute:sep_mean_temp killed 5/5 (uninformative).
- Holdout result (`#28`): **falsified**, mae_baseline=0.02088, mae_model=0.02164, years=8. Replay `#29` byte-identical.
- Replication by goldfish-F2 (`#45`): falsified (agrees); method: expanding-window: pooled province-fixed-effects OLS of oct_share on sep_mean_temp (province mean + common slope x Sep anomaly), fit on years < scored year; baseline = province mean oct_share over earlier years; sensitivity = per-province OLS; improvement=-0.0367, improvement_boot95=[-0.1233, 0.0317], improvement_per_province_ols=-0.047, mae_baseline=0.02088, mae_model=0.02164, mae_per_province_ols=0.02186, n_scored=80, slope_last_fit=-0.00245, threshold=0.1. Tester's note: September temperature made the forecast 3.7% worse than the province average (95% range 12% worse to 3% better); per-province fits also worse.


### 3.4 Prescriptive

#### P1: Splitting spring capacity between April and May by the March-temperature forecast, instead of each province's average split, cuts the cost of misallocation (under-planning April costs 2x over-planning) by at least 5% and wins in at least 60% of province-years

- **Status: blocked: rests on F1 (refuted).** Type prescriptive/allocation, rests on F1.
- Decision it informs: Adopt the March-temperature rule for the April/May split.
- Pre-registered (`#34`): predicted cost cut >= 5% and win rate >= 60%, with and without 2020; falsified if either fails in either version. Test `analysis/tests/P1.py` sha `746317149a25`.
- Scope: scored on year 2018 to 2025 (the sealed holdout), with earlier rows available as history.
- Reviewed before registration by the critic: `analysis/reviews/critic.md`.
- Seed check (`#53`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: falsified/falsified/falsified/falsified; goldfish-P1-sonnet: falsified/falsified/falsified/falsified.
- Gates: smoke run on exploration data survived; mutant permute:mar_mean_temp killed 5/5.
- Holdout result (`#35`): **falsified**, all={'cost_cut': 0.0817, 'province_years': 80, 'win_rate': 0.6}, no2020={'cost_cut': 0.1033, 'province_years': 70, 'win_rate': 0.571}. Replay `#36` byte-identical.
- Replication by goldfish-P1-sonnet (`#41`): falsified (agrees); method: pooled province-demeaned OLS of April share on March mean temp (prior years only) added to province historical mean; 2020 dropped from fit and scoring in second version; all_years={'base_cost': 2.7605251703851703, 'cut': 0.08170166938233392, 'fc_cost': 2.53498565559275, 'n': 80, 'win': 0.6}, sensitivity_quantile_shift={'all': {'base_cost': 2.7605251703851703, 'cut': 0.015487690634858442, 'fc_cost': 2.717771010556505, 'n': 80, 'win': 0.35}, 'no2020': {'base_cost': 2.166783022533023, 'cut': 0.038092911374376204, 'fc_cost': 2.0842439488881697, 'n': 70, 'win': 0.37142857142857144}}, without_2020={'base_cost': 2.166783022533023, 'cut': 0.1032640890132207, 'fc_cost': 1.9430321476218375, 'n': 70, 'win': 0.5714285714285714}. Tester's note: 2020 dropped from fitting and scoring; plain mean forecast; the win rate is exactly 60% with all years and 57% without 2020.

## 4. Threats to validity

- Not testable with this data: descriptive: levels, trends and peak months were covered in earlier runs on these tables; this run is about timing
- Not testable with this data: diagnostic/causal: no policy change inside 2010 to 2025; Quebec's mandate predates the data, so it cannot be studied as an intervention
- Not testable with this data: diagnostic/root-cause: no anomaly under study
- Not testable with this data: diagnostic/attribution: the target is a share of two months; there are no components to attribute
- Not testable with this data: predictive/classification: no class outcome in a province-year share
- Not testable with this data: predictive/forecast: covered by the leading-indicator claims
- Not testable with this data: predictive/timing: monthly sales cannot time the rush within a month
- Not testable with this data: prescriptive/policy: covered by the allocation claim
- Not testable with this data: prescriptive/trigger: the 7 C trigger was tested as G2 and adds nothing beyond October temperature
- G2 already failed on exploration data before registration, so its mutation gate says nothing.
- F2 already failed on exploration data before registration, so its mutation gate says nothing.
- P1 is blocked: rests on F1 (refuted).
- Refused at registration (`#10`, mutation gate): G3, "Within a province, a warmer March moves with a larger share of the spring swap landing in April (association)". the test has no teeth against permute:mar_mean_temp: it falsified only 3 of 5 mutants. Tighten the test or the threshold, or pick a mutant that really destroys what the claim asserts
- The diagnostic stage was reopened (`#19`): G3 was refused by a mutation-gate bug: permute skipped rows with any blank cell, leaving 17 true rows in every mutant; fixed in ledger.py.
- Data: Statistics Canada tables 20-10-0008 and 20-10-0056 (NAICS 4413 tire, parts and accessories stores, unadjusted, spliced as in the other examples) and Environment Canada daily climate data (api.weather.gc.ca), downloaded 2026-11-26. One airport station per province's largest or capital city, older and newer station IDs stitched by date.
- Disclosure: while building the dataset, the analyst's script printed each province's average October share, April share, fall 7 C day and spring 7 C day over 2010 to 2025, which includes the holdout years. Province-level averages do not show the year-to-year link between weather and timing that the claims test, but claims about province averages would be contaminated, so none is registered.
- The analyst had also seen, in earlier runs on the same sales tables, national and regional peak-month results (November vs October nationally, Alberta's October peaks, the Prairies' earlier October share). The weather link was never examined before this run.
- Weather is one city per province while sales cover the whole province.
- A framework bug found during this run: the permute mutant skipped every row with a blank cell in any column, so the 17 exploration rows missing a first-snow date kept their real values in every mutant. G3's first registration was refused because of it (the refusal is in the ledger); after the fix G3 killed 5 of 5 mutants. G1 had passed the gate at 4 of 5 under the bug.
- Weather is one city per province (for example Toronto for all of Ontario), and NAICS 4413 includes parts and accessories stores, so the October and April shares are diluted proxies for tire changeovers.
- These are industry-wide sales; the user's own stores may time differently.

## 5. Peer review

- Critic review before testing: `analysis/reviews/critic.md`.

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
| 0 | init |  | `de05efab971b` |
| 1 | profile |  | `9903e3f52dbc` |
| 2 | schema |  | `b75a6539201c` |
| 3 | register | D1 | `ff0bb199763a` |
| 4 | run | D1 | `1ec53b2efdf9` |
| 5 | replay | D1 | `f5d4d82d1d45` |
| 6 | waive |  | `9c71add0d727` |
| 7 | close | descriptive | `dc3abb9c8a1f` |
| 8 | register | G1 | `3dfc3b61d577` |
| 9 | register | G2 | `49714117ef68` |
| 10 | refused | G3 | `c312516f6f65` |
| 11 | run | G1 | `b783c5c583d7` |
| 12 | replay | G1 | `c07787620324` |
| 13 | run | G2 | `1528160c3b11` |
| 14 | replay | G2 | `0754f46ed57f` |
| 15 | waive |  | `ad9706a62e75` |
| 16 | waive |  | `e7b54b66c5f2` |
| 17 | waive |  | `917f2ef57a67` |
| 18 | close | diagnostic | `d4a98cf014f2` |
| 19 | reopen | diagnostic | `960e1a263bb3` |
| 20 | register | G3 | `9d24fbbeb378` |
| 21 | run | G3 | `5a585b5622be` |
| 22 | replay | G3 | `d7ea3ee169bc` |
| 23 | close | diagnostic | `f19b75bff21b` |
| 24 | register | F1 | `89c811a6193c` |
| 25 | register | F2 | `608b6234d1f0` |
| 26 | run | F1 | `48570ce0cf3e` |
| 27 | replay | F1 | `f5a65a6cdd6c` |
| 28 | run | F2 | `4dbc27142736` |
| 29 | replay | F2 | `a3550808d496` |
| 30 | waive |  | `c6c2f042e99d` |
| 31 | waive |  | `1415fa87baf8` |
| 32 | waive |  | `33ed93ec41fe` |
| 33 | close | predictive | `66a2b979a933` |
| 34 | register | P1 | `629fcc68ef27` |
| 35 | run | P1 | `ca6f7abd7c78` |
| 36 | replay | P1 | `c825735cd173` |
| 37 | waive |  | `abdf9dabc27d` |
| 38 | waive |  | `000676233e43` |
| 39 | close | prescriptive | `784821b3d46e` |
| 40 | goldfish | F1 | `4cde899d7038` |
| 41 | goldfish | P1 | `b03199e9fdd9` |
| 42 | goldfish | D1 | `418020d7a8aa` |
| 43 | goldfish | G1 | `6c2a30b9513a` |
| 44 | goldfish | G3 | `cab5fa6adbf6` |
| 45 | goldfish | F2 | `6642ce0b62e0` |
| 46 | goldfish | G2 | `35138571598a` |
| 47 | seeds | D1 | `ca12b51d1c46` |
| 48 | seeds | G1 | `bd8c626995b7` |
| 49 | seeds | G2 | `7d16e7c8d47d` |
| 50 | seeds | G3 | `f351268f4cef` |
| 51 | seeds | F1 | `4e55a546a032` |
| 52 | seeds | F2 | `79f10c769a4d` |
| 53 | seeds | P1 | `ca86a5603b2d` |
