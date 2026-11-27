import os, json, random
import numpy as np, pandas as pd
random.seed(int(os.environ["SEED"])); np.random.seed(int(os.environ["SEED"]))
SF = int(os.environ["SCORE_FROM"])
df = pd.read_csv(os.environ["DATA"], usecols=["year","province","apr_share","mar_mean_temp"])

def run(drop_year=None, shift=False):
    d = df if drop_year is None else df[df.year != drop_year]
    base_cost = fc_cost = 0.0; wins = n = 0
    for y in sorted(d.year[d.year >= SF].unique()):
        tr = d[d.year < y]
        # pooled slope on province-demeaned data (prior years only)
        g = tr.groupby("province")
        xs = tr.mar_mean_temp - g.mar_mean_temp.transform("mean")
        ys = tr.apr_share - g.apr_share.transform("mean")
        beta = (xs*ys).sum() / (xs*xs).sum()
        res = ys - beta*xs
        q = np.quantile(res, 2/3) if shift else 0.0
        for _, r in d[d.year == y].iterrows():
            h = tr[tr.province == r.province]
            base = h.apr_share.mean()
            fc = base + beta*(r.mar_mean_temp - h.mar_mean_temp.mean()) + q
            cost = lambda p: 2*(r.apr_share-p) if r.apr_share > p else (p-r.apr_share)
            cb, cf = cost(base), cost(fc)
            base_cost += cb; fc_cost += cf; n += 1; wins += cf < cb
    return dict(cut=1-fc_cost/base_cost, win=wins/n, n=n, base_cost=base_cost, fc_cost=fc_cost)

a, b = run(), run(2020)
ok = lambda r: r["cut"] >= 0.05 and r["win"] >= 0.60
out = {"verdict": "survived" if ok(a) and ok(b) else "falsified",
       "method": "pooled province-demeaned OLS of April share on March mean temp (prior years only) added to province historical mean; 2020 dropped from fit and scoring in second version",
       "scored_from": SF, "all_years": a, "without_2020": b,
       "sensitivity_quantile_shift": {"all": run(shift=True), "no2020": run(2020, True)}}
print(json.dumps(out))
