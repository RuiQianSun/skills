import os, json, random
import numpy as np, pandas as pd
from scipy.stats import spearmanr

seed = int(os.environ["SEED"])
random.seed(seed); np.random.seed(seed)
df = pd.read_csv(os.environ["DATA"])
nh = df[(df["hybrid"] == 0)].dropna(subset=["displ", "comb_mpg", "vclass"])
res = {}
for v, g in nh.groupby("vclass"):
    if len(g) >= 50:
        if g["displ"].nunique() < 2:
            res[v] = (None, len(g)); continue
        rho = spearmanr(g["displ"], g["comb_mpg"])[0]
        res[v] = (float(rho), len(g))
tot = len(res)
strong = sum(1 for r, n in res.values() if r is not None and r <= -0.6)
frac = strong / tot if tot else 0.0
print(json.dumps({"verdict": "survived" if frac >= 0.8 else "falsified",
  "method": "Spearman rho(displ, comb_mpg) per vclass among hybrid==0, classes n>=50; strong = rho<=-0.6; survive if >=80% strong",
  "n_classes": tot, "n_strong": strong, "fraction_strong": round(frac, 4),
  "per_class": {k: {"rho": (None if r is None else round(r, 3)), "n": n} for k, (r, n) in sorted(res.items())}}))
