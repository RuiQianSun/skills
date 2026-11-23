# Elephant Goldfish Analyst

An AI data-analysis workflow that turns a dataset into insights you can **test, falsify, trace and repeat**, and that keeps re-testing them as new data arrives.

- The **elephant** is the main agent. It remembers everything, explores the data, proposes claims, and keeps an append-only evidence ledger. Because it remembers everything, it is also the one most likely to fool itself.
- **Goldfish** are fresh-context subagents that remember nothing. A *critic* goldfish attacks each claim before it is tested; a *tester* goldfish re-tests it blind afterwards, writing its own code from the claim text alone.
- An **insight** is a claim that survived all of that and would change a decision. Everything else is reported as a hunch, a refuted claim, or trivia.

## What is in this folder

| Path | What it is |
|---|---|
| `SKILL.md` | The agent instructions (a Claude Code / Claude skill). |
| `agents/openai.yaml` | Display metadata for Codex. |
| `scripts/ledger.py` | The evidence ledger. Python 3 standard library only. Run `python3 scripts/ledger.py --help`. |
| `scripts/test_ledger.py` | Test suite for the ledger (`python3 scripts/test_ledger.py`, about 6 seconds). |
| `examples/` | Four worked runs on public data, each with its ledger, tests, goldfish scripts and generated `analysis/INSIGHTS.md`. |

The examples, from simplest to most complete: `wine` (the first run, sklearn's wine data), `tire-stores` (US tire-store sales from FRED), `canada-tire-stores` (Statistics Canada, NAICS 4413), and `coverage-other-provinces` (every feature: typed claims, critic review, coverage map, retest on data published after the seal).

## Install

**Claude Code:** copy the folder into your skills directory, then start a new session.

```bash
cp -r elephant-goldfish-analyst ~/.claude/skills/
```

**Claude apps (claude.ai, desktop):** upload the zip under Settings, Capabilities, Skills, if your organisation allows custom skills.

**Any other agent:** give it `SKILL.md` as instructions and `scripts/ledger.py` as a tool. The workflow needs an agent that can run shell commands and start subagents with a fresh context.

Requirements: Python 3.9+ for the ledger. The test scripts an agent writes usually need `pandas`, `numpy` and `scipy` (the examples also use `scikit-learn`).

## Use

Ask the agent for an analysis it can stand behind, for example: "Use elephant-goldfish-analyst on `sales.csv`. I want to know what drives our fall demand by region." For time series it will split by date, explore the past and confirm on the future.

Before you start, write down what your team already knows in `analysis/KNOWN.md` (the agent asks for it). Claims that only restate it are treated as trivia.

When new data is published, re-test everything already established:

```bash
python3 scripts/ledger.py extend new_full_file.csv
```

```bash
python3 scripts/ledger.py retest all
```

```bash
python3 scripts/ledger.py report
```

## How it earns trust: the verification layers

Ordered from cheapest to dearest. Each layer catches something the ones above cannot.

| Layer | Cost | What it contains |
|---|---|---|
| 1. Structure | free | Sealed explore/holdout split (by date for time series), frozen hashed tests, one holdout look per claim, holdout budget, typed claims, prescriptive claims blocked until their support is established, hash-chained ledger. |
| 2. Static checks | instant | Data audit before sealing (gaps, duplicates, suppressed cells), a lint for future-peeking code and hard-coded files, the output contract. |
| 3. Runtime verification | seconds | Smoke run on explore data, mutation gate (the test must falsify copies of the data with the claimed pattern destroyed), holdout run, byte-identical replay, retests on newly published data. |
| 4. Agent judgment | minutes | Critic goldfish (trivial? worded beyond its test? would the decision change? right type? uses data not yet available?), tester goldfish on more than one model, reconciling disagreements. |
| 5. Human review | your time | Which insights matter, what the team already knows, field tests of prescriptive claims. |

## Insight types

Every claim declares a category and a kind, and each kind has its own standard of evidence (`python3 scripts/ledger.py types`).

- **Descriptive** (what happened): level, trend, seasonality, composition, comparison, distribution, anomaly, change point.
- **Diagnostic** (why): attribution, driver (association only), causal (needs a design and a placebo), root cause.
- **Predictive** (what next): forecast, leading indicator, classification, timing.
- **Prescriptive** (what to do): policy, allocation, trigger. Must rest on an established predictive or diagnostic claim.

The report ends with a coverage map: each kind is tested, waived with a reason (which says what data would unlock it), or not covered.

## Reading a report

| Status | Meaning |
|---|---|
| established | survived the holdout, replayed identically, every tester agreed |
| established (narrowed) | holds, but only in the narrower reading a tester stated; quote that reading |
| refuted | falsified and confirmed the same way (a finding too) |
| contested | a tester disagreed; not an insight until reconciled |
| blocked | a prescriptive claim whose supporting claim is not established |
| held / BROKE / REVIVED on fresh data | the frozen test rerun on data published after the seal |

## Known limits

- It checks whether a pattern is real, not whether it is interesting. Relevance stays with you and the critic.
- Associations are never causes. Prescriptive claims are backtests until a field test confirms them.
- Recorded sales understate demand when stores run out, so stock-out data makes policy tests honest.
- Three rules rest on the agent's discipline alone: explore without reading the holdout, set honest thresholds, and judge novelty.
- Small samples (a handful of years) limit what any test can establish; reports say so.
