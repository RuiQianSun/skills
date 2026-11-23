import os, json, random
import numpy as np
import pandas as pd

seed = int(os.environ["SEED"])
random.seed(seed); np.random.seed(seed)
rng = np.random.default_rng(seed)

df = pd.read_csv(os.environ["DATA"])
df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
df = df.dropna(subset=["tire_store_sales_musd"]).sort_values("month")
df["year"] = df["month"].dt.year
df["m"] = df["month"].dt.month

# Complete calendar years only: all 12 months present with non-missing sales.
counts = df.groupby("year")["m"].nunique()
years = sorted(counts[counts == 12].index)

lows = {}
for y in years:
    d = df[df["year"] == y]
    lows[int(y)] = int(d.loc[d["tire_store_sales_musd"].idxmin(), "m"])

hits = [y for y, m in lows.items() if m in (1, 2)]
n = len(years)
share = len(hits) / n if n else float("nan")

# Bootstrap CI over years (descriptive only; verdict uses the point share).
boot = []
arr = np.array([1 if lows[y] in (1, 2) else 0 for y in lows])
for _ in range(10000):
    boot.append(rng.choice(arr, size=n, replace=True).mean())
ci = [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]

# Chance baseline: P(min in Jan/Feb) if lows were uniform over months = 2/12.
from math import comb
p0 = 2 / 12
k = len(hits)
p_binom = sum(comb(n, i) * p0**i * (1 - p0)**(n - i) for i in range(k, n + 1))

verdict = "falsified" if share < 0.80 else "survived"
print(json.dumps({
    "verdict": verdict,
    "method": "per complete calendar year, find month of minimum NSA sales; share of years with min in Jan or Feb vs 0.80 threshold; year-bootstrap CI and binomial-vs-uniform p as context",
    "n_complete_years": n,
    "years": [int(y) for y in years],
    "low_month_by_year": lows,
    "n_janfeb_low": k,
    "share_janfeb_low": share,
    "threshold": 0.80,
    "bootstrap_95ci_share": ci,
    "binom_p_vs_uniform_months": p_binom,
}))
