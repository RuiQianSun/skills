import os, json
import numpy as np, pandas as pd
from scipy import stats

rng = np.random.default_rng(int(os.environ["SEED"]))
df = pd.read_csv(os.environ["DATA"])
df["month"] = pd.PeriodIndex(df["month"], freq="M")
df = df.set_index("month").sort_index()
y = np.log(df["canada"].astype(float))

# Detrend: centered 2x12 moving average of log sales (removes trend + level, leaves seasonal+irregular)
trend = y.rolling(12, center=True).mean().rolling(2).mean().shift(-1)
resid = (y - trend).dropna()

gaps = {}
for yr in sorted(set(p.year for p in resid.index)):
    summer = [pd.Period(f"{yr}-{m:02d}", "M") for m in (6, 7, 8)]
    fall = [pd.Period(f"{yr}-{m:02d}", "M") for m in (10, 11)]
    if all(p in resid.index for p in summer + fall):
        gaps[yr] = float(resid[fall].mean() - resid[summer].mean())

g = np.array(list(gaps.values()))
n = len(g)
mean = g.mean()
se = g.std(ddof=1) / np.sqrt(n)
# Primary: one-sided t-test H0: gap <= 0.15 vs H1: gap > 0.15
t15 = (mean - 0.15) / se
p15 = float(stats.t.sf(t15, n - 1))
# Secondary: one-sided vs zero
p0 = float(stats.t.sf(mean / se, n - 1))
# Bootstrap CI (seeded)
boots = np.array([rng.choice(g, n, replace=True).mean() for _ in range(20000)])
ci = [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]

# Cross-check: OLS log y ~ linear trend + month dummies, contrast fall - summer
d = pd.DataFrame({"y": y.values, "t": np.arange(len(y)), "m": [p.month for p in y.index]})
X = np.column_stack([np.ones(len(d)), d["t"]] + [(d["m"] == k).astype(float) for k in range(2, 13)])
beta, *_ = np.linalg.lstsq(X, d["y"].values, rcond=None)
mcoef = {1: 0.0, **{k: beta[k] for k in range(2, 13)}}
ols_gap = float(np.mean([mcoef[10], mcoef[11]]) - np.mean([mcoef[6], mcoef[7], mcoef[8]]))

verdict = "survived" if (mean >= 0.15 and p15 < 0.002) else "falsified"
print(json.dumps({
    "verdict": verdict,
    "method": "log sales detrended by centered 2x12 MA; per-year gap = mean(Oct,Nov) - mean(Jun-Aug) resid; one-sided t-test H0 gap<=0.15",
    "n_years": n, "years": list(gaps.keys()),
    "per_year_gaps": [round(x, 4) for x in g],
    "mean_gap": round(float(mean), 4), "se": round(float(se), 4),
    "t_vs_0.15": round(float(t15), 3), "p_vs_0.15": p15,
    "p_vs_0": p0, "bootstrap_95ci": [round(c, 4) for c in ci],
    "ols_trend_plus_month_dummies_gap": round(ols_gap, 4),
}))
