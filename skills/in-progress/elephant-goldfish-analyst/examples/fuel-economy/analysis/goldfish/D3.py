import os, json
import numpy as np, pandas as pd
rng = np.random.default_rng(int(os.environ["SEED"]))
d = pd.read_csv(os.environ["DATA"])
d = d[d.hybrid == 0]
d = d[d.drive.isin(["Front-Wheel Drive", "All-Wheel Drive"])].copy()
d["band"] = pd.cut(d.displ, [0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 99])
d["g"] = np.where(d.drive == "Front-Wheel Drive", "F", "A")

def gaps(df):
    """Per year: stratified (vclass x band) FWD-AWD gap, weighted by min(nF,nA); plus unweighted cell median."""
    out = {}
    for y, s in df.groupby("year"):
        t = s.groupby(["vclass", "band", "g"], observed=True).comb_mpg.agg(["mean", "size"]).unstack("g").dropna()
        if len(t) == 0:
            out[y] = (np.nan, np.nan, 0); continue
        gap = t[("mean", "F")] - t[("mean", "A")]
        w = np.minimum(t[("size", "F")], t[("size", "A")])
        out[y] = (float((gap * w).sum() / w.sum()), float(gap.median()), len(t))
    return out

pt = gaps(d)
years = sorted(pt)
wmean = [pt[y][0] for y in years]
avg = float(np.mean(wmean))
# bootstrap rows within year for uncertainty
bs = []
for _ in range(300):
    b = pd.concat([s.sample(len(s), replace=True, random_state=int(rng.integers(1 << 31))) for _, s in d.groupby("year")])
    g = gaps(b); bs.append([g[y][0] for y in years])
bs = np.array(bs)
lo = np.nanpercentile(bs, 5, axis=0); hi = np.nanpercentile(bs, 95, axis=0)
avg_lo = float(np.percentile(np.nanmean(bs, axis=1), 5))
fals = any(v < 1 for v in wmean) or avg < 1.5
print(json.dumps({"verdict": "falsified" if fals else "survived",
  "method": "non-hybrid FWD vs AWD only; strata = vclass x displ band (8 bands) x year; per-year gap = weighted mean of FWD-AWD cell mean differences, weight=min(nF,nA); within-year bootstrap (300) 90% intervals",
  "gap_by_year": {int(y): round(pt[y][0], 3) for y in years},
  "cell_median_gap_by_year": {int(y): round(pt[y][1], 3) for y in years},
  "cells_by_year": {int(y): pt[y][2] for y in years},
  "boot90_lo": [round(x, 3) for x in lo], "boot90_hi": [round(x, 3) for x in hi],
  "avg_gap": round(avg, 3), "avg_gap_boot_p5": round(avg_lo, 3)}))
