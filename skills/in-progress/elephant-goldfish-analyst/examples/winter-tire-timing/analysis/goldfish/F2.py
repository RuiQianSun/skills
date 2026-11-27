import os, json, random
import numpy as np, pandas as pd

seed = int(os.environ["SEED"]); random.seed(seed); np.random.seed(seed)
score_from = int(os.environ.get("SCORE_FROM", "2018"))
df = pd.read_csv(os.environ["DATA"])[["year", "province", "oct_share", "sep_mean_temp"]].dropna()

def fe_slope(train):
    # pooled within-province slope of oct_share on sep_mean_temp (province fixed effects)
    g = train.groupby("province")
    x = train["sep_mean_temp"] - g["sep_mean_temp"].transform("mean")
    y = train["oct_share"] - g["oct_share"].transform("mean")
    return float((x * y).sum() / (x * x).sum())

rows = []
for yr in sorted(df.year.unique()):
    if yr < score_from:
        continue
    train = df[df.year < yr]
    test = df[df.year == yr]
    b = fe_slope(train)
    means = train.groupby("province")[["oct_share", "sep_mean_temp"]].mean()
    for _, r in test.iterrows():
        if r.province not in means.index:
            continue
        m = means.loc[r.province]
        base = m.oct_share
        fe = base + b * (r.sep_mean_temp - m.sep_mean_temp)
        tp = train[train.province == r.province]
        c = np.polyfit(tp.sep_mean_temp, tp.oct_share, 1)  # per-province OLS (sensitivity)
        pp = c[0] * r.sep_mean_temp + c[1]
        rows.append(dict(year=yr, province=r.province, y=r.oct_share, base=base, fe=fe, pp=pp, slope=b))

R = pd.DataFrame(rows)
mae_base = float((R.y - R.base).abs().mean())
mae_fe = float((R.y - R.fe).abs().mean())
mae_pp = float((R.y - R.pp).abs().mean())
imp_fe = 1 - mae_fe / mae_base
imp_pp = 1 - mae_pp / mae_base

# block bootstrap over scored years for uncertainty of the improvement (primary model)
yrs = R.year.unique(); boots = []
for _ in range(2000):
    s = np.random.choice(yrs, len(yrs), replace=True)
    B = pd.concat([R[R.year == k] for k in s])
    boots.append(1 - (B.y - B.fe).abs().mean() / (B.y - B.base).abs().mean())
lo, hi = np.percentile(boots, [2.5, 97.5])

print(json.dumps({
    "verdict": "survived" if imp_fe >= 0.10 else "falsified",
    "method": "expanding-window: pooled province-fixed-effects OLS of oct_share on sep_mean_temp (province mean + common slope x Sep anomaly), fit on years < scored year; baseline = province mean oct_share over earlier years; sensitivity = per-province OLS",
    "scored_from": score_from,
    "n_scored": int(len(R)),
    "mae_baseline": round(mae_base, 5),
    "mae_model": round(mae_fe, 5),
    "improvement": round(imp_fe, 4),
    "improvement_boot95": [round(float(lo), 4), round(float(hi), 4)],
    "mae_per_province_ols": round(mae_pp, 5),
    "improvement_per_province_ols": round(imp_pp, 4),
    "slope_last_fit": round(float(R.slope.iloc[-1]), 5),
    "threshold": 0.10,
}))
