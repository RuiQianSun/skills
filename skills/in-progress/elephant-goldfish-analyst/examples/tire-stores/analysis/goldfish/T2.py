import os, json
import numpy as np
import pandas as pd

rng = np.random.default_rng(int(os.environ["SEED"]))
df = pd.read_csv(os.environ["DATA"])
df["date"] = pd.to_datetime(df["month"] + "-01")
df = df.sort_values("date").reset_index(drop=True)
df["ly"] = np.log(df["tire_store_sales_musd"])

# Detrend: centered 2x12 moving average of log sales (removes trend, averages out seasonality)
w = np.r_[0.5, np.ones(11), 0.5] / 12.0
trend = np.convolve(df["ly"].values, w, mode="same")
trend[:6] = np.nan
trend[-6:] = np.nan
df["resid"] = df["ly"] - trend
df["m"] = df["date"].dt.month
df["y"] = df["date"].dt.year

# Pair each summer (Jun-Aug of year Y) with the preceding winter (Nov Y-1 .. Feb Y)
df["winter_year"] = np.where(df["m"] >= 11, df["y"] + 1, df["y"])
summer = df[df["m"].isin([6, 7, 8])].dropna(subset=["resid"]).groupby("y")["resid"].agg(["mean", "count"])
winter = df[df["m"].isin([11, 12, 1, 2])].dropna(subset=["resid"]).groupby("winter_year")["resid"].agg(["mean", "count"])
summer = summer[summer["count"] == 3]
winter = winter[winter["count"] == 4]
years = sorted(set(summer.index) & set(winter.index))
gaps = np.array([summer.loc[y, "mean"] - winter.loc[y, "mean"] for y in years])
n = len(gaps)
mean_gap = float(gaps.mean())

# One-sided sign-flip permutation test of H0: gap <= 0 (exact if feasible)
if n <= 20:
    signs = ((np.arange(2 ** n)[:, None] >> np.arange(n)) & 1) * 2 - 1
    perm = (signs * gaps).mean(axis=1)
    p0 = float(np.mean(perm >= mean_gap))
    perm_type = "exact"
else:
    signs = rng.choice([-1, 1], size=(200000, n))
    perm = (signs * gaps).mean(axis=1)
    p0 = float((1 + np.sum(perm >= mean_gap)) / (1 + len(perm)))
    perm_type = "monte_carlo"

# Same test against the 0.08 threshold (H0: gap <= 0.08), reported for context
g8 = gaps - 0.08
if n <= 20:
    perm8 = (signs * g8).mean(axis=1)
    p08 = float(np.mean(perm8 >= g8.mean()))
else:
    perm8 = (signs * g8).mean(axis=1)
    p08 = float((1 + np.sum(perm8 >= g8.mean())) / (1 + len(perm8)))

# Bootstrap CI over years
boot = rng.choice(gaps, size=(20000, n), replace=True).mean(axis=1)
ci = [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]

verdict = "falsified" if (mean_gap < 0.08 or p0 >= 0.002) else "survived"
print(json.dumps({
    "verdict": verdict,
    "method": "log sales detrended by centered 2x12 moving average; per-year gap = mean resid Jun-Aug(Y) minus mean resid Nov(Y-1)-Feb(Y); one-sided "
              + perm_type + " sign-flip permutation test across years (H0: gap<=0)",
    "n_years": n,
    "years": [int(y) for y in years],
    "mean_gap_log": round(mean_gap, 5),
    "min_gap": round(float(gaps.min()), 5),
    "max_gap": round(float(gaps.max()), 5),
    "p_one_sided_vs_0": p0,
    "p_one_sided_vs_0.08": p08,
    "bootstrap_95ci": [round(c, 5) for c in ci],
}))
