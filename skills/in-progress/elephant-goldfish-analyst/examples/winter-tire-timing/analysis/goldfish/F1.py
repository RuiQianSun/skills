import os, json, random
import numpy as np, pandas as pd
random.seed(int(os.environ["SEED"])); np.random.seed(int(os.environ["SEED"]))
SF = int(os.environ.get("SCORE_FROM", 2018))
d = pd.read_csv(os.environ["DATA"])[["year","province","apr_share","mar_mean_temp"]]

def run(drop_year=None, train_drop=True):
    x = d if drop_year is None else d[d.year != drop_year]
    eb, em = [], []
    for y in sorted(x.year.unique()):
        if y < SF: continue
        tr = x[x.year < y]
        te = x[x.year == y]
        # fixed-effects model: apr_share = a_p + b*(mar_temp - province mean mar_temp), b pooled
        tr = tr.copy()
        tr["mt"] = tr.mar_mean_temp - tr.groupby("province").mar_mean_temp.transform("mean")
        tr["ya"] = tr.apr_share - tr.groupby("province").apr_share.transform("mean")
        b = (tr.mt*tr.ya).sum() / (tr.mt**2).sum()
        pm = tr.groupby("province").apr_share.mean()
        mm = tr.groupby("province").mar_mean_temp.mean()
        for _, r in te.iterrows():
            if r.province not in pm.index: continue
            base = pm[r.province]
            pred = base + b*(r.mar_mean_temp - mm[r.province])
            eb.append(abs(r.apr_share-base)); em.append(abs(r.apr_share-pred))
    mb, mmod = 100*np.mean(eb), 100*np.mean(em)
    return dict(n=len(eb), mae_base_pts=round(mb,4), mae_model_pts=round(mmod,4),
                abs_gain_pts=round(mb-mmod,4), rel_gain_pct=round(100*(mb-mmod)/mb,2))

a = run(None); b = run(2020)
# variant: 2020 left out of scoring only (kept in training)
eb, em = [], []
ok = lambda r: r["abs_gain_pts"] >= 0.2 and r["rel_gain_pct"] >= 10
verdict = "survived" if ok(a) and ok(b) else "falsified"
print(json.dumps({"verdict": verdict,
  "method": "expanding-window; baseline=province mean apr_share of prior years; model=province mean + pooled slope on within-province March temp anomaly (fit on prior years only); 2020 excluded from both training and scoring in the leave-out version",
  "scored_from": SF, "all_years": a, "leave_out_2020": b}))
