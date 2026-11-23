import json, os
import numpy as np, pandas as pd
d = pd.read_csv(os.environ["DATA"]); F = os.environ.get("SCORE_FROM")
P = ["mb", "sk", "ns", "nb", "nl", "pe"]; PR, AT = ["mb", "sk"], ["ns", "nb", "nl", "pe"]
ok_rows = d[P].notna().all(axis=1); d = d[ok_rows.cummax()].reset_index(drop=True)  # drop the leading suppressed block
assert d[P].notna().all().all(), "suppressed values inside the series"
d["m"] = d.month.str[5:].astype(int); d["y"] = d.month.str[:4].astype(int)
cnt = d.dropna(subset=P).groupby("y").month.agg(["count", "min"])
years = [y for y, r in cnt.iterrows() if r["count"] == 12 and (F is None or r["min"] >= F)]  # scored: complete years inside the window
def out(ok, **kw): print(json.dumps({"verdict": "survived" if ok else "falsified", "scored_from": F, **kw}))
fy = d[d.y.isin(years)]
oc = fy[fy.m == 10].set_index("y"); nv = fy[fy.m == 11].set_index("y")
pr = oc[PR].sum(axis=1) / (oc[PR].sum(axis=1) + nv[PR].sum(axis=1)); at = oc[AT].sum(axis=1) / (oc[AT].sum(axis=1) + nv[AT].sum(axis=1))
gap = pr - at; frac = float((gap > 0).mean()) if len(gap) else float("nan")
out(frac >= 0.8 and gap.mean() >= 0.02, years=len(gap), share_years_prairie_earlier=round(frac, 3), mean_gap_pp=round(float(gap.mean()) * 100, 2))
