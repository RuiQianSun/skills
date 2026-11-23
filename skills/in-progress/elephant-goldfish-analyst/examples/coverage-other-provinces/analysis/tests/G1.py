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
import itertools
a = d[d.y.isin(years)].groupby("y")[P].sum(); pr, at = a[PR].sum(axis=1), a[AT].sum(axis=1)
pairs = [(x, y) for x, y in itertools.combinations(a.index, 2) if y - x >= 3]
wins = [bool(pr[y] / pr[x] > at[y] / at[x]) for x, y in pairs]
frac = float(np.mean(wins)) if wins else float("nan")
cagr = lambda s: float((s.iloc[-1] / s.iloc[0]) ** (1 / (len(s) - 1)) - 1) if len(s) > 1 else float("nan")
out(len(wins) > 0 and frac == 1.0, endpoint_pairs=len(wins), share_pairs_prairie_faster=round(frac, 3), prairie_cagr=round(cagr(pr), 4), atlantic_cagr=round(cagr(at), 4))
