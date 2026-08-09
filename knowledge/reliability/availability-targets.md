---
id: availability-targets
title: Availability Targets
description: >-
  Translating an availability target into permitted downtime and then into the mechanisms
  it requires, and refusing targets the architecture cannot deliver.
category: reliability
tags: [availability, slo, redundancy]
maturity: stable
confidence: high
applies_at_stage: ["1", "2", "3", "4", "5"]
related: [failure-mode-analysis, graceful-degradation, tail-latency]
complexity_cost: 0
trade_offs:
  - gains: "A target tied to concrete mechanisms and cost, instead of a number chosen because it sounds serious"
    costs: "Each additional nine multiplies cost and operational complexity"
    when_worth_it: >-
      Choose the lowest target the business genuinely needs. Most internal tools need 99%,
      most SaaS needs 99.9%, and 99.99% requires no human step in recovery.
failure_modes:
  - mode: "Target stated without the mechanisms to deliver it"
    symptom: "99.99 percent claimed on a single instance with manual restart"
    detection: "Permitted downtime shorter than the realistic recovery time of a single component"
    mitigation: "Flag the inconsistency; state what the architecture actually delivers"
  - mode: "Dependency availability ignored"
    symptom: "Own service meets its target while the user-visible path does not"
    detection: "Serial dependencies whose product is below the stated target"
    mitigation: "Multiply serial dependency availabilities; the product is the ceiling"
triggers:
  - metric: "error budget consumed"
    comparator: ">"
    threshold: 50
    unit: percent
    window: "at the midpoint of the SLO window"
    action: "Freeze risky changes and re-examine the dominant failure source"
anti_patterns:
  - "Choosing 99.99 percent because it sounds professional"
  - "Setting a target without measuring what the system currently achieves"
references:
  - title: "Site Reliability Engineering: service level objectives"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

An availability target is a downtime budget, and each nine costs roughly an order of magnitude more
than the last.

| Target | Per year | Per month | Requires |
| :-- | :-- | :-- | :-- |
| 99% | 3.65 days | 7.3 h | Single instance, manual recovery |
| 99.9% | 8.8 h | 43 min | Automated restart, monitoring, tested backups, deploy without extended downtime |
| 99.95% | 4.4 h | 22 min | Redundant instances, health-checked load balancing, database failover |
| 99.99% | 53 min | 4.4 min | Multi-AZ, automated failover under a minute, **no human step in recovery** |
| 99.999% | 5.3 min | 26 s | Multi-region, no human in the loop, very high cost |

## When it applies

Whenever a target is stated, and whenever redundancy is being considered. The target determines the
mechanisms; the mechanisms determine the cost.

**Serial dependencies multiply.** Three dependencies at 99.9% each give a ceiling of 99.7% before
your own code runs. Compute the product before claiming a target.

## When it does not apply

**Where no target has been stated.** Do not invent one. Report what the architecture realistically
delivers and let the business decide whether that is enough. Inventing a target manufactures
requirements and cost.

**For internal tools where downtime is an inconvenience.** A 99% internal admin interface is often
correct, and engineering it to 99.9% spends money the business did not ask for.

**When the target is aspirational rather than contractual.** Ask what actually happens at the fourth
nine. If the answer is "nothing", the real target is lower.

## How it works

The consistency rule OAB enforces: **if a stated target implies less downtime than a single
component's realistic recovery time, flag the inconsistency rather than producing an architecture
that pretends.**

A single virtual machine with manual restart cannot be 99.99%. A 4.4-minute monthly budget does not
survive one human being paged, waking up, and logging in. Saying so is the job.

## Trade-offs

Each nine costs roughly 10× more and adds operational complexity that must be exercised — failover
that is never tested does not work when needed.

## Failure modes

The dominant failure is a target with no mechanisms behind it, usually chosen because it sounds
serious. The second is ignoring dependency availability, so the service meets its own target while
the user-visible path does not.

## Measurement

Measure achieved availability from the user's perspective — successful requests over total
requests — not from instance uptime. Track error budget consumption within the SLO window, and use
it to decide whether to ship risk or stability.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| No stated target, measured achievement | Stage 0–1 |
| 99.9% with automated restart and tested restore | Most SaaS |
| 99.99% multi-AZ, automated failover | Revenue-critical paths with a real cost of downtime |
| 99.999% multi-region | Very few systems; verify the business genuinely requires it |

## References

Summarised from the cited source.
