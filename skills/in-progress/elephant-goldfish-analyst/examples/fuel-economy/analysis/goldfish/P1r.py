import os, json
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

SEED = int(os.environ.get("SEED", "0"))
SCORE_FROM = int(os.environ.get("SCORE_FROM", "2020"))
np.random.seed(SEED)
d = pd.read_csv(os.environ["DATA"])
cat = ["vclass", "drive", "transmission", "fuel"]
num = ["cylinders", "displ", "turbo", "supercharger", "hybrid"]
full = ["make"] + cat + num
d["key"] = d[full].astype(str).agg("|".join, axis=1)

def X(df):
    x = df[num].astype(float).copy()
    for c in cat:
        x[c] = df[c].astype("category").cat.set_categories(sorted(d[c].unique())).cat.codes
    return x

def baseline(df, which):
    h = df.hybrid == 1
    if which == "hyb":
        return h
    cw = df.vclass.str.contains("Car|Wagon", regex=True)
    return h | (cw & (df.displ <= 2.0) & (df.turbo == 0))

def score(flag, real, cut):
    return int(((real[flag] >= cut).sum()) - ((real[flag] < cut).sum()))

years = list(range(max(SCORE_FROM, d.year.min() + 3), d.year.max() + 1))
years = [y for y in years if y >= SCORE_FROM]
per = {}
tot = {k: 0 for k in ["m29", "m30", "m31", "hyb", "hcw"]}
for y in years:
    tr = d[d.year <= y - 2]
    te = d[d.year == y]
    seen = set(d.loc[d.year < y, "key"])
    te = te[~te.key.isin(seen)]
    if len(te) == 0:
        per[y] = dict(n_new=0, flagged=0, score=0); continue
    m = HistGradientBoostingRegressor(random_state=SEED, max_iter=300, learning_rate=0.08,
                                      categorical_features=[num.__len__() + i for i in range(len(cat))])
    m.fit(X(tr), tr.comb_mpg)
    p = m.predict(X(te))
    real = te.comb_mpg
    r = {"n_new": int(len(te))}
    for cut, k in [(29, "m29"), (30, "m30"), (31, "m31")]:
        f = pd.Series(p >= cut, index=te.index)
        r[k] = score(f, real, cut)
        tot[k] += r[k]
        if k == "m30":
            r["flagged"] = int(f.sum())
    for w in ["hyb", "hcw"]:
        s = score(baseline(te, w), real, 30)
        r[w] = s; tot[w] += s
    per[y] = r

n = len(years)
pos = sum(per[y]["m30"] > 0 for y in years)
ge5 = sum(per[y]["m30"] >= 5 for y in years)
c = {
    "positive_75pct": pos / n >= 0.75,
    "ge5_75pct": ge5 / n >= 0.75,
    "cut29_positive": tot["m29"] > 0,
    "cut31_positive": tot["m31"] > 0,
    "beats_hybrids_only": tot["m30"] > tot["hyb"],
    "beats_hybrid_or_small": tot["m30"] > tot["hcw"],
}
out = {"verdict": "survived" if all(c.values()) else "falsified",
       "method": "HistGradientBoosting on specs excl make, trained on years<=Y-2; flag year-Y rows whose full spec incl make unseen in any earlier year; cutoff applied to both prediction and real mpg",
       "scored_from": SCORE_FROM, "years": years, "per_year": per, "totals": tot,
       "years_positive": int(pos), "years_ge5": int(ge5), "conditions": c}
print(json.dumps(out, default=int))
