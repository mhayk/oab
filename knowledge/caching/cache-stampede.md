---
id: cache-stampede
title: Cache Stampede
description: >-
  When a popular cache entry expires, concurrent requests all miss simultaneously and
  overwhelm the origin with duplicate work.
category: caching
subcategory: failure-modes
tags: [cache, thundering-herd, concurrency, resilience]
maturity: stable
confidence: high
applies_at_stage: ["2", "3", "4", "5"]
prerequisites: [cache-aside, ttl-and-invalidation]
related: [cache-sizing, retries-backoff-jitter]
complexity_cost: 1
trade_offs:
  - gains: "Bounded origin load when hot keys expire"
    costs: "Added coordination; a lock adds a failure mode of its own"
    when_worth_it: >-
      Any cached item whose recomputation costs more than about 100 ms and which is
      requested more than about 10 times per second.
failure_modes:
  - mode: "Synchronised expiry across many keys"
    symptom: "Periodic origin load spikes at regular intervals matching the TTL"
    detection: "Origin request rate showing periodicity at the TTL boundary"
    mitigation: "Randomised TTL jitter of plus or minus 10 to 20 percent"
  - mode: "Lock holder fails mid-recompute"
    symptom: "All requests block until the lock expires; latency cliff"
    detection: "p99 latency spikes correlated with cache misses"
    mitigation: "Bounded lock TTL plus serve-stale-while-revalidate"
  - mode: "Cold start after a deploy or restart"
    symptom: "Origin overwhelmed immediately after every deploy"
    detection: "Load spike correlated with deployment events"
    mitigation: "Warm critical keys, or stagger instance restarts"
triggers:
  - metric: "origin.requests_per_second for a single cache key"
    comparator: ">"
    threshold: 10
    unit: "requests/second"
    window: "sustained 5 minutes"
    action: "Introduce TTL jitter first; evaluate request coalescing or probabilistic early expiry if it persists"
anti_patterns:
  - "Setting identical TTLs across a whole key class"
  - "Adding a distributed lock before measuring whether stampede actually occurs"
references:
  - title: "Optimal Probabilistic Cache Stampede Prevention"
    author: "Vattani, Chierichetti, Lowenstein"
    type: paper
    accessed: 2026-08-09
  - title: "Caching at scale"
    type: engineering-blog
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

A cache stampede — or dog-piling — happens when a frequently-requested entry expires and many
concurrent requests miss at the same instant. Every one recomputes the same value against the
origin, turning a 99% hit rate into a momentary 0% at the exact moment of highest demand.

## When it applies

Three conditions, all required. If any is absent, this is not your problem:

1. Request rate for a **single key** above roughly 10/second.
2. Recomputation cost above roughly 100 ms.
3. The cache uses hard expiry rather than serve-stale-while-revalidate.

## When it does not apply

**Low-traffic systems.** At one request per second for a key, a stampede is two duplicate queries.

**Keys with naturally staggered expiry** — per-user caches written at different times spread their
own load.

**Caches that already serve stale while revalidating.** The pattern is prevented by construction,
which is why that is the preferred default rather than a mitigation to add later.

**Cheap recomputation.** Ten duplicate 5 ms queries are not an incident.

## How it works

The compounding is what makes it dangerous: the origin is slower under the load spike, so the
recompute takes longer, so more requests arrive and miss during the window, so the spike grows. A
cache that was protecting the origin briefly becomes an amplifier.

## Trade-offs

Mitigations range from free to costly. TTL jitter is free and should always be applied.
Serve-stale-while-revalidate costs a small staleness window. A distributed lock costs coordination
and introduces a new failure mode — the lock holder dying mid-recompute.

## Failure modes

The lock-holder failure is the reason not to reach for a lock first: without a bounded lock TTL and
a stale fallback, every request blocks until the lock expires, converting a load problem into a
latency cliff.

## Measurement

Instrument origin request rate per cache key class and correlate with TTL boundaries. Periodicity
matching the TTL is the signature. Without this measurement, mitigation is speculative and adds
complexity for an unconfirmed problem.

## Alternatives

| Approach | Complexity | When to prefer |
| :-- | --: | :-- |
| TTL jitter (±10–20%) | 0 | Always. Free, no coordination, prevents synchronised expiry |
| Serve stale while revalidating | 1 | When slightly stale data is acceptable — the best default |
| Request coalescing / single-flight | 1 | Per-instance deduplication |
| Distributed lock | 2 | Only when recomputation is genuinely expensive and cross-instance duplication is unacceptable |
| Probabilistic early expiry | 1 | High-traffic keys where a lock's failure modes are unwelcome |

## References

Summarised from the cited sources; no verbatim text is reproduced.
