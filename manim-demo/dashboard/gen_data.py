"""Generate the sample traffic data for the Signal Explorer dashboard.

Writes daily.json (date x region x channel) and hourly.json (region x weekday x hour),
each as {rows, meta}, with this script's own text in meta so readers can rerun it.
Every number is synthetic.
"""
import json
import math
import random
import sys
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
CODE = Path(__file__).read_text()

START, DAYS = date(2024, 11, 26), 730
REGIONS = {"North America": 4200, "EMEA": 3100, "APAC": 2300}
CHANNELS = {"Organic search": 0.38, "Paid ads": 0.24, "Social": 0.14, "Email": 0.12, "Referral": 0.12}
CONV = {"Organic search": 0.031, "Paid ads": 0.024, "Social": 0.013, "Email": 0.048, "Referral": 0.039}
ARPU = {"North America": 54, "EMEA": 47, "APAC": 31}
BUDGET_CUT, APAC_LAUNCH, OUTAGE = date(2026, 3, 1), date(2026, 6, 15), date(2026, 7, 9)


def first_tuesday(d):
    return d.weekday() == 1 and d.day <= 7


rows = []
for i in range(DAYS):
    d = START + timedelta(days=i)
    years = i / 365
    weekend = d.weekday() >= 5
    holiday = d.month == 11 and 20 <= d.day <= 30
    for region, base in REGIONS.items():
        launched = region == "APAC" and d >= APAC_LAUNCH
        for ch, share in CHANNELS.items():
            v = base * share * (1 + 0.18 * years)
            if ch == "Social":
                v *= 1 + 0.6 * years
            if ch == "Paid ads" and d >= BUDGET_CUT:
                v *= 0.75
            if ch == "Email" and first_tuesday(d):
                v *= 1.8
            if holiday and ch in ("Paid ads", "Email"):
                v *= 1.35
            if launched:
                v *= 1.4
            if d == OUTAGE:
                v *= 0.45
            v *= (1.05 if ch == "Social" else 0.78) if weekend else 1.0
            v *= math.exp(random.gauss(0, 0.06))
            sessions = round(v)
            conv = CONV[ch] * (1.2 if launched else 1.0) * math.exp(random.gauss(0, 0.08))
            signups = round(sessions * conv)
            revenue = round(signups * ARPU[region] * math.exp(random.gauss(0, 0.05)), 2)
            rows.append({"date": d.isoformat(), "region": region, "channel": ch,
                         "sessions": sessions, "signups": signups, "revenue": revenue})

meta = [{"label": "gen_data.py", "value": CODE, "type": "code", "lang": "python"},
        {"label": "Input", "value": "None: synthetic, random seed 42"}]
(OUT / "daily.json").write_text(json.dumps({"rows": rows, "meta": meta}, separators=(",", ":")))

# Typical week: mean sessions per weekday-hour over the last 13 weeks, by region.
UTC_OFFSET = {"North America": -5, "EMEA": 1, "APAC": 8}
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
recent = [r for r in rows if r["date"] >= (START + timedelta(days=DAYS - 91)).isoformat()]
hourly = []
for region, off in UTC_OFFSET.items():
    daily_avg = sum(r["sessions"] for r in recent if r["region"] == region) / 91
    for wd, name in enumerate(WEEKDAYS):
        weekend = wd >= 5
        weights = []
        for h in range(24):
            local = (h + off) % 24
            morning = math.exp(-((local - (11 if weekend else 10)) ** 2) / 8)
            evening = math.exp(-((local - 20.5) ** 2) / 6) * (1.3 if weekend else 0.9)
            weights.append(0.06 + morning + evening)
        scale = daily_avg * (0.85 if weekend else 1.0) / sum(weights)
        for h, w in enumerate(weights):
            hourly.append({"region": region, "weekday": name, "weekday_index": wd, "hour_utc": h,
                           "sessions": round(w * scale * math.exp(random.gauss(0, 0.03)), 1)})
meta_h = [{"label": "gen_data.py", "value": CODE, "type": "code", "lang": "python"},
          {"label": "Input", "value": "daily.json rows from the last 13 weeks"}]
(OUT / "hourly.json").write_text(json.dumps({"rows": hourly, "meta": meta_h}, separators=(",", ":")))
print(len(rows), len(hourly))
