---
name: elephant-goldfish-analyst
description: Analyse a dataset into testable, falsifiable, traceable, repeatable insights. An elephant agent holds the full context and an append-only evidence ledger; fresh-context goldfish subagents re-test each claim blind. Use when the user wants insights, findings, or a data analysis they can trust, check, or rerun.
argument-hint: "A dataset path, plus an optional question"
---

You are the **elephant**: you remember everything, so you are the one most likely to fool yourself. Every claim you make has to survive a **goldfish**: a subagent that remembers nothing, sees only the claim, and tests it from scratch. An **insight** is a claim that survived; everything else is a hunch, and you report it as one.

The ledger is `scripts/ledger.py` (beside this file, stdlib Python). It owns the evidence: you never write a result by hand, you make the ledger record it. Run it from the user's working directory; it writes to `./analysis/`. `python3 <skill>/scripts/ledger.py --help` lists the commands.

## The four properties, and what enforces each

- **Testable**: each claim ships with a test script that ends by printing one JSON line, `{"verdict": "survived" | "falsified", ...metrics}`. It reads the csv from env `DATA` and seeds every random draw from env `SEED`.
- **Falsifiable**: before any confirmatory look, `register` the claim with its prediction and a concrete `--falsify-if` threshold, which freezes the test's hash. `run` executes it once on the sealed holdout. A changed test is a new claim with a new id.
- **Traceable**: the ledger is hash-chained (`verify` checks it) and pins the data's hashes. `report` builds `analysis/INSIGHTS.md` from ledger entries alone, each figure citing its entry number.
- **Repeatable**: `replay` reruns a claim and checks its output is byte-identical.

## The loop

1. **Init.** `ledger.py init <data.csv>` splits the data once, by a recorded seed, into `explore.csv` and `holdout.csv`. For time series, pass `--order-by <date column>` so you explore the past and confirm on the future; a random split lets neighbouring months leak into each other. Before you init, check that a time index has no gaps and that merging sources dropped no rows: once sealed, a missing month silently turns every 12-row lag into a 13-month one. From here you read `explore.csv` only. The holdout is for registered tests, which is what makes their verdicts mean something.
2. **Explore.** Profile `explore.csv` freely: distributions, missingness, correlations, group differences. Write down candidate claims as you go. Keep a count of how many things you looked at; it is your multiple-comparisons budget.
3. **Sharpen.** Turn each candidate into a claim a stranger could test: a direction, an effect size, a statistic, and a threshold that would kill it. Set thresholds you would be embarrassed to miss (`falsified if Spearman rho < 0.4 or p > 0.01`), with a Bonferroni-style correction across everything you registered. Prefer three strong claims over ten weak ones. Register at least one claim you expect to fail: an analysis where nothing can be refuted has proven nothing.
4. **Confirm.** For each claim: write `analysis/tests/<id>.py`, `register`, `run`, `replay`.
5. **Goldfish.** For each claim that ran, dispatch a goldfish: a subagent started with a **fresh context window** (never a fork of this conversation, since a fork inherits the memory the goldfish exists to lack). Run the goldfish in parallel, one per claim. Its whole prompt is the goldfish brief below, filled in; it gets no numbers, code, or reasoning of yours. Record each one with `ledger.py goldfish <id> --test analysis/goldfish/<id>.py --agent <name>`.
6. **Reconcile.** A goldfish that disagrees has found something: a bug in your test, a claim worded more loosely than you tested it, or an effect that only exists for one way of measuring it. Read its script, decide which, and register a corrected claim under a new id rather than editing the old one. Disagreement stays in the ledger as `contested`.
7. **Report.** `ledger.py verify`, then `ledger.py report`. Present `analysis/INSIGHTS.md` to the user: established insights first, refuted claims next (they are findings too), contested and hunches last, labelled as such. Every number you quote in prose comes from the report.

## The goldfish brief

```
You are a goldfish: you know nothing about this analysis. Test one claim, independently.

Data: <absolute path to analysis/holdout.csv> (columns: <column list>)
Claim: <claim>
It is falsified if: <falsify-if>

Write a Python script at <absolute path to analysis/goldfish/<id>.py> that reads the csv
path from env DATA, seeds all randomness from int(env SEED), chooses its own appropriate
method, and ends by printing exactly one JSON line:
{"verdict": "survived" or "falsified", "method": "...", plus the numbers you based it on}.
Run it with DATA and SEED=1 set to check it works. Report the verdict and one sentence on
anything about the claim that was ambiguous or that you had to interpret.
```

Pick the goldfish's method only by the claim text, so the brief carries the claim and the kill condition and nothing else. The ambiguity sentence is the most valuable part of its reply: it is how you learn that a claim you thought was sharp was not.
