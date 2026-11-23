import os, json, csv, random
from collections import defaultdict

random.seed(int(os.environ["SEED"]))
rows = defaultdict(dict)
with open(os.environ["DATA"]) as f:
    for r in csv.DictReader(f):
        y, m = r["month"].split("-")
        try:
            rows[int(y)][int(m)] = {k: float(r[k]) for k in ("canada", "alberta")}
        except (ValueError, TypeError):
            pass

# Complete years only: all 12 months present with values.
years = sorted(y for y, ms in rows.items() if set(ms) == set(range(1, 13)))
alb_peak, roc_peak = {}, {}
for y in years:
    ms = rows[y]
    alb_peak[y] = max(range(1, 13), key=lambda m: ms[m]["alberta"])
    # Rest of Canada = national total minus Alberta.
    roc_peak[y] = max(range(1, 13), key=lambda m: ms[m]["canada"] - ms[m]["alberta"])

oct_flags = [1 if alb_peak[y] == 10 else 0 for y in years]
n = len(years)
share = sum(oct_flags) / n
ahead = [1 if (alb_peak[y] == 10 and roc_peak[y] > 10) else 0 for y in years]

# Bootstrap over years for uncertainty in the share.
B = 10000
boots = sorted(sum(random.choice(oct_flags) for _ in range(n)) / n for _ in range(B))
ci = [boots[int(0.025 * B)], boots[int(0.975 * B) - 1]]

print(json.dumps({
    "verdict": "falsified" if share < 0.50 else "survived",
    "method": "per complete calendar year, argmax month of Alberta unadjusted sales; share of years where argmax is October vs 0.50 threshold; year-level bootstrap 95% CI; secondary check: rest-of-Canada (canada minus alberta) peak month later than October",
    "n_complete_years": n,
    "years": years,
    "oct_peak_years": sum(oct_flags),
    "share_oct_peak": round(share, 4),
    "bootstrap_ci95": ci,
    "alberta_peak_month_by_year": {str(y): alb_peak[y] for y in years},
    "rest_of_canada_peak_month_by_year": {str(y): roc_peak[y] for y in years},
    "share_oct_peak_and_roc_later": round(sum(ahead) / n, 4),
}))
