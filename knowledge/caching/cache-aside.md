---
id: cache-aside
title: Cache-Aside
description: >-
  The default caching pattern: the application checks the cache, falls back to the origin
  on a miss, and populates the cache itself.
category: caching
tags: [caching, patterns]
maturity: stable
confidence: high
applies_at_stage: ["2", "3", "4", "5"]
prerequisites: [when-not-to-cache]
related: [ttl-and-invalidation, cache-stampede, cache-sizing]
complexity_cost: 1
trade_offs:
  - gains: "Simple, explicit, and resilient — a cache outage degrades to origin load rather than to failure"
    costs: "Every read path contains cache logic; a miss costs a cache round trip plus the origin call"
    when_worth_it: >-
      The default whenever a cache is justified at all. Alternatives are worth it only for
      specific write patterns.
failure_modes:
  - mode: "Cache failure treated as a hard error"
    symptom: "Cache outage becomes an application outage"
    detection: "No fallback path on cache errors"
    mitigation: "Treat a cache error as a miss; degrade to origin"
  - mode: "Stale entry after a write"
    symptom: "Users see old values after saving"
    detection: "Write paths that do not invalidate"
    mitigation: "Invalidate on write; prefer deletion over update"
  - mode: "Thundering herd on a popular key"
    symptom: "Origin spike whenever a hot key expires"
    detection: "Periodic origin load matching the TTL"
    mitigation: "TTL jitter; see cache-stampede"
anti_patterns:
  - "Updating the cache with the new value on write instead of deleting the entry"
  - "Caching without a TTL as a backstop against missed invalidation"
references:
  - title: "Caching strategies and patterns"
    type: engineering-blog
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

```
read(key):
    value = cache.get(key)
    if value is None:                 # miss
        value = origin.get(key)
        cache.set(key, value, ttl)
    return value

write(key, value):
    origin.write(key, value)
    cache.delete(key)                 # delete, do not update
```

## When it applies

The default whenever a cache is justified. It is explicit, it keeps the origin authoritative, and it
fails safe: if the cache is unavailable, every read is a miss and the system degrades to origin load
rather than to errors.

**Delete on write, do not update.** Updating races with concurrent readers and can leave a stale
value permanently; deletion is idempotent and self-correcting on the next read.

## When it does not apply

**Write-heavy keys.** If a key is written more often than it is read, cache-aside spends more on
invalidation than it saves.

**When the write path must not know about the cache.** Read-through and write-through push cache
logic into a library or proxy, which is preferable when many services share the data and you cannot
rely on all of them invalidating correctly.

**When staleness is unacceptable at any duration.** Cache-aside has an inherent window between the
origin write and the cache delete.

**When the value is cheap to compute.** A cache round trip is typically 0.5–2 ms; caching something
that costs 1 ms to compute is not a saving.

## How it works

The application owns the caching decision, which is the pattern's strength and its cost: it is
visible and controllable, but the logic is repeated on every read path — usually worth wrapping in a
small helper.

Always set a TTL, even with correct invalidation. The TTL is the backstop for the invalidation you
missed, and there is always one you missed.

## Trade-offs

A miss costs a cache round trip plus the origin call — slightly worse than no cache at all. With a
90% hit rate this is comfortably favourable; below about 50% it is worth re-examining whether the
cache is justified.

## Failure modes

Treating cache errors as hard errors is the failure that turns a cache into a liability. A cache
outage should reduce performance, never availability.

## Measurement

Track hit rate, miss latency versus hit latency, and origin load with and without the cache. A hit
rate below 50% means the key set is too diverse or the TTL too short.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Cache-aside | Default |
| Read-through | Many consumers; caching should be invisible to them |
| Write-through | Reads immediately after writes must be current |
| Write-behind | Very write-heavy, and durability loss on cache failure is acceptable |

## References

Summarised from the cited source.
