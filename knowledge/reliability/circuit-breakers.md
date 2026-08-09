---
id: circuit-breakers
title: Circuit Breakers
description: >-
  Failing fast against a dependency that is already failing, so that a sustained outage
  does not consume the caller's capacity and does not prolong the dependency's recovery.
category: reliability
tags: [circuit-breaker, resilience, failure-isolation]
maturity: stable
confidence: high
applies_at_stage: ["2", "3", "4", "5"]
prerequisites: [timeouts, retries-backoff-jitter]
related: [bulkheads, graceful-degradation]
complexity_cost: 1
trade_offs:
  - gains: "A failing dependency stops consuming caller capacity, and stops receiving load that prevents its recovery"
    costs: "One more stateful component in the call path; requests are rejected that might have succeeded"
    when_worth_it: >-
      When a dependency fails in sustained episodes rather than isolated blips, and when
      there is a defined fallback for the open state. Without a fallback it only changes
      how the failure looks.
failure_modes:
  - mode: "No fallback behind the breaker"
    symptom: "Open circuit produces a 500 as surely as the timeout did"
    detection: "Error rate unchanged after adding the breaker"
    mitigation: "Define the degraded behaviour first; the breaker is what routes to it"
  - mode: "Threshold too sensitive"
    symptom: "Circuit opens during normal variance, causing self-inflicted outages"
    detection: "Open events with no corresponding dependency incident"
    mitigation: "Require a minimum request volume in the window before the rate is evaluated"
  - mode: "Half-open probe floods the recovering dependency"
    symptom: "Dependency recovers, is immediately overwhelmed, fails again"
    detection: "Oscillation between open and closed"
    mitigation: "Single probe request, and reopen on its failure"
triggers:
  - metric: "dependency sustained error rate"
    comparator: ">"
    threshold: 5
    unit: percent
    window: "sustained over 10 minutes, recurring weekly"
    action: "Evaluate a circuit breaker with a defined fallback for this dependency"
anti_patterns:
  - "Adding a breaker before timeouts are set"
  - "A breaker with no fallback, no alerting, and no defined open behaviour"
references:
  - title: "Release It! Circuit Breaker"
    author: "Michael T. Nygard"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

A state machine in front of a dependency:

```
CLOSED ──error rate exceeds threshold──▶ OPEN ──after cooldown──▶ HALF-OPEN
   ▲                                                                  │
   └──────────────── probe succeeds ─────────────────────────────────┘
                     probe fails ──▶ OPEN
```

While open, calls fail immediately without touching the dependency.

## When it applies

When **all** of these hold:

1. The dependency fails in **sustained episodes**, not isolated blips.
2. There is a **defined fallback** for the open state — cached data, a degraded response, a queued
   retry, or an explicit error contract.
3. Timeouts are already in place. A breaker on top of unbounded calls does nothing, because the
   calls never fail fast enough to trip it.

Parameters must be stated, not implied: error threshold, minimum request volume in the window,
window length, open duration, and half-open probe behaviour.

## When it does not apply

**Before timeouts exist.** Timeouts are the prerequisite. Adding a breaker first is solving the
second problem.

**When there is no fallback.** If the open state produces the same 500 the timeout produced, the
breaker has changed nothing except where the error comes from. Define the degraded behaviour first.

**For dependencies that fail in brief isolated blips.** Retries with jitter handle those better; a
breaker adds state and a new way to be wrong.

**At low request volume.** A rate computed over five requests is noise. Require a minimum volume in
the window, or the breaker will open on normal variance — a self-inflicted outage.

**For a dependency that is not on the critical path** and whose failure is already handled. Extra
state for no benefit.

## How it works

The breaker solves two problems at once. It stops the caller spending capacity on calls that will
fail, and it stops the caller's load preventing the dependency from recovering. The second is the
one teams forget: a struggling service that receives full traffic plus retries may never come back.

## Trade-offs

One more stateful thing in the call path, with its own failure modes and its own tuning. In
exchange, a dependency outage becomes a bounded degradation instead of a cascading one.

## Failure modes

The tuning failures matter most in practice: a threshold that trips on normal variance turns the
breaker into the outage, and a half-open state that lets full traffic through re-kills a recovering
dependency.

## Measurement

Track state transitions, time spent open per dependency, and requests rejected while open. Alert on
transitions to open — it is a dependency incident, and the breaker hiding it from users is precisely
why it must not be hidden from you.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Timeouts alone | Default; always first |
| Retries with jitter | Brief isolated failures |
| Circuit breaker + fallback | Sustained failure episodes with a defined degraded mode |
| Bulkhead | When the concern is one dependency starving others, rather than sustained failure |

## References

Summarised from the cited source.
