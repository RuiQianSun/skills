"""H1: flavanoids fall strictly by cultivar, 0 > 1 > 2.

Falsified if the mean order breaks, or either adjacent one-sided p >= 0.001.
Method: one-sided permutation test on the difference in means for each
adjacent pair (0 vs 1, 1 vs 2), with a Welch t-test reported alongside.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

ALPHA = 0.001
N_PERM = 100_000

df = pd.read_csv(os.environ["DATA"])
seed = int(os.environ["SEED"])
rng = np.random.default_rng(seed)

df = df[["flavanoids", "cultivar"]].dropna()
df["cultivar"] = df["cultivar"].astype(int)
groups = {c: df.loc[df["cultivar"] == c, "flavanoids"].to_numpy() for c in (0, 1, 2)}


def perm_p_greater(a, b):
    """One-sided p for H_a: mean(a) > mean(b)."""
    obs = a.mean() - b.mean()
    pooled = np.concatenate([a, b])
    na = len(a)
    count = 0
    batch = 10_000
    for start in range(0, N_PERM, batch):
        k = min(batch, N_PERM - start)
        idx = np.argsort(rng.random((k, len(pooled))), axis=1)
        perm = pooled[idx]
        diff = perm[:, :na].mean(axis=1) - perm[:, na:].mean(axis=1)
        count += int(np.sum(diff >= obs))
    return obs, (count + 1) / (N_PERM + 1)


means = {str(c): float(g.mean()) for c, g in groups.items()}
ns = {str(c): int(len(g)) for c, g in groups.items()}
order_holds = means["0"] > means["1"] > means["2"]

pairs = {}
for hi, lo in ((0, 1), (1, 2)):
    obs, p_perm = perm_p_greater(groups[hi], groups[lo])
    welch = stats.ttest_ind(groups[hi], groups[lo], equal_var=False, alternative="greater")
    pairs[f"{hi}>{lo}"] = {
        "mean_diff": float(obs),
        "p_perm_one_sided": float(p_perm),
        "p_welch_one_sided": float(welch.pvalue),
    }

p_ok = all(v["p_perm_one_sided"] < ALPHA for v in pairs.values())
verdict = "survived" if (order_holds and p_ok) else "falsified"

print(json.dumps({
    "verdict": verdict,
    "method": f"group means order check + one-sided permutation test of mean difference "
              f"for adjacent cultivar pairs ({N_PERM} perms, p=(k+1)/(N+1)); Welch t reported as cross-check",
    "alpha": ALPHA,
    "n": ns,
    "means": means,
    "order_holds": order_holds,
    "pairs": pairs,
    "seed": seed,
}))
