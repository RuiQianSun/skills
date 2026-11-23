import json, os
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.neighbors import NearestCentroid
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
d = pd.read_csv(os.environ["DATA"])
X, y = d[["proline", "color_intensity"]].values, d.cultivar.values
cv = StratifiedKFold(5, shuffle=True, random_state=int(os.environ["SEED"]))
s = cross_val_score(make_pipeline(StandardScaler(), NearestCentroid()), X, y, cv=cv)
print(json.dumps({"verdict": "survived" if s.mean() >= 0.85 else "falsified", "cv_accuracy": round(float(s.mean()), 4),
    "fold_min": round(float(s.min()), 4), "chance": round(float(np.bincount(y).max() / len(y)), 4)}))
