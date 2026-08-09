---
name: capacity
description: >-
  Capacity planning with explicit assumptions, formulas, and reproducible arithmetic.
  Computes RPS, storage growth, bandwidth and egress cost, concurrency, connection demand,
  cache sizing, worker counts, and monthly cost — with safety margins, ranges, and a
  sensitivity analysis naming the input to measure first.
argument-hint: "[what to size, e.g. 'API for 50k users' or '5x traffic spike']"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/calculators/*), Read
---

# Capacity planning

Size: **$ARGUMENTS**

Follow `${CLAUDE_PLUGIN_ROOT}/frameworks/capacity-planning/procedure.md`. Summary below; read
the framework if anything is ambiguous.

## 1. Establish inputs

Infer from the repository and from what the user already said. Ask at most **3** questions,
and only ones whose answer changes the result.

**Apply the sensitivity test before asking**: compute at both extremes of the plausible range.
If the recommendation is the same at both, do not ask — state the assumption and the range.

Where unknown, **assume small** and label it.

## 2. Run the calculators

```bash
cd ${CLAUDE_PLUGIN_ROOT}/calculators
python3 -m oab_calc --list
python3 -m oab_calc rps --users=100 --dau-share=0.3 --sessions-per-day=2 \
                        --requests-per-session=40 --peak-factor=10
```

Order matters — later calculators consume earlier results:

```
rps ──┬──▶ bandwidth · concurrency ──▶ connections
      ├──▶ cache
      └──▶ queue
storage ──▶ cost ◀── complexity points
```

**Peak for provisioning, average for volume and cost.**

Peak factors when unmeasured: single-timezone consumer app 10 · business tool 4 ·
multi-region 2 · global consumer 1.5.

If `python3` is unavailable, compute from the formulas in
`${CLAUDE_PLUGIN_ROOT}/calculators/README.md` and **say that you did so**. A silent fallback
is exactly the failure the calculators exist to prevent.

## 3. Report the full envelope

Never a bare number. In this order, for each calculation:

```
Assumptions   each labelled observed | stated | assumed | calculated, with a confidence
Formula       the literal expression
Calculation   with values substituted, so it can be checked by hand
Result        with units, and a range if any input is uncertain
Safety margin the headroom applied, and why
Confidence    propagated from the weakest input
Sensitivity   which single input most changes the result
```

At most **2 significant figures** on anything derived from an assumption. `0.28 RPS` is
honest; `0.2777 RPS` is a lie about precision.

Where the conclusion holds across the entire plausible range, say so plainly — it is a
stronger finding than the point estimate.

## 4. State what the numbers rule in and out

The deliverable is not the numbers. It is what they justify and what they refuse, each with
the threshold. Consult `${CLAUDE_PLUGIN_ROOT}/knowledge/<domain>/README.md` for the relevant
thresholds.

## 5. Emit the artifact

Write `.oab/capacity.json` conforming to
`${CLAUDE_PLUGIN_ROOT}/schemas/capacity-result.schema.json`. The calculators emit this
directly with `--json`.
