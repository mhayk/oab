---
id: bulkheads
title: Bulkheads
description: >-
  Isolating resource pools per dependency so that one slow dependency cannot consume the
  capacity every other request path needs.
category: reliability
tags: [bulkhead, isolation, resource-pools]
maturity: stable
confidence: high
applies_at_stage: ["2", "3", "4", "5"]
prerequisites: [timeouts]
related: [circuit-breakers, graceful-degradation, failure-mode-analysis]
complexity_cost: 0
trade_offs:
  - gains: "One dependency's degradation is contained to the paths that use it"
    costs: "Lower total utilisation, because capacity reserved for one pool cannot serve another"
    when_worth_it: >-
      When one dependency is materially less reliable than the rest, or when a low-value
      path shares a pool with a revenue-critical one.
failure_modes:
  - mode: "Pools sized from total capacity divided evenly"
    symptom: "Critical path starved while a background path holds reserved capacity"
    detection: "Rejections on the critical path while overall utilisation is low"
    mitigation: "Size each pool from its own measured concurrency, not by division"
  - mode: "Bulkhead without a defined rejection behaviour"
    symptom: "Pool exhaustion produces an unhandled error instead of a degraded response"
    detection: "Errors attributable to pool acquisition"
    mitigation: "Define what happens when the pool is full, per path"
anti_patterns:
  - "One shared connection pool for every outbound dependency"
references:
  - title: "Release It! Bulkhead"
    author: "Michael T. Nygard"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

Separate resource pools — threads, connections, or concurrency permits — per dependency, so
exhaustion of one does not affect the others. Named after ship compartments: a breach floods one
section, not the hull.

## When it applies

- One dependency is materially less reliable than the rest.
- A low-value path shares resources with a revenue-critical one.
- An external third-party call sits in a request path alongside internal calls.

The canonical case: a payment provider called synchronously during checkout. Without isolation, a
provider stall consumes the whole web worker pool and takes down browsing, search, and login too.

## When it does not apply

**Single-dependency systems.** With one downstream, isolation has nothing to isolate from.

**When utilisation is already the constraint.** Bulkheads reduce effective utilisation because
reserved capacity cannot be shared. On a system already tight on capacity, this trade may not be
affordable — fix capacity first.

**Where the dependency is on every path anyway.** Isolating the primary database from itself
achieves nothing; if every request needs it, its failure is total regardless.

## How it works

Each dependency gets its own bounded pool sized from its own measured concurrency (Little's Law plus
a tail multiplier). When a pool is full, calls on that path fail fast with a defined behaviour
rather than queueing on a shared resource.

## Trade-offs

Total utilisation falls, because capacity reserved for one pool sits idle when that dependency is
quiet. That is the price of containment, and it is usually worth paying for the path that earns
revenue.

## Failure modes

The sizing failure is dividing total capacity evenly rather than sizing each pool from its own
demand, which starves the busy path while the quiet one holds reserve.

## Measurement

Track pool utilisation and rejection rate per dependency. Rejections on one pool with low overall
utilisation means the sizing is wrong; rejections across all pools means capacity is wrong.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Per-dependency pools | Default where dependencies differ in reliability |
| Separate processes or services | When isolation must survive a process crash, not just pool exhaustion |
| Circuit breaker | When the concern is sustained failure rather than resource contention |

## References

Summarised from the cited source.
