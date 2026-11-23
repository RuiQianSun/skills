import os, csv, json, random
from collections import defaultdict
random.seed(int(os.environ["SEED"]))  # no randomness used; the test is an exact census
cols = ["mb", "sk", "ns", "nb", "nl", "pe"]
months = defaultdict(dict)
with open(os.environ["DATA"]) as f:
    for r in csv.DictReader(f):
        try:
            vals = {c: float(r[c]) for c in cols}
        except (ValueError, TypeError):
            continue  # month with any missing province is not usable
        months[r["month"][:4]][r["month"][5:7]] = vals
years = {}
for y, ms in sorted(months.items()):
    if len(ms) != 12:
        continue  # complete year = all 12 months present with all 6 provinces
    pr = sum(v["mb"] + v["sk"] for v in ms.values())
    tot = sum(sum(v[c] for c in cols) for v in ms.values())
    years[y] = round(pr / tot, 4)
monthly_min = min(((v["mb"] + v["sk"]) / sum(v[c] for c in cols), y + "-" + m)
                  for y, ms in months.items() for m, v in ms.items())
fails = [y for y, s in years.items() if s <= 0.5]
print(json.dumps({
    "verdict": "falsified" if fails or not years else "survived",
    "method": "exact census: annual Prairie (mb+sk) share of six-province sum over calendar years with all 12 months; falsified if any share <= 0.5",
    "complete_years": list(years),
    "annual_prairie_share": years,
    "min_annual_share": min(years.values()) if years else None,
    "min_year": min(years, key=years.get) if years else None,
    "failing_years": fails,
    "partial_years_excluded": sorted(y for y, ms in months.items() if len(ms) != 12),
    "min_monthly_share": round(monthly_min[0], 4), "min_monthly_month": monthly_min[1],
}))
