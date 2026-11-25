# Response to referee report 2

The referee's central point is right: the first revision answered referee 1 with new analyses but did not carry their conclusions into the paper. The ledger now records those conclusions as entries (`supersede`, `withdraw`), and the paper generator reads them, so the abstract can no longer present a superseded claim as plainly established.

## Carrying conclusions into the paper

- **F1, P1b and G2.** F1 is superseded by F1h and F1r, P1b by P1r, and G2 by G2r, each with its reason; G2's decision is withdrawn. The abstract now separates "established without qualification", "established only with qualifications" and "not established", and each qualified claim carries its reasons inline.
- **Seed results.** Reported in Methods and in each claim's results entry. P1r is the only unstable claim and is reported as seed-sensitive.
- **Limitations, G1 and D2.** The notes file is now included line by line in the threats section, and every claim that holds only as narrowed by its tester is listed there automatically.
- **Sample filter.** Section 4 states that electric, plug-in hybrid and gaseous-fuel vehicles are excluded.
- **Review provenance.** Claims reviewed only by a referee report are labelled as such ("no pre-test critic saw this exact wording"), and the peer review section no longer lists referee reports as critic reviews.

## Correction

Response 1 misstated P1r's replication. The tester's recorded result, at the workspace seed, is survived and agrees; its prose described a check at seed 1, where the verdict flips. The paper reports the recorded result and the seed check. The skill now tells testers to check their scripts with the workspace seed, and tells the analyst to quote recorded entries rather than a tester's prose.

## Missing analyses

- **F1r's two changes, separated.** F1h keeps make and uses the full history. It is refuted on the same bar (mean error 2.08; the tester got 2.09), while beating the similar-spec baseline in every year. So F1's original pass came from scoring fewer, easier years, not from make. No looser bar was registered: choosing a threshold after seeing the holdout would be a new hypothesis for unseen data.
- **P1r vs P1b.** P1b is superseded by P1r. P1r stays blocked, because the predictive claims it rests on are refuted at the accuracy bar they were registered with, and it is seed-sensitive in its replication. The policy evidence is promising but not established; the paper says so.
- **Not done, and listed as limitations:** errors near 30 mpg, deduplication of carried-over configurations, sales weighting, D3 band-width sensitivity, partial correlations for G1, intervals in the registered tests.

## Audit

Agreed that the audit proves reproducibility, not correctness. Seed entries are reported in the paper but not re-executed by the audit, since rerunning every test under every seed is slow; `ledger.py seeds all` reproduces them.
