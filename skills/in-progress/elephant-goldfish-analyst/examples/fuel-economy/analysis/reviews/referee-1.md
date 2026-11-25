# Referee report 1

Reviewer: a fresh-context referee agent that saw only PAPER.md, the files it cites, and the audit.

VERDICT: major-revisions

The audit reproduces cleanly, but several headline claims overstate what their ledger entries show, and the forecast and policy tests ran on a truncated history.

## 1. Claims the evidence does not support as worded

- D1 (#4, #7): "at least 60% turbocharged in every model year" is false for the paper's stated 2012 to 2025 period (exploration shows 0.469, 0.538, 0.585 for 2012 to 2014). It holds only for the 2020 to 2025 holdout; the title and abstract must say so.
- P1b (#38): "creates value (+5 or more a year)" passes exactly at its bar in the registered result (share_years_payoff_ge_5 = 0.75); the replication's 1.0 (#42) does not change the primary result.
- P1b (#38): "beats both status-quo rules" is nearly vacuous, since both rules lose money (-101, -102). The real comparator is "flag nothing" (payoff 0); against it the model earns +31 over four years from 5 to 14 flags a year.
- G2 (#21, #27): "falling fuel consumption" holds only end to end; the net change is -0.079 gal/100 mi (about 1.7%), and total consumption rose 2020 to 2021 and 2021 to 2022. One "improving" pair has a within term of -0.0003.
- G2 narrowing text quotes the replication's mix figure (+0.13) rather than the registered result's (0.1149).
- G1 (#19): "moves strongly" passes exactly at the 80% bar (12 of 15 classes); the largest class, Small SUV 4WD (n = 861), fails at rho -0.55.
- D2 (#9, #15): the replication's bootstrap slope interval [0.23, 1.26] pp leaves "not rising by more than 1 pp a year" uncertain, and the last step was +2.3 pp.
- D3 (#6): the registered thresholds (1 mpg each year, 1.5 on average) are weaker than the critic's suggestion (2 mpg) without explanation; the observed gap (mean 3.46, minimum 2.5) passes either way, so the abstract understates it.

## 2. Variable roles

- No feature appears to be recorded after the outcome; the six MPG-derived exclusions are correct.
- vclass partly duplicates drive, and lets hybrid growth hide inside "within-class" in G2 (hybrid share of holdout configurations 7.1% to 25.6%).
- make as a one-hot predictor invites memorisation; novelty on the full spec tuple counts a carried-over engine with a new label as new.
- id correlates with year; correctly a key, and should stay out of every model matrix.

## 3. Missing analyses

- F1 and P1b ran on the holdout alone, so the 2022 model trained on a single year and novelty ignored 2012 to 2019. Use the full history.
- G2 and D2 need a hybrid-stratified or non-hybrid analysis to separate engine improvement from hybrid substitution.
- No sales-weighted check; "niche" and "fuel consumption" are about configuration counts.
- Many holdout rows duplicate another row's spec within a year; G1 pools carried-over configurations. A deduplicated check is needed.
- P1b needs a "flag nothing" comparator and sensitivity to the 30 mpg cutoff and payoff weights.
- F1 errors should be broken out near the 30 mpg threshold P1b depends on.
- D3 sensitivity to band width; RWD and 4WD comparisons.
- G1 is confounded by cylinders and turbo; partial or within-year correlations expected.
- Registered tests report no intervals.

## 4. Audit

All 38 checks passed and reproduced. The audit confirms byte-identical reruns, not correctness: it cannot show the critic reviews came before any look at the data, and it does not catch the problems in sections 1 and 3.
