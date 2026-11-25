import os, json, random
import numpy as np, pandas as pd
seed = int(os.environ["SEED"]); random.seed(seed); np.random.seed(seed)
d = pd.read_csv(os.environ["DATA"])
s = d[(d.hybrid == 0) & (d.displ <= 2.0)]
res = {}
rng = np.random.default_rng(seed)
for y, g in s.groupby("year"):
    t = g.turbo.to_numpy()
    n = len(t); k = int(t.sum())
    boot = rng.choice(t, (2000, n)).mean(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    res[int(y)] = {"n": n, "turbo": k, "share": round(k / n, 4), "boot95": [round(lo, 4), round(hi, 4)],
                   "share_incl_supercharger": round(float(((g.turbo == 1) | (g.supercharger == 1)).mean()), 4)}
fals = [y for y, r in res.items() if r["share"] < 0.60]
print(json.dumps({"verdict": "falsified" if fals else "survived",
    "method": "per-year share of turbo==1 among hybrid==0 & displ<=2.0, compared directly to 0.60; bootstrap CI for context",
    "years_below_060": fals, "min_share": min(r["share"] for r in res.values()), "by_year": res}))
