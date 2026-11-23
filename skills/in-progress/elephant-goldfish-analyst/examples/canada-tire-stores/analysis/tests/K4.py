import json, os
import pandas as pd
d = pd.read_csv(os.environ["DATA"]); s = d.canada
naive = s.shift(12); drift = s.shift(12) * s.shift(1).rolling(12).sum() / s.shift(13).rolling(12).sum()
e = pd.DataFrame({"naive": abs(s - naive) / s, "drift": abs(s - drift) / s}).dropna()
mn, md = float(e.naive.mean()), float(e.drift.mean())
print(json.dumps({"verdict": "survived" if md <= 0.07 and md < mn else "falsified", "months": int(len(e)), "mape_drift": round(md, 4), "mape_naive": round(mn, 4)}))
