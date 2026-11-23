import json, os
import pandas as pd
from scipy.stats import mannwhitneyu
d = pd.read_csv(os.environ["DATA"])
a0, a2 = d[d.cultivar == 0].alcohol, d[d.cultivar == 2].alcohol
diff = float(a0.median() - a2.median())
p = mannwhitneyu(a0 - 0.5, a2, alternative="greater").pvalue  # H0: shift <= 0.5
ok = diff >= 0.5 and p < 0.001
print(json.dumps({"verdict": "survived" if ok else "falsified", "median_diff": round(diff, 3), "p_shift_gt_0.5": float(f"{p:.3g}")}))
