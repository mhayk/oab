---
id: ADR-NNNN
title: <decision, stated as an action>
status: proposed          # proposed | accepted | superseded | deprecated | rejected
date: YYYY-MM-DD
deciders: []
supersedes: []
superseded_by: null
tags: []
complexity_delta: 0       # change in complexity points; negative is a simplification
monthly_cost_delta: { currency: GBP, value: 0 }
reversibility: easy       # easy | moderate | hard | one-way
confidence: high          # high | medium | low
triggers: []              # required once status is accepted
---

# ADR-NNNN — <title>

## Status
<status> — <date>

## Context
What is true today that forces a decision. Include the numbers.

## Requirements
- R1: measurable where possible
- R2:

## Constraints
Budget, team, timeline, regulatory, existing systems, skills.

## Options Considered

### Option A — <the simplest viable option>
Gains:
Costs:
Complexity: N points · Monthly cost: <range> · Reversibility: <value>

### Option B — <alternative>
...

## Decision
The chosen option.

## Rationale
Why, **referencing the numbers**. A rationale with no numbers is a preference.

## Trade-offs Accepted
Never empty. An option with no downsides has not been understood.

## Consequences
What becomes true, including what becomes harder.

## Migration Path
How to get there, and how to get out.

## Observability
What must be measured to know this decision is still holding.

## Revisit Conditions
The trigger ids listed in the frontmatter, expanded. Each needs a metric, a source, a
comparator, a threshold with a unit, a sustained window, an action, and an owner.
