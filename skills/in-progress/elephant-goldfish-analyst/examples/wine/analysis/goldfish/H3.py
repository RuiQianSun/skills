"""H3: cultivar 0 is at least 0.5 %vol more alcoholic than cultivar 2.

Method: Hodges-Lehmann shift estimate (median of all pairwise differences
c0 - c2) as the "median diff", plus a one-sided Mann-Whitney U test of
H0: shift <= 0.5 vs H1: shift > 0.5 (computed by subtracting 0.5 from c0).
A seeded permutation test of the same shifted hypothesis is reported as a
cross-check, along with a seeded bootstrap 95% CI of the HL estimate.
Falsified if HL median diff < 0.5 or MWU p >= 0.001.
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

THRESH = 0.5
ALPHA = 0.001

seed = int(os.environ["SEED"])
rng = np.random.default_rng(seed)
df = pd.read_csv(os.environ["DATA"])

a = df.loc[df["cultivar"] == 0, "alcohol"].dropna().to_numpy(float)
b = df.loc[df["cultivar"] == 2, "alcohol"].dropna().to_numpy(float)

hl = float(np.median(np.subtract.outer(a, b)))
diff_of_medians = float(np.median(a) - np.median(b))

mw = stats.mannwhitneyu(a - THRESH, b, alternative="greater", method="auto")
p_mwu = float(mw.pvalue)

# Permutation test of the shifted hypothesis on the HL statistic.
a_s = a - THRESH
pooled = np.concatenate([a_s, b])
n_a = len(a)
obs = float(np.median(np.subtract.outer(a_s, b)))
n_perm = 20000
count = 0
for _ in range(n_perm):
    perm = rng.permutation(pooled)
    if np.median(np.subtract.outer(perm[:n_a], perm[n_a:])) >= obs:
        count += 1
p_perm = (count + 1) / (n_perm + 1)

# Bootstrap CI of HL.
boots = np.empty(5000)
for i in range(5000):
    ba = rng.choice(a, len(a), replace=True)
    bb = rng.choice(b, len(b), replace=True)
    boots[i] = np.median(np.subtract.outer(ba, bb))
ci = [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]

falsified = hl < THRESH or p_mwu >= ALPHA
print(json.dumps({
    "verdict": "falsified" if falsified else "survived",
    "method": "Hodges-Lehmann shift + one-sided Mann-Whitney U of H0: shift<=0.5 (permutation cross-check)",
    "n_cultivar0": int(len(a)),
    "n_cultivar2": int(len(b)),
    "median_diff_hodges_lehmann": round(hl, 4),
    "diff_of_medians": round(diff_of_medians, 4),
    "hl_bootstrap_95ci": [round(x, 4) for x in ci],
    "mwu_U": float(mw.statistic),
    "p_mwu_shift_gt_0.5": p_mwu,
    "p_perm_shift_gt_0.5": p_perm,
    "threshold": THRESH,
    "alpha": ALPHA,
    "seed": seed,
}))
