import json, os
import numpy as np, pandas as pd
d = pd.read_csv(os.environ["DATA"]); F = os.environ.get("SCORE_FROM")
S = d if F is None else d[d.year >= int(F)]  # scored rows; earlier rows are history only
def out(ok, **kw): print(json.dumps({"verdict": "survived" if ok else "falsified", "scored_from": F, **kw}))
s = S[(S.hybrid == 0) & (S.displ <= 2.0)].groupby("year").turbo.mean()
out(len(s) > 0 and bool((s >= 0.6).all()), years=len(s), min_share=round(float(s.min()), 4), by_year={int(k): round(float(v), 3) for k, v in s.items()})
