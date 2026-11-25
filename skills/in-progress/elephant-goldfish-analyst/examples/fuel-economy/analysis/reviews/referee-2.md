# Referee report 2

Reviewer: a fresh-context referee agent that saw the revised PAPER.md, the files it cites (including referee report 1 and the response), and the audit.

VERDICT: major-revisions

The audit reproduces cleanly, and G2r, F1r and P1r answer the substance of referee 1's main points. But the revision did not carry its own conclusions into the paper: the abstract still lists F1, P1b and G2 as established without caveat, although F1r refuted the corrected version of F1, P1r is blocked, and the response withdraws G2's decision. Several promises in the response are missing from PAPER.md.

## Response to referee 1

- D1 scope: answered.
- P1b: partly answered; P1b stays established in the abstract without caveat, contradicting the response.
- The response misstates P1r's replication: the recorded replication (#61) is survived (it agrees), with +5 or more in 5 years; the verdict flips only at seed 1 (#71), and the tester's prose ("4 of 6") does not match its recorded output.
- G2: analysis done (G2r refuted) but the paper still carries G2's decision without a withdrawal, and the withdrawn wording in the response is not G2's registered decision.
- G2 narrowing figure: answered.
- G1 and D2 marginal: promised under threats to validity, but not there.
- D3 thresholds: answered.
- make and full history: F1r done and refuted, but F1 and P1b stay established though their design is the one faulted.
- Limitations: listed only in NOTES.md, not in the paper.
- Seed robustness: done (#62 to #71) but never reported in the paper.

## Claims not supported as worded

- F1 (#28, #29): "never-before-seen" was tested against the holdout only, and "trained up to two years earlier" meant one training year for 2022. Fixed together in F1r, it fails (2.095 vs 2.0). "From specs alone" is wrong while make is a predictor.
- P1b (#38): fails "+5 a year" in one of four years; its replication agrees on the verdict but not the numbers; it rests on the faulted F1.
- P1r vs P1b: P1r has the better design and passed its own test, yet is blocked because F1r missed an MAE bar the policy does not use, while P1b stays established. Qualify both or explain.
- G2 (#21, #27): the within-class cut is mostly hybrid substitution (G2r); the abstract should say so.
- D2 (#9, #15) and G1 (#19): marginal, and should not be headlined as established.

## Variable roles

- No feature appears to be recorded after the outcome.
- make enables memorisation; F1r's failure without it suggests F1 relies on it.
- vclass overlaps drive.
- The sample excludes EVs, PHEVs and gaseous fuels; section 1 should say so.

## Missing analyses that would change a conclusion

- F1r changed the history and dropped make at once; run one change at a time to see whether F1 survives full history with make.
- F1 errors near 30 mpg, which P1b's payoff depends on.
- Deduplicate carried-over configurations; G1 and D2 are close enough that it could flip them.

## Audit

- 0 failures, 55 checks. Re-execution proves reproducibility, not correctness.
- G2r, F1r and P1r list referee-1.md as their critic review, so no pre-test critic saw their final wording, and the paper mislabels it.
- Seed entries are not re-checked by the audit and are not reported in the paper.
