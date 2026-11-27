import os, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr, rankdata

df = pd.read_csv(os.environ["DATA"])
seed = int(os.environ["SEED"]); sf = int(os.environ.get("SCORE_FROM", 2018))
rng = np.random.default_rng(seed)
df = df[["year","province","oct_share","oct_mean_temp"]].dropna().copy()

def detrend(g, c):
    # fit mean+linear trend on all history available, residuals returned
    b = np.polyfit(g.year, g[c], 1)
    return g[c] - np.polyval(b, g.year)
parts = []
for p, g in df.groupby("province"):
    g = g.copy()
    g["rt"] = detrend(g, "oct_mean_temp"); g["rs"] = detrend(g, "oct_share")
    parts.append(g)
d = pd.concat(parts)
d = d[d.year >= sf]

def pooled(x):
    return spearmanr(x.rt, x.rs)[0]
def perprov(x):
    return {p: spearmanr(g.rt, g.rs)[0] for p, g in x.groupby("province")}

r = pooled(d); pp = perprov(d)
neg = sum(v < 0 for v in pp.values())
r_no20 = pooled(d[d.year != 2020])

# province-preserving permutation: shuffle share residuals within province
def perm_p(x, n=5000):
    obs = pooled(x); cnt = 0
    groups = [g for _, g in x.groupby("province")]
    for _ in range(n):
        t = np.concatenate([g.rt.values for g in groups])
        s = np.concatenate([rng.permutation(g.rs.values) for g in groups])
        if spearmanr(t, s)[0] <= obs: cnt += 1
    return (cnt + 1) / (n + 1)
p = perm_p(d)
p20 = perm_p(d[d.year != 2020])

fals = (r > -0.25) or (p >= 0.01) or (neg < 6) or (r_no20 > -0.25)
print(json.dumps({"verdict": "falsified" if fals else "survived",
  "method": "per-province linear detrend (fit on all years), pooled Spearman on year>=SCORE_FROM residuals, within-province permutation test (5000, one-sided), per-province Spearman, leave-2020-out",
  "scored_from": sf, "n_rows": int(len(d)), "pooled_spearman": round(float(r),4),
  "perm_p": round(p,5), "perm_p_no2020": round(p20,5), "n_negative_provinces": int(neg),
  "n_provinces": len(pp), "pooled_spearman_no2020": round(float(r_no20),4),
  "per_province": {k: round(float(v),3) for k, v in pp.items()}}))
