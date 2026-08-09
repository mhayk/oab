---
id: observability-cost
title: Observability Cost
description: >-
  Log ingestion is priced per GB and log volume grows superlinearly with traffic, which
  makes observability the classic unbudgeted infrastructure cost.
category: cost
tags: [cost, observability, logging, metrics]
maturity: reviewed
confidence: high
applies_at_stage: ["2", "3", "4", "5"]
related: [operational-cost-model, egress-cost]
complexity_cost: 1
trade_offs:
  - gains: "The ability to diagnose failures; without it, incidents are debugged by guessing"
    costs: "Per-GB ingestion that grows faster than traffic, and per-series metric pricing that grows with cardinality"
    when_worth_it: >-
      Error tracking is unconditional at any scale. Full log aggregation is worth its cost
      once an incident's diagnosis time exceeds a few hours, which is roughly stage 2.
failure_modes:
  - mode: "Debug logging left on in production"
    symptom: "Ingestion volume an order of magnitude above expectation"
    detection: "Log volume per request far above a few KB"
    mitigation: "Level-based sampling; structured logs rather than verbose text"
  - mode: "Unbounded metric cardinality"
    symptom: "Metric bill growing without traffic growing"
    detection: "Series count rising with user or request identifiers in labels"
    mitigation: "Never label a metric with a user id, request id, or full URL path"
  - mode: "Retention set once and forgotten"
    symptom: "Years of logs retained at full-price hot storage"
    detection: "Storage cost rising steadily while ingestion is flat"
    mitigation: "Tiered retention: hot for days, cold for months, deleted after"
triggers:
  - metric: "observability spend as a share of infrastructure spend"
    comparator: ">"
    threshold: 25
    unit: percent
    window: "sustained over 2 months"
    action: "Review log volume per request, metric cardinality, and retention tiers before increasing budget"
anti_patterns:
  - "Logging full request and response bodies by default"
  - "Putting a user id or request id in a metric label"
references:
  - title: "Observability pricing models"
    type: official-docs
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

Observability is billed on volume: logs per GB ingested, metrics per series, traces per span. All
three grow with traffic, and logs typically grow **faster** than traffic because busier systems
produce more per-request output — retries, warnings, and slow-path branches.

## When it applies

From stage 2 onward, and it should be budgeted explicitly at design time. A common outcome is
observability reaching 20–30% of total infrastructure spend, which is defensible if intended and
alarming if discovered.

## When it does not apply

**Error tracking is unconditional.** It is cheap, it is scale-independent, and without it failures
are discovered by users. Never trade it away on cost grounds — this is one of the fundamentals that
is not proportional to traffic.

**At prototype stage**, platform-provided logs are sufficient. A log aggregation product before
there are users is a component with no problem to solve.

**When the volume is genuinely small.** Below a few GB/month, most products' free tiers cover it and
the cost conversation is moot.

## How it works

Three distinct pricing models, each with its own failure mode:

| Signal | Priced by | Grows with |
| :-- | :-- | :-- |
| Logs | GB ingested | traffic × verbosity — superlinear in practice |
| Metrics | series (cardinality) | label combinations, **not** traffic |
| Traces | spans, often sampled | traffic × service count |

Metric cardinality is the one that surprises: a single metric labelled with a user id becomes a
million series, and the bill grows with your user base rather than with your load.

## Trade-offs

Cutting observability to save money removes the ability to diagnose the incidents you are having.
The right lever is almost never "log less" as a blanket rule — it is sampling, structured logging,
and retention tiers, which reduce cost without reducing the ability to answer questions.

## Failure modes

Debug logging left on in production is the classic order-of-magnitude overrun. Unbounded metric
cardinality is the classic slow one, because the bill grows even when traffic does not.

## Measurement

Track log GB per million requests, metric series count, and observability spend as a share of
infrastructure spend. A rising series count with flat traffic means cardinality, not growth.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Error tracking only | Stage 0–1 |
| Structured logs + metrics + error tracking | Stage 2–3, the common case |
| Full tracing with sampling | Multi-service systems where causality across services is the question |
| Self-hosted stack | Very high volume with dedicated platform capacity; costs 3 points |

## References

Summarised from published pricing documentation; see `_pricing.md` for the dated table.
