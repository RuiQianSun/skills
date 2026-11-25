# Response to referee report 1

Registered claims are immutable, so each point is answered with a revised claim under a new id, a change to how the paper reports results, or an explicit limitation. Entry numbers refer to the ledger.

## Claims not supported as worded

- **D1 scope.** Agreed. Every claim was tested on model years 2020 to 2025 only. The paper now states each claim's scope in its results entry, and the abstract opens by saying all findings are about 2020 to 2025. The wording of D1 is unchanged because registrations are frozen.
- **P1b passes at its bar; P1b's comparator.** Agreed on both. P1r compares the model's flag with "flag nothing", varies the cutoff (29, 30, 31 mpg) and uses the full history. P1r survived its own test, but its tester failed it on the "+5 or more in 75% of years" condition (4 of 6 years), and the seed check found the tester's verdict flips with the random seed. P1r is also blocked because the forecast it rests on (F1r) is refuted. Conclusion: flagging predicted 30+ mpg configurations beat both status-quo rules by more than 100 points of payoff and earned a positive payoff in each year at the workspace seed, but it is **not established**. It needs more years or a field test.
- **G2's small net change and hybrid substitution.** Agreed, and the referee was right. G2r repeats the decomposition on non-hybrids only and is **refuted**: among non-hybrids the within-class cut is only 0.057 gal/100 mi, smaller than the mix effect (+0.113), and fuel consumption rose slightly. G2 stays established as worded for all configurations, but its decision ("credit efficiency gains to within-class improvement") is withdrawn: most of that gain was hybrid substitution.
- **G2 narrowing figure.** The narrowed reading is the tester's own text, which quotes its replication. The paper now labels narrowed readings as the tester's words, and the registered figure (mix +0.1149, `#21`) is the one quoted in results.
- **G1 at its bar; D2's uncertain slope.** Agreed. Both are reported with the narrowed readings their testers gave. Re-testing them with stricter wording would spend another look at the same holdout for a claim we already know is marginal, so they are left as narrowed and listed under threats to validity.
- **D3 thresholds.** The thresholds came from the exploration data, where the smallest yearly like-for-like gap was 1.0 mpg (2015). The observed holdout gap (minimum 2.5, mean 3.46) is reported in full in the results.

## Variable roles

- **make.** F1r drops make as a predictor. It is **refuted** on its accuracy bar (mean error 2.10 mpg against 2.0; the tester got 2.045), although it still beat the similar-spec baseline in every year. F1's accuracy depended partly on make, the shorter history, or both.
- **id.** It is a key in the confirmed schema and appears in no model's predictor list.
- **vclass and drive overlap.** Acknowledged as a limitation; not re-tested.

## Missing analyses

- **Full history for forecasts.** Fixed in the framework: confirmation runs in time-ordered workspaces now receive explore and holdout rows together and score only the holdout window. F1r and P1r used it.
- **Hybrid-stratified attribution.** Done (G2r, above).
- **Flag-nothing comparator and cutoff sensitivity.** Done (P1r, above).
- **Seed robustness.** Added to the framework after this review: `ledger.py seeds` reran every test and replication under four seeds. All claims were stable except P1r.
- **Not done:** a sales-weighted check (no sales data), a deduplicated check of carried-over configurations, F1 errors near the 30 mpg threshold, D3 band-width sensitivity, partial correlations for G1, and intervals in the registered tests. These are listed as limitations.

## Audit

Agreed that the audit proves reproducibility, not correctness, and that it cannot prove each critic review was written before any look at the holdout. The ledger records each review's hash at registration, which proves the review existed in that form when the claim was frozen, but not when it was written.
