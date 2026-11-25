"""Generate sample assortment data: one row per store x SKU that was recommended or carried.

Story: an assortment engine recommended SKUs per store from a demand forecast; planners
kept most recommendations, dropped some and added their own picks. One buy per
store-SKU at the start of a 12-week season, no replenishment. Every number is synthetic.
Writes assortment.json as {rows, meta}, with this script's text in meta.
"""
import json
import math
import random
import sys
from pathlib import Path

random.seed(11)
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
CODE = Path(__file__).read_text()
WEEKS = 12

CITIES = ["Ashford", "Bayview", "Cedar Park", "Dunmore", "Eastgate", "Fairhaven", "Glenwood", "Harbor Point",
          "Ironbridge", "Juniper", "Kingsley", "Lakeside", "Maple Grove", "Northfield", "Oakridge", "Pinecrest",
          "Queensway", "Riverbend", "Stonebrook", "Tidewater", "Union Square", "Valley Mall", "Westbrook", "Yarrow",
          "Alder", "Brookside", "Coral Bay", "Desert Springs", "Elm Street", "Foxhill", "Granite Falls", "Highland",
          "Ivy Lane", "Jasper", "Kestrel", "Linden", "Mesa Verde", "Newport", "Orchard", "Palm Shores"]
CLUSTERS = [("Urban flagship", "A", 8, 1.6), ("Suburban", "B", 16, 1.0), ("Value outlet", "C", 8, 0.8),
            ("Warm climate", "B", 8, 0.95)]
CAPACITY = {"A": 112, "B": 88, "C": 72}
CATEGORIES = {"Tops": 40, "Bottoms": 30, "Outerwear": 25, "Footwear": 25, "Accessories": 30}
PRICE = {"Good": (19, 39), "Better": (39, 79), "Best": (79, 189)}
WORDS = {"Tops": ["Linen tee", "Oxford shirt", "Merino crew", "Rib tank", "Poplin blouse", "Waffle henley", "Boxy tee", "Silk cami"],
         "Bottoms": ["Straight jean", "Wide trouser", "Chino", "Cargo pant", "Pleated skirt", "Jogger"],
         "Outerwear": ["Chore jacket", "Puffer vest", "Wool coat", "Rain shell", "Quilted liner"],
         "Footwear": ["Court sneaker", "Chelsea boot", "Loafer", "Trail runner", "Slide"],
         "Accessories": ["Canvas tote", "Knit beanie", "Leather belt", "Silk scarf", "Crossbody bag", "Wool scarf"]}
COLORS = ["Ink", "Oat", "Moss", "Rust", "Slate", "Bone", "Clay", "Navy", "Olive", "Sand"]

# Stores
stores = []
n = 0
for cname, grade, count, traffic in CLUSTERS:
    for _ in range(count):
        n += 1
        stores.append({"id": f"S{n:03d}", "name": CITIES[n - 1], "cluster": cname, "grade": grade,
                       "traffic": traffic * math.exp(random.gauss(0, 0.18))})

# SKUs
skus = []
k = 0
for cat, count in CATEGORIES.items():
    for i in range(count):
        k += 1
        tier = random.choices(["Good", "Better", "Best"], [0.35, 0.45, 0.2])[0]
        lo, hi = PRICE[tier]
        skus.append({"sku": f"{cat[:2].upper()}-{k:03d}",
                     "name": f"{random.choice(WORDS[cat])}, {random.choice(COLORS)}",
                     "category": cat, "tier": tier, "price": round(random.uniform(lo, hi)) - 0.01,
                     "appeal": math.exp(random.gauss(0, 0.45))})


def affinity(store, sku):
    a = 1.0
    if sku["tier"] == "Best":
        a *= {"Urban flagship": 1.5, "Value outlet": 0.45}.get(store["cluster"], 1.0)
    if sku["tier"] == "Good":
        a *= {"Value outlet": 1.4, "Urban flagship": 0.75}.get(store["cluster"], 1.0)
    if sku["category"] == "Outerwear" and store["cluster"] == "Warm climate":
        a *= 0.35
    if sku["category"] == "Footwear" and store["cluster"] == "Urban flagship":
        a *= 1.25
    return a


BASE = {"Tops": 22, "Bottoms": 16, "Outerwear": 11, "Footwear": 10, "Accessories": 14}
# Weekly demand shape: fashion decays, outerwear builds into the season.
def shape(cat):
    if cat == "Outerwear":
        w = [0.5 + 0.12 * i for i in range(WEEKS)]
    else:
        w = [math.exp(-0.07 * i) for i in range(WEEKS)]
    s = sum(w)
    return [x / s for x in w]


rows = []
for st in stores:
    cand = []
    for sk in skus:
        true = BASE[sk["category"]] * st["traffic"] * sk["appeal"] * affinity(st, sk) * math.exp(random.gauss(0, 0.2))
        forecast = true * math.exp(random.gauss(0, 0.25))
        planner_view = true * math.exp(random.gauss(0, 0.6)) * (1.35 if sk["tier"] == "Best" else 1.0)
        cand.append((sk, true, forecast, planner_view))
    cap = CAPACITY[st["grade"]]
    rec = sorted(cand, key=lambda c: -c[2])[:cap]
    rec_ids = {c[0]["sku"] for c in rec}
    decisions = {}
    for c in rec:
        decisions[c[0]["sku"]] = "Dropped by planner" if random.random() < 0.08 else "Recommended, kept"
    pool = sorted((c for c in cand if c[0]["sku"] not in rec_ids), key=lambda c: -c[3])[:30]
    for c in random.sample(pool, 10):
        decisions[c[0]["sku"]] = "Added by planner"
    for sk, true, forecast, planner_view in cand:
        dec = decisions.get(sk["sku"])
        if not dec:
            continue
        if dec == "Recommended, kept":
            received = max(6, round(forecast * 1.2))
        elif dec == "Added by planner":
            received = max(6, round(planner_view * 1.2))
        else:
            received = 0
        on_hand, sold_cum, cum, stockout, lost = received, 0, [], 0, 0.0
        for w, f in enumerate(shape(sk["category"])):
            want = true * f * math.exp(random.gauss(0, 0.15))
            sell = min(on_hand, round(want))
            if received and want - sell >= 1:
                stockout += 1
                lost += want - sell
            on_hand -= sell
            sold_cum += sell
            cum.append(sold_cum)
        if not received:
            cum = [0] * WEEKS
        rows.append({
            "store_id": st["id"], "store": st["name"], "cluster": st["cluster"], "grade": st["grade"],
            "sku": sk["sku"], "sku_name": sk["name"], "category": sk["category"], "tier": sk["tier"],
            "price": sk["price"], "decision": dec,
            "forecast_units": round(forecast, 1), "received_units": received, "sold_units": sold_cum,
            "on_hand": on_hand, "stockout_weeks": stockout, "est_lost_units": round(lost, 1),
            "revenue": round(sold_cum * sk["price"], 2),
            **{f"sold_w{w + 1:02d}": c for w, c in enumerate(cum)},
        })

meta = [{"label": "gen_assortment.py", "value": CODE, "type": "code", "lang": "python"},
        {"label": "Input", "value": "None: synthetic, random seed 11"}]
(OUT / "assortment.json").write_text(json.dumps({"rows": rows, "meta": meta}, separators=(",", ":")))

# Quick summary for the author.
from collections import defaultdict
agg = defaultdict(lambda: [0, 0, 0])
for r in rows:
    a = agg[r["decision"]]; a[0] += r["received_units"]; a[1] += r["sold_units"]; a[2] += 1
for d, (rec_u, sold, cnt) in agg.items():
    print(f"{d:22s} rows={cnt:5d} received={rec_u:7d} sold={sold:7d} ST={sold / rec_u if rec_u else 0:.1%}")
print(len(rows), "rows")
