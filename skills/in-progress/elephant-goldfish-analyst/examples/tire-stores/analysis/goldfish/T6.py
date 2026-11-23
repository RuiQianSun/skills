import os, json
import numpy as np
import pandas as pd

rng = np.random.default_rng(int(os.environ["SEED"]))
df = pd.read_csv(os.environ["DATA"]).sort_values("month").reset_index(drop=True)
df["month"] = pd.PeriodIndex(df["month"], freq="M")
s = df.set_index("month")["tire_store_sales_musd"].astype(float)
s = s.reindex(pd.period_range(s.index.min(), s.index.max(), freq="M"))

rows = []
for t in s.index[24:]:
    y = s[t]
    last12 = s[t - 12:t - 1]          # t-12 .. t-1
    prev12 = s[t - 24:t - 13]         # t-24 .. t-13
    ly = s[t - 12]
    if np.isnan(y) or np.isnan(ly) or last12.isna().any() or prev12.isna().any():
        continue
    g = last12.sum() / prev12.sum()   # trailing 12-month growth ratio, known at forecast time
    rows.append((str(t), y, ly * g, ly))
r = pd.DataFrame(rows, columns=["month", "y", "drift", "snaive"])
ape_d = np.abs(r.y - r.drift) / r.y
ape_s = np.abs(r.y - r.snaive) / r.y
mape_d, mape_s = ape_d.mean(), ape_s.mean()

# paired bootstrap (moving blocks of 12 months) on MAPE difference
n = len(r); B = 5000; L = 12
diff = (ape_d - ape_s).to_numpy()
boots = []
for _ in range(B):
    idx = np.concatenate([np.arange(st, st + L) % n for st in rng.integers(0, n, size=int(np.ceil(n / L)))])[:n]
    boots.append(diff[idx].mean())
ci = np.percentile(boots, [2.5, 97.5])

ex = ~r.month.str.match(r"^202[01]-")
mape_d_ex, mape_s_ex = ape_d[ex].mean(), ape_s[ex].mean()

falsified = bool(mape_d > 0.04 or not (mape_d < mape_s))
print(json.dumps({
    "verdict": "falsified" if falsified else "survived",
    "method": "one-step rolling forecast: y_hat[t]=y[t-12]*sum(y[t-12..t-1])/sum(y[t-24..t-13]) vs seasonal naive y[t-12]; MAPE over all months with 24m history; 12-month block bootstrap CI on MAPE difference",
    "n_months": int(n), "eval_start": r.month.iloc[0], "eval_end": r.month.iloc[-1],
    "mape_drift": round(float(mape_d), 5), "mape_seasonal_naive": round(float(mape_s), 5),
    "mape_diff_drift_minus_snaive": round(float(mape_d - mape_s), 5),
    "diff_ci95": [round(float(ci[0]), 5), round(float(ci[1]), 5)],
    "drift_wins_months_frac": round(float((ape_d < ape_s).mean()), 4),
    "excl_2020_2021": {"mape_drift": round(float(mape_d_ex), 5), "mape_seasonal_naive": round(float(mape_s_ex), 5)},
}))
