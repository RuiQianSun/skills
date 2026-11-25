import os, json, numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

seed = int(os.environ["SEED"]); np.random.seed(seed)
score_from = int(os.environ.get("SCORE_FROM", 2020))
df = pd.read_csv(os.environ["DATA"])
cats = ["make","vclass","drive","transmission","fuel"]
nums = ["cylinders","displ","turbo","supercharger","hybrid"]
spec = cats + nums
df["_key"] = df[spec].astype(str).agg("|".join, axis=1)
for c in cats: df[c] = df[c].astype("category")
codes = {c: df[c].cat.codes for c in cats}
X = pd.concat([pd.DataFrame(codes), df[nums].astype(float)], axis=1)
X["displ"] = X["displ"].fillna(-1)
catmask = [True]*len(cats) + [False]*len(nums)
bkeys = ["vclass","cylinders","turbo","hybrid","drive"]
res = {}
for Y in range(score_from, 2026):
    tr = df.year <= Y-2
    seen = set(df.loc[df.year < Y, "_key"])
    te = (df.year == Y) & (~df["_key"].isin(seen))
    if te.sum() == 0 or tr.sum() == 0: continue
    m = HistGradientBoostingRegressor(categorical_features=catmask, max_iter=400, learning_rate=0.06,
                                      random_state=seed, early_stopping=False)
    m.fit(X[tr], df.loc[tr, "comb_mpg"])
    p = m.predict(X[te])
    y = df.loc[te, "comb_mpg"].values
    hist = df[tr]
    g = hist.groupby(bkeys, observed=True)["comb_mpg"].median()
    g2 = hist.groupby(["vclass","cylinders","hybrid"], observed=True)["comb_mpg"].median()
    gm = hist["comb_mpg"].median()
    b = []
    for _, r in df[te].iterrows():
        k = tuple(r[c] for c in bkeys)
        if k in g.index: b.append(g[k])
        else:
            k2 = (r["vclass"], r["cylinders"], r["hybrid"])
            b.append(g2[k2] if k2 in g2.index else gm)
    res[Y] = dict(n=int(te.sum()), mae=float(np.mean(np.abs(p-y))), base_mae=float(np.mean(np.abs(np.array(b)-y))))
for v in res.values(): v["ratio"] = v["mae"]/v["base_mae"]
avg = float(np.mean([v["mae"] for v in res.values()]))
mx = max(v["mae"] for v in res.values())
mr = max(v["ratio"] for v in res.values())
fals = avg > 2.0 or mx > 2.5 or mr > 0.85
print(json.dumps({"verdict": "falsified" if fals else "survived",
  "method": "HistGradientBoosting (categorical specs), train years<=Y-2, test = year-Y rows with spec unseen in any year<Y; baseline median by vclass/cylinders/turbo/hybrid/drive from same training years",
  "scored_from": score_from, "avg_mae": avg, "max_mae": mx, "max_ratio": mr, "per_year": res}))
