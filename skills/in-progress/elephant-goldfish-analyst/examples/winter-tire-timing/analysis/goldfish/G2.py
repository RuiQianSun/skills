import os, json
import numpy as np, pandas as pd
from scipy.stats import rankdata, pearsonr

DATA = os.environ["DATA"]; SEED = int(os.environ["SEED"]); SCORE_FROM = int(os.environ.get("SCORE_FROM", 2018))
rng = np.random.default_rng(SEED)
df = pd.read_csv(DATA)[["year", "province", "oct_share", "fall_7c_day", "oct_mean_temp"]].dropna().astype({"fall_7c_day": float, "oct_share": float, "oct_mean_temp": float})
V = ["oct_share", "fall_7c_day", "oct_mean_temp"]

def detrend(d, fit_mask):
    out = d.copy()
    for p, g in d.groupby("province"):
        f = g[fit_mask.loc[g.index]]
        X = np.c_[np.ones(len(f)), f.year - 2017.5]
        Xa = np.c_[np.ones(len(g)), g.year - 2017.5]
        for v in V:
            b = np.linalg.lstsq(X, f[v].values, rcond=None)[0]
            out.loc[g.index, v] = g[v].values - Xa @ b
    return out

def partial_spearman(d):
    rx, ry, rz = (rankdata(d[c]) for c in ("fall_7c_day", "oct_share", "oct_mean_temp"))
    Z = np.c_[np.ones(len(rz)), rz]
    ex = rx - Z @ np.linalg.lstsq(Z, rx, rcond=None)[0]
    ey = ry - Z @ np.linalg.lstsq(Z, ry, rcond=None)[0]
    return pearsonr(ex, ey)[0]

score = df.year >= SCORE_FROM
# primary: province mean+trend fit on all years, score only SCORE_FROM+ rows
res = detrend(df, pd.Series(True, index=df.index))
S = res[score]
r = partial_spearman(S)
# sensitivity: detrend fit only on scored rows
r_scored_only = partial_spearman(detrend(df[score], pd.Series(True, index=df[score].index)))
# sensitivity: trend fit on history only, applied out of sample to scored rows
r_hist = partial_spearman(detrend(df, ~score)[score])
raw_spear = pearsonr(rankdata(S.fall_7c_day), rankdata(S.oct_share))[0]
# province-cluster bootstrap CI
provs = S.province.unique(); bs = []
for _ in range(2000):
    pick = rng.choice(provs, len(provs), replace=True)
    b = pd.concat([S[S.province == p] for p in pick])
    bs.append(partial_spearman(b))
lo, hi = np.percentile(bs, [2.5, 97.5])
# permutation p (within province shuffle of fall_7c_day residual)
perm = []
for _ in range(2000):
    P = S.copy()
    P["fall_7c_day"] = P.groupby("province").fall_7c_day.transform(lambda s: rng.permutation(s.values))
    perm.append(partial_spearman(P))
p_one = (np.sum(np.array(perm) <= r) + 1) / (len(perm) + 1)
verdict = "falsified" if r > -0.2 else "survived"
print(json.dumps({"verdict": verdict,
  "method": "per-province linear (mean+trend) detrend of oct_share, fall_7c_day, oct_mean_temp fit on all years; partial Spearman (rank-residual) of fall_7c_day vs oct_share controlling oct_mean_temp on scored rows; province-cluster bootstrap CI, within-province permutation p",
  "scored_from": SCORE_FROM, "n_scored": int(len(S)), "n_provinces": int(len(provs)),
  "partial_spearman": round(r, 4), "threshold": -0.2,
  "boot_ci95": [round(lo, 4), round(hi, 4)], "perm_p_one_sided": round(p_one, 4),
  "sens_detrend_scored_only": round(r_scored_only, 4), "sens_detrend_history_only": round(r_hist, 4),
  "detrended_spearman_no_control": round(raw_spear, 4)}))
