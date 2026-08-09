---
name: adr
description: >-
  Create or review an Architecture Decision Record with options, trade-offs, consequences,
  a migration path, required observability, and measurable revisit conditions. Use when a
  significant technical decision is being made or needs recording.
argument-hint: "[decision title]"
allowed-tools: Read, Glob
---

# Architecture Decision Record

Decision: **$ARGUMENTS**

Use `${CLAUDE_PLUGIN_ROOT}/templates/adr.md` and follow
`${CLAUDE_PLUGIN_ROOT}/frameworks/evolution-triggers/procedure.md` for the revisit conditions.

## 1. Number it

Find the highest existing `docs/adr/NNNN-*.md` and use the next number, zero-padded to four
digits. Create `docs/adr/` if it does not exist.

## 2. Establish context with numbers

An ADR whose context contains no numbers is an opinion with a template around it. State the
measured or assumed scale that forces this decision.

## 3. Generate at least two options

**One must be the simplest viable option**, stated fairly rather than as a straw man. Most
architecture failure is failing to consider "just use what you already have".

Each option needs: components, complexity cost, monthly cost range, reversibility
(easy/moderate/hard/one-way), and trade-offs.

`trade_offs` on the selected option must **never be empty**. An option with no downsides has
not been understood.

For rejected options, give **the measurement that would change the answer**, not merely why
it lost.

## 4. Refuse to complete without

- Two or more options → otherwise no alternative was considered
- Non-empty trade-offs on the decision
- At least one **measurable** trigger

A trigger needs all of: metric, source (where it is actually read), comparator, threshold with
a unit, a sustained window, an action that is a *next step* rather than a predetermined
solution, and an owner.

> Good: "Re-run capacity analysis; evaluate broker options against measured demand"
> Bad: "Add a message broker" — this pre-decides what the analysis should conclude

## 5. Validate

Frontmatter must conform to `${CLAUDE_PLUGIN_ROOT}/schemas/adr.schema.json`. Note that
`status: accepted` requires at least one trigger, and `status: superseded` requires
`superseded_by`.
