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
x = pd.DataFrame({"a": s, "d": drift * 1.05, "n": naive * 1.05, "m": d.m, "y": d.y}).dropna()
x = x[x.m.isin([10, 11]) & x.y.isin(years)].groupby("y")[["a", "d", "n"]].sum()
cost = lambda q: ((q - x.a).clip(lower=0) + 3 * (x.a - q).clip(lower=0)) / x.a  # stated: shortfall costs 3x overstock
cd, cn = cost(x.d), cost(x.n)
win = float((cd < cn).mean()) if len(x) else float("nan")
out(len(x) > 0 and win >= 0.7 and cd.mean() < cn.mean(), years=len(x), win_rate=round(win, 3), mean_cost_drift=round(float(cd.mean()), 4), mean_cost_status_quo=round(float(cn.mean()), 4))
