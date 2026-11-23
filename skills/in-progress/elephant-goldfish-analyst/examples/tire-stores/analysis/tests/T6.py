import json, os
import numpy as np, pandas as pd
d = pd.read_csv(os.environ["DATA"]); s = d.tire_store_sales_musd
naive = s.shift(12)
drift = s.shift(12) * s.shift(1).rolling(12).sum() / s.shift(13).rolling(12).sum()
e = pd.DataFrame({"naive": abs(s - naive) / s, "drift": abs(s - drift) / s}).dropna()
mn, md = float(e.naive.mean()), float(e.drift.mean())
ok = md <= 0.04 and md < mn
print(json.dumps({"verdict": "survived" if ok else "falsified", "months": int(len(e)), "mape_drift": round(md, 4), "mape_naive": round(mn, 4)}))
