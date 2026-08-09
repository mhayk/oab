---
id: tail-latency
title: Tail Latency
description: >-
  Why average latency is misleading, and why at fan-out the p99 becomes the median
  user experience rather than a rare edge case.
category: fundamentals
tags: [latency, percentiles, performance, slo]
maturity: stable
confidence: high
applies_at_stage: ["2", "3", "4", "5"]
prerequisites: [utilisation-and-queueing]
related: [little-law, availability-targets]
complexity_cost: 0
trade_offs:
  - gains: "Latency targets that reflect what users actually experience"
    costs: "Percentile measurement needs histograms; percentiles cannot be averaged across hosts"
    when_worth_it: >-
      Whenever a user-facing request fans out to more than a few backend calls, or whenever
      an SLO is being set. Below roughly 10 calls per page the mean is still misleading but
      less catastrophically so.
failure_modes:
  - mode: "Averaging percentiles across instances or time buckets"
    symptom: "Dashboard p99 much lower than user reports"
    detection: "Percentiles computed as a mean of per-host percentiles"
    mitigation: "Aggregate from histograms, never average percentiles"
  - mode: "SLO set on the mean"
    symptom: "Mean meets target while a material share of users see multi-second responses"
    detection: "Wide gap between p50 and p99"
    mitigation: "Set targets at p95 and p99; report p50 for context only"
  - mode: "Tail ignored at fan-out"
    symptom: "Page latency far worse than any individual service's reported latency"
    detection: "Page p50 exceeding backend p99"
    mitigation: "Compute the probability that at least one call hits the tail"
triggers:
  - metric: "http.response_time.p99"
    comparator: ">"
    threshold: 3
    unit: "multiple of p50"
    window: "sustained over 1 day"
    action: "Investigate the source of variance before adding capacity; the tail is usually contention, not throughput"
anti_patterns:
  - "Reporting average response time as the performance metric"
  - "Averaging p99 values from multiple hosts"
references:
  - title: "The Tail at Scale"
    author: "Jeffrey Dean, Luiz André Barroso"
    type: paper
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

Response times are not normally distributed. They are long-tailed: most requests are fast, and a
small share are far slower — because of garbage collection, lock contention, cache misses, queueing,
retries, or a slow dependency.

The mean hides this. A service with a 40 ms mean can have a 2-second p99, and the mean gives no
hint.

## When it applies

**Always for SLOs**, and critically at **fan-out**. If a page makes N independent backend calls, the
probability that at least one lands in the tail is:

```
P(at least one slow call) = 1 − (1 − p)^N
```

| Calls per page | Chance of hitting the p99 |
| --: | --: |
| 1 | 1% |
| 10 | 10% |
| 50 | 39% |
| 100 | 63% |

At 100 calls per page, **the majority of page loads contain a p99 request**. The tail is not an
edge case; it is the median experience. This is the central result of *The Tail at Scale*, and it
is why fan-out architectures need tail-tolerance rather than just average throughput.

## When it does not apply

**For capacity and cost planning.** Throughput, egress, and storage are driven by volume, so the
mean is the right statistic there. Sizing a monthly bill from p99 would overstate it substantially.

**For batch and asynchronous work** where nobody is waiting on an individual item. What matters is
total completion time, not per-item distribution.

**When the distribution is genuinely tight.** If p99 is within about 1.5× of p50, the mean is a
reasonable summary and percentile machinery adds little. This is rare in networked systems but
common in simple in-process operations.

**As a reason to chase the extreme tail everywhere.** p99.9 and p99.99 matter for high-fan-out
systems and for infrastructure other services depend on. For a low-traffic application, optimising
p99.9 usually means optimising a handful of requests per day at real engineering cost.

## How it works

Tail latency comes from variance, not from average slowness. The usual sources:

| Source | Signature |
| :-- | :-- |
| Queueing near saturation | Tail grows sharply as utilisation passes ~70% |
| Garbage collection or compaction | Periodic spikes, correlated across requests on one host |
| Lock or row contention | Tail correlates with concurrency, not with throughput |
| Cache miss | Bimodal distribution |
| Retry on a slow dependency | Tail at roughly a multiple of a timeout value |
| Noisy neighbour | Tail varies by host |

Adding capacity fixes the queueing source and none of the others, which is why "the p99 is bad,
scale up" is so often ineffective.

## Trade-offs

Percentile measurement requires histograms and more storage than counters. The significant
operational constraint is that **percentiles cannot be averaged** — you must aggregate the
underlying histograms, or your dashboard will report a p99 that no user experienced.

## Failure modes

Averaging percentiles across hosts is the most common and most misleading error, because it
produces a number that looks authoritative and is systematically optimistic.

## Measurement

Record p50, p95, p99 and, for fan-out systems, p99.9. Aggregate from histograms. Report p50
alongside so the *spread* is visible — a p99 three times the p50 is a variance problem, and no
amount of extra capacity will close it.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Percentile targets (p95, p99) | Default for user-facing latency |
| Mean | Capacity, cost, and volume planning |
| Hedged requests, tied requests | High fan-out where tail tolerance must be built in |

## References

Summarised from *The Tail at Scale*; the fan-out probability is elementary.
