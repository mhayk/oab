---
id: ttl-and-invalidation
title: TTL and Invalidation
description: >-
  Choosing expiry from tolerable staleness, and treating the TTL as the backstop for the
  invalidation that was missed.
category: caching
tags: [caching, ttl, invalidation, staleness]
maturity: stable
confidence: high
applies_at_stage: ["2", "3", "4", "5"]
prerequisites: [cache-aside]
related: [cache-stampede, cache-sizing]
complexity_cost: 0
trade_offs:
  - gains: "Bounded staleness without needing perfect invalidation"
    costs: "Shorter TTL means lower hit rate and more origin load"
    when_worth_it: >-
      Always set a TTL, even with correct invalidation. It is the safety net for the
      invalidation path you missed, and there is always one you missed.
failure_modes:
  - mode: "Invalidation relied on with no TTL"
    symptom: "An entry stays stale indefinitely after a missed invalidation path"
    detection: "Cached entries older than any plausible write interval"
    mitigation: "Always set a TTL as a backstop"
  - mode: "Identical TTLs across a key class"
    symptom: "Synchronised expiry and periodic origin spikes"
    detection: "Origin load periodicity matching the TTL"
    mitigation: "Jitter of 10 to 20 percent"
  - mode: "TTL chosen by habit"
    symptom: "Everything cached for an hour regardless of how often it changes"
    detection: "Uniform TTLs across data with very different change rates"
    mitigation: "Derive from tolerable staleness per data class"
anti_patterns:
  - "Invalidating by clearing the whole cache"
  - "TTLs that are round numbers chosen without reference to change rate"
references:
  - title: "HTTP caching semantics"
    type: rfc
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

Two independent mechanisms for keeping a cache from serving wrong data:

- **TTL** — the entry expires after a fixed period, regardless of anything else.
- **Invalidation** — a write explicitly removes the entry.

They are complementary, not alternatives. Invalidation gives freshness; TTL guarantees a bound even
when invalidation is missed.

## When it applies

Every cached entry gets a TTL. Derive it from **tolerable staleness per data class**, not from
habit:

| Data | Tolerable staleness | TTL |
| :-- | :-- | :-- |
| Reference data (countries, currencies) | hours | 1–24 h |
| Product catalogue | minutes | 5–15 min |
| User profile | seconds after their own edit | 30–60 s, with invalidation on write |
| Prices, inventory | near zero | seconds, or do not cache |
| Session state | until logout | session lifetime |

Add **10–20% jitter** to every TTL. Free, and it prevents synchronised expiry.

## When it does not apply

**Where staleness is genuinely unacceptable** — authorisation decisions, balances, inventory at
checkout. Either do not cache, or cache with a TTL measured in single-digit seconds and accept that
the benefit is small.

**For immutable content.** Content-addressed or versioned assets never change; give them a very long
TTL and change the key when the content changes. Invalidation is then unnecessary by construction —
the best invalidation strategy is not needing one.

**Where a write cannot be observed.** If the data changes outside your system, invalidation is not
available and the TTL is the only mechanism. Set it from the external change rate.

## How it works

Prefer **deleting** an entry on write over updating it. Deletion is idempotent and self-correcting;
an update races with concurrent readers and can leave a stale value permanently.

Never invalidate by clearing the whole cache. It converts one stale key into a full stampede across
every key.

## Trade-offs

Shorter TTL means fresher data and a lower hit rate. The hit-rate cost is non-linear: halving the
TTL does not halve the hit rate, but for short TTLs it approaches doing so.

## Failure modes

Relying on invalidation with no TTL is the one that produces the longest-lived bugs, because a
missed invalidation path leaves an entry stale until someone notices — which can be months.

## Measurement

Track hit rate by key class and observed staleness at read time. If hit rate is low, the TTL is
shorter than the read interval and the cache is not earning its place.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| TTL only | Data changing outside your system |
| TTL + invalidation on write | Default |
| Versioned keys, long TTL | Immutable or content-addressed data — no invalidation needed |
| No cache | Staleness unacceptable at any duration |

## References

Summarised from the cited specification.
