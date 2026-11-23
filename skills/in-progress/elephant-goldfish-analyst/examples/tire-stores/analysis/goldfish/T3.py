"""T3: Tire-store sales growth tracks growth in vehicle miles driven.

Both series are not seasonally adjusted, so growth is measured year over year
(12-month log difference), which removes the seasonal cycle. Association is
Spearman rank correlation. Overlapping YoY growth is heavily autocorrelated,
so the naive p-value is too optimistic: the p-value uses an effective sample
size (Pyper & Peterman 1998) computed from the rank series' autocorrelations.
A moving-block bootstrap gives a 95% CI for rho as a robustness check.
Falsified if rho < 0.3 or adjusted p >= 0.002.
"""
import os, json
import numpy as np
import pandas as pd
from scipy import stats

rng = np.random.default_rng(int(os.environ["SEED"]))
df = pd.read_csv(os.environ["DATA"])
df["month"] = pd.PeriodIndex(df["month"], freq="M")
df = df.sort_values("month").set_index("month")
df = df.reindex(pd.period_range(df.index.min(), df.index.max(), freq="M"))  # guard gaps

sales = np.log(df["tire_store_sales_musd"])
vmt = np.log(df["vehicle_miles_m"])
g = pd.DataFrame({"s": sales - sales.shift(12), "v": vmt - vmt.shift(12)}).dropna()
x, y = g["s"].to_numpy(), g["v"].to_numpy()
n = len(x)

rho, p_naive = stats.spearmanr(x, y)

def acf(a, k):
    a = a - a.mean()
    return np.sum(a[:-k] * a[k:]) / np.sum(a * a)

rx, ry = stats.rankdata(x), stats.rankdata(y)
L = n // 5
inv = 1.0 / n + (2.0 / n) * sum(((n - k) / n) * acf(rx, k) * acf(ry, k) for k in range(1, L + 1))
n_eff = float(np.clip(1.0 / inv, 3, n))
t = rho * np.sqrt((n_eff - 2) / max(1e-12, 1 - rho ** 2))
p_adj = float(2 * stats.t.sf(abs(t), df=n_eff - 2))

block, B = 12, 2000
boots = []
for _ in range(B):
    starts = rng.integers(0, n - block + 1, size=int(np.ceil(n / block)))
    idx = np.concatenate([np.arange(s, s + block) for s in starts])[:n]
    boots.append(stats.spearmanr(x[idx], y[idx])[0])
lo, hi = np.percentile(boots, [2.5, 97.5])

# sensitivity: excluding the 2020-2021 pandemic swing in driving
mask = ~((g.index.year >= 2020) & (g.index.year <= 2021))
rho_ex, _ = stats.spearmanr(x[mask], y[mask])

verdict = "falsified" if (rho < 0.3 or p_adj >= 0.002) else "survived"
print(json.dumps({
    "verdict": verdict,
    "method": "Spearman rho of YoY log growth (sales vs VMT), p-value with autocorrelation-adjusted effective N (Pyper-Peterman); 12-month moving-block bootstrap CI",
    "n": n, "rho": round(float(rho), 4), "p_naive": float(p_naive),
    "n_eff": round(n_eff, 1), "p_adjusted": p_adj,
    "boot_ci95": [round(float(lo), 4), round(float(hi), 4)],
    "rho_excl_2020_2021": round(float(rho_ex), 4),
    "first_month": str(g.index.min()), "last_month": str(g.index.max()),
}))
