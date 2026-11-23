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
from scipy.stats import spearmanr
rng = np.random.default_rng(int(os.environ["SEED"]))
gp = np.log(d[PR].sum(axis=1)).diff(12); ga = np.log(d[AT].sum(axis=1)).diff(12)
m = pd.DataFrame({"p": gp, "a": ga, "month": d.month, "y": d.y}).dropna()
if F: m = m[m.month >= F]
m = m[~m.y.isin([2020, 2021])].reset_index(drop=True)
x, y = m.p.values, m.a.values
rho = float(spearmanr(x, y).statistic) if len(m) > 2 else float("nan")
null = np.array([spearmanr(x, np.roll(y, k)).statistic for k in rng.integers(24, len(y) - 24, 5000)]) if len(y) > 60 else np.array([np.nan])
p = float((1 + np.sum(null >= rho)) / (1 + len(null)))
out(rho >= 0.5 and p < 0.005, n=len(m), rho=round(rho, 4), p_circular=float(f"{p:.3g}"))
