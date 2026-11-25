import os, json
import numpy as np, pandas as pd

rng = np.random.default_rng(int(os.environ["SEED"]))
d = pd.read_csv(os.environ["DATA"])
d = d[["year", "comb_mpg"]].dropna()
d["hi"] = (d["comb_mpg"] >= 30).astype(float)

def shares(df):
    g = df.groupby("year")["hi"]
    return g.mean(), g.size()

s, n = shares(d)
years = s.index.values.astype(float)

def slope(y, x, w=None):
    return float(np.polyfit(x, y, 1, w=None if w is None else np.sqrt(w))[0])

ols_pp = 100 * slope(s.values, years)
wls_pp = 100 * slope(s.values, years, n.values.astype(float))

# Bootstrap: resample configurations within each year, refit OLS slope.
B = 2000
by_year = {y: g["hi"].values for y, g in d.groupby("year")}
boots = np.empty(B)
for b in range(B):
    sh = [rng.choice(v, size=len(v), replace=True).mean() for v in by_year.values()]
    boots[b] = 100 * slope(np.array(sh), np.array(list(by_year.keys()), float))
lo, hi = np.percentile(boots, [2.5, 97.5])

max_share_pct = float(100 * s.max())
level_fail = max_share_pct >= 20.0
trend_fail = ols_pp > 1.0
verdict = "falsified" if (level_fail or trend_fail) else "survived"

print(json.dumps({
    "verdict": verdict,
    "method": "per-year share of configs with comb_mpg>=30; max-share check vs 20%; OLS slope of yearly share on year (pp/yr) vs 1 pp, with count-weighted slope and within-year bootstrap 95% CI as sensitivity",
    "years": [int(y) for y in years],
    "share_pct_by_year": {int(k): round(100 * v, 2) for k, v in s.items()},
    "n_by_year": {int(k): int(v) for k, v in n.items()},
    "max_share_pct": round(max_share_pct, 2),
    "ols_slope_pp_per_year": round(ols_pp, 3),
    "weighted_slope_pp_per_year": round(wls_pp, 3),
    "bootstrap_slope_ci95_pp": [round(float(lo), 3), round(float(hi), 3)],
    "bootstrap_frac_slope_gt_1pp": round(float((boots > 1).mean()), 3),
    "last2_year_change_pp": round(100 * (s.values[-1] - s.values[-2]), 2),
}))
