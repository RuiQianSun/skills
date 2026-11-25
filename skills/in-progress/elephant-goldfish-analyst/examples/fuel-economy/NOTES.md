# Analyst notes

- Sample: electric, plug-in hybrid and gaseous-fuel vehicles are excluded, so every finding is about gasoline, diesel and conventional hybrid configurations.
- Data: EPA fueleconomy.gov `vehicles.csv` (downloaded 2026-11-25), model years 2012 to 2025; electric, plug-in hybrid and gaseous-fuel vehicles dropped because their combined MPG measures something else. Rows are configurations, not sales: a niche trim counts as much as a best-seller, so no finding here is about market share.
- Split: by model year as a panel (`--panel`): 2012 to 2019 explored, 2020 to 2025 sealed. Predictive and prescriptive tests train only on years up to Y-2 and score only configurations whose spec never appeared before, following the critic's horizon review.
- Roles were confirmed by the user at the checkpoint, including excluding six columns computed from MPG.
- The first P1 draft was refused by the mutation gate (on data with MPG shuffled it still "beat" the status quo by flagging nothing, because both status-quo rules lose money). The refusal is in the ledger; P1b adds a "creates value" condition.
- D1 is about recent years, so it already failed on 2012 to 2019 exploration data and its mutation check is uninformative; the paper flags this.
- Revision round after referee-1 (major revisions): G2r (non-hybrid attribution) refuted, F1r (full history, no make) refuted narrowly, P1r (flag-nothing comparator, cutoff sensitivity) survived its own test but is seed-sensitive and blocked. See `analysis/reviews/response-1.md`.
- Limitations not addressed: no sales weighting, no deduplication of carried-over configurations, no error breakdown near 30 mpg, no D3 band-width sensitivity, no partial correlations for G1, no intervals in registered tests.
- Correction to response 1: it said P1r's tester failed P1r. The tester's recorded result (at the workspace seed) is survived; the tester's prose described a check at seed 1, where the verdict flips. The seed check records this, and P1r is reported as seed-sensitive.
- F1h (full history, make kept) also misses the 2.0 mpg bar (mean 2.08), so F1's pass came from scoring fewer, easier years, not from make. The forecast still beat the similar-spec baseline in every year; a looser accuracy bar would be a new hypothesis for data not yet seen, so none was registered.
- G1 and D2 pass at or near their bars and hold only as narrowed by their testers.
