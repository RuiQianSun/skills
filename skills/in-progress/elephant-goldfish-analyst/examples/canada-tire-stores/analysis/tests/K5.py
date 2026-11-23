import json, os
import pandas as pd
d = pd.read_csv(os.environ["DATA"]); d["y"] = d.month.str[:4]; d["m"] = d.month.str[5:].astype(int)
full = d.groupby("y").filter(lambda g: len(g) == 12)
top = full.loc[full.groupby("y").alberta.idxmax()].m
share = float((top == 10).mean())
print(json.dumps({"verdict": "survived" if share >= 0.5 else "falsified", "years": int(len(top)), "share_oct_peak": round(share, 3), "peak_months": {str(k): int(v) for k, v in top.value_counts().items()}}))
