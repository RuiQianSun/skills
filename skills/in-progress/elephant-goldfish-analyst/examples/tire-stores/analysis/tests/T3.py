import json, os
import numpy as np, pandas as pd
from scipy.stats import spearmanr
d = pd.read_csv(os.environ["DATA"]); rng = np.random.default_rng(int(os.environ["SEED"]))
y = np.log(d.tire_store_sales_musd).diff(12)
x = d.vehicle_miles_m.diff(12) if "vehicle_miles_m" == "unemployment" else np.log(d.vehicle_miles_m).diff(12)
m = pd.concat([y, x], axis=1).dropna().values; y, x = m[:, 0], m[:, 1]
rho = spearmanr(y, x).statistic
# circular-shift null keeps each series' autocorrelation intact
shifts = rng.integers(24, len(x) - 24, 5000)
null = np.array([spearmanr(y, np.roll(x, k)).statistic for k in shifts])
sign = 1 if "pos" == "pos" else -1
p = (1 + np.sum(sign * null >= sign * rho)) / (1 + len(null))
ok = sign * rho >= 0.3 and p < 0.002
print(json.dumps({"verdict": "survived" if ok else "falsified", "n": int(len(y)), "rho": round(float(rho), 4), "p_circular": float(f"{p:.3g}")}))
