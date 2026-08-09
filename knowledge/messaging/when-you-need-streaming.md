---
id: when-you-need-streaming
title: When You Need Event Streaming
description: >-
  The measured thresholds at which a durable, replayable event log earns its considerable
  operational cost — and the far more common case where it does not.
category: messaging
tags: [streaming, kafka, event-log, overengineering]
maturity: reviewed
confidence: high
applies_at_stage: ["4", "5"]
prerequisites: [database-backed-queues, delivery-guarantees]
related: [sync-vs-async-decision, transactional-outbox, partitioning-and-sharding]
complexity_cost: 3
trade_offs:
  - gains: "Independent consumer groups, replay from an arbitrary offset, and throughput far beyond a queue"
    costs: "3 to 4 complexity points, partition and retention design, and consumer-group operations"
    when_worth_it: >-
      Above roughly 500 events per second sustained, or with 3 or more independent consumer
      groups that must replay the same stream. Below both, a queue is the correct answer.
failure_modes:
  - mode: "Adopted as a queue"
    symptom: "Considerable operational cost for work a jobs table handled"
    detection: "One consumer group, no replay usage, low throughput"
    mitigation: "Use a queue; streaming is for fan-out and replay, not for background jobs"
  - mode: "Partition key produces hot partitions"
    symptom: "One partition saturated while others idle; consumer lag concentrated"
    detection: "Per-partition lag variance"
    mitigation: "Choose a key with even distribution and adequate cardinality"
  - mode: "Retention shorter than the replay need"
    symptom: "A new consumer cannot rebuild its state"
    detection: "Retention shorter than the time to build and deploy a consumer"
    mitigation: "Set retention from the replay requirement, not from storage cost alone"
triggers:
  - metric: "sustained event throughput"
    comparator: ">"
    threshold: 500
    unit: "events/second"
    window: "sustained at peak over 1 week"
    action: "Evaluate event streaming against measured throughput and confirmed consumer-group requirements"
  - metric: "independent consumer groups requiring replay of the same stream"
    comparator: ">="
    threshold: 3
    unit: "consumer groups"
    window: "confirmed requirement, not anticipated"
    action: "Evaluate event streaming; this is the requirement a broker genuinely satisfies"
anti_patterns:
  - "Adopting a streaming platform with one consumer and 10 events per second"
  - "Choosing streaming for throughput a database-backed queue handles comfortably"
references:
  - title: "Designing Data-Intensive Applications: streams"
    author: "Martin Kleppmann"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

A durable, ordered, replayable log. Consumers track their own position, so multiple independent
consumer groups can read the same events at their own pace, and a new consumer can rebuild state
from the beginning.

This is genuinely different from a queue, where a message is consumed once and then gone.

## When it applies

Two thresholds, either of which justifies it:

| Signal | Threshold |
| :-- | :-- |
| Sustained event throughput | above roughly 500/second |
| Independent consumer groups needing replay of the same stream | 3 or more, **confirmed** |

The second is the real differentiator. Throughput can often be handled another way; **replay across
independent consumers cannot**. A search indexer, an analytics pipeline, and a notification service
all reading the same order events, each at its own pace, each able to rebuild from scratch — that is
the workload this exists for.

Partition count from throughput:

```
partitions = ceil(events_per_second / per_consumer_throughput) × headroom
           = ceil(7500 / 500) × 3 = 48
```

## When it does not apply

**Below roughly 500 events/second with one consumer.** This is by far the most common case, and the
answer is a database-backed queue. A streaming platform here costs 3–4 complexity points to solve a
problem that a jobs table already solved.

**When "replay" is aspirational.** Teams often justify streaming by future replay needs that never
materialise. The trigger requires a *confirmed* requirement, not an anticipated one.

**When the team has no operational capacity for it.** Partition rebalancing, consumer lag, retention
tuning, and broker upgrades are a discipline. Without dedicated capacity, a managed queue is a
better trade even at moderate volume.

**When ordering requirements are global.** Streaming preserves order within a partition, not across
partitions. Systems needing total order need a single partition, which caps throughput at what one
consumer can handle — and at that point the justification usually evaporates.

## How it works

The partition key determines both distribution and ordering. Order is guaranteed within a partition,
so entities requiring ordered processing must share a key — which means that key must also
distribute evenly, or one partition becomes hot.

Retention determines what can be replayed. Set it from the replay requirement — long enough to build
and deploy a new consumer — not from storage cost alone.

## Trade-offs

Three to four complexity points, partition and retention design, and consumer-group operations. In
exchange, fan-out and replay that nothing else provides.

## Failure modes

Adopting it as a queue is the expensive mistake: full operational cost, none of the benefit, and a
migration away that nobody wants to do.

## Measurement

Before adopting: sustained event throughput, number of confirmed independent consumers, and whether
replay is a real requirement or an anticipated one.

After: consumer lag per partition, partition throughput variance, and consumer-group rebalance
frequency.

## Alternatives

| Approach | Complexity | When to prefer |
| :-- | --: | :-- |
| Database-backed queue | 0 | Below ~500 jobs/second, single consumer — the common case |
| Managed queue service | 2 | Isolation from database load, elastic consumers |
| Fan-out to several queues | 2 | A few consumers, no replay requirement |
| Event streaming | 3–4 | Confirmed replay across 3+ independent consumers, or high throughput |

## References

Summarised from the cited source.
