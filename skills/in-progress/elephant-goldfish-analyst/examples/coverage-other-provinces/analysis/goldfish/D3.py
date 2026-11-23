import os, json, csv, random
import numpy as np

seed = int(os.environ["SEED"]); random.seed(seed); rng = np.random.default_rng(seed)
rows = list(csv.DictReader(open(os.environ["DATA"])))
d = {r["month"]: r for r in rows}

def tot(r, cols): return sum(float(r[c]) for c in cols)
P, A = ["mb", "sk"], ["ns", "nb", "nl", "pe"]

years, gaps, pv, av = [], [], [], []
for y in sorted({m[:4] for m in d}):
    o, n = d.get(f"{y}-10"), d.get(f"{y}-11")
    if not (o and n): continue  # only complete Oct+Nov pairs
    p = tot(o, P) / (tot(o, P) + tot(n, P))
    a = tot(o, A) / (tot(o, A) + tot(n, A))
    years.append(int(y)); pv.append(p); av.append(a); gaps.append(100 * (p - a))

g = np.array(gaps)
share_above = float(np.mean(g > 0))
mean_gap = float(g.mean())
boot = rng.choice(g, size=(10000, len(g)), replace=True).mean(axis=1)
ci = [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]

falsified = share_above < 0.80 or mean_gap < 2.0
print(json.dumps({
    "verdict": "falsified" if falsified else "survived",
    "method": "per-year Oct/(Oct+Nov) share for summed Prairie (mb+sk) and Atlantic (ns+nb+nl+pe) sales, complete Oct+Nov years only; gap in pp; share of years Prairie>Atlantic and mean gap vs thresholds 0.80 and 2pp; bootstrap 95% CI on mean gap (10000 resamples of years)",
    "years": years, "n_years": len(years),
    "prairie_share": [round(x, 4) for x in pv], "atlantic_share": [round(x, 4) for x in av],
    "gap_pp": [round(x, 3) for x in gaps],
    "share_years_prairie_above": round(share_above, 4),
    "mean_gap_pp": round(mean_gap, 3), "median_gap_pp": round(float(np.median(g)), 3),
    "min_gap_pp": round(float(g.min()), 3),
    "mean_gap_boot95_pp": [round(x, 3) for x in ci],
}))
