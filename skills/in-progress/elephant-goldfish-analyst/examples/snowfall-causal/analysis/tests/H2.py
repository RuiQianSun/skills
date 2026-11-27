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
# H0: holding temperature fixed (and each province's level and trend), oct_snow_cm has no effect on oct_share.
# Supported causally only if (a) the snow coefficient is positive with permutation p < alpha AND
# (b) the placebo, December snow (after the outcome months), shows no such link (p >= alpha).
def coef(x, snow, y, controls):
    cols = [resid(x, c) for c in [snow] + controls]
    X = np.column_stack(cols + [np.ones(len(x))]); Y = resid(x, y)
    return float(np.linalg.lstsq(X, Y, rcond=None)[0][0]), cols, Y
def perm(x, snow, y, controls):
    b, cols, Y = coef(x, snow, y, controls)
    null = []
    for _ in range(5000):
        X = np.column_stack([shuffle_within(x, cols[0])] + cols[1:] + [np.ones(len(x))])
        null.append(float(np.linalg.lstsq(X, Y, rcond=None)[0][0]))
    return b, float((1 + np.sum(np.abs(null) >= abs(b))) / 5001)
controls = ["oct_mean_temp"]
b, p = perm(S, "oct_snow_cm", "oct_share", controls)
bp, pp = perm(S, "dec_snow_cm", "oct_share", controls)
ok = b > 0 and p < ALPHA and pp >= ALPHA
out(ok, snow_effect_pp_per_10cm=round(b * 1000, 3), p_snow=float(f"{p:.3g}"),
    placebo_dec_effect_pp_per_10cm=round(bp * 1000, 3), p_placebo=float(f"{pp:.3g}"), n=int(len(S)))
