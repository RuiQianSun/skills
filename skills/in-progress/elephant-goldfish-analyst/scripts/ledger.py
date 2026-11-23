#!/usr/bin/env python3
"""Append-only evidence ledger for elephant-goldfish data analysis.

Every insight must pass through: register (frozen test, before any confirmatory
look) -> run (on the holdout) -> replay (byte-identical) -> goldfish (a
fresh-context agent's independent test agrees). For time series, `extend` seals
newly published rows as a fresh window and `retest` reruns frozen tests on it, so
claims keep facing data nobody had when they were made. `report` derives each
claim's status from the ledger alone, so every number is traceable to an entry.

Stdlib only. Test scripts read env DATA (csv path) and SEED, and must print one
final line of JSON: {"verdict": "survived"|"falsified", ...any metrics}. A test
that will be retested also reads env SCORE_FROM (absent = score every row): it
scores only rows whose order key is >= SCORE_FROM, uses earlier rows as history
only, and echoes "scored_from": SCORE_FROM (or null) in its JSON.
"""
import argparse, csv, hashlib, json, os, random, subprocess, sys, time
from pathlib import Path

WS = Path(os.environ.get("EG_WORKSPACE", "analysis"))
LEDGER = WS / "LEDGER.jsonl"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def entries():
    if not LEDGER.exists():
        return []
    return [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()]


def append(kind, **data):
    prev = entries()
    prev_hash = prev[-1]["hash"] if prev else "0" * 64
    body = {"seq": len(prev), "kind": kind, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **data, "prev": prev_hash}
    body["hash"] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    with LEDGER.open("a") as f:
        f.write(json.dumps(body, sort_keys=True) + "\n")
    return body


def die(msg):
    sys.exit(f"ledger: {msg}")


def meta():
    m = [e for e in entries() if e["kind"] == "init"]
    if not m:
        die("no workspace; run `init` first")
    return m[0]


def check_data():
    m = meta()
    for name in ("explore", "holdout"):
        if sha(WS / f"{name}.csv") != m[f"{name}_sha"]:
            die(f"{name}.csv changed since init; the evidence is void")
    ext = [e for e in entries() if e["kind"] == "extend"]
    if ext and sha(WS / "fresh.csv") != ext[-1]["fresh_sha"]:
        die("fresh.csv changed since the last extend; the evidence is void")
    return m


def month_key(k):
    """'2025-10' or '2025-10-01' -> 2025*12+9; anything else -> None."""
    parts = k.split("-")
    if len(parts) in (2, 3) and parts[0].isdigit() and parts[1].isdigit() and (len(parts) == 2 or parts[2] == "01"):
        return int(parts[0]) * 12 + int(parts[1]) - 1
    return None


def audit(header, body, order_by):
    """Data contract checked before anything is sealed: gaps, duplicates, empty cells."""
    report = {"empty_cells": {h: sum(1 for r in body if r[i].strip() in ("", ".", "NA", "nan")) for i, h in enumerate(header)}}
    report["empty_cells"] = {k: v for k, v in report["empty_cells"].items() if v}
    if order_by:
        col = header.index(order_by)
        keys = [r[col] for r in body]
        report["duplicate_keys"] = sorted({k for k in keys if keys.count(k) > 1})
        mk = sorted({month_key(k) for k in keys} - {None})
        if mk and len(mk) == len(set(keys)):
            have = set(mk)
            report["missing_months"] = [f"{m // 12}-{m % 12 + 1:02d}" for m in range(mk[0], mk[-1] + 1) if m not in have]
    return report


def audit_problems(rep):
    return {k: v for k, v in rep.items() if k in ("duplicate_keys", "missing_months") and v}


def find(kind, hid):
    return [e for e in entries() if e["kind"] == kind and e.get("id") == hid]


def execute(script, data, seed, extra_env=None):
    env = {**os.environ, "DATA": str(data), "SEED": str(seed), "PYTHONHASHSEED": "0", **(extra_env or {})}
    p = subprocess.run([sys.executable, "-I", str(script)], capture_output=True, text=True, env=env, timeout=600)
    if p.returncode != 0:
        die(f"{script} failed:\n{p.stderr}")
    last = [l for l in p.stdout.strip().splitlines() if l.strip()][-1]
    result = json.loads(last)
    if result.get("verdict") not in ("survived", "falsified"):
        die('final JSON line needs "verdict": "survived" | "falsified"')
    return result, hashlib.sha256(p.stdout.encode()).hexdigest()


def cmd_init(a):
    if LEDGER.exists():
        die(f"{LEDGER} already exists")
    WS.mkdir(parents=True, exist_ok=True)
    with open(a.data, newline="") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]
    rep = audit(header, body, a.order_by)
    if audit_problems(rep) and not a.allow_gaps:
        WS.rmdir() if not any(WS.iterdir()) else None
        die(f"data audit failed, nothing sealed: {json.dumps(audit_problems(rep))}\n"
            "fix the source (a dropped row turns every 12-row lag into a 13-month one), "
            "or pass --allow-gaps to seal it anyway with the defect recorded")
    idx = list(range(len(body)))
    if a.order_by:  # time series: explore the past, confirm on the future
        col = header.index(a.order_by)
        idx.sort(key=lambda i: body[i][col])
    else:
        random.Random(a.seed).shuffle(idx)
    cut = int(len(idx) * a.explore_fraction)
    for name, part in (("explore", idx[:cut]), ("holdout", idx[cut:])):
        with open(WS / f"{name}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(body[i] for i in sorted(part))
    e = append("init", source=str(a.data), source_sha=sha(a.data), seed=a.seed, rows=len(body),
               columns=header, split=f"ordered by {a.order_by}" if a.order_by else "random",
               explore_until=body[idx[cut - 1]][header.index(a.order_by)] if a.order_by else None, explore_rows=cut, holdout_rows=len(body) - cut,
               explore_sha=sha(WS / "explore.csv"), holdout_sha=sha(WS / "holdout.csv"),
               order_by=a.order_by, audit=rep, holdout_budget=a.budget)
    print(f"workspace {WS}: explore={cut} rows, holdout={len(body) - cut} rows, seed={a.seed}")
    print(f"elephant: explore on {WS}/explore.csv only. holdout is sealed for registered tests.")
    if rep["empty_cells"]:
        print(f"note: empty cells {rep['empty_cells']}")
    if a.budget:
        print(f"holdout budget: {a.budget} confirmatory looks")
    return e


def cmd_register(a):
    check_data()
    if find("register", a.id):
        die(f"{a.id} already registered; claims are immutable, register a new id")
    append("register", id=a.id, claim=a.claim, prediction=a.prediction, falsify_if=a.falsify_if,
           decision=a.decision, min_fresh=a.min_fresh, test=str(a.test), test_sha=sha(a.test),
           review=str(a.review) if a.review else None, review_sha=sha(a.review) if a.review else None)
    print(f"{a.id} registered; test frozen at {sha(a.test)[:12]}")


def cmd_run(a):
    m = check_data()
    reg = find("register", a.id)
    if not reg:
        die(f"{a.id} is not registered")
    if find("run", a.id):
        die(f"{a.id} already ran on the holdout; one confirmatory look per claim")
    reg = reg[0]
    if sha(reg["test"]) != reg["test_sha"]:
        die(f"{reg['test']} changed after registration; register a new id instead")
    used = len([e for e in entries() if e["kind"] == "run"])
    if m.get("holdout_budget") and used >= m["holdout_budget"]:
        die(f"holdout budget spent ({used}/{m['holdout_budget']}); wait for fresh data and use `retest`")
    result, out_sha = execute(reg["test"], WS / "holdout.csv", m["seed"])
    append("run", id=a.id, result=result, stdout_sha=out_sha)
    print(f"{a.id}: {result['verdict']}  {json.dumps(result)}")


def cmd_replay(a):
    m = check_data()
    reg, run = find("register", a.id), find("run", a.id)
    if not run:
        die(f"{a.id} has not run")
    reg, run = reg[0], run[0]
    if sha(reg["test"]) != reg["test_sha"]:
        die(f"{reg['test']} changed after registration")
    result, out_sha = execute(reg["test"], WS / "holdout.csv", m["seed"])
    same = out_sha == run["stdout_sha"]
    append("replay", id=a.id, identical=same, stdout_sha=out_sha)
    print(f"{a.id}: replay {'IDENTICAL' if same else 'DIVERGED'}")


def cmd_goldfish(a):
    m = check_data()
    run = find("run", a.id)
    if not run:
        die(f"{a.id} has not run")
    result, out_sha = execute(a.test, WS / "holdout.csv", m["seed"])
    agrees = result["verdict"] == run[0]["result"]["verdict"]
    append("goldfish", id=a.id, agent=a.agent, test=str(a.test), test_sha=sha(a.test),
           result=result, agrees=agrees, stdout_sha=out_sha, narrowed=a.narrowed)
    print(f"{a.id}: goldfish {a.agent} says {result['verdict']} -> {'AGREES' if agrees else 'DISAGREES'}"
          + (f" (narrowed: {a.narrowed})" if a.narrowed else ""))


def cmd_extend(a):
    m = check_data()
    if not m.get("order_by"):
        die("extend needs a workspace initialised with --order-by")
    with open(a.data, newline="") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]
    if header != m["columns"]:
        die("new file's columns differ from the sealed data")
    col = header.index(m["order_by"])
    sealed = {}
    for name in ("explore", "holdout"):
        with open(WS / f"{name}.csv", newline="") as f:
            for r in list(csv.reader(f))[1:]:
                sealed[r[col]] = r
    last = max(sealed)
    revised = sorted(r[col] for r in body if r[col] in sealed and r != sealed[r[col]])
    fresh = sorted((r for r in body if r[col] > last), key=lambda r: r[col])
    if not fresh:
        die(f"no rows after {last}; nothing to extend")
    rep = audit(header, fresh, m["order_by"])
    if audit_problems(rep):
        die(f"fresh rows fail the audit: {json.dumps(audit_problems(rep))}")
    with open(WS / "fresh.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(fresh)
    append("extend", source=str(a.data), source_sha=sha(a.data), fresh_from=fresh[0][col], fresh_to=fresh[-1][col],
           fresh_rows=len(fresh), fresh_sha=sha(WS / "fresh.csv"), revised_rows=len(revised), revised_sample=revised[:12])
    print(f"fresh window {fresh[0][col]}..{fresh[-1][col]} ({len(fresh)} rows); {len(revised)} sealed rows revised at source"
          + (" (sealed copies kept; see revised_sample)" if revised else ""))


def cmd_retest(a):
    m = check_data()
    ext = [e for e in entries() if e["kind"] == "extend"]
    if not ext:
        die("no fresh window; run `extend` first")
    x = ext[-1]
    window = f"{x['fresh_from']}..{x['fresh_to']}"
    # history + fresh rows, so lagged tests have context; SCORE_FROM says where scoring starts
    col = m["columns"].index(m["order_by"])
    rows = []
    for name in ("explore", "holdout", "fresh"):
        with open(WS / f"{name}.csv", newline="") as f:
            rows += list(csv.reader(f))[1:]
    with open(WS / "retest.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(m["columns"])
        w.writerows(sorted(rows, key=lambda r: r[col]))
    ids = [e["id"] for e in entries() if e["kind"] == "run"] if a.id == "all" else [a.id]

    def pending(hid, why):
        append("retest", id=hid, window=window, pending=why)
        print(f"{hid}: pending ({why})")

    for hid in ids:
        reg = find("register", hid)[0]
        if sha(reg["test"]) != reg["test_sha"]:
            die(f"{reg['test']} changed after registration")
        need = reg.get("min_fresh") or 0
        if x["fresh_rows"] < need:
            pending(hid, f"{x['fresh_rows']} of {need} fresh rows needed")
            continue
        try:
            result, out_sha = execute(reg["test"], WS / "retest.csv", m["seed"], {"SCORE_FROM": x["fresh_from"]})
        except SystemExit as err:
            pending(hid, "test could not run: " + str(err)[-200:])
            continue
        if result.get("scored_from") != x["fresh_from"]:
            pending(hid, "test does not honour SCORE_FROM, so it would score sealed rows too")
            continue
        if any(isinstance(v, float) and v != v for v in result.values()):
            pending(hid, "test returned NaN: too little fresh data to score")
            continue
        held = result["verdict"] == find("run", hid)[0]["result"]["verdict"]
        append("retest", id=hid, window=window, result=result, held=held, stdout_sha=out_sha)
        print(f"{hid}: fresh {result['verdict']} -> {'HELD' if held else 'BROKE'}  {json.dumps(result)}")


def status(hid):
    run = find("run", hid)
    if not run:
        return "registered"
    if run[0]["result"]["verdict"] == "falsified":
        base = "falsified"
    else:
        base = "survived"
    reps, fish = find("replay", hid), find("goldfish", hid)
    if not reps or not all(r["identical"] for r in reps):
        return f"{base} (unreplayed)" if not reps else "not repeatable"
    if not fish:
        return f"{base} (no goldfish yet)"
    if not all(g["agrees"] for g in fish):
        return "contested"
    st = "established" if base == "survived" else "refuted"
    if any(g.get("narrowed") for g in fish):
        st += " (narrowed)"
    rt = [r for r in find("retest", hid) if "held" in r]
    if rt:
        st += ", held on fresh data" if rt[-1]["held"] else ", BROKE on fresh data"
    return st


def cmd_verify(a):
    es = entries()
    prev = "0" * 64
    for e in es:
        h = e.pop("hash")
        if e["prev"] != prev or hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest() != h:
            die(f"chain broken at seq {e['seq']}")
        prev = h
    check_data()
    print(f"ledger intact: {len(es)} entries, head {prev[:12]}")


def cmd_report(a):
    m = meta()
    lines = [f"# Insights: {m['source']}", "",
             f"Source sha256 `{m['source_sha'][:12]}`, {m['rows']} rows, split seed {m['seed']} "
             f"({m['explore_rows']} explore / {m['holdout_rows']} holdout). Generated from `{LEDGER}`; "
             "every figure below cites the ledger entry it came from.", ""]
    runs = len([e for e in entries() if e["kind"] == "run"])
    lines.append(f"Holdout looks: {runs}" + (f" of a budget of {m['holdout_budget']}." if m.get("holdout_budget") else " (no budget set)."))
    if m.get("audit"):
        lines.append(f"Data audit at seal: {json.dumps(m['audit'])}.")
    ext = [e for e in entries() if e["kind"] == "extend"]
    if ext:
        lines.append(f"Fresh window: {ext[-1]['fresh_from']}..{ext[-1]['fresh_to']} ({ext[-1]['fresh_rows']} rows, "
                     f"`#{ext[-1]['seq']}`); {ext[-1]['revised_rows']} sealed rows revised at source.")
    lines += ["", "| id | status | claim | decision it informs | falsified if | holdout result | goldfish | fresh data |",
              "|---|---|---|---|---|---|---|---|"]
    for r in [e for e in entries() if e["kind"] == "register"]:
        run = find("run", r["id"])
        res = f"`#{run[0]['seq']}` " + ", ".join(f"{k}={v}" for k, v in run[0]["result"].items() if k != "verdict") if run else ""
        fish = "; ".join(f"`#{g['seq']}` {g['result']['verdict']}" + (f" (narrowed: {g['narrowed']})" if g.get("narrowed") else "")
                         for g in find("goldfish", r["id"]))
        rt = find("retest", r["id"])
        fr = ""
        if rt:
            x = rt[-1]
            fr = f"`#{x['seq']}` {x['window']}: " + (f"pending ({x['pending']})" if "pending" in x else
                 x["result"]["verdict"] + ", " + ", ".join(f"{k}={v}" for k, v in x["result"].items() if k != "verdict"))
        if not r.get("review") and "decision" in r:
            fish += " (claim not reviewed before registration)"
        lines.append(f"| {r['id']} | **{status(r['id'])}** | {r['claim']} | {r.get('decision') or ''} | {r['falsify_if']} | {res} | {fish} | {fr} |")
    lines += ["", "Statuses: **established** = survived holdout, replayed byte-identical, every goldfish agrees. "
              "**refuted** = falsified and confirmed the same way. **(narrowed)** = a goldfish found the claim holds only in a "
              "narrower reading; quote the narrowed version. **held / BROKE on fresh data** = the frozen test rerun on rows "
              "published after the seal. Anything else is not yet an insight."]
    out = WS / "INSIGHTS.md"
    out.write_text("\n".join(lines) + "\n")
    print(out.read_text())


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    i = s.add_parser("init"); i.add_argument("data"); i.add_argument("--seed", type=int, default=20261123)
    i.add_argument("--explore-fraction", type=float, default=0.5)
    i.add_argument("--order-by", help="column to sort by for a time split (explore earliest rows, hold out the latest)")
    i.add_argument("--budget", type=int, help="max confirmatory looks at the holdout across all claims")
    i.add_argument("--allow-gaps", action="store_true", help="seal despite gaps or duplicate keys (recorded)")
    r = s.add_parser("register"); r.add_argument("id"); r.add_argument("--claim", required=True)
    r.add_argument("--prediction", required=True); r.add_argument("--falsify-if", required=True)
    r.add_argument("--test", required=True)
    r.add_argument("--decision", required=True, help="the decision this claim would change if it holds")
    r.add_argument("--min-fresh", type=int, help="fresh rows needed before `retest` may judge this claim")
    r.add_argument("--review", help="the critic goldfish's review of this claim, saved before registering")
    for n in ("run", "replay"):
        s.add_parser(n).add_argument("id")
    g = s.add_parser("goldfish"); g.add_argument("id"); g.add_argument("--test", required=True)
    g.add_argument("--agent", default="goldfish-1")
    g.add_argument("--narrowed", help="the narrower reading under which the goldfish found the claim holds")
    s.add_parser("extend").add_argument("data")
    s.add_parser("retest").add_argument("id", help="a claim id, or `all`")
    s.add_parser("verify"); s.add_parser("report")
    a = p.parse_args()
    globals()[f"cmd_{a.cmd}"](a)


if __name__ == "__main__":
    main()
