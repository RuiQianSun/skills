import os, json, csv
import numpy as np

rng = np.random.default_rng(int(os.environ["SEED"]))
rows = list(csv.DictReader(open(os.environ["DATA"])))
cols = ["mb", "sk", "ns", "nb", "nl", "pe"]
tot = {r["month"]: sum(float(r[c]) for c in cols) for r in rows}
months = sorted(tot)
idx = {m: i for i, m in enumerate(months)}
# sanity: contiguous months
def nxt(m):
    y, mo = map(int, m.split("-")); mo += 1
    if mo == 13: y, mo = y + 1, 1
    return f"{y:04d}-{mo:02d}"
assert all(nxt(months[i]) == months[i + 1] for i in range(len(months) - 1))

def drift(m, anchor=None):
    # anchor: month whose preceding 24 months define the drift ratio (default: m itself)
    a = idx[anchor or m]; i = idx[m]
    if a - 24 < 0 or i - 12 < 0: return None
    last12 = sum(tot[months[k]] for k in range(a - 12, a))
    prev12 = sum(tot[months[k]] for k in range(a - 24, a - 12))
    return tot[months[i - 12]] * last12 / prev12

def cost(q, d): return 3 * max(d - q, 0) + max(q - d, 0)

def evaluate(anchor_oct, pooled):
    res = []
    for y in range(2000, 2100):
        o, n = f"{y}-10", f"{y}-11"
        if o not in idx or n not in idx: continue
        fo = drift(o); fn = drift(n, anchor=o if anchor_oct else None)
        if fo is None or fn is None: continue
        so, sn = tot[months[idx[o] - 12]], tot[months[idx[n] - 12]]
        do, dn = tot[o], tot[n]
        if pooled:
            cd = cost(1.05 * (fo + fn), do + dn); cs = cost(1.05 * (so + sn), do + dn)
        else:
            cd = cost(1.05 * fo, do) + cost(1.05 * fn, dn); cs = cost(1.05 * so, do) + cost(1.05 * sn, dn)
        res.append((y, cd, cs))
    return res

variants = {}
for anchor_oct in (False, True):
    for pooled in (False, True):
        r = evaluate(anchor_oct, pooled)
        cd = np.array([x[1] for x in r]); cs = np.array([x[2] for x in r])
        variants[f"anchor={'oct' if anchor_oct else 'own_month'},cost={'pooled' if pooled else 'per_month'}"] = dict(
            years=[x[0] for x in r], win_frac=float(np.mean(cd < cs)),
            mean_cost_drift=float(cd.mean()), mean_cost_sq=float(cs.mean()),
            per_year=[[x[0], round(x[1]), round(x[2])] for x in r])

prim = "anchor=own_month,cost=per_month"
r = evaluate(False, False)
diff = np.array([x[2] - x[1] for x in r])  # positive = drift cheaper
boot = np.array([rng.choice(diff, len(diff)).mean() for _ in range(10000)])
p = variants[prim]
survived = p["win_frac"] >= 0.7 and p["mean_cost_drift"] < p["mean_cost_sq"]
all_survive = all(v["win_frac"] >= 0.7 and v["mean_cost_drift"] < v["mean_cost_sq"] for v in variants.values())
print(json.dumps({
    "verdict": "survived" if survived else "falsified",
    "method": "Backtest on six-province total, every year with Oct+Nov actuals and 24 prior months; order=1.05*forecast per month, cost=3*shortfall+1*overstock summed over Oct and Nov; compare drift vs same-month-last-year; bootstrap (10k) of mean cost saving. Variants: Nov drift anchored at Oct (info at order time), pooled Oct+Nov cost.",
    "primary": prim, "n_years": len(diff), "win_frac": p["win_frac"],
    "mean_cost_drift": p["mean_cost_drift"], "mean_cost_status_quo": p["mean_cost_sq"],
    "mean_saving_boot_95ci": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
    "all_variants_survive": all_survive, "variants": variants}))
