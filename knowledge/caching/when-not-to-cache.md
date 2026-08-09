---
id: when-not-to-cache
title: When Not to Cache
description: >-
  The thresholds below which a cache adds a component, a failure mode, and a class of
  staleness bug in exchange for no measurable benefit.
category: caching
tags: [caching, overengineering, decision-making]
maturity: stable
confidence: high
applies_at_stage: ["0", "1", "2", "3", "4", "5"]
related: [cache-aside, cache-sizing, cache-stampede, proportional-architecture]
complexity_cost: 0
trade_offs:
  - gains: "Avoids a component, a staleness class, and an invalidation problem"
    costs: "Origin load that a cache would have relieved"
    when_worth_it: >-
      Whenever the relieved load is a small share of what the origin already handles
      comfortably, which at low traffic is nearly always.
failure_modes:
  - mode: "Cache added on intuition"
    symptom: "New staleness bugs; no measurable latency improvement"
    detection: "No before-and-after measurement of origin load or latency"
    mitigation: "Measure the dominant query and what a cache would actually relieve"
  - mode: "Cache used to hide a slow query"
    symptom: "Cold cache produces the original latency; first request after deploy is slow"
    detection: "Large gap between cached and uncached latency"
    mitigation: "Fix the query; a cache over an unindexed query is a latency landmine"
anti_patterns:
  - "Caching before profiling"
  - "Caching data that changes on nearly every read"
references:
  - title: "Latency numbers every programmer should know"
    type: engineering-blog
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

The inverse of the usual caching document: the conditions under which a cache is **not** justified.
Listed first in this domain deliberately, because reflexive caching is one of the most common
sources of unnecessary complexity and of subtle bugs.

## When it applies

Do **not** add a cache when any of these hold:

| Condition | Why |
| :-- | :-- |
| No single key exceeds ~10 requests/second | The relieved load is negligible |
| Recomputation costs under ~10 ms | You are caching to save less than the network round trip to the cache |
| The data changes on nearly every read | Hit rate will be low; you have added a component for nothing |
| The origin is comfortable | Relieving 5% of a database at 10% utilisation achieves nothing measurable |
| Staleness is unacceptable and TTL would be near zero | A cache with a 1-second TTL is a component with a rounding error of benefit |
| The slow thing is a missing index | Fix the query; a cache over an unindexed query hides a landmine |

Compute what the cache would relieve, in absolute terms, before adding it. "Improves read
performance" is not a justification; "removes 112 queries/second from a database doing 312" is.

## When it does not apply

That is — cases where a cache **is** justified despite looking marginal:

**Shared state across instances.** Sessions, rate-limit counters, and idempotency keys cannot live in
process memory across a horizontally-scaled fleet. The justification is coordination, not load
relief — and naming the real reason matters, because it determines the failure behaviour to design
for.

**Protecting an expensive external dependency**, particularly a rate-limited or per-call-priced API.
Here the saving is money or quota, not latency.

**Absorbing a known spike** whose shape is understood, such as a scheduled campaign.

## How it works

A cache is a managed component (1 complexity point), a new failure mode, and a permanent question on
every write path: what invalidates this. Those costs are paid continuously; the benefit must be
measurable to be worth them.

## Trade-offs

Not caching costs origin load. At low traffic that load is free, because the origin is idle. The
trade only becomes favourable when the origin is genuinely under pressure.

## Failure modes

The dangerous one is caching over a slow query. The cache hides the problem until it is cold — after
a deploy, an eviction, or a restart — at which point the original latency returns at the worst
moment, amplified by the stampede of requests that all miss together.

## Measurement

Before adding a cache, measure: requests/second for the dominant key, recomputation cost, current
origin utilisation, and acceptable staleness. If you cannot state all four, you cannot justify the
cache.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Do nothing | Origin comfortable; relieved load negligible |
| Fix the query or add an index | The slow path is a database problem |
| In-process cache | Single instance, or per-instance data is acceptable |
| Distributed cache | Measured pressure, or genuine shared state across instances |

## References

Summarised from the cited source and the sizing arithmetic in `calculators/`.
