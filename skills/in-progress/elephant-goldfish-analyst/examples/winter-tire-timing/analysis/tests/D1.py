import json, os
import numpy as np, pandas as pd
from scipy.stats import spearmanr
d = pd.read_csv(os.environ["DATA"]); F = os.environ.get("SCORE_FROM"); rng = np.random.default_rng(int(os.environ["SEED"]))
S = d if F is None else d[d.year >= int(F)]  # scored rows; earlier rows are history only
def out(ok, **kw): print(json.dumps({"verdict": "survived" if ok else "falsified", "scored_from": F, **kw}))
def detrend(x, col):  # remove each province's mean and linear trend, so only year-to-year swings remain
    return x.groupby("province", group_keys=False).apply(lambda g: g[col] - np.polyval(np.polyfit(g.year, g[col], 1), g.year))
def within_rho(x, a, b):
    x = x.dropna(subset=[a, b]); return float(spearmanr(detrend(x, a), detrend(x, b)).statistic), x
def perm_p(x, a, b, rho, sign):  # shuffle a within each province: keeps province structure, breaks the year link
    null = []
    for _ in range(2000):
        y = x.copy(); y[a] = y.groupby("province")[a].transform(lambda s: rng.permutation(s.values))
        null.append(float(spearmanr(detrend(y, a), detrend(y, b)).statistic))
    return float((1 + np.sum(sign * np.array(null) >= sign * rho)) / 2001)
sd = S.groupby("province").oct_share.std()
k = int((sd >= 0.02).sum())
out(k >= 6, provinces_sd_ge_2pp=k, sd_by_province={p: round(float(v), 4) for p, v in sd.items()})
