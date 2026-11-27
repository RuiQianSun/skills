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
def folds(drop2020=False):
    rows = []
    for Y in sorted(S.year.unique()):
        if drop2020 and Y == 2020: continue
        tr = d[(d.year < Y) & ~((d.year == 2020) & drop2020)]  # only earlier years: nothing from year Y, any province
        if tr.year.nunique() < 3: continue
        te = d[d.year == Y]
        mu = tr.groupby("province").apr_share.mean(); mx = tr.groupby("province").mar_mean_temp.mean()
        b = np.polyfit(tr.mar_mean_temp - tr.province.map(mx), tr.apr_share - tr.province.map(mu), 1)[0]  # pooled slope, province intercepts
        base = te.province.map(mu); pred = base + b * (te.mar_mean_temp - te.province.map(mx))
        rows.append(pd.DataFrame({"year": Y, "province": te.province, "actual": te.apr_share, "pred": pred, "base": base}))
    return pd.concat(rows) if rows else pd.DataFrame()
res = {}
for tag, drop in (("all", False), ("no2020", True)):
    f = folds(drop); m, b = float(abs(f.pred - f.actual).mean()), float(abs(f.base - f.actual).mean())
    res[tag] = {"mae_model": round(m, 5), "mae_baseline": round(b, 5), "gain_pp": round((b - m) * 100, 3), "rel_gain": round(1 - m / b, 4), "years": int(f.year.nunique())}
ok = all(v["rel_gain"] >= 0.10 and v["gain_pp"] >= 0.2 for v in res.values())
out(ok, **res)
