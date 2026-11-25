import json, os
import numpy as np, pandas as pd
d = pd.read_csv(os.environ["DATA"]); F = os.environ.get("SCORE_FROM")
S = d if F is None else d[d.year >= int(F)]  # scored rows; earlier rows are history only
def out(ok, **kw): print(json.dumps({"verdict": "survived" if ok else "falsified", "scored_from": F, **kw}))
n = S[S.hybrid == 0].copy(); n["band"] = (n.displ * 2).round() / 2
def gap(x):
    f = x[x.drive == "Front-Wheel Drive"].groupby(["vclass", "band"]).comb_mpg.median()
    a = x[x.drive == "All-Wheel Drive"].groupby(["vclass", "band"]).comb_mpg.median()
    j = f.index.intersection(a.index)
    return float((f[j] - a[j]).median()) if len(j) else float("nan")
g = pd.Series({y: gap(x) for y, x in n.groupby("year")})
out(len(g) > 0 and bool((g >= 1).all()) and g.mean() >= 1.5, years=len(g), min_gap=float(g.min()), mean_gap=round(float(g.mean()), 3))
