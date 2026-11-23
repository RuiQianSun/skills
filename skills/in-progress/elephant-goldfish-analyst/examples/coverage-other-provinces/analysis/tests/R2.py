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
fall = d[d.m.isin([10, 11])].groupby("y")[P].sum(); ann = d.groupby("y")[P].sum()
fs = fall.div(fall.sum(axis=1), axis=0); an = ann.div(ann.sum(axis=1), axis=0)
k = [y for y in years if y - 1 in fs.index and y - 1 in cnt.index and cnt.loc[y - 1, "count"] == 12]
ef = (fs.shift(1) - fs).abs().sum(axis=1).loc[k] / 2; ea = (an.shift(1) - fs).abs().sum(axis=1).loc[k] / 2  # share of stock in the wrong province
win = float((ef < ea).mean()) if k else float("nan"); cut = float(1 - ef.mean() / ea.mean()) if k else float("nan")
out(len(k) > 0 and win >= 0.7 and cut >= 0.2, years=len(k), win_rate=round(win, 3), misallocated_fall_share=round(float(ef.mean()), 4), misallocated_annual_share=round(float(ea.mean()), 4), cut=round(cut, 4))
