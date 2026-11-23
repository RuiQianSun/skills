# Notes on this run

- Source: Statistics Canada tables 20-10-0008 (archived) and 20-10-0056 (current), NAICS 4413, unadjusted, for MB, SK, NS, NB, NL, PE, spliced as in the canada-tire-stores example. Sealed as of 2024-09 (`provinces_asof_2024-09.csv`); `provinces_full.csv` (to 2026-09) was added later with `extend` as fresh data.
- The old table suppresses most of these provinces for 2004 to 2009, so the usable explore window was 2010-01 to 2015-04 (five complete years). Tests drop that leading block before computing anything.
- The elephant had analysed the national total and five other regions from the same tables in an earlier run; these six provinces were not examined before this run.
- Claims were revised once after the critic review (`analysis/reviews/batch-1.md`), before registration. Thresholds were set on explore data only.
- R1 leaks slightly: November's drift forecast uses October sales, which a buyer ordering fall stock would not have yet. The R1 goldfish tested the leak-free reading too, with the same verdict.
- G2 was registered as expected to fail and survived; the goldfish narrowed "strongly" to "moderately" (rho about 0.54).
- Sales are not demand: stock-outs censor them, so R1's shortfall cost is understated where stores ran out.
