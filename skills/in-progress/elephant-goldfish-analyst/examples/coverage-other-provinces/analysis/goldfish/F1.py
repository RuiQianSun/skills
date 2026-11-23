import os, json, random
import numpy as np, pandas as pd
random.seed(int(os.environ["SEED"])); np.random.seed(int(os.environ["SEED"]))
d = pd.read_csv(os.environ["DATA"]).sort_values("month")
y = d[["mb","sk","ns","nb","nl","pe"]].sum(axis=1).values
n = len(y)
sml, drift = [], []
idx = list(range(24, n))
for t in idx:
    # info available up to t-1 only
    g = y[t-12:t].sum() / y[t-24:t-12].sum()
    sml.append(y[t-12]); drift.append(y[t-12]*g)
a = y[idx]
mape = lambda f: float(np.mean(np.abs(np.array(f)-a)/a))
ms, md = mape(sml), mape(drift)
# robustness: last 24 months and without 2020-2021
m = d["month"].values[idx]
mask = np.array([not ("2020-03" <= x <= "2021-12") for x in m])
def mp(f, k): f=np.array(f)[k]; return float(np.mean(np.abs(f-a[k])/a[k]))
ex = {"mape_drift_ex_covid": mp(drift,mask), "mape_sml_ex_covid": mp(sml,mask)}
fals = md > 0.05 or md > 0.9*ms
print(json.dumps({"verdict":"falsified" if fals else "survived",
 "method":"rolling one-step-per-month backtest on 6-province sum; drift=y[t-12]*sum(y[t-12..t-1])/sum(y[t-24..t-13])",
 "n_months":len(idx),"first":str(m[0]),"last":str(m[-1]),
 "mape_drift":md,"mape_sml":ms,"ratio":md/ms,**ex}))
