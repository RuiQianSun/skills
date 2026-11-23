import json, os
import pandas as pd
d = pd.read_csv(os.environ["DATA"]); d["y"] = d.month.str[:4]; d["m"] = d.month.str[5:].astype(int)
full = d.groupby("y").filter(lambda g: len(g) == 12)
apr = full[full.m == 4].set_index("y")[["quebec", "ontario"]] / full.groupby("y")[["quebec", "ontario"]].sum()
share = float((apr.quebec > apr.ontario).mean())
print(json.dumps({"verdict": "survived" if share >= 0.8 else "falsified", "years": int(len(apr)), "share_qc_gt_on": round(share, 3), "mean_apr_share_qc": round(float(apr.quebec.mean()), 4), "mean_apr_share_on": round(float(apr.ontario.mean()), 4)}))
