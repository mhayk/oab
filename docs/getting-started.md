# Getting started

> Released as [v0.1.7](https://github.com/mhayk/oab/releases/tag/v0.1.7) — the M1 milestone,
> install and both commands verified with live evidence (see `examples/live-run/` and
> `examples/live-review/`). One caveat: artifact-validation hooks currently fire via
> `--plugin-dir` but not for marketplace installs in headless sessions
> ([#45](https://github.com/mhayk/oab/issues/45)).

## Install

```
/plugin marketplace add mhayk/oab
/plugin install oab@oab
```

Or from a checkout, which is the reliable path today:

```bash
git clone https://github.com/mhayk/oab && cd oab
claude --plugin-dir ./
```

## Your first run

### Size something

```
/oab:capacity "API for a marketplace with 5,000 users"
```

You get assumptions labelled by source, the literal formula, the substituted calculation, the
result with units, the safety margin, a propagated confidence, and — most usefully — **which
single input to go and measure first**.

### Review a repository

```
/oab:review
```

Establishes what the system actually is, then what scale it actually runs at, and only then
produces findings weighted by that scale. Writes `docs/architecture/review.md` and
`.oab/review.json`.

**Zero findings is a valid outcome.** If your architecture is proportional and the fundamentals
are in place, OAB says so and gives you triggers to watch instead of inventing work.

### Design a system

```
/oab:design "internal tool for expense approvals, 200 staff"
```

Asks at most five questions, and only ones whose answer changes the architecture. Writes
`docs/architecture/design.md` and `.oab/design.json`.

## Reading the output

Three things to look at first:

**The complexity budget.** `Complexity: 4 / 4 — no headroom` is the most actionable line. It
means adding anything requires removing something or adding an engineer.

**What was rejected.** More valuable than what was recommended. Each rejection carries the
measurement that would reverse it, so a "no" is a plan rather than an opinion.

**The sensitivity statement.** It names the assumption to go and measure. Sometimes it says the
recommendation holds across the whole plausible range — which means you can stop worrying about
the inputs entirely.

## When you disagree

OAB's reasoning is meant to be contestable. Every recommendation exposes its assumptions,
formulas and options, so you can point at the specific link you think is wrong.

Usually the fastest fix is correcting an **assumption**: they are all listed with a confidence,
and a wrong input produces a wrong answer far more often than wrong reasoning does.

## Running the calculators directly

No plugin needed. Standard-library Python, no install:

```bash
cd calculators
python3 -m oab_calc --list
python3 -m oab_calc rps --users=100 --dau-share=0.3 --sessions-per-day=2 \
                        --requests-per-session=40 --peak-factor=10
```

## Next

- [Principles](principles.md) — the ten rules behind every recommendation
- [Examples](../examples/) — reference output, with what to notice
- [Command reference](reference/commands.md)
- [Contributing knowledge](contributing/knowledge.md) — needs no understanding of the codebase
