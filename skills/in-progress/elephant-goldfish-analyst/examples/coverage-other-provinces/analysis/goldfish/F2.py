import os, json, random, csv

path = os.environ["DATA"]
rng = random.Random(int(os.environ["SEED"]))
provs = ["ns", "nb", "nl", "pe"]
THRESH = 0.75

rows = {}
with open(path) as f:
    for r in csv.DictReader(f):
        rows[r["month"]] = r

def val(m, p):
    r = rows.get(m)
    if r is None or r[p] in ("", None):
        return None
    try:
        return float(r[p])
    except ValueError:
        return None

years = sorted({m[:4] for m in rows})
res = {}
falsified = False
for p in provs:
    comps = []
    for y in years:
        o, n = val(f"{y}-10", p), val(f"{y}-11", p)
        if o is not None and n is not None:
            comps.append({"year": y, "oct": o, "nov": n, "hit": n > o})
    hits = [c["hit"] for c in comps]
    k, N = sum(hits), len(hits)
    rate = k / N if N else None
    # bootstrap over years for context on precision of the rate
    boots = []
    for _ in range(5000):
        s = [hits[rng.randrange(N)] for _ in range(N)]
        boots.append(sum(s) / N)
    boots.sort()
    res[p] = {
        "hits": k, "years": N, "hit_rate": round(rate, 4) if rate is not None else None,
        "miss_years": [c["year"] for c in comps if not c["hit"]],
        "median_nov_over_oct_pct": round(sorted((c["nov"] / c["oct"] - 1) * 100 for c in comps)[N // 2], 2),
        "boot95": [round(boots[int(0.025 * len(boots))], 3), round(boots[int(0.975 * len(boots)) - 1], 3)],
    }
    if rate is None or rate < THRESH:
        falsified = True

print(json.dumps({
    "verdict": "falsified" if falsified else "survived",
    "method": "per-province count of years with Nov > Oct (strict), hit rate vs 0.75 threshold; bootstrap-over-years 95% CI reported for context only",
    "threshold": THRESH,
    "provinces": res,
}))
