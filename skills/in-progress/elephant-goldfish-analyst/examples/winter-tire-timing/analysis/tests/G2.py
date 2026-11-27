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
x = S.dropna(subset=["fall_7c_day", "oct_mean_temp", "oct_share"])
r = pd.DataFrame({k: detrend(x, k) for k in ["fall_7c_day", "oct_mean_temp", "oct_share"]}).rank()
def resid(y, z): return y - np.polyval(np.polyfit(z, y, 1), z)
pr = float(np.corrcoef(resid(r.fall_7c_day, r.oct_mean_temp), resid(r.oct_share, r.oct_mean_temp))[0, 1])  # partial Spearman
out(pr <= -0.2, partial_rho_given_oct_temp=round(pr, 4), n=len(x))
