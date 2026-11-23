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
fy = d[d.y.isin(years)]; tot = fy.groupby("y")[P].sum()
fa = fy[fy.m.isin([10, 11])].groupby("y")[P].sum() / tot; sp = fy[fy.m.isin([4, 5])].groupby("y")[P].sum() / tot
good = ((fa >= 0.18) & (fa > sp)).all(axis=1)
frac = float(good.mean()) if len(good) else float("nan")
out(frac >= 0.8, years=len(good), share_years_fall_ge_18pct_and_above_spring=round(frac, 3), min_fall_share=round(float(fa.min().min()), 4), min_fall_minus_spring=round(float((fa - sp).min().min()), 4))
