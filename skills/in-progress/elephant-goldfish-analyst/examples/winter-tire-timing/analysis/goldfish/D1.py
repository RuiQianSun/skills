import os, json, random
import numpy as np
import pandas as pd

seed = int(os.environ["SEED"]); random.seed(seed); np.random.seed(seed)
score_from = int(os.environ["SCORE_FROM"])
df = pd.read_csv(os.environ["DATA"], usecols=["year", "province", "oct_share"])
df = df[df["year"] >= score_from].dropna(subset=["oct_share"])

THR, NEED = 0.02, 6
g = df.groupby("province")["oct_share"]
sd_sample = g.std(ddof=1).round(5).to_dict()
sd_pop = g.std(ddof=0).round(5).to_dict()
n_years = g.size().to_dict()
n_sample = sum(v >= THR for v in sd_sample.values())
n_pop = sum(v >= THR for v in sd_pop.values())
verdict = "survived" if n_sample >= NEED else "falsified"
print(json.dumps({
    "verdict": verdict,
    "method": "per-province sample SD (ddof=1) of oct_share over scored years; count provinces with SD >= 0.02, need >= 6",
    "scored_from": score_from,
    "years_scored": [int(df.year.min()), int(df.year.max())],
    "n_provinces": int(g.ngroups),
    "n_years_per_province": n_years,
    "sd_sample": sd_sample,
    "sd_population": sd_pop,
    "provinces_meeting_threshold_sample": int(n_sample),
    "provinces_meeting_threshold_population": int(n_pop),
}))
