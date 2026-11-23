import json, os
import pandas as pd
from scipy.stats import mannwhitneyu
d = pd.read_csv(os.environ["DATA"])
g = {k: v.flavanoids.values for k, v in d.groupby("cultivar")}
med = {k: float(pd.Series(v).median()) for k, v in g.items()}
p01 = mannwhitneyu(g[0], g[1], alternative="greater").pvalue
p12 = mannwhitneyu(g[1], g[2], alternative="greater").pvalue
ok = med[0] > med[1] > med[2] and p01 < 0.001 and p12 < 0.001
print(json.dumps({"verdict": "survived" if ok else "falsified", "median_0": round(med[0], 3),
    "median_1": round(med[1], 3), "median_2": round(med[2], 3), "p_0gt1": float(f"{p01:.3g}"), "p_1gt2": float(f"{p12:.3g}")}))
