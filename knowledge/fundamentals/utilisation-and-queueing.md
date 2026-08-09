---
id: utilisation-and-queueing
title: Utilisation and Queueing
description: >-
  Waiting time grows non-linearly as utilisation approaches 1, which is why systems are
  sized for 60-70% rather than for the capacity they nominally have.
category: fundamentals
tags: [queueing, latency, capacity, saturation]
maturity: stable
confidence: high
applies_at_stage: ["1", "2", "3", "4", "5"]
prerequisites: [little-law]
related: [tail-latency, proportional-architecture]
complexity_cost: 0
trade_offs:
  - gains: "Stable latency, and headroom to absorb bursts and failures"
    costs: "Roughly 30-40% of nominal capacity is deliberately unused"
    when_worth_it: >-
      Whenever latency matters. The unused capacity is not waste; it is what keeps latency
      linear, and reclaiming it costs far more in tail latency than it saves in instances.
failure_modes:
  - mode: "Sizing to nominal capacity"
    symptom: "Latency stable up to a point, then a sudden cliff with no warning"
    detection: "Latency versus throughput curve with a knee; utilisation above 85%"
    mitigation: "Target 60-70%; alert at 70%, not at 95%"
  - mode: "Averaging utilisation over too long a window"
    symptom: "Dashboards show 40% while requests queue during minute-long peaks"
    detection: "Per-minute percentiles far above the hourly mean"
    mitigation: "Measure utilisation at the granularity of the bursts, not the hour"
triggers:
  - metric: "cpu.utilisation"
    comparator: ">"
    threshold: 70
    unit: percent
    window: "sustained at peak over 3 consecutive days"
    action: "Re-run capacity analysis; scale before latency degrades rather than after"
anti_patterns:
  - "Alerting on utilisation at 90% or above"
  - "Treating spare capacity as waste to be reclaimed"
references:
  - title: "Fundamentals of Queueing Theory"
    type: book
    accessed: 2026-08-09
  - title: "The Art of Computer Systems Performance Analysis"
    author: "Raj Jain"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

As utilisation rises, waiting time does not rise proportionally — it rises hyperbolically. For a
single-server approximation:

```
W = W_service / (1 − ρ)          ρ = utilisation
```

| Utilisation ρ | Latency vs service time |
| --: | --: |
| 0.5 | 2× |
| 0.7 | 3.3× |
| 0.8 | 5× |
| 0.9 | 10× |
| 0.95 | 20× |
| 0.99 | 100× |

This is why 60–70% is the standard operating point. It is not conservatism; it is the region where
latency is stable and predictable.

## When it applies

Any resource with a queue in front of it: CPU, database connections, worker pools, thread pools,
disk I/O, network links. Whenever you are deciding how much headroom to leave, this is the reason.

It applies most sharply when:

- Service times are variable — variability makes the curve steeper.
- Arrivals are bursty rather than smooth.
- The queue is unbounded, so pressure shows up as latency rather than as rejection.

## When it does not apply

**Where queueing is not possible.** A system that rejects work above a threshold — a bounded pool
with fail-fast, or an admission controller — converts the latency cliff into a rejection rate. That
is often the better trade, and it changes the question from "how much headroom" to "what do we shed
and how do we tell the caller".

**For batch workloads with no latency requirement.** A nightly job that must finish before morning
can run at 95% utilisation quite happily. High utilisation is only a problem when someone is waiting.

**When the exact multiplier is taken literally.** M/M/1 is an approximation. Multiple servers,
service-time distributions, and scheduling all change the constant. The *shape* — non-linear, with
a knee — is what matters; the specific numbers are illustrative.

## How it works

At low utilisation an arriving request usually finds the resource free. As utilisation rises, the
probability of arriving while the resource is busy rises, and each queued request waits behind the
ones ahead of it. The compounding is what produces the hyperbola.

The practical consequence: **there is no gentle warning**. A system at 60% looks fine, a system at
85% looks slightly worse, and a system at 95% is in trouble. Alerting at 90% means alerting after
the users have noticed.

## Trade-offs

Targeting 70% means deliberately not using 30% of what you pay for. That capacity is buying two
things: stable latency, and the ability to absorb a burst or the loss of an instance without
entering the steep region.

## Failure modes

The measurement failure is as common as the sizing one: utilisation averaged over an hour hides
minute-long peaks where the resource was saturated. Measure at the granularity of your bursts.

## Measurement

Track utilisation at peak, not on average, and at a granularity close to your burst duration. Plot
latency against throughput during a load test to find the knee — the throughput at which p99
exceeds twice its steady-state value. Size for well below the knee.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Target 60–70% utilisation | Default for latency-sensitive work |
| Target 90%+ with admission control | When rejecting work is better than queueing it |
| Target 95%+ | Batch work with a deadline rather than a latency requirement |

## References

Standard queueing theory; summarised from the cited texts.
