import json, os
import numpy as np, pandas as pd
from scipy.stats import wilcoxon
d = pd.read_csv(os.environ["DATA"]); ls = np.log(d.canada)
d["seas"] = ls - ls.rolling(12, center=True).mean(); d["m"] = d.month.str[5:].astype(int); d["y"] = d.month.str[:4]
d = d.dropna(subset=["seas"])
fall = d[d.m.isin([10, 11])].groupby("y").seas.mean(); summer = d[d.m.isin([6, 7, 8])].groupby("y").seas.mean()
gap = (fall - summer).dropna()
p = wilcoxon(gap - 0.15, alternative="greater").pvalue
ok = gap.mean() >= 0.15 and p < 0.002
print(json.dumps({"verdict": "survived" if ok else "falsified", "years": int(len(gap)), "mean_gap_logpts": round(float(gap.mean()), 4), "min_gap": round(float(gap.min()), 4), "p_gap_gt_0.15": float(f"{p:.3g}")}))
