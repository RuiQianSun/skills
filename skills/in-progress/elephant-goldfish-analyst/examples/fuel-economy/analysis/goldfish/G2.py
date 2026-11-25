import os, json
import numpy as np, pandas as pd

rng = np.random.default_rng(int(os.environ["SEED"]))
df = pd.read_csv(os.environ["DATA"])
df = df[df["comb_mpg"] > 0].copy()
df["gpm"] = 100.0 / df["comb_mpg"]

def decompose(d, y0, y1):
    """Symmetric (midpoint) shift-share of change in mean gpm between y0 and y1.
    Classes present in only one year form an entry/exit term."""
    a = d[d.year == y0]; b = d[d.year == y1]
    sa = a.vclass.value_counts(normalize=True); sb = b.vclass.value_counts(normalize=True)
    ga = a.groupby("vclass").gpm.mean(); gb = b.groupby("vclass").gpm.mean()
    common = sa.index.intersection(sb.index)
    total = b.gpm.mean() - a.gpm.mean()
    sbar = (sa[common] + sb[common]) / 2; gbar = (ga[common] + gb[common]) / 2
    within = float((sbar * (gb[common] - ga[common])).sum())
    mix = float(((sb[common] - sa[common]) * gbar).sum())
    entry_exit = float(total - within - mix)
    return dict(total=float(total), within=within, mix=mix, entry_exit=entry_exit)

years = sorted(df.year.unique())
y0, y1 = years[0], years[-1]
main = decompose(df, y0, y1)

pairs = {}
wrong = []
for p, q in zip(years[:-1], years[1:]):
    r = decompose(df, p, q)
    pairs[f"{p}-{q}"] = {k: round(v, 4) for k, v in r.items()}
    wrong.append(r["within"] > 0)  # within-class gpm rising = wrong way
# max run of consecutive wrong-way pairs
run = best = 0
for w in wrong:
    run = run + 1 if w else 0; best = max(best, run)
n_wrong = int(sum(wrong))

# bootstrap within each year for uncertainty on first-to-last components
B = 1000
sub = df[df.year.isin([y0, y1])]
groups = [g for _, g in sub.groupby("year")]
bw, bm = [], []
for _ in range(B):
    s = pd.concat([g.iloc[rng.integers(0, len(g), len(g))] for g in groups])
    r = decompose(s, y0, y1); bw.append(r["within"]); bm.append(r["mix"])
bw, bm = np.array(bw), np.array(bm)

within_reduction = -main["within"]
mix_reduction = -main["mix"]
fail_small = within_reduction < 0.1
fail_vs_mix = abs(main["within"]) < abs(main["mix"])
# "two or more adjacent-year pairs" read as two or more pairs in total (stricter); also report consecutive run
fail_pairs = n_wrong >= 2
falsified = fail_small or fail_vs_mix or fail_pairs

print(json.dumps({
    "verdict": "falsified" if falsified else "survived",
    "method": "symmetric (midpoint-weight) shift-share of mean gallons/100mi across vclass, first vs last model year, plus each adjacent-year pair; entry/exit classes split out; 1000x within-year bootstrap for CIs",
    "years": [int(y0), int(y1)],
    "mean_gpm_first": round(float(df[df.year == y0].gpm.mean()), 4),
    "mean_gpm_last": round(float(df[df.year == y1].gpm.mean()), 4),
    "total_change": round(main["total"], 4),
    "within_change": round(main["within"], 4),
    "mix_change": round(main["mix"], 4),
    "entry_exit_change": round(main["entry_exit"], 4),
    "within_ci95": [round(float(x), 4) for x in np.percentile(bw, [2.5, 97.5])],
    "mix_ci95": [round(float(x), 4) for x in np.percentile(bm, [2.5, 97.5])],
    "adjacent_pairs": pairs,
    "n_pairs_within_wrong_way": n_wrong,
    "max_consecutive_wrong_way": best,
    "fail_within_under_0.1": bool(fail_small),
    "fail_within_smaller_than_mix": bool(fail_vs_mix),
    "fail_pairs": bool(fail_pairs),
}))
