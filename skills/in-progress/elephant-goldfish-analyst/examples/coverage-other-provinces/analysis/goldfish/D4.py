import os, json, random
import numpy as np, pandas as pd
seed = int(os.environ["SEED"]); random.seed(seed); rng = np.random.default_rng(seed)
df = pd.read_csv(os.environ["DATA"])
df["year"] = df.month.str[:4].astype(int)
df["pr"] = df.mb + df.sk
df["tot"] = df[["mb","sk","ns","nb","nl","pe"]].sum(axis=1)
cnt = df.groupby("year").size()
full = [y for y in cnt.index if cnt[y] == 12]
ann = df[df.year.isin(full)].groupby("year")[["pr","tot"]].sum()
share = (ann.pr / ann.tot * 100)
first, last = full[:3], full[-3:]
diff = share[last].mean() - share[first].mean()
# slope: OLS on monthly shares (complete years) with year-month dummies for seasonality
d = df[df.year.isin(full)].copy()
d["s"] = d.pr / d.tot * 100
d["t"] = np.arange(len(d)) / 12.0
m = d.month.str[5:].astype(int)
X = np.column_stack([d.t.values] + [(m == k).astype(float).values for k in range(1, 13)])
beta = np.linalg.lstsq(X, d.s.values, rcond=None)[0]
slope = beta[0]
res = d.s.values - X @ beta
# residual bootstrap for slope CI
bs = []
for _ in range(2000):
    y = X @ beta + rng.choice(res, len(res), replace=True)
    bs.append(np.linalg.lstsq(X, y, rcond=None)[0][0])
lo, hi = np.percentile(bs, [2.5, 97.5])
ann_slope = np.polyfit(np.array(full), share.values, 1)[0]
verdict = "falsified" if (diff < 1 or slope <= 0) else "survived"
print(json.dumps({"verdict": verdict,
 "method": "annual share from summed sales over complete calendar years; first3 vs last3 mean diff; monthly share OLS slope with month dummies, residual bootstrap CI",
 "complete_years": full, "annual_share_pct": {int(k): round(float(v), 3) for k, v in share.items()},
 "first3_mean": round(float(share[first].mean()), 3), "last3_mean": round(float(share[last].mean()), 3),
 "diff_pp": round(float(diff), 3), "slope_pp_per_year": round(float(slope), 4),
 "slope_ci95": [round(float(lo), 4), round(float(hi), 4)], "annual_slope_pp_per_year": round(float(ann_slope), 4)}))
