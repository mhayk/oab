---
id: complexity-cost
title: Operational Complexity as a First-Class Cost
description: >-
  A component's real price is its invoice plus its on-call surface, upgrade burden, and
  the engineer-hours needed to understand it when it breaks.
category: fundamentals
tags: [cost, operations, decision-making]
maturity: stable
confidence: high
applies_at_stage: ["0", "1", "2", "3", "4", "5"]
prerequisites: [proportional-architecture]
related: [managed-vs-self-hosted, operational-cost-model, maturity-stages]
complexity_cost: 0
trade_offs:
  - gains: "Architecture decisions made on total cost rather than on the invoice"
    costs: "Requires estimating engineering time, which is imprecise"
    when_worth_it: >-
      Whenever a decision trades money against operational surface, which is most
      infrastructure decisions. Being roughly right beats ignoring the larger term entirely.
failure_modes:
  - mode: "Only the invoice is compared"
    symptom: "A self-hosted option chosen to save money; the team then spends weeks operating it"
    detection: "Infrastructure cost falls while delivery velocity falls further"
    mitigation: "Compute the operational line explicitly and put both in the comparison"
  - mode: "Complexity points treated as precise"
    symptom: "Decisions defended by a score rather than by reasoning"
    detection: "An option rejected solely on a fractional point difference"
    mitigation: "Report the model as a heuristic; the score prompts the conversation, it does not end it"
triggers:
  - metric: "engineering time spent on infrastructure operations"
    comparator: ">"
    threshold: 20
    unit: "percent of team capacity"
    window: "sustained over 2 months"
    action: "Re-examine which components are earning their operational cost; consider managed replacements"
anti_patterns:
  - "Comparing a managed service price against a virtual machine price and calling it a saving"
  - "Adding a component whose operating cost exceeds the problem it solves"
references:
  - title: "Site Reliability Engineering: toil and its measurement"
    type: book
    accessed: 2026-08-09
  - title: "Total cost of ownership in infrastructure decisions"
    type: engineering-blog
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

The cost of a component is not what the provider charges. It is:

```
total = invoice
      + on-call surface        (it can wake someone up)
      + upgrade burden         (versions, patches, breaking changes)
      + failure modes          (new ways the system can break)
      + comprehension cost     (every engineer must learn why it exists)
```

OAB models the non-invoice part as **complexity points**, and converts them to money:

```
operational_cost_per_month = complexity_points × hours_per_point × loaded_hourly_rate
```

Defaults: 4 hours per point per month, £60/hour loaded — roughly **£240 per point per month**.

## When it applies

Any decision that trades money against operational surface. The arithmetic frequently inverts the
obvious answer:

> Self-hosting a database to save £250/month against a managed instance costs 3 complexity points,
> or about £720/month of engineering attention. The managed service is roughly **£470/month
> cheaper**, not £250/month more expensive.

It applies most strongly to small teams, where the operational line routinely exceeds the
infrastructure line — and is invisible in every cloud pricing calculator.

## When it does not apply

**When the team already operates the technology at scale.** The marginal cost of one more instance
of something you already run well is close to zero. The model charges for a technology, not per
instance, for exactly this reason.

**When operations are genuinely someone else's job.** With a platform team that already runs the
component as a service, the cost lands on their budget, not yours. Do not double-count it — though
do check they agree it is free.

**When the numbers are close.** The point estimate is not precise enough to decide between options
within roughly 20% of each other. Use it to notice order-of-magnitude mistakes, not to settle
close calls.

**For techniques rather than components.** TTL jitter, timeouts, and retries change how existing
components behave and add no operational surface. They cost 0.

## How it works

Operational cost is dominated by three things, which is why the weights in
`frameworks/complexity-budget/weights.yaml` are shaped as they are:

- **State.** Backup, restore, migration, replication, and failover are what make operations hard.
  Stateless components are far cheaper to run than stateful ones.
- **Self-hosting.** It transfers an entire operational domain — patching, capacity, failure
  handling — to your team.
- **Diversity.** Each additional technology multiplies what every engineer must know, and what
  every incident might involve.

## Trade-offs

The model is imprecise: `hours_per_point` is judgement, not measurement, and it varies enormously
with team experience. The alternative — ignoring the larger of the two cost terms — is worse. Being
roughly right about the dominant term beats being precise about the smaller one.

## Failure modes

The common failure is comparing invoices. The subtler one is treating the score as authoritative:
the number exists to prompt a conversation about whether the team can carry the thing, not to
settle an argument by arithmetic.

## Measurement

Track the share of engineering time spent on infrastructure operations rather than product work.
Above roughly 20% sustained, some component is not earning its cost.

Calibrate `hours_per_point` against your own incident and maintenance records rather than the
default.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Complexity points converted to money | Default; makes the invisible term visible |
| Explicit engineer-hour estimates per component | When deciding a single large migration |
| Invoice comparison only | Never, unless operations are genuinely externalised |

## References

Summarised from the cited sources. The point-to-hours conversion is OAB's own model and is
documented as a heuristic in `frameworks/complexity-budget/procedure.md`.
