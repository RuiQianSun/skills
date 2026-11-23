import csv, json, os, random
from collections import defaultdict

random.seed(int(os.environ["SEED"]))
rows = list(csv.DictReader(open(os.environ["DATA"])))
by_year = defaultdict(dict)
for r in rows:
    y, m = r["month"].split("-")
    v = r["canada"].strip()
    if v and v.lower() != "nan":
        by_year[int(y)][int(m)] = float(v)

complete = sorted(y for y, d in by_year.items() if len(d) == 12)
peaks = {y: max(by_year[y], key=by_year[y].get) for y in complete}
n = len(complete)
n_nov = sum(1 for p in peaks.values() if p == 11)
share = n_nov / n if n else float("nan")

# Supplementary: bootstrap over years for uncertainty in the share (not used for verdict)
boots = sorted(sum(peaks[random.choice(complete)] == 11 for _ in range(n)) / n for _ in range(10000))
ci = [boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots)) - 1]]

# Margin of Nov over the runner-up month each year
margins = {}
for y in complete:
    d = by_year[y]
    others = max(v for m, v in d.items() if m != 11)
    margins[y] = round(d[11] / others - 1, 4)

print(json.dumps({
    "verdict": "falsified" if share < 0.80 else "survived",
    "method": "count of complete calendar years (12 months present, national 'canada' series) whose max-sales month is November; threshold 0.80",
    "complete_years": complete,
    "n_complete_years": n,
    "n_peak_nov": n_nov,
    "share_peak_nov": round(share, 4),
    "peak_month_by_year": {str(y): p for y, p in peaks.items()},
    "nov_vs_best_other_month_ratio_minus_1": {str(y): m for y, m in margins.items()},
    "bootstrap_95ci_share": ci,
}))
