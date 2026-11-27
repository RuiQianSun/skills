import json, os
import numpy as np, pandas as pd
from scipy.stats import spearmanr
d = pd.read_csv(os.environ["DATA"]); F = os.environ.get("SCORE_FROM"); rng = np.random.default_rng(int(os.environ["SEED"]))
d["fall_snow_cm"] = d.oct_snow_cm + d.nov_snow_cm
S = d if F is None else d[d.year >= int(F)]  # scored rows only
ALPHA = 0.05
def out(ok, **kw): print(json.dumps({"verdict": "survived" if ok else "falsified", "scored_from": F, "alpha": ALPHA, **kw}))
def resid(x, c):  # remove each province's own mean and linear trend: only year-to-year swings within a province remain
    return x.groupby("province", group_keys=False)[["year", c]].apply(lambda g: g[c] - np.polyval(np.polyfit(g.year, g[c], 1), g.year))
def shuffle_within(x, s):  # permute a residual series within each province: the null of no within-province link
    return pd.concat([pd.Series(rng.permutation(s[g.index].values), index=g.index) for _, g in x.groupby("province")])
# H0: no within-province association between oct_snow_cm and oct_share. Two-sided permutation test at alpha 0.05.
ra, rb = resid(S, "oct_snow_cm"), resid(S, "oct_share")
rho = float(spearmanr(ra, rb).statistic)
null = np.array([spearmanr(shuffle_within(S, ra), rb).statistic for _ in range(5000)])
p = float((1 + np.sum(np.abs(null) >= abs(rho))) / 5001)
boots = []
years = S.year.unique()
for _ in range(2000):  # bootstrap whole years, since one year's weather hits several provinces at once
    ys = rng.choice(years, len(years)); idx = np.concatenate([S.index[S.year == y] for y in ys])
    boots.append(spearmanr(ra[idx], rb[idx]).statistic)
lo, hi = np.nanpercentile(boots, [2.5, 97.5])
detectable = float(np.percentile(np.abs(null), 95))  # smallest |rho| this test could call significant
out(rho > 0 and p < ALPHA, rho=round(rho, 4), p_two_sided=float(f"{p:.3g}"), rho_95ci=[round(float(lo), 3), round(float(hi), 3)],
    smallest_detectable_rho=round(detectable, 3), n=int(len(S)))
