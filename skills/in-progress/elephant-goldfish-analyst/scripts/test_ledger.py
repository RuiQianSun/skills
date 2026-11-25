"""Unit and chaos tests for ledger.py. Run: python3 test_ledger.py

Each test builds a throwaway workspace on synthetic monthly data where the truth is known:
column `a` peaks every November and trends up; column `b` is seeded noise.
"""
import csv, json, os, random, subprocess, sys, tempfile, unittest
from pathlib import Path

LEDGER = Path(__file__).with_name("ledger.py")

SEASONAL = '''import csv, json, os
F = os.environ.get("SCORE_FROM")
rows = list(csv.DictReader(open(os.environ["DATA"])))
years = {}
for r in rows:
    if r["a"] and (F is None or r["month"] >= F):
        years.setdefault(r["month"][:4], []).append((float(r["a"]), r["month"][5:]))
full = [v for v in years.values() if len(v) == 12]
share = sum(max(v)[1] == "11" for v in full) / len(full) if full else float("nan")
print(json.dumps({"verdict": "survived" if share >= 0.8 else "falsified", "scored_from": F, "years": len(full), "share": share}))
'''
TOOTHLESS = '''import json, os
print(json.dumps({"verdict": "survived", "scored_from": os.environ.get("SCORE_FROM")}))
'''
LEAKY = '''import json, os
import pandas as pd
d = pd.read_csv(os.environ["DATA"]); F = os.environ.get("SCORE_FROM")
m = d.a.rolling(3, center=True).mean()
print(json.dumps({"verdict": "survived", "scored_from": F}))
'''
UNSEEDED = '''import json, os
import numpy as np
x = np.random.permutation(10)
print(json.dumps({"verdict": "survived", "scored_from": os.environ.get("SCORE_FROM")}))
'''
CRASHES = '''import json, os
F = os.environ.get("SCORE_FROM")  # contract-clean, so the lint passes and the smoke run is what fails
raise RuntimeError("boom")
print(json.dumps({"verdict": "survived", "scored_from": F}))
'''


def make_rows(start=2000, years=20, drop=(), dup=None):
    rng = random.Random(7)
    rows = []
    for y in range(start, start + years):
        for m in range(1, 13):
            key = f"{y}-{m:02d}"
            if key in drop:
                continue
            a = 100 + 2 * (y - start) + (40 if m == 11 else 0) + rng.uniform(-5, 5)
            rows.append([key, f"{a:.2f}", f"{rng.uniform(0, 100):.2f}"])
            if key == dup:
                rows.append(rows[-1][:])
    return rows


class Workspace:
    def __init__(self, tmp):
        self.dir = Path(tmp)

    def csv(self, name, rows):
        p = self.dir / name
        with open(p, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["month", "a", "b"])
            w.writerows(rows)
        return p

    def script(self, name, src):
        p = self.dir / name
        p.write_text(src)
        return p

    def run(self, *args):
        p = subprocess.run([sys.executable, str(LEDGER), *map(str, args)], cwd=self.dir,
                           capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def ok(self, *args):
        code, out = self.run(*args)
        assert code == 0, f"ledger {' '.join(map(str, args))} failed:\n{out}"
        return out

    def init(self, rows=None, *extra, staged=False):
        self.csv("data.csv", rows or make_rows())
        return self.ok("init", "data.csv", "--order-by", "month", *extra, *([] if staged else ["--unstaged"]))

    def register(self, hid, test, *extra, category="descriptive", kind="seasonality"):
        return self.run("register", hid, "--category", category, "--kind", kind, "--claim", "c",
                        "--prediction", "p", "--falsify-if", "f", "--decision", "d", "--test", test, *extra)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = Workspace(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def seasonal(self, hid="S1", *extra):
        t = self.ws.script(f"{hid}.py", SEASONAL)
        code, out = self.ws.register(hid, t, "--mutant", "shuffle-months", *extra)
        self.assertEqual(code, 0, out)
        return t

    # data audit (chaos: broken inputs must not be sealed)
    def test_init_refuses_missing_month(self):
        self.ws.csv("data.csv", make_rows(drop={"2010-10"}))
        code, out = self.ws.run("init", "data.csv", "--order-by", "month")
        self.assertNotEqual(code, 0)
        self.assertIn("2010-10", out)
        self.assertFalse((self.ws.dir / "analysis" / "LEDGER.jsonl").exists())

    def test_init_refuses_duplicate_key(self):
        self.ws.csv("data.csv", make_rows(dup="2005-03"))
        code, out = self.ws.run("init", "data.csv", "--order-by", "month")
        self.assertNotEqual(code, 0)
        self.assertIn("2005-03", out)

    def test_allow_gaps_records_the_defect(self):
        self.ws.init(make_rows(drop={"2010-10"}), "--allow-gaps")
        init = json.loads((self.ws.dir / "analysis" / "LEDGER.jsonl").read_text().splitlines()[0])
        self.assertEqual(init["audit"]["missing_months"], ["2010-10"])

    # mutation testing
    def test_register_requires_a_mutant_or_a_reason(self):
        self.ws.init()
        t = self.ws.script("S1.py", SEASONAL)
        code, out = self.ws.register("S1", t)
        self.assertNotEqual(code, 0)
        self.assertIn("--mutant", out)
        code, out = self.ws.register("S1", t, "--no-mutant", "exact count on a frozen table")
        self.assertEqual(code, 0, out)

    def test_toothless_test_is_refused(self):
        self.ws.init()
        t = self.ws.script("T.py", TOOTHLESS)
        code, out = self.ws.register("T1", t, "--mutant", "shuffle-months")
        self.assertNotEqual(code, 0)
        self.assertIn("no teeth", out)
        kinds = [json.loads(l)["kind"] for l in (self.ws.dir / "analysis" / "LEDGER.jsonl").read_text().splitlines()]
        self.assertEqual(kinds[-1], "refused")  # the abandoned attempt stays on the record

    def test_real_seasonality_test_kills_its_mutants(self):
        self.ws.init()
        self.seasonal()
        reg = [json.loads(l) for l in (self.ws.dir / "analysis" / "LEDGER.jsonl").read_text().splitlines()][-1]
        self.assertGreaterEqual(reg["mutants"][0]["killed"], 4)
        self.assertEqual(reg["smoke"]["verdict"], "survived")

    def test_wrong_mutant_is_refused(self):
        # shuffling whole years keeps each year's November peak, so it cannot kill a seasonality claim
        self.ws.init()
        t = self.ws.script("S1.py", SEASONAL)
        code, out = self.ws.register("S1", t, "--mutant", "shuffle-years")
        self.assertNotEqual(code, 0)
        self.assertIn("no teeth", out)

    def test_crashing_test_fails_the_smoke_run(self):
        self.ws.init()
        t = self.ws.script("C.py", CRASHES)
        code, out = self.ws.register("C1", t, "--no-mutant", "x")
        self.assertNotEqual(code, 0)
        self.assertIn("smoke run", out)

    # static analysis
    def test_lint_blocks_future_peeking_in_forecasts_only(self):
        self.ws.init()
        t = self.ws.script("L.py", LEAKY)
        code, out = self.ws.register("L1", t, "--no-mutant", "x", category="predictive", kind="forecast")
        self.assertNotEqual(code, 0)
        self.assertIn("centred-window", out)
        code, out = self.ws.register("L2", t, "--no-mutant", "x")  # descriptive: a warning, not a block
        self.assertEqual(code, 0, out)
        self.assertIn("lint warning", out)

    def test_lint_requires_score_from_in_ordered_workspaces(self):
        self.ws.init()
        t = self.ws.script("N.py", 'import json\nprint(json.dumps({"verdict": "survived"}))\n')
        code, out = self.ws.register("N1", t, "--no-mutant", "x")
        self.assertNotEqual(code, 0)
        self.assertIn("score-from", out)

    def test_lint_blocks_unseeded_randomness(self):
        self.ws.init()
        t = self.ws.script("U.py", UNSEEDED)
        code, out = self.ws.register("U1", t, "--no-mutant", "x")
        self.assertNotEqual(code, 0)
        self.assertIn("unseeded", out)

    def test_lint_blocks_reading_the_holdout_directly(self):
        self.ws.init()
        t = self.ws.script("H.py", SEASONAL.replace('os.environ["DATA"]', '"analysis/holdout.csv"'))
        code, out = self.ws.register("H1", t, "--no-mutant", "x")
        self.assertNotEqual(code, 0)
        self.assertIn("workspace-file", out)

    # freezing, budget, replay, tamper evidence
    def test_test_edited_after_registration_cannot_run(self):
        self.ws.init()
        t = self.seasonal()
        t.write_text(t.read_text() + "\n# tweak\n")
        code, out = self.ws.run("run", "S1")
        self.assertNotEqual(code, 0)
        self.assertIn("changed after registration", out)

    def test_one_look_per_claim_and_budget(self):
        self.ws.init(None, "--budget", "1")
        self.seasonal("S1")
        self.seasonal("S2")
        self.ws.ok("run", "S1")
        code, out = self.ws.run("run", "S1")
        self.assertIn("one confirmatory look", out)
        code, out = self.ws.run("run", "S2")
        self.assertIn("budget spent", out)

    def test_replay_is_byte_identical(self):
        self.ws.init()
        self.seasonal()
        self.ws.ok("run", "S1")
        self.assertIn("IDENTICAL", self.ws.ok("replay", "S1"))

    def test_verify_detects_a_forged_result(self):
        self.ws.init()
        self.seasonal()
        self.ws.ok("run", "S1")
        led = self.ws.dir / "analysis" / "LEDGER.jsonl"
        led.write_text(led.read_text().replace('"verdict": "survived"', '"verdict": "falsified"', 1))
        code, out = self.ws.run("verify")
        self.assertIn("chain broken", out)

    def test_verify_detects_an_edited_holdout(self):
        self.ws.init()
        h = self.ws.dir / "analysis" / "holdout.csv"
        h.write_text(h.read_text().replace(",", ";", 1))
        code, out = self.ws.run("verify")
        self.assertIn("holdout.csv changed", out)

    # types, dependencies, coverage
    def test_prescriptive_needs_support_and_is_blocked_until_established(self):
        self.ws.init()
        self.seasonal("S1")
        t = self.ws.script("P.py", SEASONAL)
        code, out = self.ws.register("P1", t, "--mutant", "shuffle-months", category="prescriptive", kind="policy")
        self.assertIn("must rest on", out)
        f = self.ws.script("F1.py", SEASONAL)
        code, out = self.ws.register("F1", f, "--mutant", "shuffle-months", category="predictive", kind="timing")
        self.assertEqual(code, 0, out)
        code, out = self.ws.register("P1", t, "--mutant", "shuffle-months", "--rests-on", "F1",
                                     category="prescriptive", kind="policy")
        self.assertEqual(code, 0, out)
        self.ws.ok("run", "P1")
        self.ws.ok("replay", "P1")
        self.assertIn("blocked: rests on F1", self.ws.ok("report"))

    def test_waiver_shows_in_coverage(self):
        self.ws.init()
        self.ws.ok("waive", "diagnostic/causal", "--reason", "no intervention in window")
        report = self.ws.ok("report")
        self.assertIn("no intervention in window", report)
        self.assertIn("**not covered**", report)

    # prospective retests (chaos: revisions, gaps, thin windows)
    def test_extend_counts_revisions_and_refuses_gappy_fresh_rows(self):
        self.ws.init(make_rows(years=20))
        full = make_rows(years=23)
        full[5][1] = "999.00"  # a revised sealed row
        self.ws.csv("newer.csv", full)
        out = self.ws.ok("extend", "newer.csv")
        self.assertIn("36 rows", out)
        self.assertIn("1 sealed rows revised", out)
        gappy = [r for r in make_rows(years=24) if r[0] != "2022-06"]
        self.ws.csv("gappy.csv", gappy)
        code, out = self.ws.run("extend", "gappy.csv")
        self.assertIn("fail the audit", out)

    def test_retest_waits_for_enough_fresh_data_then_scores_it(self):
        self.ws.init(make_rows(years=20))
        self.seasonal("S1", "--min-fresh", "36")
        self.ws.ok("run", "S1")
        self.ws.csv("plus1.csv", make_rows(years=21))
        self.ws.ok("extend", "plus1.csv")
        self.assertIn("pending", self.ws.ok("retest", "S1"))
        self.ws.csv("plus3.csv", make_rows(years=23))
        self.ws.ok("extend", "plus3.csv")
        self.assertIn("HELD", self.ws.ok("retest", "S1"))

    def test_retest_refuses_a_test_that_ignores_score_from(self):
        self.ws.init(make_rows(years=20))
        t = self.ws.script("I.py", SEASONAL.replace('F = os.environ.get("SCORE_FROM")', 'F = None  # SCORE_FROM ignored'))
        code, out = self.ws.register("I1", t, "--mutant", "shuffle-months")
        self.assertEqual(code, 0, out)
        self.ws.ok("run", "I1")
        self.ws.csv("plus3.csv", make_rows(years=23))
        self.ws.ok("extend", "plus3.csv")
        self.assertIn("does not honour SCORE_FROM", self.ws.ok("retest", "I1"))


class HistoryModeTests(unittest.TestCase):
    def test_confirmatory_runs_get_history_and_score_only_the_holdout(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = Workspace(tmp)
            ws.init()
            src = SEASONAL.replace('print(json.dumps({', 'print(json.dumps({"rows_seen": len(rows), ')
            t = ws.script("H.py", src)
            code, out = ws.register("H1", t, "--mutant", "shuffle-months")
            self.assertEqual(code, 0, out)
            res = json.loads(ws.ok("run", "H1").split("  ", 1)[1])
            self.assertEqual(res["rows_seen"], 240)      # explore + holdout available as history
            self.assertEqual(res["scored_from"], "2010-01")  # scoring starts at the holdout
            self.assertEqual(res["years"], 10)
            self.assertIn("IDENTICAL", ws.ok("replay", "H1"))
            self.assertIn("0 failure(s)", ws.ok("audit"))


class PanelTests(unittest.TestCase):
    def test_panel_allows_repeated_periods_and_splits_on_a_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = Workspace(tmp)
            rows = [[str(2000 + i // 7), f"{i}", f"{i % 3}"] for i in range(70)]  # 7 rows per year
            ws.csv("data.csv", rows)
            code, out = ws.run("init", "data.csv", "--order-by", "month", "--unstaged")
            self.assertIn("duplicate_keys", out)
            ws.ok("init", "data.csv", "--order-by", "month", "--panel", "--unstaged")
            ex = (ws.dir / "analysis" / "explore.csv").read_text().splitlines()[1:]
            ho = (ws.dir / "analysis" / "holdout.csv").read_text().splitlines()[1:]
            self.assertFalse({r.split(",")[0] for r in ex} & {r.split(",")[0] for r in ho})


class StagedFlowTests(unittest.TestCase):
    """The audited workflow: confirmed roles, stages in order, paper, audit."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ws = Workspace(self.tmp.name)
        self.ws.init(staged=True)

    def tearDown(self):
        self.tmp.cleanup()

    def schema(self, *extra):
        return self.ws.ok("schema", "--time", "month", "--target", "a", "--feature", "b", "--confirmed-by", "test", *extra)

    def claim(self, hid, category, kind, src=SEASONAL, *extra):
        t = self.ws.script(f"{hid}.py", src)
        return self.ws.register(hid, t, "--mutant", "shuffle-months", *extra, category=category, kind=kind)

    def test_register_needs_a_confirmed_schema(self):
        code, out = self.claim("S1", "descriptive", "seasonality")
        self.assertIn("no confirmed schema", out)

    def test_schema_needs_a_target_and_every_column(self):
        code, out = self.ws.run("schema", "--time", "month", "--feature", "a,b", "--confirmed-by", "x")
        self.assertIn("--target", out)
        code, out = self.ws.run("schema", "--time", "month", "--target", "a", "--confirmed-by", "x")
        self.assertIn("unassigned", out)
        code, out = self.ws.run("schema", "--time", "month", "--target", "a", "--feature", "a,b", "--confirmed-by", "x")
        self.assertIn("conflicting roles", out)

    def test_stages_run_in_order(self):
        self.schema()
        code, out = self.claim("G1", "diagnostic", "driver")
        self.assertIn("close descriptive", out)
        code, out = self.claim("S1", "descriptive", "seasonality")
        self.assertEqual(code, 0, out)
        code, out = self.ws.run("close", "descriptive", "--note", "x")
        self.assertIn("run and replay", out)
        self.ws.ok("run", "S1")
        self.ws.ok("replay", "S1")
        code, out = self.ws.run("close", "descriptive")
        self.assertIn("neither tested nor waived", out)
        self.ws.ok("close", "descriptive", "--note", "only seasonality matters here")
        code, out = self.claim("S2", "descriptive", "trend")
        self.assertIn("closed", out)
        self.ws.ok("reopen", "descriptive", "--reason", "referee asked for a trend claim")
        code, out = self.claim("S2", "descriptive", "trend")
        self.assertEqual(code, 0, out)

    def test_leaky_column_blocks_forecasts(self):
        self.ws.ok("schema", "--time", "month", "--target", "a", "--exclude", "b:recorded after the outcome", "--confirmed-by", "test")
        self.ws.ok("waive", "descriptive", "--reason", "x")
        self.ws.ok("close", "descriptive")
        self.ws.ok("waive", "diagnostic", "--reason", "x")
        self.ws.ok("close", "diagnostic")
        leaky = SEASONAL.replace('if r["a"]', 'if r["a"] and r["b"]')
        code, out = self.claim("F1", "predictive", "timing", leaky)
        self.assertIn("excluded-column", out)

    def test_paper_and_audit(self):
        self.schema()
        self.claim("S1", "descriptive", "seasonality")
        self.ws.ok("run", "S1")
        self.ws.ok("replay", "S1")
        fish = self.ws.script("fish.py", SEASONAL)
        self.ws.ok("goldfish", "S1", "--test", fish, "--agent", "g1", "--note", "read peak as the annual maximum")
        self.ws.ok("paper")
        paper = (self.ws.dir / "analysis" / "PAPER.md").read_text()
        for part in ("## Abstract", "### 1.1 Variables", "## 2. Methods", "#### S1", "## 4. Threats to validity", "read peak as the annual maximum"):
            self.assertIn(part, paper)
        out = self.ws.ok("audit")
        self.assertIn("0 failure(s)", out)
        fish.write_text(fish.read_text().replace(">= 0.8", ">= 0.1"))  # a replication edited after the fact
        code, out = self.ws.run("audit")
        self.assertNotEqual(code, 0)
        self.assertIn("FAIL", out)


if __name__ == "__main__":
    unittest.main(verbosity=1)
