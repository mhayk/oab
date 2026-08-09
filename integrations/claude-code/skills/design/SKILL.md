---
name: design
description: >-
  Design a system architecture proportional to its actual requirements: quantifies scale,
  computes capacity, applies a complexity budget, generates options with explicit rejections,
  and produces ADRs with measurable revisit triggers.
argument-hint: "[brief description of the system]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash(python3 ${CLAUDE_PLUGIN_ROOT}/calculators/*)
---

# Design a system

System: **$ARGUMENTS**

Follow `${CLAUDE_PLUGIN_ROOT}/frameworks/architecture-design/procedure.md`. Read it now — this
skill is the entry point, not the full procedure.

## Pipeline

```
1 FRAME  2 GATHER  3 ASSUME  4 QUANTIFY  5 CLASSIFY  6 RETRIEVE
7 OPTION  8 CONSTRAIN ──over budget──▶ back to 7  9 DECIDE  10 TRIGGER  11 RECORD
```

Steps 4, 5, 8 and 10 are the ones that produce proportionality. Do not skip them.

## Key moves

**Frame (1).** Watch for the mis-frame: "design a scalable API" is usually "choose a datastore
and a deployment target for something small". Design the real question.

**Gather (2–3).** `frameworks/discovery/procedure.md`. **At most 5 questions**, and apply the
sensitivity test first — if the recommendation does not change across the plausible range of
an unknown, do not ask. Where unknown, assume small and label it.

**Quantify (4).** Run the calculators. `frameworks/capacity-planning/procedure.md`.

**Classify (5).** Determine stage 0–5, then the complexity budget:
`available = 4 + 1.5 × (engineers − 2) + 4 × dedicated_ops`. Two developers ≈ 4 points.

**Retrieve (6).** Read `${CLAUDE_PLUGIN_ROOT}/knowledge/<domain>/README.md` for each domain the
design touches, and select units whose `applies_at_stage` includes this system's stage. Name
the file and the condition — never "consult the knowledge base".

Start with `knowledge/caching/when-not-to-cache.md` before any caching decision, and
`knowledge/messaging/when-you-need-streaming.md` before any broker decision.

**Option (7).** At least two, one of which is the **simplest viable option** stated fairly.
Rejected options need the measurement that would change the answer.

**Constrain (8).** Over budget ⇒ **return to step 7 and generate simpler options.** Do not
proceed and justify the expensive one.

**Trigger (10).** At least one measurable trigger. Where capacity analysis produced a
sensitivity limit, that limit is a trigger.

## Output

Write `.oab/design.json` **first** — conforming to
`${CLAUDE_PLUGIN_ROOT}/schemas/design-output.schema.json` — then
`docs/architecture/design.md` from it, using `${CLAUDE_PLUGIN_ROOT}/templates/system-design.md`.

Writing the artifact first makes a skipped step detectable as a missing field.

**Adaptive output.** Emit only sections with content for this system. A stage-1 design has no
partitioning, multi-region, or streaming section. Executive summary first, ~1 page.

Include one Mermaid diagram, capped at ~12 nodes.

## Report the budget plainly

```
Complexity: 4 / 4 — no headroom. Adding a cache requires removing something
or adding an engineer.
```

And state the limitations: the budget is a calibrated heuristic, not a measurement.
