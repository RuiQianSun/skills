import json, os
import numpy as np, pandas as pd
from scipy.stats import wilcoxon
d = pd.read_csv(os.environ["DATA"]); d["ls"] = np.log(d.tire_store_sales_musd)
d["seas"] = d.ls - d.ls.rolling(12, center=True).mean(); d["m"] = d.month.str[5:].astype(int); d["y"] = d.month.str[:4]
d = d.dropna()
summer = d[d.m.isin([6, 7, 8])].groupby("y").seas.mean(); winter = d[d.m.isin([11, 12, 1, 2])].groupby("y").seas.mean()
both = pd.concat([summer, winter], axis=1, keys=["s", "w"]).dropna(); gap = both.s - both.w
p = wilcoxon(gap - 0.08, alternative="greater").pvalue
ok = gap.mean() >= 0.08 and p < 0.002
print(json.dumps({"verdict": "survived" if ok else "falsified", "years": int(len(gap)), "mean_gap_logpts": round(float(gap.mean()), 4), "p_gap_gt_0.08": float(f"{p:.3g}")}))
