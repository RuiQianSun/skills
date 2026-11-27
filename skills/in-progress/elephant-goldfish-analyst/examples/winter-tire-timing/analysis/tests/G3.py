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
sign = 1
rho, x = within_rho(S, "mar_mean_temp", "apr_share")
p = perm_p(x, "mar_mean_temp", "apr_share", rho, sign)
da, db = detrend(x, "mar_mean_temp"), detrend(x, "apr_share")
per = {pv: float(spearmanr(da[g.index], db[g.index]).statistic) for pv, g in x.groupby("province")}
same = sum(np.sign(v) == sign for v in per.values())
rho_no2020, _ = within_rho(S[S.year != 2020], "mar_mean_temp", "apr_share")
ok = sign * rho >= 0.25 and p < 0.01 and same >= 6 and sign * rho_no2020 >= 0.25
out(ok, rho=round(rho, 4), p_within_perm=float(f"{p:.3g}"), provinces_same_sign=int(same), rho_without_2020=round(rho_no2020, 4))
