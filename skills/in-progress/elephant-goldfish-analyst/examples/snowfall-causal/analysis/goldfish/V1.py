import os, json
import numpy as np, pandas as pd
from scipy import stats

seed = int(os.environ["SEED"]); rng = np.random.default_rng(seed)
score_from = int(os.environ.get("SCORE_FROM", 2018))
df = pd.read_csv(os.environ["DATA"])
df = df[df.year >= score_from].copy()
df["snow"] = df.oct_snow_cm + df.nov_snow_cm
df = df.dropna(subset=["fall_share", "snow"])

# within province: residualise on own intercept and linear trend (FWL), then slope per province
slopes, ys, xs = [], [], []
for p, g in df.groupby("province"):
    t = g.year.values - g.year.values.mean()
    Z = np.column_stack([np.ones(len(t)), t])
    def res(v):
        return v - Z @ np.linalg.lstsq(Z, v, rcond=None)[0]
    x, y = res(g.snow.values.astype(float)), res(g.fall_share.values.astype(float))
    xs.append(x); ys.append(y)
    slopes.append((x @ y) / (x @ x))
slopes = np.array(slopes)
n = len(slopes)
X, Y = np.concatenate(xs), np.concatenate(ys)
pooled = (X @ Y) / (X @ X)
# primary: province-level t-test of per-province slopes (province is the unit)
t, p_t = stats.ttest_1samp(slopes, 0.0)
se = slopes.std(ddof=1) / np.sqrt(n)
tc = stats.t.ppf(0.975, n - 1)
ci = [slopes.mean() - tc * se, slopes.mean() + tc * se]
# secondary: seeded sign-flip test over provinces on pooled slope contributions
obs = slopes.mean()
flips = rng.choice([-1, 1], size=(20000, n))
p_perm = float(np.mean(np.abs((flips * slopes).mean(1)) >= abs(obs) - 1e-15))
verdict = "survived" if (slopes.mean() > 0 and p_t < 0.05) else "falsified"
print(json.dumps({"verdict": verdict,
  "method": "per-province detrended (intercept+linear trend) slope of fall_share on Oct+Nov snow, scored rows only; one-sample two-sided t-test across provinces (df=%d); sign-flip permutation as check" % (n-1),
  "scored_from": score_from, "n_rows": int(len(df)), "n_provinces": int(n),
  "effect_mean_slope_per_cm": float(slopes.mean()), "pooled_within_slope": float(pooled),
  "t": float(t), "p_value": float(p_t), "ci95": [float(c) for c in ci],
  "p_signflip": p_perm, "n_positive_slopes": int((slopes>0).sum())}))
