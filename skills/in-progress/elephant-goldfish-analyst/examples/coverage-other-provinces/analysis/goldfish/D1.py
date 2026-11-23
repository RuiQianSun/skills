import os, json, random
import pandas as pd
import numpy as np
random.seed(int(os.environ["SEED"])); np.random.seed(int(os.environ["SEED"]))
df = pd.read_csv(os.environ["DATA"])
df["year"] = df["month"].str[:4].astype(int)
df["m"] = df["month"].str[5:7].astype(int)
provs = ["mb","sk","ns","nb","nl","pe"]
rows = []
for y, g in df.groupby("year"):
    if len(g) != 12 or g[provs].isna().any().any():
        continue
    ok_all = True; detail = {}
    for p in provs:
        tot = g[p].sum()
        on = g.loc[g.m.isin([10,11]), p].sum()
        am = g.loc[g.m.isin([4,5]), p].sum()
        share = on/tot
        ok = (share >= 0.18) and (on > am)
        detail[p] = round(share, 4)
        detail[p+"_on_over_am"] = round(on/am, 4)
        ok_all &= bool(ok)
    rows.append((y, ok_all, detail))
n = len(rows); k = sum(r[1] for r in rows)
frac = k/n if n else 0.0
print(json.dumps({"verdict": "survived" if frac >= 0.80 else "falsified",
  "method": "per complete calendar year (12 months), per province: Oct+Nov share of annual >= 0.18 and Oct+Nov > Apr+May; fraction of years where all six pass vs 0.80",
  "complete_years": [r[0] for r in rows], "years_passing": k, "n_years": n, "share_passing": frac,
  "per_year": {str(r[0]): {"all_pass": r[1], **r[2]} for r in rows}}))
