---
id: maturity-stages
title: Architecture Maturity Stages
description: >-
  A six-stage model of system evolution used as a retrieval filter, so that concepts
  from a larger system than yours are never offered as advice.
category: fundamentals
tags: [stages, evolution, filtering]
maturity: stable
confidence: medium
applies_at_stage: ["0", "1", "2", "3", "4", "5"]
related: [proportional-architecture, complexity-cost]
complexity_cost: 0
trade_offs:
  - gains: "Concepts are filtered to the system's actual situation; stage-4 machinery never reaches a stage-1 design"
    costs: "Any staged model is a simplification; real systems sit between stages and in different stages per subsystem"
    when_worth_it: >-
      As a filter, always. As a roadmap, never — that is the misuse this model is most
      vulnerable to.
failure_modes:
  - mode: "Treated as a ladder to climb"
    symptom: "Teams plan to 'reach stage 3' with no trigger having fired"
    detection: "A migration justified by stage rather than by a measurement"
    mitigation: "Systems move when a trigger fires; many excellent systems stay at stage 2 permanently"
  - mode: "Applied to a whole system with mixed subsystems"
    symptom: "A stage-4 data pipeline forces stage-4 thinking onto a stage-1 admin interface"
    detection: "Uniform architecture across subsystems with very different load"
    mitigation: "Stage per subsystem where they genuinely differ"
anti_patterns:
  - "Using the stage as a target or a maturity score"
  - "Presenting the model to a team as a checklist of things they are missing"
references:
  - title: "Evolutionary Architectures and fitness functions"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

Six stages describing where a system is in its life, used by OAB for exactly one purpose: to filter
knowledge retrieval via the `applies_at_stage` field, so concepts drawn from far larger systems are
not offered as advice.

| Stage | Goal | Optimise for |
| :-- | :-- | :-- |
| 0 Prototype | Validate the idea | Speed, simplicity, throwaway cost |
| 1 MVP | Serve the first real users | Development velocity, basic reliability, simple deployment |
| 2 Early production | Operate reliably with growing usage | Monitoring, background work, database tuning, basic redundancy |
| 3 Growth | Absorb load the metrics show | Horizontal scaling, replicas, dedicated queues, CDN |
| 4 Scale | Handle load one instance cannot | Partitioning, event-driven work, autoscaling, service separation |
| 5 Global | Meet geographic and availability requirements | Multi-region, regional isolation, advanced failure management |

## When it applies

As a **filter** during knowledge retrieval and option generation. A stage-1 system should never be
shown partitioning strategies, and the mechanism is mechanical rather than a matter of judgement.

Determining the stage:

| Signals | Stage |
| :-- | :-- |
| No real users; throwaway acceptable | 0 |
| First users; small team; velocity dominates | 1 |
| Real usage; downtime now costs something | 2 |
| Metrics show one instance is saturating | 3 |
| Load exceeds what vertical scaling reaches | 4 |
| Geographic or availability requirements one region cannot meet | 5 |

## When it does not apply

**As a roadmap.** OAB never recommends "moving to stage 3". Systems move when a **trigger fires**,
and many excellent systems stay at stage 2 for their entire life. A stage is a description, not an
ambition, and treating it as a ladder produces exactly the overengineering this model exists to
prevent.

**As a maturity score.** It says nothing about engineering quality. A well-run stage-1 system is
better engineered than a badly-run stage-4 one.

**Uniformly across subsystems.** A system can have a stage-4 ingestion pipeline and a stage-1 admin
interface. Where subsystems genuinely differ, stage them separately.

**When a subsystem has requirements out of step with its load.** A payment path may need stage-3
reliability at stage-1 traffic because the cost of failure, not the volume, drives the requirement.

## How it works

Every knowledge unit declares `applies_at_stage`. During retrieval, units whose stages do not
include the system's stage are excluded. This is the mechanism that makes proportionality
enforceable rather than aspirational — the concept is not weighed and rejected, it is never
surfaced.

Rule R-F in the design framework hardens this: a stage-N system may not use stage-(N+2) machinery
without a written override.

## Trade-offs

Any staged model simplifies. Real systems sit between stages, and the boundaries are judgement. The
model earns its place by being a *filter* rather than a *prescription*: a slightly wrong stage
produces slightly wrong retrieval, not a wrong architecture.

## Failure modes

The dominant failure is treating it as a ladder. Guard against it by ensuring every architectural
change is justified by a fired trigger, never by a stage.

## Measurement

The stage is derived from the capacity numbers and team context, not asserted. Where the numbers
disagree with the intuition, the numbers win.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Stage as a retrieval filter | Default |
| Per-subsystem staging | Subsystems with materially different load or failure cost |
| No staging | Very small knowledge bases where everything applies |

## References

The stage model is OAB's own synthesis; the underlying idea of architecture as an evolving system
with fitness functions is drawn from the cited source.
