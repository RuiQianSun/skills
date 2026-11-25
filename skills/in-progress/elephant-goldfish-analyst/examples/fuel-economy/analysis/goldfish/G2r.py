import os, json, random
import numpy as np, pandas as pd
random.seed(int(os.environ["SEED"])); np.random.seed(int(os.environ["SEED"]))
S = int(os.environ["SCORE_FROM"])
d = pd.read_csv(os.environ["DATA"])
d = d[(pd.to_numeric(d.hybrid, errors="coerce") == 0) & (d.year >= S)].copy()
d["comb_mpg"] = pd.to_numeric(d.comb_mpg, errors="coerce")
d = d[d.comb_mpg > 0].copy()
d["g"] = 100 / d.comb_mpg
def stats(y):
    x = d[d.year == y]
    return x.groupby("vclass").g.agg(["mean", "size"]).assign(w=lambda t: t["size"] / t["size"].sum()), x.g.mean()
def decomp(a, b):
    A, ma = stats(a); B, mb = stats(b)
    cls = A.index.union(B.index)
    wa = A.w.reindex(cls).fillna(0); wb = B.w.reindex(cls).fillna(0)
    ga = A["mean"].reindex(cls); gb = B["mean"].reindex(cls)
    # class absent in one year: use the other year's mean (no within change there)
    ga = ga.fillna(gb); gb = gb.fillna(ga)
    within = float((((wa + wb) / 2) * (gb - ga)).sum())
    mix = float((((ga + gb) / 2) * (wb - wa)).sum())
    return within, mix, mb - ma
years = sorted(d.year.unique()); F, L = years[0], years[-1]
within, mix, tot = decomp(F, L)
pairs = [(y, y + 1) + decomp(y, y + 1)[:1] for y in years[:-1] if y + 1 in years]
wrong = [p[0] for p in pairs if p[2] > 0]
consec = any(wrong[i] + 1 == wrong[i + 1] for i in range(len(wrong) - 1))
fals = (-within < 0.1) or (abs(within) < abs(mix)) or (len(wrong) >= 2)
print(json.dumps({"verdict": "falsified" if fals else "survived",
  "method": "midpoint (Shapley) shift-share over vclass, non-hybrid, mean of 100/comb_mpg per config; first vs last scored year; adjacent-year within change sign count",
  "scored_from": S, "first_year": int(F), "last_year": int(L),
  "total_change": tot, "within": within, "mix": mix, "check_sum": within + mix,
  "wrong_direction_pairs": [int(y) for y in wrong], "n_wrong": len(wrong), "wrong_consecutive": bool(consec),
  "within_by_pair": {str(p[0]): round(p[2], 4) for p in pairs}}))
