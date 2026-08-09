---
id: managed-vs-self-hosted
title: Managed versus Self-Hosted
description: >-
  Comparing total cost rather than invoice, and the specific conditions under which
  self-hosting a stateful service becomes the cheaper option.
category: cost
tags: [cost, operations, managed-services]
maturity: reviewed
confidence: high
applies_at_stage: ["1", "2", "3", "4", "5"]
prerequisites: [operational-cost-model]
related: [complexity-cost, backup-restore-and-pitr]
complexity_cost: 0
trade_offs:
  - gains: "Managed services trade money for operational surface, which is the right trade for a small team"
    costs: "Higher invoice; less control over version, tuning, and failover behaviour; provider lock-in"
    when_worth_it: >-
      Managed is right until the invoice difference exceeds the operational cost of running
      it yourself — typically above roughly 3 to 5 engineers of dedicated platform capacity.
failure_modes:
  - mode: "Self-hosting chosen on invoice alone"
    symptom: "Infrastructure spend falls, delivery velocity falls further, backups untested"
    detection: "Rising share of engineering time on operations after the migration"
    mitigation: "Compute the operational line before deciding"
  - mode: "Managed service assumed to remove all responsibility"
    symptom: "No restore test, no failover drill, because the provider is trusted to handle it"
    detection: "No documented recovery procedure"
    mitigation: "Managed reduces operational surface; it does not remove ownership of recovery"
triggers:
  - metric: "managed service invoice"
    comparator: ">"
    threshold: 1000
    unit: "GBP/month for a single service"
    window: "sustained over 3 months"
    action: "Compare against the fully loaded cost of self-hosting, including on-call and restore testing"
anti_patterns:
  - "Self-hosting a stateful service with no dedicated operations capacity"
  - "Comparing a managed database price against a bare virtual machine price"
references:
  - title: "Managed service economics"
    type: engineering-blog
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

A managed service moves backup, patching, failover, and the pager to the provider, in exchange for
a higher invoice. The decision is about **where the operational burden lands**, not about price.

## When it applies

Every stateful component: databases, caches, queues, search, object storage.

Managed is the default below roughly 3–5 dedicated platform engineers. The crossover is not about
company size — it is about whether anyone's job is to operate infrastructure.

## When it does not apply

**When a compliance or residency requirement rules out the managed option.** Then the decision is
made and the operational cost is simply the price of the requirement.

**When you already run the technology.** Adding another instance to infrastructure you operate well
costs very little extra.

**At large invoice scale with real platform capacity.** Above roughly £1,000/month for a single
service and with dedicated operations staff, the arithmetic can genuinely favour self-hosting.
Compute it rather than assuming either way.

**For stateless components.** These are cheap to self-host — no backup, no restore, no replication —
so the trade is much less lopsided.

## How it works

The invoice difference funds someone else's expertise in the operations you would otherwise do
badly. The specific things a small team most often does badly:

- Restore testing. Backups exist; restores are untested until an incident.
- Version upgrades, especially major ones with breaking changes.
- Failover, which is only exercised when it is needed.
- Capacity headroom, noticed when it runs out.

## Trade-offs

Managed costs more money, offers less control over tuning and version timing, and creates provider
coupling. Self-hosting costs attention, and the attention is spent unpredictably — usually during
an incident.

## Failure modes

The subtle one is assuming a managed service removes ownership of recovery. It reduces the
operational surface; it does not mean you can skip a documented, tested restore procedure.

## Measurement

Compare total cost, not invoices:

```
managed_total      = invoice + (points × £240)
self_hosted_total  = invoice + (points × £240) + one-off migration cost
```

Track restore test frequency. A self-hosted database whose restore has never been tested is not
cheaper; it is unpriced risk.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Managed | Default below 3–5 dedicated platform engineers |
| Self-hosted | Large single-service invoice **and** dedicated operations capacity |
| Hybrid | Managed for stateful, self-hosted for stateless |

## References

Summarised from the cited source and the cost model in this repository.
