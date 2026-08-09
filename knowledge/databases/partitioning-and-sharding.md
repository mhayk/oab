---
id: partitioning-and-sharding
title: Partitioning and Sharding
description: >-
  Splitting data across partitions or instances when one instance can no longer hold the
  write throughput or the volume — and the thresholds below which it is unjustified.
category: databases
tags: [partitioning, sharding, scaling, write-throughput]
maturity: reviewed
confidence: medium
applies_at_stage: ["4", "5"]
prerequisites: [read-replicas, indexing-fundamentals]
related: [transactions-and-mvcc, relational-vs-document]
complexity_cost: 3
trade_offs:
  - gains: "Write throughput and data volume beyond one instance; smaller indexes and faster maintenance per partition"
    costs: "Cross-partition queries and transactions become hard or impossible; the partition key is close to irreversible"
    when_worth_it: >-
      When sustained writes approach the limit of one well-tuned instance, typically a few
      thousand per second, or when one table's maintenance window becomes unmanageable.
failure_modes:
  - mode: "Hot partition"
    symptom: "One partition saturated while others are idle"
    detection: "Per-partition throughput variance"
    mitigation: "Choose a key with even distribution; avoid monotonic keys for hash partitioning"
  - mode: "Cross-partition queries dominate"
    symptom: "Most queries fan out to every partition, so nothing was gained"
    detection: "Query patterns not aligned to the partition key"
    mitigation: "Partition by the dominant access dimension, or do not partition"
  - mode: "Partition key chosen before access patterns are known"
    symptom: "A migration that is effectively a rewrite"
    detection: "Queries routinely needing a different key"
    mitigation: "Delay until patterns are measured; this is close to a one-way door"
triggers:
  - metric: "sustained write throughput"
    comparator: ">"
    threshold: 3000
    unit: "writes/second"
    window: "sustained at peak over 1 week"
    action: "Evaluate partitioning against the measured access patterns; verify vertical scaling and write batching are exhausted first"
anti_patterns:
  - "Sharding before vertical scaling and query optimisation are exhausted"
  - "Partitioning by a monotonically increasing key, which concentrates all writes on one partition"
references:
  - title: "Designing Data-Intensive Applications: partitioning"
    author: "Martin Kleppmann"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

**Partitioning** splits one table into pieces within an instance — usually by time or by key range.
**Sharding** distributes data across instances. Partitioning is an operational convenience;
sharding is an architecture change.

## When it applies

Only when the numbers demand it:

| Signal | Threshold |
| :-- | :-- |
| Sustained writes | above roughly 3,000–5,000/second on a well-tuned instance |
| Table size making maintenance unmanageable | index rebuilds or vacuums exceeding the window |
| Retention where whole periods are dropped | time partitioning makes deletion a metadata operation |
| Data volume beyond one instance's storage | hard limit |

Time-based partitioning for retention is the cheapest and most defensible case: dropping a partition
is instant, while deleting a billion rows is an incident.

## When it does not apply

**Below a few thousand writes/second.** This is the important one. A single well-tuned instance
handles far more write throughput than most teams assume, and OAB's most common correct answer here
is "not yet, and here is the trigger".

**Before vertical scaling is exhausted.** Doubling the instance is one afternoon; sharding is a
quarter and a permanent constraint.

**Before query optimisation.** A write bottleneck caused by excessive index maintenance is fixed by
dropping indexes, not by sharding.

**When access patterns are not yet measured.** The partition key is close to a one-way door.
Choosing it before you know the dominant access dimension usually means choosing wrong.

**When queries would fan out across partitions anyway.** If most queries need every partition, you
have added coordination cost and gained nothing.

## How it works

The partition key determines everything. Queries that include it are routed to one partition;
queries that do not must fan out. Transactions spanning partitions are hard or unavailable.

Monotonic keys — timestamps, auto-increment ids — concentrate all current writes on one partition,
which is the classic hot-partition mistake.

## Trade-offs

Three complexity points, cross-partition operations that become hard or impossible, and a key choice
that is effectively permanent. In exchange, write throughput and volume beyond one instance.

## Failure modes

The hot partition is the common operational failure; the wrong key is the expensive strategic one,
because correcting it is a rewrite.

## Measurement

Before partitioning: sustained write throughput, index maintenance cost, largest table size, and
maintenance window duration. After: per-partition throughput variance and the share of queries that
fan out.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Vertical scaling | Always try first; cheap and reversible |
| Index reduction, write batching | When index maintenance dominates write cost |
| Time partitioning for retention | Retention-driven; cheap and low-risk |
| Move one hot table to a purpose-built store | When one workload dominates |
| Sharding | Genuine multi-instance write demand, with access patterns measured |

## References

Summarised from the cited source.
