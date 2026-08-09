---
id: cache-sizing
title: Cache Sizing
description: >-
  Sizing a cache from its working set rather than from the total data volume, and computing
  what the cache actually relieves.
category: caching
tags: [caching, capacity, working-set]
maturity: reviewed
confidence: medium
applies_at_stage: ["2", "3", "4", "5"]
prerequisites: [cache-aside]
related: [when-not-to-cache, ttl-and-invalidation, cache-stampede]
complexity_cost: 0
trade_offs:
  - gains: "A cache that holds its working set achieves a high hit rate cheaply"
    costs: "Under-sizing causes thrashing; over-sizing wastes money on memory that is never touched"
    when_worth_it: >-
      Size to the working set with roughly 30 percent headroom. The working set is usually a
      small fraction of total data.
failure_modes:
  - mode: "Sized to total data volume"
    symptom: "Expensive cache with a hit rate no better than a much smaller one"
    detection: "Memory utilisation far below capacity with a stable hit rate"
    mitigation: "Measure distinct key access over a representative window"
  - mode: "Under-sized, causing eviction thrashing"
    symptom: "Hit rate collapses; eviction rate approaches insertion rate"
    detection: "Eviction rate close to write rate"
    mitigation: "Increase capacity, or reduce what is cached to the genuinely hot subset"
  - mode: "One large value evicting many small ones"
    symptom: "Hit rate variance uncorrelated with traffic"
    detection: "Wide value-size distribution"
    mitigation: "Separate key classes into different caches or namespaces"
anti_patterns:
  - "Sizing from database size rather than from measured access"
  - "Caching large blobs alongside small hot keys in the same instance"
references:
  - title: "Cache replacement policies and working set theory"
    type: paper
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

```
working_set = hot_keys × avg_value_bytes × overhead      (overhead ≈ 1.3)
origin_reads = read_rate × (1 − hit_rate)
relieved     = read_rate − origin_reads
```

The **working set** is the set of keys actually accessed in a window, not the total data. It is
usually a small fraction — access distributions are typically heavily skewed, with a small share of
keys serving most requests.

## When it applies

Whenever a cache is being provisioned. Two questions must both be answered:

1. **Does the working set fit?** If not, eviction thrashes and the hit rate collapses.
2. **What does the hit rate actually relieve, in absolute terms?**

The second is the one that gets skipped. A 60% hit rate on 187 reads/second removes 112
reads/second — meaningful only if the origin is under pressure. Against a database doing 312
queries/second comfortably, it is marginal, and the cache should be justified on something else or
not added.

## When it does not apply

**When the access distribution is flat.** If every key is equally likely, there is no working set
smaller than the data, and caching requires holding everything — usually not economic.

**When the value size distribution is very wide.** Sizing by average is misleading when a few large
values evict many small hot ones. Separate the key classes instead.

**For caches whose purpose is coordination**, not load relief — sessions, rate limits, idempotency
keys. Size those from concurrent entity count, not from access frequency.

## How it works

Add roughly 30% headroom over the measured working set: key storage, per-entry metadata, allocator
slack, and replication overhead all consume memory beyond the raw values.

Then check the eviction rate. Eviction approaching insertion means the cache is too small for its
key set, and the hit rate will be poor no matter how much traffic it receives.

## Trade-offs

Memory is the cost and it is usually modest relative to the origin capacity it saves. Under-sizing
is worse than over-sizing: a thrashing cache costs money and delivers little.

## Failure modes

Sizing from total data volume produces an expensive cache with no better hit rate than a much
smaller one, because the extra capacity holds keys nobody requests.

## Measurement

Measure distinct keys accessed over a representative window — a day covering a full traffic cycle.
Track memory utilisation, eviction rate, and hit rate together: high utilisation with high eviction
and a falling hit rate is under-sizing; low utilisation with a stable hit rate is over-sizing.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Size to measured working set + 30% | Default |
| Size to concurrent entities | Session, rate-limit, and idempotency caches |
| Separate caches per key class | Wide value-size distribution |
| No cache | Flat access distribution, or marginal relieved load |

## References

Summarised from the cited source and the sizing implementation in `calculators/oab_calc/cache.py`.
