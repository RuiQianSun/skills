import os, json
import numpy as np, pandas as pd
from scipy import stats

rng = np.random.default_rng(int(os.environ["SEED"]))
df = pd.read_csv(os.environ["DATA"])
df["month"] = pd.PeriodIndex(df["month"], freq="M")
df = df.set_index("month").sort_index()
full = pd.period_range(df.index.min(), df.index.max(), freq="M")
df = df.reindex(full)
prai = np.log(df["mb"] + df["sk"])
atl = np.log(df["ns"] + df["nb"] + df["nl"] + df["pe"])
g = pd.DataFrame({"p": prai - prai.shift(12), "a": atl - atl.shift(12)})
g["year"] = g.index.year
g["base_year"] = (g.index - 12).year

def analyse(mask, label):
    d = g[mask].dropna()
    rx = stats.rankdata(d["p"]); ry = stats.rankdata(d["a"])
    rho = stats.spearmanr(d["p"], d["a"]).statistic
    n = len(d)
    # Pyper-Peterman effective n on the ranks, using lag autocorrelations within contiguous runs
    idx = d.index
    def acf(x, k):
        s = pd.Series(x - x.mean(), index=idx)
        lagged = s.reindex(idx - k)
        lagged.index = idx
        m = lagged.notna()
        return float((s[m] * lagged[m]).sum() / (s ** 2).sum())
    K = n // 5
    inv = 1 / n + (2 / n) * sum(((n - k) / n) * acf(rx, k) * acf(ry, k) for k in range(1, K + 1))
    neff = max(3.0, min(n, 1 / inv))
    t = rho * np.sqrt((neff - 2) / (1 - rho ** 2))
    p_pp = 2 * stats.t.sf(abs(t), neff - 2)
    # block permutation: shuffle 12-month blocks of the Atlantic series, preserve within-block autocorrelation
    a = d["a"].to_numpy(); pv = d["p"].to_numpy()
    B = 12
    blocks = [np.arange(i, min(i + B, n)) for i in range(0, n, B)]
    R = 20000; cnt = 0
    for _ in range(R):
        order = rng.permutation(len(blocks))
        perm = np.concatenate([blocks[j] for j in order])
        r = stats.spearmanr(pv, a[perm]).statistic
        if abs(r) >= abs(rho):
            cnt += 1
    p_block = (cnt + 1) / (R + 1)
    return {"label": label, "n": n, "rho": round(float(rho), 4), "n_eff": round(float(neff), 2),
            "p_pyper_peterman": float(p_pp), "p_block_perm_12m": float(p_block)}

main = analyse(~g["year"].isin([2020, 2021]), "exclude growth months dated 2020-2021")
strict = analyse(~g["year"].isin([2020, 2021]) & ~g["base_year"].isin([2020, 2021]),
                 "also exclude months whose 12-month base is in 2020-2021")
allm = analyse(g["year"].notna(), "all months (reference)")
p_main = max(main["p_pyper_peterman"], main["p_block_perm_12m"])
falsified = main["rho"] < 0.5 or p_main >= 0.005
print(json.dumps({"verdict": "falsified" if falsified else "survived",
    "method": "Spearman rho of 12-month log growth, Prairies (mb+sk) vs Atlantic (ns+nb+nl+pe), growth months in 2020-2021 dropped; "
              "autocorrelation-aware p = max(Pyper-Peterman effective-n t-test on ranks, 12-month block permutation)",
    "rho": main["rho"], "n": main["n"], "n_eff": main["n_eff"], "p_used": p_main,
    "main": main, "sensitivity_base_also_excluded": strict, "reference_all_months": allm}))
