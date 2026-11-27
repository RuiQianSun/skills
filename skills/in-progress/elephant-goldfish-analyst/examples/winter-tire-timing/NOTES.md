# Analyst notes

- Data: Statistics Canada tables 20-10-0008 and 20-10-0056 (NAICS 4413 tire, parts and accessories stores, unadjusted, spliced as in the other examples) and Environment Canada daily climate data (api.weather.gc.ca), downloaded 2026-11-26. One airport station per province's largest or capital city, older and newer station IDs stitched by date.
- Disclosure: while building the dataset, the analyst's script printed each province's average October share, April share, fall 7 C day and spring 7 C day over 2010 to 2025, which includes the holdout years. Province-level averages do not show the year-to-year link between weather and timing that the claims test, but claims about province averages would be contaminated, so none is registered.
- The analyst had also seen, in earlier runs on the same sales tables, national and regional peak-month results (November vs October nationally, Alberta's October peaks, the Prairies' earlier October share). The weather link was never examined before this run.
- Weather is one city per province while sales cover the whole province.
- A framework bug found during this run: the permute mutant skipped every row with a blank cell in any column, so the 17 exploration rows missing a first-snow date kept their real values in every mutant. G3's first registration was refused because of it (the refusal is in the ledger); after the fix G3 killed 5 of 5 mutants. G1 had passed the gate at 4 of 5 under the bug.
- Weather is one city per province (for example Toronto for all of Ontario), and NAICS 4413 includes parts and accessories stores, so the October and April shares are diluted proxies for tire changeovers.
- These are industry-wide sales; the user's own stores may time differently.
