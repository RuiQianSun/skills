# Referee report 3

Reviewer: a fresh-context referee agent that saw the twice-revised PAPER.md, the files it cites (both earlier reports and responses), and the audit.

VERDICT: minor-revisions

The ledger and audit are clean, and the revision now carries its conclusions into the abstract honestly: refuted, superseded and blocked claims are shown as such.

## Response 2

Mostly adequate: supersede and withdraw entries, a three-tier abstract, seed results reported, limitations and narrowings in the paper, review provenance relabelled, P1r's replication corrected. F1h runs the requested one-change test, but its interpretation is wrong (below). The sample filter appears in section 4, not section 1.

## Claims still stated more strongly than the evidence

- F1h explanation (#76 vs #29): "F1's pass came from scoring fewer, easier years" is contradicted by the paper's own numbers: on the same 2022 to 2025 years F1h averages 2.02 against F1's 1.90. The difference comes from the longer training history and the changed "never seen" test set. The #79 supersede reason is the accurate one.
- D3 (#6, #11, #16): "like for like (same class)" holds only for car and wagon classes, because EPA splits SUV, pickup and minivan classes by drive, so FWD and AWD never share an SUV class. The claim and decision should say "cars and wagons".
- G1 (#19, #26): fragile even as narrowed: three passing classes are within 0.06 of the bar, and a class-stratified bootstrap reaches the 80% bar about 74% of the time.
- G2 supersede and withdraw notes (#82, #83): "mostly hybrid substitution" is inferred from two shift-shares on different populations; no hybrid-share decomposition was registered, so word it as an inference.
- D2 (#9, #15): "stay a niche" reads as forward-looking; the replication's slope interval reaches 1.26 pp a year and 2025 rose 2.3 pp.

## Variable roles

- vclass encodes drive (2WD/4WD classes), which is the source of D3's restriction and overlaps drive in the forecasts.
- make is mostly harmless now (F1h and F1r differ by 0.016 MAE), but F1h's wording "a spec model" should say it uses make.
- D3 compares only Front-Wheel Drive with All-Wheel Drive and silently drops 4-Wheel Drive and part-time 4WD.

## Missing analyses that would change a stated conclusion

- D2 among newly introduced configurations (first appearance since 2012): the 30+ mpg share reaches 22.3% in 2025, breaking "under 20% every year". Within-year deduplication still passes.
- D3 for SUVs (Small SUV 2WD FWD against Small SUV 4WD AWD at the same displacement) before the penalty is quoted beyond cars.
- G1 under deduplication helps it: 9 of 11 classes pass, with a 90% bootstrap pass rate.

## Audit

0 failures across 62 checks. Not re-checked: seed entries and supersede and withdraw entries. AUDIT.md still labels referee reports as the critic review for G2r, F1r, P1r and F1h.

The referee's own checks were ad hoc scripts, not ledger entries.
