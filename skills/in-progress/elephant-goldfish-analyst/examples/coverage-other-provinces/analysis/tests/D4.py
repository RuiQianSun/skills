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
a = d[d.y.isin(years)].groupby("y")[P].sum(); s = a[PR].sum(axis=1) / a.sum(axis=1)
k = min(3, len(s) // 2)
early, late = (float(s.iloc[:k].mean()), float(s.iloc[-k:].mean())) if k else (float("nan"), float("nan"))
slope = float(np.polyfit(s.index, s.values, 1)[0]) if len(s) > 2 else float("nan")
out(late - early >= 0.01 and slope > 0, years=len(s), first3_mean=round(early, 4), last3_mean=round(late, 4), slope_per_year=round(slope, 5))
