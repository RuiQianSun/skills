import os, json, random, csv
from collections import defaultdict
random.seed(int(os.environ.get("SEED", "0")))
rows = list(csv.DictReader(open(os.environ["DATA"])))
agg = defaultdict(lambda: [0, 0.0, 0.0])
for r in rows:
    y = int(r["month"][:4]); a = agg[y]
    a[0] += 1
    a[1] += float(r["mb"]) + float(r["sk"])
    a[2] += float(r["ns"]) + float(r["nb"]) + float(r["nl"]) + float(r["pe"])
years = sorted(y for y, a in agg.items() if a[0] == 12)
P = {y: agg[y][1] for y in years}; A = {y: agg[y][2] for y in years}
pairs = []; viol = []
for i, y1 in enumerate(years):
    for y2 in years[i+1:]:
        if y2 - y1 >= 3:
            pg = P[y2]/P[y1] - 1; ag = A[y2]/A[y1] - 1
            pairs.append((y1, y2, round(pg, 4), round(ag, 4)))
            if ag >= pg: viol.append((y1, y2, round(pg, 4), round(ag, 4)))
print(json.dumps({"verdict": "falsified" if viol else "survived",
  "method": "calendar years with all 12 months; annual totals; growth=total[y2]/total[y1]-1 for every pair >=3 yrs apart; falsified if Atlantic growth >= Prairie growth",
  "complete_years": years, "n_pairs": len(pairs), "n_violations": len(viol), "violations": viol[:10],
  "min_margin_pairs": sorted(pairs, key=lambda p: p[2]-p[3])[:3]}))
