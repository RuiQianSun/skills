import os, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr, rankdata

df = pd.read_csv(os.environ["DATA"])
seed = int(os.environ["SEED"]); sf = int(os.environ.get("SCORE_FROM", 2018))
rng = np.random.default_rng(seed)
df = df[df.year >= sf][["year","province","mar_mean_temp","apr_share"]].dropna().copy()

def resid(g, col):
    X = np.column_stack([np.ones(len(g)), g.year - g.year.mean()])
    b, *_ = np.linalg.lstsq(X, g[col].values, rcond=None)
    return g[col].values - X @ b

parts = []
for p, g in df.groupby("province"):
    g = g.sort_values("year").copy()
    g["mx"] = resid(g, "mar_mean_temp"); g["ay"] = resid(g, "apr_share")
    parts.append(g)
d = pd.concat(parts).reset_index(drop=True)

def pooled(x, y): return spearmanr(x, y)[0]
obs = pooled(d.mx, d.ay)
d2 = d[d.year != 2020]
obs_no2020 = pooled(d2.mx, d2.ay)
per = {p: spearmanr(g.mx, g.ay)[0] for p, g in d.groupby("province")}
npos = int(sum(v > 0 for v in per.values()))

# within-province permutation of March residuals (keeps province structure)
B = 10000
groups = [g.index.values for _, g in d.groupby("province")]
ay_r = rankdata(d.ay.values)
cnt = 0
mx = d.mx.values
for _ in range(B):
    perm = mx.copy()
    for ix in groups:
        perm[ix] = mx[rng.permutation(ix)] if False else mx[rng.permutation(ix)]
    if pooled(perm, d.ay.values) >= obs: cnt += 1
p = (cnt + 1) / (B + 1)

fals = (obs < 0.25) or (p >= 0.01) or (npos < 6) or (obs_no2020 < 0.25)
print(json.dumps({"verdict": "falsified" if fals else "survived",
  "method": "per-province demean+linear detrend within scored window, pooled Spearman, within-province permutation test (10000, one-sided), per-province signs, drop-2020",
  "scored_from": sf, "n_rows": int(len(d)), "n_provinces": len(per),
  "pooled_spearman": round(float(obs), 4), "perm_p": round(p, 5),
  "n_positive_provinces": npos, "pooled_spearman_no2020": round(float(obs_no2020), 4),
  "per_province": {k: round(float(v), 3) for k, v in per.items()}}))
