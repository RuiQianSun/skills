# Notes on this run

- Source: Statistics Canada tables 20-10-0008 (archived, 2004 to 2022) and 20-10-0056 (current, 2017 to 2026), NAICS 4413 "Automotive parts, accessories and tire stores", unadjusted, $ thousands. Pulled 2026-11-23. NAICS 4413 includes parts and accessories stores, so it is not tire stores alone.
- Splice: in the 72 overlapping months the archived table runs 0.2% to 6% below the current one (revisions). Pre-2017 months are rescaled by each region's mean overlap ratio (Canada 1.030, Ontario 1.040, Quebec 1.060, Alberta 1.008, BC 1.002), and 2017 onward is the current table unchanged. The holdout (2016-07 onward) is almost all current-table data.
- No missing months. BC has one suppressed value; no claim uses BC.
- K5 overclaims in its wording. The test checks only that Alberta peaks in October in at least half of years (6 of 9). The goldfish found "ahead of the rest of Canada" holds in only 3 of 9 years, because the rest of Canada often peaks in October too. Read K5 as "Alberta usually peaks in October", nothing more.
- K2 and K4 pass with thin margins on 9 years and 99 months: K2's Wilcoxon p is the floor a 9-year sample allows, and K4's bootstrap interval for "drift beats naive" ends just below zero.
