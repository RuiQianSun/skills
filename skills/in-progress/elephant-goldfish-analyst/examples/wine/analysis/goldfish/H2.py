"""H2: proline and color_intensity alone identify the cultivar.
Falsified if cross-validated accuracy < 0.85.

Primary method (fixed before looking at results): standardized multinomial
logistic regression on [proline, color_intensity], scored by repeated
stratified 5-fold CV (10 repeats). Secondary models are reported for context
only and do not drive the verdict.
"""
import json
import os
import random

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.dummy import DummyClassifier

seed = int(os.environ["SEED"])
random.seed(seed)
np.random.seed(seed)

df = pd.read_csv(os.environ["DATA"])
X = df[["proline", "color_intensity"]].to_numpy()
y = df["cultivar"].to_numpy()

THRESHOLD = 0.85
cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=seed)

def score(model):
    s = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
    return float(s.mean()), float(s.std())

primary = make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000))
acc, sd = score(primary)

secondary = {
    "knn5_scaled": make_pipeline(StandardScaler(), KNeighborsClassifier(5)),
    "tree_depth3": DecisionTreeClassifier(max_depth=3, random_state=seed),
    "majority_baseline": DummyClassifier(strategy="most_frequent"),
}
sec = {k: round(score(m)[0], 4) for k, m in secondary.items()}

print(json.dumps({
    "verdict": "falsified" if acc < THRESHOLD else "survived",
    "method": "standardized multinomial logistic regression on proline+color_intensity, "
              "repeated stratified 5-fold CV x10",
    "cv_accuracy": round(acc, 4),
    "cv_accuracy_sd_across_folds": round(sd, 4),
    "threshold": THRESHOLD,
    "n": int(len(y)),
    "class_counts": {str(k): int(v) for k, v in zip(*np.unique(y, return_counts=True))},
    "secondary_cv_accuracy": sec,
}))
