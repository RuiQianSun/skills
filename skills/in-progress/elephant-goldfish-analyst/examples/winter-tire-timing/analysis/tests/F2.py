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
years = sorted(S.year.unique()); errs = []
for Y in years:
    tr = d[d.year < Y]
    if tr.year.nunique() < 3: continue
    te = d[d.year == Y]
    base = te.province.map(tr.groupby("province").oct_share.mean())
    dm = tr.oct_share - tr.groupby("province").oct_share.transform("mean"); dx = tr.sep_mean_temp - tr.groupby("province").sep_mean_temp.transform("mean")
    b = np.polyfit(dx, dm, 1)[0]
    pred = base + b * (te.sep_mean_temp - te.province.map(tr.groupby("province").sep_mean_temp.mean()))
    errs.append((abs(pred - te.oct_share).mean(), abs(base - te.oct_share).mean()))
m, bl = (float(np.mean([e[i] for e in errs])) for i in (0, 1))
out(len(errs) > 0 and m <= 0.9 * bl, years=len(errs), mae_model=round(m, 5), mae_baseline=round(bl, 5))
