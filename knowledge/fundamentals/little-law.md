---
id: little-law
title: Little's Law
description: >-
  The relationship L = lambda x W between concurrency, arrival rate, and time in system,
  which sizes in-flight requests, worker pools, and connection pools without simulation.
category: fundamentals
tags: [queueing, concurrency, capacity]
maturity: stable
confidence: high
applies_at_stage: ["1", "2", "3", "4", "5"]
related: [utilisation-and-queueing, connection-pooling, tail-latency]
complexity_cost: 0
trade_offs:
  - gains: "Exact concurrency sizing from two numbers, with no simulation and no assumptions about arrival distribution"
    costs: "Gives the mean only; says nothing about the tail, which is what actually saturates pools"
    when_worth_it: >-
      Whenever sizing anything that holds a resource for a duration. Always pair with a
      tail multiplier rather than using the mean directly.
failure_modes:
  - mode: "Unit mismatch between milliseconds and per-second rates"
    symptom: "A result 1000x wrong that still looks plausible"
    detection: "Concurrency figures that are absurd relative to instance count"
    mitigation: "Convert explicitly; OAB's calculator takes milliseconds and converts internally"
  - mode: "Mean used directly for pool sizing"
    symptom: "Pool exhaustion under bursts despite adequate average capacity"
    detection: "Connection acquisition wait time appearing in latency traces"
    mitigation: "Apply a tail multiplier, typically 4x, and a practical floor"
  - mode: "Applied to an unstable system"
    symptom: "Result understates reality while a queue is growing without bound"
    detection: "Queue depth trending upward over the measurement window"
    mitigation: "The law assumes stability; fix the capacity deficit first"
references:
  - title: "A Proof for the Queuing Formula L = λW"
    author: "John D. C. Little"
    type: paper
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

For any **stable** system:

```
L = λ × W

L  average number of items in the system     (concurrent operations)
λ  average arrival rate                      (operations per second)
W  average time each spends in the system    (seconds)
```

It holds regardless of arrival distribution, service-time distribution, or service order, which is
what makes it usable for sizing without simulating anything.

## When it applies

Anywhere something holds a resource for a duration:

| Sizing question | λ | W | L |
| :-- | :-- | :-- | :-- |
| In-flight HTTP requests | requests/second | response time | concurrent requests |
| Worker pool size | jobs/second | job duration | busy workers |
| Database connections | queries/second | query time | concurrent queries |
| Open WebSocket connections | connections/second | session duration | concurrent sessions |

Worked example: 208 requests/second at 80 ms gives `208 × 0.08 = 16.6` concurrent requests. A
fleet sized for hundreds of concurrent requests is over-provisioned by an order of magnitude.

## When it does not apply

**To an unstable system.** The law assumes arrivals and departures balance over the measurement
window. If the queue is growing without bound, the law describes a steady state that does not
exist, and the answer will understate reality. Fix the capacity deficit first.

**As a pool size on its own.** It gives the **mean**. Pools sized to the mean queue on acquisition
during any burst, which shows up as latency nobody can attribute. Apply a tail multiplier —
typically 4× — and a practical floor.

**When W depends on L.** Under contention, service time rises as concurrency rises: more concurrent
queries means more lock contention means slower queries means more concurrency. The law still
holds, but you cannot use a low-load measurement of W to predict high-load L. Measure W at the
load you are sizing for.

**For tail sizing.** A p99 far above the mean means peak concurrency far above L. Little's Law will
not tell you that; see `tail-latency`.

## How it works

The intuition: if 10 people arrive per hour and each stays 30 minutes, there are on average 5
people inside. Nothing about *when* they arrive or the order they are served changes that average.

## Trade-offs

Extremely cheap — two numbers and a multiplication — but it answers only the average question. Its
value is that it converts vague concurrency intuitions into a number you can check.

## Failure modes

The unit mismatch is the one that bites in practice: milliseconds against per-second rates gives an
answer 1000× wrong that still looks plausible. OAB's `concurrency` calculator takes milliseconds
explicitly and converts internally for exactly this reason.

## Measurement

Measure λ as requests/second at the load you care about, and W as the **mean** time in the system
including all waiting, not just service time. If your latency histogram shows a long tail, record
p99 alongside so the tail multiplier can be set from data rather than convention.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Little's Law + tail multiplier | Default for pool and concurrency sizing |
| Queueing model (M/M/c) | When you need waiting-time distribution, not just concurrency |
| Load testing | When contention makes W load-dependent, which it usually is above 70% utilisation |

## References

Summarised from Little's original proof; the sizing applications are conventional practice.
