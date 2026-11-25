"""Goldfish test of claim F1: spec-only model (no make) on novel year-Y configs,
trained on years <= Y-2, vs. a grouped-median baseline."""
import json
import os

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

DATA = os.environ["DATA"]
SEED = int(os.environ["SEED"])
SCORE_FROM = int(os.environ["SCORE_FROM"])
np.random.seed(SEED)

df = pd.read_csv(DATA)
SPECS = ["vclass", "drive", "transmission", "cylinders", "displ", "turbo",
         "supercharger", "hybrid", "fuel"]
CATS = ["vclass", "drive", "transmission", "fuel"]
FULL = ["make"] + SPECS
BASE_KEYS = ["vclass", "cylinders", "turbo", "hybrid", "drive"]

for c in CATS:
    df[c] = df[c].astype("category")
df["key"] = df[FULL].astype(str).agg("|".join, axis=1)
first_year = df.groupby("key")["year"].min()
df["novel"] = df["year"] == df["key"].map(first_year)


def fallback_median(train, row_keys):
    # progressively coarser groups if the exact baseline group is empty
    for keys in (BASE_KEYS, ["vclass", "cylinders", "hybrid"], ["vclass"], []):
        if not keys:
            return train["comb_mpg"].median()
        m = train.groupby(keys, observed=True)["comb_mpg"].median()
        k = tuple(row_keys[k] for k in keys) if len(keys) > 1 else row_keys[keys[0]]
        if k in m.index:
            return m.loc[k]


per_year = {}
years = sorted(y for y in df["year"].unique() if y >= SCORE_FROM)
for Y in years:
    train = df[df["year"] <= Y - 2]
    test = df[(df["year"] == Y) & df["novel"]]
    if len(test) == 0 or len(train) == 0:
        continue
    X = train[SPECS]
    # model log(mpg): multiplicative effects, hybrids have large MPG
    model = HistGradientBoostingRegressor(
        loss="absolute_error", max_iter=600, learning_rate=0.05,
        max_leaf_nodes=31, min_samples_leaf=10, l2_regularization=1.0,
        categorical_features=[SPECS.index(c) for c in CATS], random_state=SEED)
    model.fit(X, np.log(train["comb_mpg"]))
    pred = np.exp(model.predict(test[SPECS]))
    mae = float(np.mean(np.abs(pred - test["comb_mpg"].values)))

    grp = train.groupby(BASE_KEYS, observed=True)["comb_mpg"].median()
    base = []
    n_fallback = 0
    for _, r in test.iterrows():
        k = tuple(r[k] for k in BASE_KEYS)
        if k in grp.index:
            base.append(grp.loc[k])
        else:
            n_fallback += 1
            base.append(fallback_median(train, r))
    base = np.array(base, dtype=float)
    bmae = float(np.mean(np.abs(base - test["comb_mpg"].values)))
    per_year[int(Y)] = {"n": int(len(test)), "mae": round(mae, 3),
                        "baseline_mae": round(bmae, 3),
                        "ratio": round(mae / bmae, 3),
                        "baseline_fallbacks": n_fallback}

maes = [v["mae"] for v in per_year.values()]
avg = float(np.mean(maes))
worst = float(np.max(maes))
worst_ratio = float(max(v["ratio"] for v in per_year.values()))
fails = []
if avg > 2.0:
    fails.append("average MAE > 2.0")
if worst > 2.5:
    fails.append("a year MAE > 2.5")
if worst_ratio > 0.85:
    fails.append("a year MAE > 0.85 x baseline")

print(json.dumps({
    "verdict": "falsified" if fails else "survived",
    "method": "per-year walk-forward HistGradientBoosting (L1 loss on log mpg, native categoricals) on 9 spec columns, no make; train years <= Y-2; test = year-Y rows whose make+spec key never appeared in any earlier year; baseline = median comb_mpg of training rows with same vclass/cylinders/turbo/hybrid/drive (coarser fallback when group empty)",
    "scored_from": SCORE_FROM,
    "seed": SEED,
    "avg_mae": round(avg, 3),
    "max_year_mae": round(worst, 3),
    "max_ratio_to_baseline": round(worst_ratio, 3),
    "failed_conditions": fails,
    "per_year": per_year,
}))
