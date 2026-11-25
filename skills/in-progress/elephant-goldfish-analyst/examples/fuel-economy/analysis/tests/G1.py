import json, os
import numpy as np, pandas as pd
d = pd.read_csv(os.environ["DATA"]); F = os.environ.get("SCORE_FROM")
S = d if F is None else d[d.year >= int(F)]  # scored rows; earlier rows are history only
def out(ok, **kw): print(json.dumps({"verdict": "survived" if ok else "falsified", "scored_from": F, **kw}))
from scipy.stats import spearmanr
n = S[S.hybrid == 0]
r = {c: float(spearmanr(x.displ, x.comb_mpg).statistic) for c, x in n.groupby("vclass") if len(x) >= 50}
share = float(np.mean([v <= -0.6 for v in r.values()])) if r else float("nan")
out(len(r) > 0 and share >= 0.8, classes=len(r), share_rho_le_minus_0_6=round(share, 3), weakest={k: round(v, 3) for k, v in sorted(r.items(), key=lambda t: -t[1])[:3]})
