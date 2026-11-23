import os, json, random
import pandas as pd
import numpy as np

seed = int(os.environ["SEED"])
random.seed(seed)
rng = np.random.default_rng(seed)

df = pd.read_csv(os.environ["DATA"])
df["year"] = df["month"].str[:4].astype(int)
df["mon"] = df["month"].str[5:7].astype(int)

# Only complete calendar years (12 months, no missing values) so annual totals are comparable.
counts = df.dropna(subset=["ontario", "quebec"]).groupby("year")["mon"].nunique()
years = sorted(counts[counts == 12].index)
d = df[df["year"].isin(years)]

rows = []
for y in years:
    g = d[d["year"] == y]
    apr = g[g["mon"] == 4]
    on = float(apr["ontario"].iloc[0] / g["ontario"].sum())
    qc = float(apr["quebec"].iloc[0] / g["quebec"].sum())
    rows.append((y, qc, on))

qc = np.array([r[1] for r in rows])
on = np.array([r[2] for r in rows])
wins = qc > on
frac = float(wins.mean())

# Bootstrap over years for an uncertainty interval on the fraction (reported, not used for the verdict).
boots = [wins[rng.integers(0, len(wins), len(wins))].mean() for _ in range(10000)]
lo, hi = np.percentile(boots, [2.5, 97.5])

verdict = "falsified" if frac < 0.80 else "survived"
print(json.dumps({
    "verdict": verdict,
    "method": "per complete calendar year, April sales / annual sales for Quebec and Ontario; "
              "fraction of years Quebec share > Ontario share vs threshold 0.80; year bootstrap CI reported",
    "years": [int(y) for y in years],
    "n_years": len(years),
    "years_quebec_higher": int(wins.sum()),
    "fraction_quebec_higher": round(frac, 4),
    "bootstrap_95ci": [round(float(lo), 4), round(float(hi), 4)],
    "mean_april_share_quebec": round(float(qc.mean()), 4),
    "mean_april_share_ontario": round(float(on.mean()), 4),
    "per_year": {int(y): {"quebec": round(q, 4), "ontario": round(o, 4)} for y, q, o in rows},
}))
