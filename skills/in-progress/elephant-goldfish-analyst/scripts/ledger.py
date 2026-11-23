#!/usr/bin/env python3
"""Append-only evidence ledger for elephant-goldfish data analysis.

Every insight must pass through: register (frozen test, before any confirmatory
look) -> run (on the holdout) -> replay (byte-identical) -> goldfish (a
fresh-context agent's independent test agrees). `report` derives each claim's
status from the ledger alone, so every number is traceable to an entry.

Stdlib only. Test scripts read env DATA (csv path) and SEED, and must print one
final line of JSON: {"verdict": "survived"|"falsified", ...any metrics}.
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
    return m


def find(kind, hid):
    return [e for e in entries() if e["kind"] == kind and e.get("id") == hid]


def execute(script, data, seed):
    env = {**os.environ, "DATA": str(data), "SEED": str(seed), "PYTHONHASHSEED": "0"}
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
    rng = random.Random(a.seed)
    idx = list(range(len(body)))
    rng.shuffle(idx)
    cut = int(len(idx) * a.explore_fraction)
    for name, part in (("explore", idx[:cut]), ("holdout", idx[cut:])):
        with open(WS / f"{name}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(body[i] for i in sorted(part))
    e = append("init", source=str(a.data), source_sha=sha(a.data), seed=a.seed, rows=len(body),
               columns=header, explore_rows=cut, holdout_rows=len(body) - cut,
               explore_sha=sha(WS / "explore.csv"), holdout_sha=sha(WS / "holdout.csv"))
    print(f"workspace {WS}: explore={cut} rows, holdout={len(body) - cut} rows, seed={a.seed}")
    print(f"elephant: explore on {WS}/explore.csv only. holdout is sealed for registered tests.")
    return e


def cmd_register(a):
    check_data()
    if find("register", a.id):
        die(f"{a.id} already registered; claims are immutable, register a new id")
    append("register", id=a.id, claim=a.claim, prediction=a.prediction, falsify_if=a.falsify_if,
           test=str(a.test), test_sha=sha(a.test))
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
           result=result, agrees=agrees, stdout_sha=out_sha)
    print(f"{a.id}: goldfish {a.agent} says {result['verdict']} -> {'AGREES' if agrees else 'DISAGREES'}")


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
    return "established" if base == "survived" else "refuted"


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
             "every figure below cites the ledger entry it came from.", "",
             "| id | status | claim | falsified if | holdout result | goldfish |", "|---|---|---|---|---|---|"]
    for r in [e for e in entries() if e["kind"] == "register"]:
        run = find("run", r["id"])
        res = f"`#{run[0]['seq']}` " + ", ".join(f"{k}={v}" for k, v in run[0]["result"].items() if k != "verdict") if run else ""
        fish = "; ".join(f"`#{g['seq']}` {g['result']['verdict']}" for g in find("goldfish", r["id"]))
        lines.append(f"| {r['id']} | **{status(r['id'])}** | {r['claim']} | {r['falsify_if']} | {res} | {fish} |")
    lines += ["", "Statuses: **established** = survived holdout, replayed byte-identical, every goldfish agrees. "
              "**refuted** = falsified and confirmed the same way. Anything else is not yet an insight."]
    out = WS / "INSIGHTS.md"
    out.write_text("\n".join(lines) + "\n")
    print(out.read_text())


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    i = s.add_parser("init"); i.add_argument("data"); i.add_argument("--seed", type=int, default=20261123)
    i.add_argument("--explore-fraction", type=float, default=0.5)
    r = s.add_parser("register"); r.add_argument("id"); r.add_argument("--claim", required=True)
    r.add_argument("--prediction", required=True); r.add_argument("--falsify-if", required=True)
    r.add_argument("--test", required=True)
    for n in ("run", "replay"):
        s.add_parser(n).add_argument("id")
    g = s.add_parser("goldfish"); g.add_argument("id"); g.add_argument("--test", required=True)
    g.add_argument("--agent", default="goldfish-1")
    s.add_parser("verify"); s.add_parser("report")
    a = p.parse_args()
    globals()[f"cmd_{a.cmd}"](a)


if __name__ == "__main__":
    main()
