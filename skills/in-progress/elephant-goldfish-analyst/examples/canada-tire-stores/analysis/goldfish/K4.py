import os, json, csv, random

random.seed(int(os.environ["SEED"]))
rows = list(csv.DictReader(open(os.environ["DATA"])))
rows.sort(key=lambda r: r["month"])
months = [r["month"] for r in rows]
y = [float(r["canada"]) for r in rows]

# Check contiguity of months
def idx(m):
    a, b = m.split("-"); return int(a) * 12 + int(b) - 1
gaps = [months[i] for i in range(1, len(months)) if idx(months[i]) - idx(months[i-1]) != 1]

# One-step-ahead forecasts for month t, using only data through t-1.
# seasonal naive: y[t-12]
# drift: y[t-12] * sum(y[t-12..t-1]) / sum(y[t-24..t-13])  (trailing 12m YoY growth)
ape_d, ape_s, used = [], [], []
for t in range(24, len(y)):
    g = sum(y[t-12:t]) / sum(y[t-24:t-12])
    fd = y[t-12] * g
    fs = y[t-12]
    ape_d.append(abs(y[t] - fd) / abs(y[t]))
    ape_s.append(abs(y[t] - fs) / abs(y[t]))
    used.append(months[t])

n = len(ape_d)
mape_d = sum(ape_d) / n
mape_s = sum(ape_s) / n
diff = [a - b for a, b in zip(ape_d, ape_s)]
wins = sum(1 for d in diff if d < 0)

# Moving-block bootstrap of mean APE difference (block length 12) for robustness
B, L = 5000, 12
boots = []
for _ in range(B):
    s = []
    while len(s) < n:
        st = random.randrange(0, n - L + 1)
        s.extend(diff[st:st+L])
    s = s[:n]
    boots.append(sum(s) / n)
boots.sort()
ci = [boots[int(0.025*B)], boots[int(0.975*B)]]
p_not_better = sum(1 for b in boots if b >= 0) / B

# Sensitivity: excluding 2020-03..2021-12 COVID-disrupted targets
keep = [i for i, m in enumerate(used) if not ("2020-03" <= m <= "2021-12")]
mape_d_x = sum(ape_d[i] for i in keep) / len(keep)
mape_s_x = sum(ape_s[i] for i in keep) / len(keep)

falsified = mape_d > 0.07 or not (mape_d < mape_s)
print(json.dumps({
    "verdict": "falsified" if falsified else "survived",
    "method": "rolling one-step-ahead backtest on canada column: drift = y[t-12]*sum(y[t-12..t-1])/sum(y[t-24..t-13]) vs seasonal naive y[t-12]; MAPE over all targets with 24m history; block-bootstrap (L=12) CI on mean APE difference",
    "n_forecasts": n, "first_target": used[0], "last_target": used[-1],
    "mape_drift": round(mape_d, 5),
    "mape_seasonal_naive": round(mape_s, 5),
    "mape_diff_drift_minus_snaive": round(mape_d - mape_s, 5),
    "diff_ci95_block_bootstrap": [round(c, 5) for c in ci],
    "bootstrap_p_drift_not_better": round(p_not_better, 4),
    "months_drift_wins": wins,
    "excl_covid_2020_03_to_2021_12": {"n": len(keep), "mape_drift": round(mape_d_x, 5), "mape_seasonal_naive": round(mape_s_x, 5)},
    "month_gaps": gaps,
}))
