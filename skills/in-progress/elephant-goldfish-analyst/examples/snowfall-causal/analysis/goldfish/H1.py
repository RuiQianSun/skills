import os, json
import numpy as np, pandas as pd

rng = np.random.default_rng(int(os.environ["SEED"]))
score_from = int(os.environ.get("SCORE_FROM", 2018))
df = pd.read_csv(os.environ["DATA"], usecols=["year", "province", "oct_share", "oct_snow_cm"])
df = df[df.year >= score_from].dropna().copy()

def detrend(g, col):
    X = np.column_stack([np.ones(len(g)), g.year.values - g.year.mean()])
    b, *_ = np.linalg.lstsq(X, g[col].values, rcond=None)
    return g[col].values - X @ b

xs, ys = [], []
for p, g in df.groupby("province"):
    xs.append(detrend(g, "oct_snow_cm")); ys.append(detrend(g, "oct_share"))

def slope(xs, ys):
    num = sum((x * y).sum() for x, y in zip(xs, ys))
    den = sum((x * x).sum() for x in xs)
    return num / den

obs = slope(xs, ys)
B = 20000
perm = np.empty(B)
for i in range(B):
    perm[i] = slope([rng.permutation(x) for x in xs], ys)
p = (1 + np.sum(np.abs(perm) >= abs(obs) - 1e-12)) / (B + 1)

# cluster bootstrap over provinces for CI
k = len(xs)
bs = np.empty(B)
for i in range(B):
    idx = rng.integers(0, k, k)
    bs[i] = slope([xs[j] for j in idx], [ys[j] for j in idx])
lo, hi = np.percentile(bs, [2.5, 97.5])
per_prov = [float((x * y).sum() / (x * x).sum()) for x, y in zip(xs, ys)]

verdict = "survived" if (obs > 0 and p < 0.05) else "falsified"
print(json.dumps({"verdict": verdict,
  "method": "province-specific linear detrending (own level+trend) on scored rows, pooled within slope of oct_share on oct_snow_cm; two-sided within-province permutation test (20000), cluster bootstrap CI over provinces",
  "scored_from": score_from, "n_rows": int(len(df)), "n_provinces": k,
  "slope_per_cm": float(obs), "p_value": float(p), "ci95": [float(lo), float(hi)],
  "provinces_positive": int(sum(s > 0 for s in per_prov))}))
