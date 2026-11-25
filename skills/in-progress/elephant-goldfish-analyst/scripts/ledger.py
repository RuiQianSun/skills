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

# category -> kind -> (what it claims, the evidence that can falsify it). Descriptive says what
# happened; the three inferential categories say why, what next, and what to do.
TYPES = {
    "descriptive": {
        "level": ("size or rate of a quantity over a period", "recomputed on the holdout; falsified by a magnitude threshold"),
        "trend": ("direction and pace of change over time", "slope sign and size with an autocorrelation-aware interval"),
        "seasonality": ("a recurring calendar pattern", "holds in a stated share of holdout cycles"),
        "composition": ("shares or mix across segments", "share thresholds that hold period by period"),
        "comparison": ("segment A differs from segment B", "effect size plus a test, and consistency across periods"),
        "distribution": ("spread, skew or concentration (Pareto)", "quantile or top-share thresholds"),
        "anomaly": ("a point or period far from its expected value", "deviation beyond k robust SDs of a baseline fit without it"),
        "change-point": ("a break in level or trend at a date", "a break test, with stability on both sides"),
    },
    "diagnostic": {
        "attribution": ("which components account for a change (mix vs rate, price vs volume, segments)", "the decomposition recomputed; falsified if another component dominates"),
        "driver": ("an outcome moves with a candidate driver", "an autocorrelation-aware null; reported as association, never cause"),
        "causal": ("an event or intervention changed the outcome", "a design (diff-in-diff, event study, discontinuity, experiment) plus a placebo that must come out null"),
        "root-cause": ("why a specific anomaly happened", "the explanation implies something else checkable, and that implication holds"),
    },
    "predictive": {
        "forecast": ("future values of a quantity", "out-of-time error beats a naive baseline; retested prospectively"),
        "leading-indicator": ("X now predicts Y later", "out-of-time gain over Y's own history"),
        "classification": ("which units or periods fall in a class", "out-of-sample accuracy or AUC beats the base rate"),
        "timing": ("when an event (a peak, a threshold crossing) will happen", "hit rate beats a naive timing rule"),
    },
    "prescriptive": {
        "policy": ("a rule (order, staff, price) beats the status quo", "backtested payoff against the stated status-quo rule, objective and costs stated"),
        "allocation": ("how to split a resource across segments", "backtested payoff against a proportional or naive split"),
        "trigger": ("act when a metric crosses a value", "backtested precision and recall against alternative triggers"),
    },
}
RESTS_ON = {"prescriptive": ("predictive", "diagnostic")}
FORWARD = ("predictive", "prescriptive")  # categories that must never peek at later rows
STAGES = list(TYPES)  # descriptive -> diagnostic -> predictive -> prescriptive, closed in order
ROLES = {
    "target": "dependent variable: the outcome the analysis explains or predicts",
    "feature": "independent variable: a candidate explanation or predictor",
    "time": "the order key for time series",
    "key": "an identifier; never a predictor",
    "segment": "a grouping used to slice results (can also be a feature)",
    "exclude": "unusable or leaky: recorded after the outcome, a duplicate of the target, or junk",
}

# Static checks on a test script: (code, regex, applies to, message). "error" blocks registration.
LINT = [
    ("centred-window", r"center\s*=\s*True", FORWARD, "centred rolling window reads future rows"),
    ("negative-shift", r"\.shift\(\s*(periods\s*=\s*)?-\s*\d", FORWARD, "negative shift pulls later rows backwards"),
    ("backfill", r"\.bfill\(|backfill|method\s*=\s*['\"]bfill", FORWARD, "backfill copies later values into earlier rows"),
    ("other-file", r"(read_csv|open|loadtxt|read_parquet)\(\s*[rf]?['\"]", None, "reads a hard-coded path; read only env DATA"),
    ("workspace-file", r"(explore|holdout|fresh|retest)\.csv", None, "names a workspace file; read only env DATA"),
]
LINT_WARN = [
    ("interpolate", r"\.interpolate\(", FORWARD, "interpolation can use later rows"),
    ("centred-window", r"center\s*=\s*True", ("descriptive", "diagnostic"), "centred window: fine for describing the past, never for a forecast"),
]


def lint(path, category, ordered, excluded=()):
    """Return (errors, warnings) as lists of 'code: message (line n)'."""
    import re
    src = Path(path).read_text()
    lines = src.splitlines()

    def scan(rules):
        hits = []
        for code, rx, cats, msg in rules:
            if cats and category not in cats:
                continue
            for n, line in enumerate(lines, 1):
                if re.search(rx, line.split("#")[0]):
                    hits.append(f"{code}: {msg} (line {n})")
        return hits

    errors, warnings = scan(LINT), scan(LINT_WARN)
    for col in excluded:  # a column the confirmed schema marks unusable or leaky
        rx = r"""(['"])""" + re.escape(col) + r"""\1|\.""" + re.escape(col) + r"\b"
        for n, line in enumerate(lines, 1):
            if re.search(rx, line.split("#")[0]):
                (errors if category in FORWARD else warnings).append(
                    f"excluded-column: uses {col!r}, which the schema excludes (line {n})")
    if ordered and "SCORE_FROM" not in src:
        errors.append("score-from: ordered workspace, but the test never reads env SCORE_FROM")
    if ordered and "scored_from" not in src:
        errors.append("scored-from: the JSON output must echo scored_from")
    if re.search(r"np\.random\.(rand|randn|choice|shuffle|permutation|normal|uniform)\(|\brandom\.(random|choice|shuffle|sample)\(", src) \
            and "SEED" not in src:
        errors.append("unseeded: draws random numbers without reading env SEED")
    return errors, warnings


# Mutants: copies of explore data with one structure destroyed. A test with teeth falsifies them.
def _complete(header, body):
    return [i for i, r in enumerate(body) if all(c.strip() not in ("", ".", "NA", "nan") for c in r)]


def mutate(spec, header, body, key, rng):
    name, _, arg = spec.partition(":")
    body = [list(r) for r in body]
    idx = _complete(header, body)  # leave rows with missing cells where they are
    kc = header.index(key) if key else None
    vals = [i for i in range(len(header)) if i != kc]
    if name == "shuffle-rows":  # destroys time order, trend and seasonality
        perm = idx[:]
        rng.shuffle(perm)
        src = {i: body[j][:] for i, j in zip(idx, perm)}
        for i in idx:
            for c in vals:
                body[i][c] = src[i][c]
    elif name in ("shuffle-months", "shuffle-years"):
        if kc is None:
            die(f"mutant {name} needs an ordered workspace")
        by_year = {}
        for i in idx:
            by_year.setdefault(body[i][kc][:4], []).append(i)
        if name == "shuffle-months":  # destroys within-year (seasonal) patterns, keeps annual totals
            for rows in by_year.values():
                perm = rows[:]
                rng.shuffle(perm)
                src = {i: body[j][:] for i, j in zip(rows, perm)}
                for i in rows:
                    for c in vals:
                        body[i][c] = src[i][c]
        else:  # destroys trend across years, keeps each year's seasonal shape
            years = [y for y, r in by_year.items() if len(r) == 12]
            perm = years[:]
            rng.shuffle(perm)
            src = {y: [body[i][:] for i in sorted(by_year[y], key=lambda i: body[i][kc])] for y in years}
            for y, z in zip(years, perm):
                for i, srow in zip(sorted(by_year[y], key=lambda i: body[i][kc]), src[z]):
                    for c in vals:
                        body[i][c] = srow[c]
    elif name == "permute":  # destroys one column's link to everything else
        if arg not in header:
            die(f"mutant permute:{arg}: no such column")
        c = header.index(arg)
        col = [body[i][c] for i in idx]
        rng.shuffle(col)
        for i, v in zip(idx, col):
            body[i][c] = v
    elif name == "swap":  # trades two columns' identities
        a, b = arg.split(",")
        ca, cb = header.index(a), header.index(b)
        for r in body:
            r[ca], r[cb] = r[cb], r[ca]
    else:
        die(f"unknown mutant {name!r}; use shuffle-rows, shuffle-months, shuffle-years, permute:COL or swap:A,B")
    return body


def try_execute(script, data, seed, extra_env=None):
    try:
        return execute(script, data, seed, extra_env)[0], None
    except SystemExit as err:
        return None, str(err)[-300:]
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


def audit(header, body, order_by, panel=False):
    """Data contract checked before anything is sealed: gaps, duplicates, empty cells."""
    report = {"empty_cells": {h: sum(1 for r in body if r[i].strip() in ("", ".", "NA", "nan")) for i, h in enumerate(header)}}
    report["empty_cells"] = {k: v for k, v in report["empty_cells"].items() if v}
    if order_by:
        col = header.index(order_by)
        keys = [r[col] for r in body]
        from collections import Counter
        report["duplicate_keys"] = [] if panel else sorted(k for k, n in Counter(keys).items() if n > 1)
        mk = sorted({month_key(k) for k in keys} - {None})
        if mk and len(mk) == len(set(keys)):
            have = set(mk)
            report["missing_months"] = [f"{m // 12}-{m % 12 + 1:02d}" for m in range(mk[0], mk[-1] + 1) if m not in have]
    return report


def audit_problems(rep):
    return {k: v for k, v in rep.items() if k in ("duplicate_keys", "missing_months") and v}


def schema():
    s = [e for e in entries() if e["kind"] == "schema"]
    return s[-1] if s else None


def staged():
    return bool(meta().get("staged"))


def stage_closed(stage):
    ev = [e for e in entries() if e["kind"] in ("close", "reopen") and e["stage"] == stage]
    return bool(ev) and ev[-1]["kind"] == "close"


def holdout_window(m):
    if not m.get("order_by"):
        return None
    col = m["columns"].index(m["order_by"])
    with open(WS / "holdout.csv", newline="") as f:
        keys = [r[col] for r in list(csv.reader(f))[1:]]
    return min(keys), max(keys)


def confirm_inputs(reg, m):
    """(DATA path, extra env) for a confirmatory run of a registered claim.
    history: explore + holdout in order, scored from the first holdout key (time series and panels).
    train: holdout as DATA, explore offered as TRAIN (random splits). holdout: legacy, holdout only."""
    mode = reg.get("data_mode", "holdout")
    if mode == "history":
        col = m["columns"].index(m["order_by"])
        rows = []
        for name in ("explore", "holdout"):
            with open(WS / f"{name}.csv", newline="") as f:
                rows += list(csv.reader(f))[1:]
        with open(WS / "confirm.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(m["columns"])
            w.writerows(sorted(rows, key=lambda r: r[col]))
        return WS / "confirm.csv", {"SCORE_FROM": holdout_window(m)[0]}
    if mode == "train":
        return WS / "holdout.csv", {"TRAIN": str(WS / "explore.csv")}
    return WS / "holdout.csv", {}


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
    rep = audit(header, body, a.order_by, a.panel)
    if a.panel and not a.order_by:
        die("--panel needs --order-by")
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
    if a.panel:  # many rows per period: move the cut to a period boundary so no period straddles the split
        col = header.index(a.order_by)
        while 0 < cut < len(idx) and body[idx[cut]][col] == body[idx[cut - 1]][col]:
            cut += 1
    for name, part in (("explore", idx[:cut]), ("holdout", idx[cut:])):
        with open(WS / f"{name}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(body[i] for i in sorted(part))
    e = append("init", source=str(a.data), source_sha=sha(a.data), seed=a.seed, rows=len(body),
               columns=header, split=f"ordered by {a.order_by}" if a.order_by else "random",
               explore_until=body[idx[cut - 1]][header.index(a.order_by)] if a.order_by else None, explore_rows=cut, holdout_rows=len(body) - cut,
               explore_sha=sha(WS / "explore.csv"), holdout_sha=sha(WS / "holdout.csv"),
               order_by=a.order_by, panel=a.panel, audit=rep, holdout_budget=a.budget, staged=not a.unstaged)
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
    if a.kind not in TYPES[a.category]:
        die(f"unknown {a.category} kind {a.kind!r}; `ledger.py types` lists them")
    parents = [x for x in (a.rests_on or "").split(",") if x]
    for pid in parents:
        if not find("register", pid):
            die(f"--rests-on {pid} is not registered")
    if a.category in RESTS_ON:
        ok = [pid for pid in parents if find("register", pid)[0].get("category") in RESTS_ON[a.category]]
        if not ok:
            die(f"a {a.category} claim must rest on a registered {' or '.join(RESTS_ON[a.category])} claim (--rests-on)")
    m = meta()
    ordered = bool(m.get("order_by"))
    sc = schema()
    if m.get("staged"):
        if not sc:
            die("no confirmed schema: run `profile`, agree the variable roles with the user, then `schema`")
        i = STAGES.index(a.category)
        open_before = [st for st in STAGES[:i] if not stage_closed(st)]
        if open_before:
            die(f"stages run in order: close {', '.join(open_before)} before registering {a.category} claims")
        if stage_closed(a.category):
            die(f"the {a.category} stage is closed; `reopen {a.category} --reason ...` to amend it (recorded)")
    excluded = sc["roles"].get("exclude", []) if sc else []

    def refuse(gate, msg):  # refused attempts stay on the record: they are part of the multiple-comparisons count
        append("refused", id=a.id, gate=gate, claim=a.claim, category=a.category, test=str(a.test), test_sha=sha(a.test), reason=msg[:500])
        die(msg)
    # 1. static: lint the test before anything runs
    errors, warnings = lint(a.test, a.category, ordered, excluded)
    for w in warnings:
        print(f"lint warning {w}")
    if errors:
        refuse("lint", "lint failed, nothing registered:\n  " + "\n  ".join(errors))
    # 2. smoke: the test must run on explore data and honour the output contract
    smoke, err = try_execute(a.test, WS / "explore.csv", m["seed"])
    if smoke is None:
        refuse("smoke", f"smoke run on explore.csv failed, nothing registered:\n{err}")
    if ordered and "scored_from" not in smoke:
        die('smoke run: JSON lacks "scored_from"')
    if smoke["verdict"] != "survived":
        print(f"warning: the claim is already falsified on explore data: {json.dumps(smoke)}")
    # 3. mutation: on data with the claimed structure destroyed, the test must say falsified
    if not a.mutant and not a.no_mutant:
        die("give at least one --mutant that should kill this claim, or --no-mutant \"<reason>\"")
    with open(WS / "explore.csv", newline="") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]
    mutants = []
    (WS / "mutants").mkdir(exist_ok=True)
    for spec in a.mutant or []:
        verdicts = []
        for k in range(5):
            mbody = mutate(spec, header, body, m.get("order_by"), random.Random(f"{m['seed']}:{spec}:{k}"))
            path = WS / "mutants" / f"{a.id}.csv"
            with open(path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(header)
                w.writerows(mbody)
            res, err = try_execute(a.test, path, m["seed"])
            verdicts.append(res["verdict"] if res else "error")
        killed = verdicts.count("falsified")
        informative = smoke["verdict"] == "survived"
        mutants.append({"mutant": spec, "verdicts": verdicts, "killed": killed, "informative": informative})
        print(f"mutant {spec}: killed {killed}/5 {verdicts}"
              + ("" if informative else " (uninformative: the claim already fails on unmutated explore data)"))
        if informative and killed < 4:
            refuse("mutation", f"the test has no teeth against {spec}: it falsified only {killed} of 5 mutants. "
                "Tighten the test or the threshold, or pick a mutant that really destroys what the claim asserts")
    (WS / "mutants" / f"{a.id}.csv").unlink(missing_ok=True)
    append("register", id=a.id, claim=a.claim, prediction=a.prediction, falsify_if=a.falsify_if,
           category=a.category, insight_kind=a.kind, rests_on=parents, smoke=smoke,
           data_mode="history" if ordered else "train",
           lint_warnings=warnings, mutants=mutants, no_mutant=a.no_mutant,
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
    data, env = confirm_inputs(reg, m)
    result, out_sha = execute(reg["test"], data, m["seed"], env)
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
    data, env = confirm_inputs(reg, m)
    result, out_sha = execute(reg["test"], data, m["seed"], env)
    same = out_sha == run["stdout_sha"]
    append("replay", id=a.id, identical=same, stdout_sha=out_sha)
    print(f"{a.id}: replay {'IDENTICAL' if same else 'DIVERGED'}")


def cmd_goldfish(a):
    m = check_data()
    run = find("run", a.id)
    if not run:
        die(f"{a.id} has not run")
    reg = find("register", a.id)[0]
    data, env = confirm_inputs(reg, m)
    result, out_sha = execute(a.test, data, m["seed"], env)
    agrees = result["verdict"] == run[0]["result"]["verdict"]
    g_err, g_warn = lint(a.test, reg.get("category") or "descriptive", False)
    for x in g_err + g_warn:
        print(f"goldfish lint: {x}")
    append("goldfish", id=a.id, agent=a.agent, test=str(a.test), test_sha=sha(a.test),
           result=result, agrees=agrees, stdout_sha=out_sha, narrowed=a.narrowed, note=a.note, lint=g_err + g_warn)
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
    rep = audit(header, fresh, m["order_by"], m.get("panel", False))
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


def build_retest(m):
    col = m["columns"].index(m["order_by"])
    rows = []
    for name in ("explore", "holdout", "fresh"):
        with open(WS / f"{name}.csv", newline="") as f:
            rows += list(csv.reader(f))[1:]
    with open(WS / "retest.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(m["columns"])
        w.writerows(sorted(rows, key=lambda r: r[col]))


def cmd_retest(a):
    m = check_data()
    ext = [e for e in entries() if e["kind"] == "extend"]
    if not ext:
        die("no fresh window; run `extend` first")
    x = ext[-1]
    window = f"{x['fresh_from']}..{x['fresh_to']}"
    # history + fresh rows, so lagged tests have context; SCORE_FROM says where scoring starts
    build_retest(m)
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
        flip = "BROKE" if result["verdict"] == "falsified" else "REVIVED"
        print(f"{hid}: fresh {result['verdict']} -> {'HELD' if held else flip}  {json.dumps(result)}")


def status(hid):
    reg = find("register", hid)
    for pid in (reg[0].get("rests_on") or []) if reg else []:
        if not status(pid).startswith("established"):
            return f"blocked: rests on {pid} ({status(pid)})"
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
    sd = find("seeds", hid)
    if sd and not sd[-1]["stable"]:
        return "seed-sensitive (verdict flips with the random seed)"
    if not fish:
        return f"{base} (no goldfish yet)"
    if not all(g["agrees"] for g in fish):
        return "contested"
    st = "established" if base == "survived" else "refuted"
    if any(g.get("narrowed") for g in fish):
        st += " (narrowed)"
    rt = [r for r in find("retest", hid) if "held" in r]
    if rt:
        flipped = "BROKE on fresh data" if base == "survived" else "REVIVED on fresh data (recheck it)"
        st += ", held on fresh data" if rt[-1]["held"] else f", {flipped}"
    return st


def cmd_waive(a):
    cat, _, kind = a.type.partition("/")
    if cat not in TYPES or (kind and kind not in TYPES[cat]):
        die(f"unknown type {a.type!r}; `ledger.py types` lists them")
    append("waive", category=cat, insight_kind=kind or None, reason=a.reason)
    print(f"waived {a.type}: {a.reason}")


def _num(v):
    try:
        float(v)
        return True
    except ValueError:
        return False


def cmd_profile(a):
    """Describe every column of explore.csv and suggest a role; the user confirms roles with `schema`."""
    m = meta()
    with open(WS / "explore.csv", newline="") as f:
        rows = list(csv.reader(f))
    header, body = rows[0], rows[1:]
    out = ["# Variable profile (explore data)", "",
           f"{len(body)} rows. Suggested roles are a starting point for the conversation with the user, not a decision.", "",
           "| column | type | distinct | empty | range or top values | suggested role |", "|---|---|---|---|---|---|"]
    for i, h in enumerate(header):
        vals = [r[i] for r in body if r[i].strip() not in ("", ".", "NA", "nan")]
        numeric = bool(vals) and all(_num(v) for v in vals)
        distinct = len(set(vals))
        if numeric:
            nums = [float(v) for v in vals]
            rng = f"{min(nums):g} to {max(nums):g}"
        else:
            from collections import Counter
            rng = ", ".join(v for v, _ in Counter(vals).most_common(3))
        if h == m.get("order_by"):
            role = "time"
        elif distinct == len(body) and (not numeric or all(float(v).is_integer() for v in vals)):
            role = "key"
        elif not numeric and distinct <= 30:
            role = "segment"
        elif numeric and distinct > 20:
            role = "feature or target"
        else:
            role = "feature"
        out.append(f"| {h} | {'numeric' if numeric else 'text'} | {distinct} | {len(body) - len(vals)} | {rng} | {role} |")
    (WS / "PROFILE.md").write_text("\n".join(out) + "\n")
    append("profile", file=str(WS / "PROFILE.md"), file_sha=sha(WS / "PROFILE.md"))
    print("\n".join(out))


def cmd_schema(a):
    """Record each column's role (dependent, independent, and the rest) and who confirmed it."""
    m = check_data()
    if [e for e in entries() if e["kind"] == "run"]:
        die("roles are frozen once a claim has run on the holdout")
    roles = {}
    for role in ROLES:
        for col in [c for c in (getattr(a, role) or "").split(",") if c]:
            col, _, why = col.partition(":")
            if col not in m["columns"]:
                die(f"{col!r} is not a column")
            roles.setdefault(role, []).append(col)
            if why:
                roles.setdefault("_reasons", {})[col] = why
    if not roles.get("target"):
        die("name at least one --target (the dependent variable)")
    assigned = [c for r, cs in roles.items() if r != "_reasons" for c in cs]
    per = {c: {r for r, cs in roles.items() if r != "_reasons" and c in cs} for c in assigned}
    dup = sorted(c for c, rs in per.items() if len(rs) > 1 and rs != {"segment", "feature"})
    if dup:
        die(f"columns with conflicting roles: {dup} (only segment+feature may overlap)")
    missing = [c for c in m["columns"] if c not in assigned]
    if missing:
        die(f"every column needs a role; unassigned: {missing}")
    reasons = roles.pop("_reasons", {})
    append("schema", roles=roles, reasons=reasons, confirmed_by=a.confirmed_by, notes=a.notes)
    for r, cs in roles.items():
        print(f"{r:8} {', '.join(cs)}")
    print(f"confirmed by: {a.confirmed_by}")


def cmd_close(a):
    if not staged():
        die("this workspace is unstaged")
    i = STAGES.index(a.stage)
    if any(not stage_closed(st) for st in STAGES[:i]):
        die("close the earlier stages first")
    if stage_closed(a.stage):
        die(f"{a.stage} is already closed")
    regs = [e for e in entries() if e["kind"] == "register" and e.get("category") == a.stage]
    unrun = [r["id"] for r in regs if not find("run", r["id"]) or not find("replay", r["id"])]
    if unrun:
        die(f"run and replay every {a.stage} claim before closing: {unrun}")
    waived = {(w["category"], w.get("insight_kind")) for w in entries() if w["kind"] == "waive"}
    gaps = [k for k in TYPES[a.stage] if not any(r.get("insight_kind") == k for r in regs)
            and (a.stage, k) not in waived and (a.stage, None) not in waived]
    if gaps and not a.note:
        die(f"kinds neither tested nor waived: {gaps}; waive them or close with --note saying why they are left open")
    if not regs and (a.stage, None) not in waived:
        die(f"no {a.stage} claims: register at least one, or `waive {a.stage} --reason ...`")
    append("close", stage=a.stage, claims={r["id"]: status(r["id"]) for r in regs}, open_kinds=gaps, note=a.note)
    print(f"{a.stage} closed: {len(regs)} claims, open kinds {gaps or 'none'}")


def cmd_reopen(a):
    if not stage_closed(a.stage):
        die(f"{a.stage} is not closed")
    later = [st for st in STAGES[STAGES.index(a.stage) + 1:] if stage_closed(st)]
    append("reopen", stage=a.stage, reason=a.reason, later_closed=later)
    print(f"{a.stage} reopened (recorded as an amendment)" + (f"; later stages already closed: {later}" if later else ""))


def cmd_referee(a):
    append("referee", agent=a.agent, verdict=a.verdict, report=str(a.report), report_sha=sha(a.report))
    print(f"referee {a.agent}: {a.verdict}")


def cmd_supersede(a):
    for x in (a.id, a.by):
        if not find("register", x):
            die(f"{x} is not registered")
    append("supersede", id=a.id, by=a.by, reason=a.reason)
    print(f"{a.id} superseded by {a.by}")


def cmd_withdraw(a):
    if not find("register", a.id):
        die(f"{a.id} is not registered")
    append("withdraw", id=a.id, reason=a.reason)
    print(f"{a.id}: decision withdrawn")


def caveats(hid):
    """Plain-language qualifiers the abstract must carry for a claim."""
    out = []
    for e in find("supersede", hid):
        out.append(f"superseded by {e['by']} ({status(e['by'])}): {e['reason']}")
    for e in find("withdraw", hid):
        out.append(f"decision withdrawn: {e['reason']}")
    sd = find("seeds", hid)
    if sd and not sd[-1]["stable"]:
        out.append("verdict flips with the random seed")
    return out


def cmd_respond(a):
    ref = [e for e in entries() if e["kind"] == "referee" and e["agent"] == a.to]
    if not ref:
        die(f"no referee report from {a.to!r}")
    append("response", to=a.to, file=str(a.file), file_sha=sha(a.file))
    print(f"response to {a.to} recorded")


def cmd_seeds(a):
    """Rerun a claim's frozen test and every replication under several seeds; a verdict that flips is not a finding."""
    m = check_data()
    ids = [e["id"] for e in entries() if e["kind"] == "run"] if a.id == "all" else [a.id]
    seeds = [m["seed"] + k for k in range(a.n)] + [1]
    for hid in ids:
        reg = find("register", hid)[0]
        data, env = confirm_inputs(reg, m)
        scripts = [("elephant", reg["test"])] + [(g["agent"], g["test"]) for g in find("goldfish", hid)]
        out = {}
        for who, path in scripts:
            vs = []
            for sd in seeds:
                res, err = try_execute(path, data, sd, env)
                vs.append(res["verdict"] if res else "error")
            out[who] = vs
        stable = len({v for vs in out.values() for v in vs}) == 1
        append("seeds", id=hid, seeds=seeds, verdicts=out, stable=stable)
        print(f"{hid}: {'stable' if stable else 'SEED-SENSITIVE'} {json.dumps(out)}")


def cmd_audit(a):
    """Read-only re-execution of every recorded result. Writes AUDIT.md; exit code 1 on any failure."""
    m = meta()
    rows, fails = [], 0

    def check(what, ok, detail=""):
        nonlocal fails
        fails += 0 if ok else 1
        rows.append(f"| {what} | {'pass' if ok else '**FAIL**'} | {detail} |")

    ok, msg, head = chain()
    check("ledger hash chain", ok, msg)
    for name in ("explore", "holdout"):
        check(f"{name}.csv hash", sha(WS / f"{name}.csv") == m[f"{name}_sha"])
    ext = [e for e in entries() if e["kind"] == "extend"]
    if ext:
        check("fresh.csv hash", sha(WS / "fresh.csv") == ext[-1]["fresh_sha"])
    for e in entries():
        k = e["kind"]
        if k == "register":
            check(f"{e['id']} test frozen", Path(e["test"]).exists() and sha(e["test"]) == e["test_sha"], e["test"])
            if e.get("review"):
                check(f"{e['id']} critic review", Path(e["review"]).exists() and sha(e["review"]) == e["review_sha"], e["review"])
        elif k == "run":
            reg = find("register", e["id"])[0]
            try:
                data, env = confirm_inputs(reg, m)
                _, out = execute(reg["test"], data, m["seed"], env)
                check(f"{e['id']} holdout result `#{e['seq']}` re-executed", out == e["stdout_sha"], "byte-identical" if out == e["stdout_sha"] else "output differs")
            except SystemExit as err:
                check(f"{e['id']} holdout result `#{e['seq']}` re-executed", False, str(err)[-120:])
        elif k == "goldfish":
            check(f"{e['id']} replication script by {e['agent']} unchanged", Path(e["test"]).exists() and sha(e["test"]) == e["test_sha"], e["test"])
            try:
                data, env = confirm_inputs(find("register", e["id"])[0], m)
                _, out = execute(e["test"], data, m["seed"], env)
                check(f"{e['id']} replication by {e['agent']} `#{e['seq']}`", out == e["stdout_sha"], "byte-identical" if out == e["stdout_sha"] else "output differs")
            except SystemExit as err:
                check(f"{e['id']} replication by {e['agent']} `#{e['seq']}`", False, str(err)[-120:])
        elif k == "retest" and "result" in e and ext and e["window"] == f"{ext[-1]['fresh_from']}..{ext[-1]['fresh_to']}":
            build_retest(m)
            reg = find("register", e["id"])[0]
            _, out = execute(reg["test"], WS / "retest.csv", m["seed"], {"SCORE_FROM": ext[-1]["fresh_from"]})
            check(f"{e['id']} fresh-data result `#{e['seq']}` re-executed", out == e["stdout_sha"])
        elif k == "response":
            check(f"response to {e['to']}", Path(e["file"]).exists() and sha(e["file"]) == e["file_sha"], e["file"])
        elif k == "referee":
            check(f"referee report by {e['agent']}", Path(e["report"]).exists() and sha(e["report"]) == e["report_sha"], e["report"])
    text = ["# Audit", "", f"Ledger head `{head[:16]}`. Every recorded result re-executed from its frozen script and sealed data. "
            f"{fails} failure(s).", "", "| check | result | detail |", "|---|---|---|"] + rows
    (WS / "AUDIT.md").write_text("\n".join(text) + "\n")
    print("\n".join(text))
    if fails:
        sys.exit(1)


def cmd_lint(a):
    ordered = bool(meta().get("order_by")) if LEDGER.exists() else False
    errors, warnings = lint(a.test, a.category, ordered)
    for w in warnings:
        print(f"warning {w}")
    for e in errors:
        print(f"error {e}")
    if errors:
        sys.exit(1)
    print("lint clean" if not warnings else "lint passed with warnings")


def cmd_types(a):
    for cat, kinds in TYPES.items():
        print(f"{cat}" + (f"  (must rest on: {' or '.join(RESTS_ON[cat])})" if cat in RESTS_ON else ""))
        for k, (what, ev) in kinds.items():
            print(f"  {k:18} {what}\n  {'':18} evidence: {ev}")


def coverage():
    regs = [e for e in entries() if e["kind"] == "register"]
    waived = [e for e in entries() if e["kind"] == "waive"]
    lines = ["## Coverage", "", "| category | kind | claims | waived |", "|---|---|---|---|"]
    for cat, kinds in TYPES.items():
        cat_waive = [w["reason"] for w in waived if w["category"] == cat and not w.get("insight_kind")]
        for k in kinds:
            ids = [f"{r['id']} ({status(r['id'])})" for r in regs if r.get("category") == cat and r.get("insight_kind") == k]
            w = cat_waive + [x["reason"] for x in waived if x["category"] == cat and x.get("insight_kind") == k]
            lines.append(f"| {cat} | {k} | {'; '.join(ids) or ('' if w else '**not covered**')} | {'; '.join(w)} |")
    untyped = [r["id"] for r in regs if not r.get("category")]
    if untyped:
        lines += ["", f"Untyped claims (registered before types existed): {', '.join(untyped)}."]
    return lines


def chain():
    """(ok, message, head) for the hash chain."""
    prev = "0" * 64
    es = entries()
    for e in es:
        h = e.pop("hash")
        if e["prev"] != prev or hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest() != h:
            return False, f"chain broken at seq {e['seq']}", prev
        prev = h
    return True, f"{len(es)} entries", prev


def cmd_verify(a):
    ok, msg, head = chain()
    if not ok:
        die(msg)
    check_data()
    print(f"ledger intact: {msg}, head {head[:12]}")


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
    regs = [e for e in entries() if e["kind"] == "register"]
    for cat in list(TYPES) + [None]:
        group = [r for r in regs if r.get("category") == cat]
        if not group:
            continue
        lines += ["", f"## {cat.capitalize() if cat else 'Untyped'}", "",
                  "| id | kind | status | claim | decision it informs | falsified if | holdout result | goldfish | fresh data |",
                  "|---|---|---|---|---|---|---|---|---|"]
        lines += [row(r) for r in group]
    lines += [""] + coverage()
    lines += ["", "Statuses: **established** = survived holdout, replayed byte-identical, every goldfish agrees. "
              "**refuted** = falsified and confirmed the same way. **(narrowed)** = a goldfish found the claim holds only in a "
              "narrower reading; quote the narrowed version. **held / BROKE on fresh data** = the frozen test rerun on rows "
              "published after the seal. **blocked** = a prescriptive claim whose supporting claim is not established. "
              "**seed-sensitive** = the verdict changes with the random seed (`seeds`), so it is not a finding. "
              "Anything else is not yet an insight."]
    out = WS / "INSIGHTS.md"
    out.write_text("\n".join(lines) + "\n")
    print(out.read_text())


def scope(r, m):
    w = holdout_window(m)
    mode = r.get("data_mode", "holdout")
    if w and mode == "history":
        return f"scored on {m['order_by']} {w[0]} to {w[1]} (the sealed holdout), with earlier rows available as history"
    if w:
        return f"tested on {m['order_by']} {w[0]} to {w[1]} only (the sealed holdout, without earlier history)"
    if mode == "train":
        return f"tested on the {m['holdout_rows']} sealed holdout rows, with the {m['explore_rows']} exploration rows available for training"
    return f"tested on the {m['holdout_rows']} sealed holdout rows"


def _res(d):
    return ", ".join(f"{k}={v}" for k, v in d.items() if k not in ("verdict", "scored_from")) if d else ""


def cmd_paper(a):
    """A peer-review style write-up generated from the ledger alone: every figure cites its entry."""
    m = meta()
    es = entries()
    ok, msg, head = chain()
    regs = [e for e in es if e["kind"] == "register"]
    sc = schema()
    waives = [e for e in es if e["kind"] == "waive"]
    st = {r["id"]: status(r["id"]) for r in regs}
    superseded = [r for r in regs if find("supersede", r["id"])]
    est = [r for r in regs if st[r["id"]].startswith("established") and r not in superseded]
    L = [f"# {a.title or 'Findings: ' + Path(m['source']).name}", "",
         f"*Generated from the evidence ledger `{LEDGER}` (head `{head[:16]}`, {msg}, chain {'intact' if ok else 'BROKEN'}). "
         "Every number below cites the ledger entry it came from as `#n`. To check this paper, run "
         "`python3 ledger.py audit`, which re-executes every result.*", "", "## Abstract", ""]
    w = holdout_window(m)
    L.append((f"All findings below are about {m['order_by']} {w[0]} to {w[1]}, the period sealed before analysis; earlier periods were used only to form hypotheses. " if w else "")
             + f"We registered {len(regs)} claims before testing them on held-out data, across "
             f"{len({r.get('category') for r in regs})} insight categories. "
             f"{len(est)} stand as established, {sum(v.startswith('refuted') for v in st.values())} were refuted, "
             f"{len(superseded)} were superseded by later tests, and "
             + (lambda n: f"{n} {'is' if n == 1 else 'are'} open (contested, blocked, seed-sensitive or untested).")(
                 sum(not (v.startswith('established') or v.startswith('refuted')) for v in st.values())))
    clean = [r for r in est if not caveats(r["id"]) and not any(g.get("narrowed") for g in find("goldfish", r["id"]))]
    qual = [r for r in est if r not in clean]
    if clean:
        L += ["", "Established without qualification:", ""]
        L += [f"- **{r['id']}** ({r.get('category')}/{r.get('insight_kind')}): {r['claim']}" for r in clean]
    if qual:
        L += ["", "Established only with qualifications (read these before acting):", ""]
        for r in qual:
            nar = [g["narrowed"] for g in find("goldfish", r["id"]) if g.get("narrowed")]
            q = caveats(r["id"]) + ([f"holds only as narrowed by its tester: {nar[-1]}"] if nar else [])
            L.append(f"- **{r['id']}** ({r.get('category')}/{r.get('insight_kind')}): {r['claim']} *{'; '.join(q)}.*")
    if superseded:
        L += ["", "Superseded by later tests (do not act on these as worded):", ""]
        L += [f"- **{r['id']}** (passed its own test): {r['claim']} *{'; '.join(caveats(r['id']))}.*" for r in superseded]
    other = [r for r in regs if r not in est and r not in superseded]
    if other:
        L += ["", "Not established:", ""]
        L += [f"- **{r['id']}**: {st[r['id']]}. {r['claim']}" + (f" *{'; '.join(caveats(r['id']))}.*" if caveats(r["id"]) else "") for r in other]
    # 1 Data
    L += ["", "## 1. Data", "",
          f"- Source: `{m['source']}`, sha256 `{m['source_sha'][:16]}`, {m['rows']} rows, {len(m['columns'])} columns.",
          f"- Split (`#{0}`): {m.get('split', 'random')}, seed {m['seed']}; {m['explore_rows']} rows for exploration, "
          f"{m['holdout_rows']} sealed for confirmation" + (f" (exploration up to {m['explore_until']})" if m.get("explore_until") else "") + ".",
          f"- Data audit before sealing: {json.dumps(m.get('audit', {}))}."]
    ext = [e for e in es if e["kind"] == "extend"]
    if ext:
        x = ext[-1]
        L.append(f"- Fresh data added after sealing (`#{x['seq']}`): {x['fresh_from']} to {x['fresh_to']}, {x['fresh_rows']} rows; {x['revised_rows']} sealed rows revised at source.")
    if sc:
        L += ["", f"### 1.1 Variables (`#{sc['seq']}`, confirmed by {sc['confirmed_by']})", "", "| role | columns | meaning |", "|---|---|---|"]
        for role, cols in sc["roles"].items():
            why = "; ".join(f"{c}: {sc['reasons'][c]}" for c in cols if c in sc.get("reasons", {}))
            L.append(f"| {role} | {', '.join(cols)} | {ROLES[role]}" + (f" ({why})" if why else "") + " |")
        if sc.get("notes"):
            L += ["", sc["notes"]]
    # 2 Methods
    runs = [e for e in es if e["kind"] == "run"]
    L += ["", "## 2. Methods", "",
          "Each claim was written down with its kill criterion and the decision it informs, reviewed by a critic agent that saw no data, "
          "and frozen (its test script hashed) before its single look at the sealed holdout. Registration required the test to pass a "
          "lint for future-peeking and leaky code, a smoke run on exploration data, and a mutation gate: on copies of the data with the "
          "claimed pattern destroyed, the test had to report falsified at least 4 times in 5. Results were replayed byte-for-byte, then "
          "replicated by independent agents who saw only the claim and the holdout and wrote their own method. Prescriptive claims count "
          "only if the claim they rest on is established.", "",
          f"- Holdout looks used: {len(runs)}" + (f" of a budget of {m['holdout_budget']}" if m.get("holdout_budget") else "") + ".",
          f"- Claims registered: {len(regs)}; attempts refused by the gates: {len([e for e in es if e['kind'] == 'refused'])} "
          "(together, the multiple-comparisons count; thresholds were set per claim at registration).",
          f"- Replicating agents: {', '.join(sorted({g['agent'] for g in es if g['kind'] == 'goldfish'})) or 'none'}."]
    seeds_e = {e["id"]: e for e in es if e["kind"] == "seeds"}
    if seeds_e:
        bad = [k for k, v in seeds_e.items() if not v["stable"]]
        L.append(f"- Seed check: {len(seeds_e)} claims rerun under several seeds; " + (f"unstable: {', '.join(bad)}." if bad else "all stable."))
    closes = [e for e in es if e["kind"] in ("close", "reopen")]
    if closes:
        L.append("- Stage log: " + "; ".join(f"`#{c['seq']}` {c['kind']} {c['stage']}" + (f" ({c.get('reason')})" if c['kind'] == 'reopen' else "") for c in closes) + ".")
    # 3 Results
    L += ["", "## 3. Results"]
    for n, cat in enumerate(STAGES, 1):
        group = [r for r in regs if r.get("category") == cat]
        L += ["", f"### 3.{n} {cat.capitalize()}", ""]
        if not group:
            w = [x["reason"] for x in waives if x["category"] == cat and not x.get("insight_kind")]
            L.append(f"No claims. " + (f"Waived: {w[-1]}" if w else "Not covered."))
            continue
        for r in group:
            run, reps, fish, rt = find("run", r["id"]), find("replay", r["id"]), find("goldfish", r["id"]), find("retest", r["id"])
            L += [f"#### {r['id']}: {r['claim']}", "",
                  f"- **Status: {st[r['id']]}.** Type {cat}/{r.get('insight_kind')}" + (f", rests on {', '.join(r['rests_on'])}" if r.get("rests_on") else "") + ".",
                  f"- Decision it informs: {r.get('decision')}.",
                  f"- Pre-registered (`#{r['seq']}`): predicted {r['prediction']}; falsified if {r['falsify_if']}. Test `{r['test']}` sha `{r['test_sha'][:12]}`.",
                  f"- Scope: {scope(r, m)}."]
            for c in caveats(r["id"]):
                L.append(f"- **Note:** {c}.")
            if r.get("review"):
                refs = {e["report"] for e in es if e["kind"] == "referee"}
                L.append(f"- Reviewed before registration by " + ("a referee report (no pre-test critic saw this exact wording)" if r["review"] in refs else "the critic") + f": `{r['review']}`.")
            sd = find("seeds", r["id"])
            if sd:
                x = sd[-1]
                L.append(f"- Seed check (`#{x['seq']}`, seeds {x['seeds']}): {'stable' if x['stable'] else 'UNSTABLE'}; " + "; ".join(f"{k}: {'/'.join(v)}" for k, v in x["verdicts"].items()) + ".")
            gates = []
            if r.get("smoke"):
                gates.append(f"smoke run on exploration data {r['smoke']['verdict']}")
            for mu in r.get("mutants") or []:
                gates.append(f"mutant {mu['mutant']} killed {mu['killed']}/5" + ("" if mu.get("informative", True) else " (uninformative)"))
            if r.get("no_mutant"):
                gates.append(f"no mutant: {r['no_mutant']}")
            if r.get("lint_warnings"):
                gates.append(f"lint warnings: {'; '.join(r['lint_warnings'])}")
            if gates:
                L.append(f"- Gates: {'; '.join(gates)}.")
            if run:
                L.append(f"- Holdout result (`#{run[0]['seq']}`): **{run[0]['result']['verdict']}**, {_res(run[0]['result'])}."
                         + (f" Replay `#{reps[-1]['seq']}` {'byte-identical' if reps[-1]['identical'] else 'DIVERGED'}." if reps else " Not replayed."))
            for g in fish:
                L.append(f"- Replication by {g['agent']} (`#{g['seq']}`): {g['result']['verdict']} ({'agrees' if g['agrees'] else 'DISAGREES'}); "
                         f"method: {g['result'].get('method', 'see script')}; {_res({k: v for k, v in g['result'].items() if k != 'method'})}."
                         + (f" Tester's note: {g['note']}." if g.get("note") else "") + (f" Narrowed (the tester's words): {g['narrowed']}." if g.get("narrowed") else ""))
            for x in rt[-1:]:
                L.append(f"- Fresh data (`#{x['seq']}`, {x['window']}): " + (f"pending ({x['pending']})." if "pending" in x else f"{x['result']['verdict']}, {_res(x['result'])}."))
            L.append("")
    # 4 Threats
    L += ["## 4. Threats to validity", ""]
    threats = []
    if not sc:
        threats.append("No variable roles were confirmed, so leaky predictors were not screened.")
    elif "elephant" in sc["confirmed_by"].lower() or "agent" in sc["confirmed_by"].lower():
        threats.append(f"Variable roles were confirmed by {sc['confirmed_by']}, not by a domain owner.")
    for x in waives:
        threats.append(f"Not testable with this data: {x['category']}{'/' + x['insight_kind'] if x.get('insight_kind') else ''}: {x['reason']}")
    for c in [e for e in es if e["kind"] == "close" and e.get("open_kinds")]:
        threats.append(f"{c['stage'].capitalize()} kinds left open at close (`#{c['seq']}`): {', '.join(c['open_kinds'])}. {c.get('note') or ''}".strip())
    for r in regs:
        v = st[r["id"]]
        if not (v.startswith("established") or v.startswith("refuted")):
            threats.append(f"{r['id']} is {v}.")
        if r.get("smoke", {}).get("verdict") == "falsified":
            threats.append(f"{r['id']} already failed on exploration data before registration, so its mutation gate says nothing.")
        if not r.get("review"):
            threats.append(f"{r['id']} was not reviewed by a critic before registration.")
        if not find("goldfish", r["id"]):
            threats.append(f"{r['id']} has no independent replication.")
    for e in [e for e in es if e["kind"] == "refused"]:
        threats.append(f"Refused at registration (`#{e['seq']}`, {e['gate']} gate): {e['id']}, \"{e['claim']}\". {e['reason'].splitlines()[0]}")
    for e in [e for e in es if e["kind"] == "reopen"]:
        threats.append(f"The {e['stage']} stage was reopened (`#{e['seq']}`): {e['reason']}.")
    for r in regs:
        for g in find("goldfish", r["id"]):
            if g.get("narrowed") and st[r["id"]].startswith("established"):
                threats.append(f"{r['id']} holds only in its tester's narrower reading (`#{g['seq']}`): {g['narrowed']}")
    if a.notes and Path(a.notes).exists():
        threats += [l.lstrip("- ").strip() for l in Path(a.notes).read_text().splitlines() if l.startswith("- ")]
    L += [f"- {t}" for t in threats] or ["- None recorded."]
    # 5 Review
    L += ["", "## 5. Peer review", ""]
    refs = {e["report"] for e in es if e["kind"] == "referee"}
    revs = sorted({r["review"] for r in regs if r.get("review") and r["review"] not in refs})
    L += [f"- Critic review before testing: `{p}`." for p in revs] or ["- No critic reviews recorded."]
    for e in [e for e in es if e["kind"] == "referee"]:
        L.append(f"- Referee report by {e['agent']} (`#{e['seq']}`): **{e['verdict']}**. `{e['report']}`.")
        for x in [x for x in es if x["kind"] == "response" and x["to"] == e["agent"]]:
            L.append(f"  - Response (`#{x['seq']}`): `{x['file']}`.")
    # Appendix
    L += ["", "## Appendix A. Reproduce", "", "```bash", "python3 ledger.py verify", "```", "", "```bash", "python3 ledger.py audit", "```", "",
          "`audit` re-runs every frozen test and every replication against the sealed data and checks each output is byte-identical to the "
          "recorded one. It changes nothing and writes `AUDIT.md`.", "",
          "## Appendix B. Ledger index", "", "| # | entry | claim | hash |", "|---|---|---|---|"]
    L += [f"| {e['seq']} | {e['kind']} | {e.get('id') or e.get('stage') or ''} | `{e['hash'][:12]}` |" for e in es]
    (WS / "PAPER.md").write_text("\n".join(L) + "\n")
    print(f"wrote {WS / 'PAPER.md'} ({len(L)} lines)")


def row(r):
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
    kind = r.get("insight_kind") or ""
    if r.get("rests_on"):
        kind += f" (rests on {', '.join(r['rests_on'])})"
    return f"| {r['id']} | {kind} | **{status(r['id'])}** | {r['claim']} | {r.get('decision') or ''} | {r['falsify_if']} | {res} | {fish} | {fr} |"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    i = s.add_parser("init"); i.add_argument("data"); i.add_argument("--seed", type=int, default=20261123)
    i.add_argument("--explore-fraction", type=float, default=0.5)
    i.add_argument("--order-by", help="column to sort by for a time split (explore earliest rows, hold out the latest)")
    i.add_argument("--budget", type=int, help="max confirmatory looks at the holdout across all claims")
    i.add_argument("--allow-gaps", action="store_true", help="seal despite gaps or duplicate keys (recorded)")
    i.add_argument("--panel", action="store_true", help="many rows per --order-by value (e.g. models per year); split on a period boundary")
    i.add_argument("--unstaged", action="store_true", help="skip the schema and stage gates (not for audited work)")
    r = s.add_parser("register"); r.add_argument("id"); r.add_argument("--claim", required=True)
    r.add_argument("--prediction", required=True); r.add_argument("--falsify-if", required=True)
    r.add_argument("--test", required=True)
    r.add_argument("--category", required=True, choices=list(TYPES))
    r.add_argument("--kind", required=True, help="a kind within the category; `ledger.py types` lists them")
    r.add_argument("--rests-on", help="comma-separated claim ids this claim depends on (required for prescriptive)")
    r.add_argument("--decision", required=True, help="the decision this claim would change if it holds")
    r.add_argument("--min-fresh", type=int, help="fresh rows needed before `retest` may judge this claim")
    r.add_argument("--mutant", action="append", help="data mutation that should kill the claim (repeatable): "
                   "shuffle-rows, shuffle-months, shuffle-years, permute:COL, swap:A,B")
    r.add_argument("--no-mutant", help="why no mutation applies (recorded)")
    r.add_argument("--review", help="the critic goldfish's review of this claim, saved before registering")
    for n in ("run", "replay"):
        s.add_parser(n).add_argument("id")
    g = s.add_parser("goldfish"); g.add_argument("id"); g.add_argument("--test", required=True)
    g.add_argument("--agent", default="goldfish-1")
    g.add_argument("--narrowed", help="the narrower reading under which the goldfish found the claim holds")
    g.add_argument("--note", help="the goldfish's sentence on what was ambiguous or interpreted")
    s.add_parser("extend").add_argument("data")
    s.add_parser("retest").add_argument("id", help="a claim id, or `all`")
    w = s.add_parser("waive"); w.add_argument("type", help="category or category/kind")
    w.add_argument("--reason", required=True, help="why this data cannot support that type")
    li = s.add_parser("lint"); li.add_argument("test"); li.add_argument("--category", required=True, choices=list(TYPES))
    s.add_parser("profile")
    sc = s.add_parser("schema")
    for role, what in ROLES.items():
        sc.add_argument(f"--{role}", help=f"comma-separated columns: {what} (col:reason allowed)")
    sc.add_argument("--confirmed-by", required=True, help="who agreed these roles (the user, a domain owner)")
    sc.add_argument("--notes", help="anything the roles alone do not say")
    c = s.add_parser("close"); c.add_argument("stage", choices=STAGES); c.add_argument("--note")
    ro = s.add_parser("reopen"); ro.add_argument("stage", choices=STAGES); ro.add_argument("--reason", required=True)
    rf = s.add_parser("referee"); rf.add_argument("--report", required=True); rf.add_argument("--agent", required=True)
    rf.add_argument("--verdict", required=True, choices=["accept", "minor-revisions", "major-revisions", "reject"])
    rs = s.add_parser("respond"); rs.add_argument("--to", required=True, help="the referee agent name"); rs.add_argument("--file", required=True)
    pa = s.add_parser("paper"); pa.add_argument("--title"); pa.add_argument("--notes", help="path to analyst notes to cite")
    s.add_parser("audit")
    su = s.add_parser("supersede"); su.add_argument("id"); su.add_argument("--by", required=True); su.add_argument("--reason", required=True)
    wd = s.add_parser("withdraw"); wd.add_argument("id"); wd.add_argument("--reason", required=True)
    se = s.add_parser("seeds"); se.add_argument("id", help="a claim id, or `all`"); se.add_argument("--n", type=int, default=3, help="seeds to try besides seed 1")
    s.add_parser("types"); s.add_parser("verify"); s.add_parser("report")
    a = p.parse_args()
    globals()[f"cmd_{a.cmd}"](a)


if __name__ == "__main__":
    main()
