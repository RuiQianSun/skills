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
s = d[P].sum(axis=1)
drift = s.shift(12) * s.shift(1).rolling(12).sum() / s.shift(13).rolling(12).sum(); naive = s.shift(12)
e = pd.DataFrame({"d": abs(s - drift) / s, "n": abs(s - naive) / s, "month": d.month}).dropna()
if F: e = e[e.month >= F]
md, mn = float(e.d.mean()), float(e.n.mean())
out(md <= 0.05 and md <= 0.9 * mn, months=len(e), mape_drift=round(md, 4), mape_naive=round(mn, 4), relative_gain=round(1 - md / mn, 4))
