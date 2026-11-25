import json, os
import numpy as np, pandas as pd
d = pd.read_csv(os.environ["DATA"]); F = os.environ.get("SCORE_FROM")
S = d if F is None else d[d.year >= int(F)]  # scored rows; earlier rows are history only
def out(ok, **kw): print(json.dumps({"verdict": "survived" if ok else "falsified", "scored_from": F, **kw}))
from sklearn.ensemble import HistGradientBoostingRegressor
SPEC = ["make", "vclass", "drive", "transmission", "cylinders", "displ", "turbo", "supercharger", "hybrid", "fuel"]
PRED = [c for c in SPEC if c != "make"]
X = pd.get_dummies(d[PRED], columns=["vclass", "drive", "transmission", "fuel"], dtype=float)
key = d[SPEC].astype(str).agg("|".join, axis=1)
first = int(d.year.min())
years = [int(y) for y in sorted(S.year.unique()) if y >= first + 2]  # need a training year and a one-year gap
def fold(Y):
    tr = d.year <= Y - 2                          # last year still being rated: leave it out
    te = (d.year == Y) & ~key.isin(key[d.year < Y])  # only configurations never seen before
    m = HistGradientBoostingRegressor(random_state=int(os.environ["SEED"])).fit(X[tr], d.comb_mpg[tr])
    return tr, te, m.predict(X[te]), d.comb_mpg[te].values
car = d.vclass.str.contains("Cars|Wagons")
rows = []
for Y in years:
    tr, te, p, yt = fold(Y)
    hi = yt >= 30
    pay = lambda f: int((hi & f).sum() - (~hi & f).sum())  # stated objective: +1 right target, -1 wrong target
    rows.append({"year": Y, "cut29": pay(p >= 29), "cut30": pay(p >= 30), "cut31": pay(p >= 31),
                 "hybrids_only": pay(d.hybrid[te].values == 1),
                 "hybrid_or_small_car": pay((d.hybrid[te].values == 1) | (car[te].values & (d.displ[te].values <= 2.0) & (d.turbo[te].values == 0))),
                 "flagged": int((p >= 30).sum())})
t = pd.DataFrame(rows)
ok = (len(t) > 0 and float((t.cut30 > 0).mean()) >= 0.75 and float((t.cut30 >= 5).mean()) >= 0.75   # beats flag-nothing in most years
      and t.cut29.sum() > 0 and t.cut31.sum() > 0                                           # not an artefact of the cutoff
      and t.cut30.sum() > max(t.hybrids_only.sum(), t.hybrid_or_small_car.sum()))
out(ok, years=len(t), by_year=t.set_index("year").to_dict("index"), totals=t.drop(columns="year").sum().astype(int).to_dict())
