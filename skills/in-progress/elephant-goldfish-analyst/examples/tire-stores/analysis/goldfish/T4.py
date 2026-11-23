# T4: Tire-store sales growth falls when unemployment rises.
# Sales are not seasonally adjusted, so growth is 12-month log growth, paired with
# the 12-month change in the unemployment rate (pp). Overlapping 12-month windows are
# heavily autocorrelated, so the p-value comes from a one-sided circular block
# permutation test (block length 12) on Spearman rho, not the naive iid p-value.
import json, os
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

df = pd.read_csv(os.environ["DATA"])
rng = np.random.default_rng(int(os.environ["SEED"]))
df["month"] = pd.PeriodIndex(df["month"], freq="M")
df = df.set_index("month").sort_index().asfreq("M")

g = np.log(df["tire_store_sales_musd"]).diff(12)
du = df["unemployment"].diff(12)
d = pd.concat([g, du], axis=1, keys=["g", "du"]).dropna()
x, y = d["du"].to_numpy(), d["g"].to_numpy()
n = len(d)

rho, p_naive_two = spearmanr(x, y)
rho = float(rho)

# circular block permutation: rotate y by random offset and shuffle 12-month blocks
B, R = 12, 10000
ry = pd.Series(y).rank().to_numpy()
rx = pd.Series(x).rank().to_numpy()
nb = int(np.ceil(n / B))
null = np.empty(R)
for i in range(R):
    off = rng.integers(n)
    yy = np.roll(ry, off)
    blocks = [yy[j * B:(j + 1) * B] for j in range(nb)]
    order = rng.permutation(nb)
    perm = np.concatenate([blocks[k] for k in order])[:n]
    null[i] = np.corrcoef(rx, perm)[0, 1]
p_block = float((1 + np.sum(null <= rho)) / (R + 1))  # one-sided: negative association

# sensitivity: excluding 2020-2021 (COVID shock)
mask = ~((d.index.year >= 2020) & (d.index.year <= 2021))
rho_ex = float(spearmanr(x[mask], y[mask])[0])

falsified = (rho > -0.3) or (p_block >= 0.002)
print(json.dumps({
    "verdict": "falsified" if falsified else "survived",
    "method": "Spearman rho between 12-month change in unemployment (pp) and 12-month log growth of NSA tire-store sales; one-sided circular block permutation p (block=12, 10000 reps)",
    "n": n,
    "period": f"{d.index[0]}..{d.index[-1]}",
    "rho": round(rho, 4),
    "p_block_one_sided": round(p_block, 5),
    "p_naive_two_sided": float(p_naive_two),
    "rho_excl_2020_2021": round(rho_ex, 4),
}))
