import json, os
import numpy as np, pandas as pd
d = pd.read_csv(os.environ["DATA"]); F = os.environ.get("SCORE_FROM")
S = d if F is None else d[d.year >= int(F)]  # scored rows; earlier rows are history only
def out(ok, **kw): print(json.dumps({"verdict": "survived" if ok else "falsified", "scored_from": F, **kw}))
from sklearn.ensemble import HistGradientBoostingRegressor
SPEC = ["make", "vclass", "drive", "transmission", "cylinders", "displ", "turbo", "supercharger", "hybrid", "fuel"]
X = pd.get_dummies(d[SPEC], columns=["make", "vclass", "drive", "transmission", "fuel"], dtype=float)
key = d[SPEC].astype(str).agg("|".join, axis=1)
first = int(d.year.min())
years = [int(y) for y in sorted(S.year.unique()) if y >= first + 2]  # need a training year and a one-year gap
def fold(Y):
    tr = d.year <= Y - 2                          # last year still being rated: leave it out
    te = (d.year == Y) & ~key.isin(key[d.year < Y])  # only configurations never seen before
    m = HistGradientBoostingRegressor(random_state=int(os.environ["SEED"])).fit(X[tr], d.comb_mpg[tr])
    return tr, te, m.predict(X[te]), d.comb_mpg[te].values
grp = ["vclass", "cylinders", "turbo", "hybrid", "drive"]
res = {}
for Y in years:
    tr, te, p, yt = fold(Y)
    t = d[tr]
    b = d[te].merge(t.groupby(grp).comb_mpg.median().rename("b").reset_index(), on=grp, how="left").b
    b = b.fillna(pd.Series(d[te].vclass.map(t.groupby("vclass").comb_mpg.median()).values)).fillna(t.comb_mpg.median())
    res[Y] = (float(np.mean(abs(p - yt))), float(np.mean(abs(b.values - yt))), int(te.sum()))
mae = np.array([v[0] for v in res.values()]); base = np.array([v[1] for v in res.values()])
ok = len(res) > 0 and mae.mean() <= 2.0 and (mae <= 2.5).all() and (mae <= 0.85 * base).all()
out(ok, years=len(res), mean_mae=round(float(mae.mean()), 3), by_year={y: {"mae": round(v[0], 2), "baseline": round(v[1], 2), "new_configs": v[2]} for y, v in res.items()})
