---
id: failure-mode-analysis
title: Failure Mode Analysis
description: >-
  Nine structured questions asked of every component and dependency edge, so that failure
  reasoning is exhaustive rather than dependent on what the reviewer happens to think of.
category: reliability
tags: [failure-analysis, review, resilience]
maturity: stable
confidence: high
applies_at_stage: ["1", "2", "3", "4", "5"]
related: [timeouts, circuit-breakers, bulkheads, graceful-degradation, availability-targets]
complexity_cost: 0
trade_offs:
  - gains: "Systematic coverage; the questions catch what intuition skips, particularly slow-but-alive failures"
    costs: "Time proportional to the number of components and edges"
    when_worth_it: >-
      Before any significant launch, and during any architecture review. For a small system
      the full pass takes under an hour.
failure_modes:
  - mode: "Only total failure considered"
    symptom: "System handles a dependency being down but collapses when it is merely slow"
    detection: "No timeout or bulkhead on a dependency that has a failover plan"
    mitigation: "Question 2 is mandatory and is where most real outages live"
  - mode: "Analysis produces a list nobody acts on"
    symptom: "Documented failure modes with no corresponding mechanism or trigger"
    detection: "Findings without an owner or a remedy"
    mitigation: "Each identified mode gets a mechanism, an accepted-risk note, or a trigger"
anti_patterns:
  - "Asking only 'what if it goes down'"
  - "Running the analysis once at launch and never again"
references:
  - title: "Release It! Stability antipatterns"
    author: "Michael T. Nygard"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

Nine questions, asked mechanically of every component and every dependency edge. Being mechanical
is the point: it removes reliance on the reviewer happening to think of the right scenario.

1. What if it fails completely?
2. **What if it becomes slow but does not fail?**
3. What if the network between us partitions?
4. What if a request is duplicated?
5. What if messages arrive out of order?
6. What if traffic increases 10×?
7. What if it returns wrong data?
8. What happens during **its** deployment?
9. What happens during **our** deployment?

## When it applies

Before any significant launch, during architecture review, and whenever a new dependency enters a
critical path. For a small system the full pass takes under an hour.

**Question 2 is where most real outages live.** A dependency that is down fails fast and is
obvious. One that is slow but healthy-looking holds connections until the caller's pool drains, and
health checks keep passing throughout.

## When it does not apply

**Exhaustively on every component of a large system at once.** Prioritise: the critical path, then
components with external dependencies, then the rest. A complete analysis nobody finishes is worth
less than a partial one that is acted on.

**On components where the answer is already known and handled.** Do not re-derive; check that the
mechanism is still in place.

**As a substitute for testing the answers.** The analysis produces hypotheses. Failover that is
never exercised does not work.

## How it works

Each question maps to mechanisms, which is what makes the output actionable rather than a list of
worries:

| Question | Usual mechanism |
| :-- | :-- |
| 1 Complete failure | Redundancy, failover, graceful degradation |
| 2 Slow but alive | **Timeouts**, bulkheads, circuit breakers |
| 3 Partition | Idempotency, reconciliation, defined consistency behaviour |
| 4 Duplication | Idempotency keys, deduplication |
| 5 Out of order | Ordering guarantees, version numbers, commutative operations |
| 6 10× traffic | Autoscaling, load shedding, rate limiting, backpressure |
| 7 Wrong data | Validation at trust boundaries, checksums, reconciliation |
| 8 Their deploy | Retries, connection draining, version compatibility |
| 9 Our deploy | Rolling or blue-green deploys, backward-compatible migrations |

## Trade-offs

Costs time proportional to component count. The alternative is discovering the same list during an
incident, at much higher cost and with less patience available.

## Failure modes

The analysis producing a document nobody acts on. Every identified mode must end with one of three
outcomes: a mechanism, an explicitly accepted risk, or a trigger that will reopen it.

## Measurement

Track which identified failure modes have a corresponding mechanism, and which mechanisms have been
exercised in the last quarter. Untested failover is a hypothesis, not a capability.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Nine-question pass | Default; cheap and systematic |
| Formal FMEA with severity scoring | Safety-critical or regulated systems |
| Chaos experiments | Once the mechanisms exist and need verification, not before |

## References

Summarised from the cited source; the question set is OAB's own consolidation.
