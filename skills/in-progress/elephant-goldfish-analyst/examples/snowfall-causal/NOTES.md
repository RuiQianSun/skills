# Analyst notes

- Question (from the user): is winter-tire buying correlated with snowfall, and if so, is it caused by it? Alpha 0.05, set by the user. The causal test runs only if the association test rejects first (fixed-sequence testing), which keeps the overall false-positive rate at 5% without dividing alpha.
- Design for the causal step: reverse causation is ruled out (buying tires cannot make it snow), so the remaining threat is confounding, mainly cold, which drives both snow and tire buying. The causal test holds temperature fixed within each province and adds a placebo, December snow, which falls after the outcome months and so cannot cause them.
- Data: the same Statistics Canada sales and Environment Canada weather as the winter-tire-timing example. Manitoba and Saskatchewan are excluded because their stations record no snowfall at all (automated stations), and zero would be wrong, not missing. Some years have up to about 20 unrecorded snow days in October to December, which undercounts snow slightly.
- Power: the association tests could only detect within-province correlations of about 0.25 or stronger (see each result's smallest detectable correlation). A weaker real effect would go unseen.
- Monthly sales blur the effect: a snowfall late in October and the rush it triggers may fall in the same month or straddle two. Daily or weekly store sales around each region's first-snowfall date (an event study) would be the right design to settle the causal question.
- The analyst had analysed the same sales and temperature data in the winter-tire-timing example (where October temperature was linked to timing) before this run; snowfall itself had not been examined.
- No critic reviewed these hypotheses before testing; the user specified them directly.
