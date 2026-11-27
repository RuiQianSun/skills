# Does Snowfall Drive Fall Tire Sales in Canada?

*Generated from the evidence ledger `analysis/LEDGER.jsonl` (head `8a88e26837c3d9fb`, 25 entries, chain intact). Every number below cites the ledger entry it came from as `#n`. To check this paper, run `python3 ledger.py audit`, which re-executes every result.*

## Abstract

All findings below are about year 2018 to 2025, the period sealed before analysis; earlier periods were used only to form hypotheses. We registered 4 claims before testing them on held-out data, across 1 insight categories. 0 stand as established, 2 were refuted, 0 were superseded by later tests, and 2 are open (contested, blocked, seed-sensitive or untested).

Not established:

- **H1**: refuted. Within a province, snowier Octobers move with a larger share of the fall rush landing in October
- **H2**: not tested: fixed-sequence rule: H1 did not reject its null, so the causal test is not run. Holding October temperature fixed, more October snow causes more of the fall rush to land in October (tested only if H1 rejects)
- **V1**: refuted. Within a province, snowier falls (October plus November) move with a larger share of the year's sales landing in October and November
- **V2**: not tested: fixed-sequence rule: V1 did not reject its null, so the causal test is not run. Holding fall temperatures fixed, more fall snow causes a larger fall share of annual sales (tested only if V1 rejects)

## 1. Data

- Source: `fall_snow_by_province.csv`, sha256 `b32590e23f160ddb`, 128 rows, 13 columns.
- Split (`#0`): ordered by year, seed 20261123; 64 rows for exploration, 64 sealed for confirmation (exploration up to 2017).
- Data audit before sealing: {"duplicate_keys": [], "empty_cells": {}}.

### 1.1 Variables (`#1`, confirmed by the user (domain owner), 2026-11-27)

| role | columns | meaning |
|---|---|---|
| exclude | oct_sales, nov_sales, annual_sales, snow_days_recorded_oct_dec | unusable or leaky: recorded after the outcome, a duplicate of the target, or junk (oct_sales: ingredient of the targets; nov_sales: ingredient of the targets; annual_sales: ingredient of fall_share; snow_days_recorded_oct_dec: data-quality count) |
| feature | oct_snow_cm, nov_snow_cm, dec_snow_cm, oct_mean_temp, nov_mean_temp, province | independent variable: a candidate explanation or predictor |
| segment | province | a grouping used to slice results (can also be a feature) |
| target | oct_share, fall_share | dependent variable: the outcome the analysis explains or predicts |
| time | year | the order key for time series |

Exposure: October and November snowfall. Controls: October and November mean temperature. Placebo: December snowfall, which falls after the outcome months. Alpha 0.05 with fixed-sequence testing (the causal test only if the association test rejects).

## 2. Methods

Each claim was written down with its kill criterion and the decision it informs, reviewed by a critic agent that saw no data, and frozen (its test script hashed) before its single look at the sealed holdout. Registration required the test to pass a lint for future-peeking and leaky code, a smoke run on exploration data, and a mutation gate: on copies of the data with the claimed pattern destroyed, the test had to report falsified at least 4 times in 5. Results were replayed byte-for-byte, then replicated by independent agents who saw only the claim and the holdout and wrote their own method. Prescriptive claims count only if the claim they rest on is established.

- Holdout looks used: 2 of a budget of 6.
- Claims registered: 4; attempts refused by the gates: 0 (together, the multiple-comparisons count; thresholds were set per claim at registration).
- Replicating agents: goldfish-H1-sonnet, goldfish-V1-sonnet.
- Seed check: 2 claims rerun under several seeds; all stable.
- Stage log: `#3` close descriptive; `#16` close diagnostic; `#18` close predictive; `#20` close prescriptive.

## 3. Results

### 3.1 Descriptive

No claims. Waived: this workspace answers one question: is snowfall associated with, and a cause of, fall tire sales

### 3.2 Diagnostic

#### H1: Within a province, snowier Octobers move with a larger share of the fall rush landing in October

- **Status: refuted.** Type diagnostic/driver.
- Decision it informs: Treat October snowfall as a timing signal for fall staffing.
- Pre-registered (`#4`): predicted detrended within-province Spearman > 0 with two-sided permutation p < 0.05; falsified if rho <= 0 or p >= 0.05. Test `analysis/tests/H1.py` sha `503ec5ad00e6`.
- Scope: scored on year 2018 to 2025 (the sealed holdout), with earlier rows available as history.
- Seed check (`#23`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: falsified/falsified/falsified/falsified; goldfish-H1-sonnet: falsified/falsified/falsified/falsified.
- Gates: smoke run on exploration data falsified; mutant permute:oct_snow_cm killed 5/5 (uninformative).
- Holdout result (`#6`): **falsified**, alpha=0.05, n=64, p_two_sided=0.372, rho=-0.1121, rho_95ci=[-0.412, 0.245], smallest_detectable_rho=0.242. Replay `#7` byte-identical.
- Replication by goldfish-H1-sonnet (`#21`): falsified (agrees); method: province-specific linear detrending (own level+trend) on scored rows, pooled within slope of oct_share on oct_snow_cm; two-sided within-province permutation test (20000), cluster bootstrap CI over provinces; ci95=[-0.0029779066580566467, -0.00022898201830345516], n_provinces=8, n_rows=64, p_value=0.1800409979501025, provinces_positive=3, slope_per_cm=-0.0007527044450117281. Tester's note: pooled slope -0.00075 per cm (permutation p 0.18); only 3 of 8 provinces positive; detrend fitted on scored years only.

#### H2: Holding October temperature fixed, more October snow causes more of the fall rush to land in October (tested only if H1 rejects)

- **Status: not tested: fixed-sequence rule: H1 did not reject its null, so the causal test is not run.** Type diagnostic/causal.
- Decision it informs: Plan around snowfall forecasts, not just temperature.
- Pre-registered (`#5`): predicted positive snow coefficient with permutation p < 0.05, and the December-snow placebo not significant; falsified if coefficient <= 0, p >= 0.05, or placebo p < 0.05. Test `analysis/tests/H2.py` sha `d453971a5707`.
- Scope: scored on year 2018 to 2025 (the sealed holdout), with earlier rows available as history.
- Gates: smoke run on exploration data falsified; mutant permute:oct_snow_cm killed 5/5 (uninformative).

#### V1: Within a province, snowier falls (October plus November) move with a larger share of the year's sales landing in October and November

- **Status: refuted.** Type diagnostic/driver.
- Decision it informs: Expect higher fall volume in snowy years.
- Pre-registered (`#8`): predicted detrended within-province Spearman > 0 with two-sided permutation p < 0.05; falsified if rho <= 0 or p >= 0.05. Test `analysis/tests/V1.py` sha `a3735ede2a64`.
- Scope: scored on year 2018 to 2025 (the sealed holdout), with earlier rows available as history.
- Seed check (`#24`, seeds [20261123, 20261124, 20261125, 1]): stable; elephant: falsified/falsified/falsified/falsified; goldfish-V1-sonnet: falsified/falsified/falsified/falsified.
- Gates: smoke run on exploration data falsified; mutant permute:oct_snow_cm killed 5/5 (uninformative); mutant permute:nov_snow_cm killed 5/5 (uninformative).
- Holdout result (`#10`): **falsified**, alpha=0.05, n=64, p_two_sided=0.445, rho=-0.1022, rho_95ci=[-0.23, 0.064], smallest_detectable_rho=0.255. Replay `#11` byte-identical.
- Replication by goldfish-V1-sonnet (`#22`): falsified (agrees); method: per-province detrended (intercept+linear trend) slope of fall_share on Oct+Nov snow, scored rows only; one-sample two-sided t-test across provinces (df=7); sign-flip permutation as check; ci95=[-0.0002574541103765794, 0.00019846162847133604], effect_mean_slope_per_cm=-2.9496240952621693e-05, n_positive_slopes=3, n_provinces=8, n_rows=64, p_signflip=0.76265, p_value=0.7685290689864819, pooled_within_slope=-1.1237746002562444e-05, t=-0.30596674229164916. Tester's note: per-province slopes t-tested across 8 provinces: t -0.31, p 0.77; 3 of 8 positive.

#### V2: Holding fall temperatures fixed, more fall snow causes a larger fall share of annual sales (tested only if V1 rejects)

- **Status: not tested: fixed-sequence rule: V1 did not reject its null, so the causal test is not run.** Type diagnostic/causal.
- Decision it informs: Size fall winter-tire stock to snowfall forecasts.
- Pre-registered (`#9`): predicted positive snow coefficient with permutation p < 0.05, and the December-snow placebo not significant; falsified if coefficient <= 0, p >= 0.05, or placebo p < 0.05. Test `analysis/tests/V2.py` sha `e37e20a2d9bb`.
- Scope: scored on year 2018 to 2025 (the sealed holdout), with earlier rows available as history.
- Gates: smoke run on exploration data falsified; mutant permute:oct_snow_cm killed 5/5 (uninformative); mutant permute:nov_snow_cm killed 5/5 (uninformative).


### 3.3 Predictive

No claims. Waived: the question is diagnostic only

### 3.4 Prescriptive

No claims. Waived: the question is diagnostic only
## 4. Threats to validity

- Not testable with this data: descriptive: this workspace answers one question: is snowfall associated with, and a cause of, fall tire sales
- Not testable with this data: diagnostic/attribution: not part of the snowfall question
- Not testable with this data: diagnostic/root-cause: not part of the snowfall question
- Not testable with this data: predictive: the question is diagnostic only
- Not testable with this data: prescriptive: the question is diagnostic only
- H1 already failed on exploration data before registration, so its mutation gate says nothing.
- H1 was not reviewed by a critic before registration.
- H2 is not tested: fixed-sequence rule: H1 did not reject its null, so the causal test is not run.
- H2 already failed on exploration data before registration, so its mutation gate says nothing.
- H2 was not reviewed by a critic before registration.
- H2 has no independent replication.
- V1 already failed on exploration data before registration, so its mutation gate says nothing.
- V1 was not reviewed by a critic before registration.
- V2 is not tested: fixed-sequence rule: V1 did not reject its null, so the causal test is not run.
- V2 already failed on exploration data before registration, so its mutation gate says nothing.
- V2 was not reviewed by a critic before registration.
- V2 has no independent replication.
- Question (from the user): is winter-tire buying correlated with snowfall, and if so, is it caused by it? Alpha 0.05, set by the user. The causal test runs only if the association test rejects first (fixed-sequence testing), which keeps the overall false-positive rate at 5% without dividing alpha.
- Design for the causal step: reverse causation is ruled out (buying tires cannot make it snow), so the remaining threat is confounding, mainly cold, which drives both snow and tire buying. The causal test holds temperature fixed within each province and adds a placebo, December snow, which falls after the outcome months and so cannot cause them.
- Data: the same Statistics Canada sales and Environment Canada weather as the winter-tire-timing example. Manitoba and Saskatchewan are excluded because their stations record no snowfall at all (automated stations), and zero would be wrong, not missing. Some years have up to about 20 unrecorded snow days in October to December, which undercounts snow slightly.
- Power: the association tests could only detect within-province correlations of about 0.25 or stronger (see each result's smallest detectable correlation). A weaker real effect would go unseen.
- Monthly sales blur the effect: a snowfall late in October and the rush it triggers may fall in the same month or straddle two. Daily or weekly store sales around each region's first-snowfall date (an event study) would be the right design to settle the causal question.
- The analyst had analysed the same sales and temperature data in the winter-tire-timing example (where October temperature was linked to timing) before this run; snowfall itself had not been examined.
- No critic reviewed these hypotheses before testing; the user specified them directly.

## 5. Peer review

- No critic reviews recorded.

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
| 0 | init |  | `c06613098419` |
| 1 | schema |  | `a6dbb5ce40d3` |
| 2 | waive |  | `e57225ee83aa` |
| 3 | close | descriptive | `e40b9f06d767` |
| 4 | register | H1 | `607ace1c039d` |
| 5 | register | H2 | `5cd370b20dc0` |
| 6 | run | H1 | `b6f70e317320` |
| 7 | replay | H1 | `d1b6778b9431` |
| 8 | register | V1 | `50bb12310b43` |
| 9 | register | V2 | `65dc07f99a62` |
| 10 | run | V1 | `e89ba72b6a23` |
| 11 | replay | V1 | `17124b4f3563` |
| 12 | skip | H2 | `63a3780f0515` |
| 13 | skip | V2 | `e57b3c75d33b` |
| 14 | waive |  | `eaaafbb902a7` |
| 15 | waive |  | `24edd66dc6a3` |
| 16 | close | diagnostic | `a8312797f4b6` |
| 17 | waive |  | `c3b5ff482c52` |
| 18 | close | predictive | `01d59d27ffb0` |
| 19 | waive |  | `f7e6105f6bac` |
| 20 | close | prescriptive | `f74c50d76a1e` |
| 21 | goldfish | H1 | `500a72962161` |
| 22 | goldfish | V1 | `48aaee458440` |
| 23 | seeds | H1 | `c28cf2cbbf43` |
| 24 | seeds | V1 | `8a88e26837c3` |
