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
car = d.vclass.str.contains("Cars|Wagons")
pay = {"model": [], "hybrids_only": [], "hybrid_or_small_car": []}
for Y in years:
    tr, te, p, yt = fold(Y)
    hi = yt >= 30
    rules = {"model": p >= 30, "hybrids_only": d.hybrid[te].values == 1,
             "hybrid_or_small_car": (d.hybrid[te].values == 1) | (car[te].values & (d.displ[te].values <= 2.0) & (d.turbo[te].values == 0))}
    for k, f in rules.items():
        pay[k].append(int((hi & f).sum() - (~hi & f).sum()))  # stated objective: +1 right target, -1 wrong target
m, h, r = (np.array(pay[k]) for k in pay)
wins = float(np.mean((m > h) & (m > r))) if len(m) else float("nan")
pos = float(np.mean(m >= 5)) if len(m) else float("nan")  # must create value, not just avoid losses
out(len(m) > 0 and m.sum() > max(h.sum(), r.sum()) and wins >= 0.75 and pos >= 0.75, share_years_payoff_ge_5=round(pos, 3), years=len(m), win_rate=round(wins, 3), total_payoff={k: int(sum(v)) for k, v in pay.items()})
