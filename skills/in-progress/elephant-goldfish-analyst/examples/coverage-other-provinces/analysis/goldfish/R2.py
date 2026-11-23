import os, json, random
import numpy as np, pandas as pd

df = pd.read_csv(os.environ["DATA"])
rng = np.random.default_rng(int(os.environ["SEED"])); random.seed(int(os.environ["SEED"]))
cols = ["mb", "sk", "ns", "nb", "nl", "pe"]
df["y"] = df.month.str[:4].astype(int); df["m"] = df.month.str[5:].astype(int)

def shares(sub):
    s = sub[cols].sum(); return (s / s.sum()).values

def mis(pred, actual):  # share of stock sent to the wrong province (total variation distance)
    return 0.5 * np.abs(pred - actual).sum()

def run(annual_fn, years):
    rows = []
    for y in years:
        act = shares(df[(df.y == y) & df.m.isin([10, 11])])
        if len(df[(df.y == y) & df.m.isin([10, 11])]) != 2: continue
        fall = shares(df[(df.y == y - 1) & df.m.isin([10, 11])])
        ann = annual_fn(y)
        if ann is None: continue
        rows.append((y, mis(fall, act), mis(ann, act)))
    return rows

def cal_annual(y):
    s = df[df.y == y - 1]
    return shares(s) if len(s) == 12 else None

def trail_annual(y):  # 12 months ending Sep of year y
    s = df[((df.y == y - 1) & (df.m >= 10)) | ((df.y == y) & (df.m <= 9))]
    return shares(s) if len(s) == 12 else None

def summarize(rows):
    f = np.array([r[1] for r in rows]); a = np.array([r[2] for r in rows])
    red = 1 - f.mean() / a.mean()
    idx = rng.integers(0, len(f), (5000, len(f)))
    bs = 1 - f[idx].mean(1) / a[idx].mean(1)
    return dict(n_years=len(f), win_rate=float((f < a).mean()), mean_mis_fall=float(f.mean()),
                mean_mis_annual=float(a.mean()), mean_reduction=float(red),
                boot_ci90=[float(np.percentile(bs, 5)), float(np.percentile(bs, 95))],
                years=[r[0] for r in rows], per_year_reduction=[float(1 - x / y) for x, y in zip(f, a)])

main = summarize(run(cal_annual, range(2016, 2025)))
alt = summarize(run(trail_annual, range(2016, 2025)))
ok = main["win_rate"] >= 0.7 and main["mean_reduction"] >= 0.2
ok_alt = alt["win_rate"] >= 0.7 and alt["mean_reduction"] >= 0.2
print(json.dumps({"verdict": "survived" if ok else "falsified",
  "method": "Per fall year Y (Oct+Nov actual province shares), compare misallocation = half L1 distance between predicted and actual shares; fall prediction = Y-1 Oct+Nov shares, annual = Y-1 calendar-year shares (alt: trailing 12 months to Sep of Y). Win = fall misallocation < annual; reduction = 1 - mean(fall)/mean(annual); bootstrap over years.",
  "primary_calendar_annual": main, "alt_trailing12": alt, "alt_also_survives": bool(ok_alt)}))
