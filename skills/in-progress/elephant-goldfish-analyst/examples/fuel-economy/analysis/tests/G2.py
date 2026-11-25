import json, os
import numpy as np, pandas as pd
d = pd.read_csv(os.environ["DATA"]); F = os.environ.get("SCORE_FROM")
S = d if F is None else d[d.year >= int(F)]  # scored rows; earlier rows are history only
def out(ok, **kw): print(json.dumps({"verdict": "survived" if ok else "falsified", "scored_from": F, **kw}))
S = S.assign(gpm=100 / S.comb_mpg)
def ss(a, b):
    sa, sb = a.vclass.value_counts(normalize=True), b.vclass.value_counts(normalize=True)
    cl = sa.index.union(sb.index); sa, sb = sa.reindex(cl, fill_value=0), sb.reindex(cl, fill_value=0)
    ra, rb = a.groupby("vclass").gpm.mean().reindex(cl), b.groupby("vclass").gpm.mean().reindex(cl)
    both = ra.notna() & rb.notna()
    within = float((((sa + sb) / 2) * (rb - ra))[both].sum())
    mix = float(((sb - sa) * ((ra.fillna(rb) + rb.fillna(ra)) / 2)).sum())
    return within, mix
ys = sorted(S.year.unique())
if len(ys) < 3: out(False, years=len(ys), within=float("nan")); raise SystemExit
w_, m_ = ss(S[S.year == ys[0]], S[S.year == ys[-1]])
adj = [ss(S[S.year == a], S[S.year == b])[0] for a, b in zip(ys, ys[1:])]
same = sum(x < 0 for x in adj)
out(w_ <= -0.1 and abs(w_) > abs(m_) and same >= len(adj) - 1, first=int(ys[0]), last=int(ys[-1]), within_gal_per_100mi=round(w_, 4), mix_gal_per_100mi=round(m_, 4), adjacent_pairs_improving=f"{same}/{len(adj)}")
