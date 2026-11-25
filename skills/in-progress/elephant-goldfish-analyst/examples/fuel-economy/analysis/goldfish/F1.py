import os, json, random
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

seed = int(os.environ["SEED"]); random.seed(seed); np.random.seed(seed)
df = pd.read_csv(os.environ["DATA"])
cats = ["make", "vclass", "drive", "transmission", "fuel"]
nums = ["cylinders", "displ", "turbo", "supercharger", "hybrid"]
spec = cats + nums
for c in cats: df[c] = df[c].astype("category")
X = pd.get_dummies(df[spec], columns=cats).astype(float)
df["key"] = df[spec].astype(str).agg("|".join, axis=1)
bkey = ["vclass", "cylinders", "turbo", "hybrid", "drive"]
years = sorted(df.year.unique())
res = {}
for Y in years:
    tr = df[df.year <= Y - 2]
    if len(tr) == 0: continue
    seen = set(df.loc[df.year < Y, "key"])
    te = df[(df.year == Y) & ~df.key.isin(seen)]
    if len(te) == 0: continue
    m = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.06, random_state=seed)
    m.fit(X.loc[tr.index], tr.comb_mpg)
    pm = m.predict(X.loc[te.index])
    med = tr.groupby(bkey).comb_mpg.median()
    fb = tr.groupby(["vclass", "cylinders", "hybrid"]).comb_mpg.median()
    gm = tr.comb_mpg.median()
    def base(r):
        k = tuple(r[c] for c in bkey)
        if k in med.index: return med[k]
        k2 = (r.vclass, r.cylinders, r.hybrid)
        return fb[k2] if k2 in fb.index else gm
    pb = te.apply(base, axis=1).values
    res[int(Y)] = dict(n=len(te), mae=float(np.mean(np.abs(pm - te.comb_mpg))),
                       base_mae=float(np.mean(np.abs(pb - te.comb_mpg))))
for r in res.values(): r["ratio"] = r["mae"] / r["base_mae"]
avg = float(np.mean([r["mae"] for r in res.values()]))
fals = avg > 2.0 or any(r["mae"] > 2.5 or r["ratio"] > 0.85 for r in res.values())
print(json.dumps({"verdict": "falsified" if fals else "survived",
  "method": "HistGradientBoosting on one-hot specs, train years<=Y-2, test = year-Y configs whose full spec tuple not seen in any year<Y; baseline median by class/cyl/turbo/hybrid/drive with coarser fallback",
  "avg_mae": avg, "per_year": res}))
