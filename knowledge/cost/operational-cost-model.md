---
id: operational-cost-model
title: Operational Cost Model
description: >-
  Converting complexity points into money, so that the engineering attention a component
  consumes appears in the same comparison as its invoice.
category: cost
tags: [cost, operations, tco]
maturity: reviewed
confidence: medium
applies_at_stage: ["1", "2", "3", "4", "5"]
prerequisites: [complexity-cost]
related: [managed-vs-self-hosted, observability-cost]
complexity_cost: 0
trade_offs:
  - gains: "The larger of the two cost terms becomes visible and comparable"
    costs: "Rests on two constants that are judgement rather than measurement"
    when_worth_it: >-
      Whenever an option trades money against operational surface. Being roughly right
      about the dominant term beats being precise about the smaller one.
failure_modes:
  - mode: "Constants used without calibration"
    symptom: "Model disagrees with the team's lived experience and gets dismissed"
    detection: "Estimated operational hours far from actual maintenance and incident time"
    mitigation: "Calibrate hours_per_point against your own records; the defaults are a starting point"
  - mode: "Double counting"
    symptom: "Operational cost charged to a team that does not operate the component"
    detection: "A platform team already runs it as a service"
    mitigation: "Charge the cost where it lands, and confirm the other team agrees it is free"
triggers:
  - metric: "share of engineering time on infrastructure operations"
    comparator: ">"
    threshold: 20
    unit: percent
    window: "sustained over 2 months"
    action: "Identify which components are not earning their operational cost; evaluate managed replacements"
anti_patterns:
  - "Presenting the output as a precise figure rather than an order of magnitude"
references:
  - title: "Site Reliability Engineering: eliminating toil"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

```
operational_cost_per_month = complexity_points × hours_per_point × loaded_hourly_rate
```

Defaults: **4 hours per point per month**, **£60/hour loaded** — about **£240 per point per month**.

Those hours cover patching and upgrades, incident diagnosis, capacity checks, backup verification,
and the time each new engineer spends learning why the component exists.

## When it applies

Any comparison where one option costs less money and more attention. The arithmetic frequently
inverts the invoice comparison:

| Option | Invoice | Points | Operational | Total |
| :-- | --: | --: | --: | --: |
| Managed database | £250 | 1 | £240 | **£490** |
| Self-hosted on a VM | £25 | 3 | £720 | **£745** |

The "cheap" option is £255/month more expensive.

## When it does not apply

**When the team already operates the technology well.** The model charges per technology, not per
instance. A second database on infrastructure you already run costs close to nothing extra.

**When operations genuinely belong to another team.** Charge the cost where it lands. Confirm with
that team rather than assuming.

**For close calls.** The output is an order of magnitude, not a quote. Do not use it to decide
between options within about 20% of each other.

**For techniques.** Timeouts, retries, TTL jitter and in-process caching add no operational
surface. They cost 0 points and therefore £0.

## How it works

The constants encode a claim: an average component consumes about half a day of somebody's month
once you count everything, and an engineer's loaded cost is roughly three times a naive hourly
rate. Both are defensible defaults and both should be replaced with your own numbers.

## Trade-offs

Imprecise by construction. The alternative — ignoring the term entirely, which every cloud pricing
calculator does — is worse, because for small teams this term is usually the larger one.

## Failure modes

Uncalibrated constants that disagree with lived experience cause the whole model to be dismissed,
including the part that was right. Calibrate early.

## Measurement

Track engineering hours spent on infrastructure operations for one quarter, divide by complexity
points, and replace the default. Above 20% of team capacity spent on operations, some component is
not earning its cost.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Points converted to money | Default |
| Explicit hour estimates per component | A single large migration decision |
| Invoice only | Never, unless operations are genuinely externalised |

## References

Summarised from the cited source; the conversion model is OAB's own.
