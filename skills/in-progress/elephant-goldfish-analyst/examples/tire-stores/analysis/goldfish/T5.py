"""T5: does tire PPI inflation show up as higher nominal tire-store sales growth?

Method: year-over-year log growth (removes seasonality of NSA sales) of sales and of
tire PPI, Spearman rank correlation. Because overlapping 12-month growth rates are
heavily autocorrelated, the naive p-value is too optimistic, so the p-value used for
the verdict comes from a phase-randomization surrogate test (surrogates of the PPI
growth series preserve its autocorrelation spectrum). Falsified if rho < 0.3 or p >= 0.002.
"""
import json, os
import numpy as np
import pandas as pd
from scipy import stats

rng = np.random.default_rng(int(os.environ["SEED"]))
df = pd.read_csv(os.environ["DATA"])
df["month"] = pd.PeriodIndex(df["month"], freq="M")
df = df.set_index("month").sort_index().asfreq("M")

g = pd.DataFrame({
    "sales": np.log(df["tire_store_sales_musd"]).diff(12),
    "ppi": np.log(df["tire_ppi"]).diff(12),
}).dropna()
x, y = g["ppi"].to_numpy(), g["sales"].to_numpy()
n = len(x)
rho, p_naive = stats.spearmanr(x, y)

# Phase-randomization surrogates on ranks-to-normal transformed PPI growth
def surrogate(v):
    f = np.fft.rfft(v - v.mean())
    ph = rng.uniform(0, 2 * np.pi, len(f))
    ph[0] = 0
    if len(v) % 2 == 0:
        ph[-1] = 0
    s = np.fft.irfft(np.abs(f) * np.exp(1j * ph), n=len(v))
    # rank-remap to original values (amplitude adjustment)
    return np.sort(v)[np.argsort(np.argsort(s))]

N = 19999
ry = stats.rankdata(y)
null = np.empty(N)
for i in range(N):
    null[i] = np.corrcoef(stats.rankdata(surrogate(x)), ry)[0, 1]
# one-sided: claim is a positive association
p_surr = (1 + np.sum(null >= rho)) / (N + 1)

# effective-sample-size sanity check (Bartlett, lag-1 AR approx)
r1x = np.corrcoef(x[:-1], x[1:])[0, 1]
r1y = np.corrcoef(y[:-1], y[1:])[0, 1]
n_eff = n * (1 - r1x * r1y) / (1 + r1x * r1y)
t = rho * np.sqrt((n_eff - 2) / (1 - rho ** 2))
p_neff = float(stats.t.sf(t, n_eff - 2))

verdict = "falsified" if (rho < 0.3 or p_surr >= 0.002) else "survived"
print(json.dumps({
    "verdict": verdict,
    "method": "Spearman rho of YoY log growth (sales vs tire PPI), one-sided p from 19999 phase-randomized (amplitude-adjusted) surrogates of PPI growth",
    "n": int(n),
    "period": f"{g.index[0]}..{g.index[-1]}",
    "rho": round(float(rho), 4),
    "p_surrogate": round(float(p_surr), 5),
    "p_naive_two_sided": float(p_naive),
    "n_eff_ar1": round(float(n_eff), 1),
    "p_neff_one_sided": float(p_neff),
    "thresholds": {"rho_min": 0.3, "p_max": 0.002},
}))
