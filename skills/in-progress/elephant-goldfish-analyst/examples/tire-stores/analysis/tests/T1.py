import json, os
import pandas as pd
d = pd.read_csv(os.environ["DATA"]); d["y"] = d.month.str[:4]; d["m"] = d.month.str[5:].astype(int)
full = d.groupby("y").filter(lambda g: len(g) == 12)
low = full.loc[full.groupby("y").tire_store_sales_musd.idxmin()].m
share = float(low.isin([1, 2]).mean())
print(json.dumps({"verdict": "survived" if share >= 0.8 else "falsified", "years": int(len(low)), "share_jan_feb_low": round(share, 3), "low_months": low.value_counts().to_dict()}))
