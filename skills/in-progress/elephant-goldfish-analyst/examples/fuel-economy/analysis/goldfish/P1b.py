import os, json
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

SEED = int(os.environ["SEED"])
np.random.seed(SEED)
df = pd.read_csv(os.environ["DATA"])

SPEC = ["make", "vclass", "drive", "transmission", "cylinders", "displ",
        "turbo", "supercharger", "hybrid", "fuel"]
CAT = ["make", "vclass", "drive", "transmission", "fuel"]
for c in CAT:
    df[c] = df[c].astype(str).astype("category")
df["spec_key"] = df[SPEC].astype(str).agg("|".join, axis=1)

X = df[SPEC]
is_cat = [c in CAT for c in SPEC]
years = sorted(df.year.unique())
test_years = [y for y in years if any(t <= y - 2 for t in years)]


def payoff(flag, real):
    return int(np.where(real[flag] >= 30, 1, -1).sum())


def rule_a(d):
    return (d.hybrid == 1).values


def rule_b(d):
    carwagon = d.vclass.astype(str).str.contains("Cars|Wagons", regex=True)
    return ((d.hybrid == 1) | (carwagon & (d.displ <= 2.0) & (d.turbo == 0))).values


def run(novel_ref):
    per = []
    for y in test_years:
        tr = df[df.year <= y - 2]
        if novel_ref == "all_prior":
            seen = set(df.loc[df.year < y, "spec_key"])
        else:  # training window only
            seen = set(tr.spec_key)
        te = df[(df.year == y) & (~df.spec_key.isin(seen))]
        m = HistGradientBoostingRegressor(categorical_features=is_cat, random_state=SEED,
                                          max_iter=300, learning_rate=0.05)
        m.fit(tr[SPEC], tr.comb_mpg)
        pred = m.predict(te[SPEC]) if len(te) else np.array([])
        real = te.comb_mpg.values
        f = pred >= 30
        pm, pa, pb = payoff(f, real), payoff(rule_a(te), real), payoff(rule_b(te), real)
        per.append(dict(year=int(y), n_novel=int(len(te)), n_flag=int(f.sum()),
                        model=pm, hybrids_only=pa, hybrid_or_small_car=pb,
                        beats_both=bool(pm > pa and pm > pb)))
    n = len(per)
    tot = {k: sum(p[k] for p in per) for k in ["model", "hybrids_only", "hybrid_or_small_car"]}
    frac_ge5 = sum(p["model"] >= 5 for p in per) / n
    frac_beat = sum(p["beats_both"] for p in per) / n
    survived = (frac_ge5 >= 0.75 and tot["model"] > tot["hybrids_only"]
                and tot["model"] > tot["hybrid_or_small_car"] and frac_beat >= 0.75)
    return survived, dict(per_year=per, totals=tot, frac_years_payoff_ge5=frac_ge5,
                          frac_years_beats_both=frac_beat)


surv, res = run("all_prior")
surv_alt, res_alt = run("train_only")
out = {"verdict": "survived" if surv else "falsified",
       "method": ("Expanding-window by year: HistGradientBoostingRegressor (native categoricals) on 10 spec "
                  "columns trained on years <= Y-2; test on year-Y configs whose full 10-field spec never "
                  "appeared in any earlier year; flag pred>=30; +1/-1 payoff vs real comb_mpg>=30; rules "
                  "applied to same novel set; car/wagon = vclass containing 'Cars' or 'Wagons'."),
       "test_years": [int(y) for y in test_years],
       **res,
       "sensitivity_novel_vs_training_window_only": {"verdict": "survived" if surv_alt else "falsified",
                                                     **{k: res_alt[k] for k in ["totals", "frac_years_payoff_ge5", "frac_years_beats_both"]},
                                                     "per_year": res_alt["per_year"]}}
print(json.dumps(out))
