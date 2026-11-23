import os, json
import numpy as np
import pandas as pd
from scipy import stats

DELTA = 0.5
rng = np.random.default_rng(int(os.environ["SEED"]))
df = pd.read_csv(os.environ["DATA"])
x0 = df.loc[df["cultivar"] == 0, "alcohol"].dropna().to_numpy(float)
x2 = df.loc[df["cultivar"] == 2, "alcohol"].dropna().to_numpy(float)

# Effect size: Hodges-Lehmann shift (median of all pairwise differences) and difference of medians
hl = float(np.median(np.subtract.outer(x0, x2)))
med_diff = float(np.median(x0) - np.median(x2))

# Test H0: shift <= 0.5 vs H1: shift > 0.5, by shifting cultivar 0 down by 0.5
x0s = x0 - DELTA
mw = stats.mannwhitneyu(x0s, x2, alternative="greater", method="auto")

# Seeded permutation test of the rank-sum statistic on shifted data as a check
pooled = np.concatenate([x0s, x2]); n0 = len(x0s)
ranks = stats.rankdata(pooled)
obs = ranks[:n0].sum()
B = 100000
cnt = 0
for _ in range(B // 10000):
    perm = np.argsort(rng.random((10000, len(pooled))), axis=1)[:, :n0]
    cnt += int((ranks[perm].sum(axis=1) >= obs).sum())
p_perm = (cnt + 1) / (B + 1)

p = max(float(mw.pvalue), p_perm)
survived = (min(hl, med_diff) >= DELTA) and (p < 0.001)
print(json.dumps({
    "verdict": "survived" if survived else "falsified",
    "method": "one-sided Mann-Whitney U on (cultivar0 - 0.5) vs cultivar2, confirmed by 100k seeded rank-sum permutations; effect = Hodges-Lehmann shift and difference of medians",
    "n0": int(len(x0)), "n2": int(len(x2)),
    "median0": float(np.median(x0)), "median2": float(np.median(x2)),
    "median_diff": med_diff, "hodges_lehmann_shift": hl,
    "mw_U": float(mw.statistic), "p_mw_shift_gt_0.5": float(mw.pvalue),
    "p_perm_shift_gt_0.5": p_perm, "p_used": p,
}))
