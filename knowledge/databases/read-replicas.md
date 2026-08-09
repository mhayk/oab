---
id: read-replicas
title: Read Replicas
description: >-
  Offloading reads to a replica, and the replication lag that makes it a correctness
  decision rather than only a performance one.
category: databases
tags: [replication, scaling, consistency]
maturity: stable
confidence: high
applies_at_stage: ["3", "4", "5"]
prerequisites: [connection-pooling]
related: [indexing-fundamentals, partitioning-and-sharding, backup-restore-and-pitr]
complexity_cost: 1
trade_offs:
  - gains: "Read capacity, and isolation of heavy reporting queries from the transactional path"
    costs: "One more instance, and every read path must decide whether it tolerates stale data"
    when_worth_it: >-
      When primary CPU is sustained above 70 percent after query optimisation, or when
      reporting queries interfere with transactional work.
failure_modes:
  - mode: "Read-after-write from a replica"
    symptom: "A user saves a change and does not see it"
    detection: "Bug reports of vanishing updates shortly after a write"
    mitigation: "Route reads to the primary within a session's write window, or wait for the replica's position"
  - mode: "Replication lag unmonitored"
    symptom: "Stale data served silently for minutes during load"
    detection: "No lag metric or alert"
    mitigation: "Alert on lag exceeding the RPO or the tolerance of the read paths"
  - mode: "Replica treated as a backup"
    symptom: "A bad DELETE is faithfully replicated"
    detection: "No independent backup"
    mitigation: "Replicas are availability, not recoverability"
triggers:
  - metric: "database.replication_lag"
    comparator: ">"
    threshold: 5
    unit: seconds
    window: "sustained over 15 minutes"
    action: "Investigate write volume and replica capacity; review which read paths tolerate this lag"
anti_patterns:
  - "Adding a replica before optimising queries"
  - "Routing all reads to replicas by default"
references:
  - title: "Designing Data-Intensive Applications: replication"
    author: "Martin Kleppmann"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

A copy of the primary that receives changes asynchronously and serves reads. It adds read capacity
at the cost of **lag**: the replica is always some interval behind.

## When it applies

- Primary CPU sustained above 70% **after** query optimisation and indexing.
- Reporting or analytical queries interfering with transactional work — often the better reason,
  because isolation matters even when capacity does not.
- Read:write ratio strongly read-heavy, typically above 10:1.

## When it does not apply

**Before query optimisation.** A replica of an unindexed database gives you two slow databases. Read
the plans first.

**For write capacity.** Replicas do not help writes at all; every write still goes to the primary.

**When every read must be current.** If no read path tolerates lag, a replica adds a component with
nowhere to send traffic.

**As a backup.** A replica replicates `DELETE` faithfully and instantly. It is availability, not
recoverability.

**At low load.** At 0.3 requests/second the primary is idle. A replica adds a point of complexity
and a class of consistency bug for no measured benefit.

## How it works

Each read path must be classified: can it tolerate data that is a few seconds old?

| Path | Typically |
| :-- | :-- |
| Reporting, analytics, exports | Yes |
| Public browse and search | Usually |
| A user's own profile after they edited it | **No** |
| Anything driving a write decision | **No** |

Read-after-write is the failure that reaches users: they save something, the read hits a lagging
replica, and their change appears to have vanished. Fix by routing a session's reads to the primary
for a window after a write, or by waiting for the replica to reach the write's position.

## Trade-offs

One managed component (1 point), roughly the cost of the primary, and a consistency decision on
every read path. In exchange, read capacity and workload isolation.

## Failure modes

Unmonitored lag is the quiet one: during a write spike the replica falls minutes behind and serves
stale data with no alert.

## Measurement

Track replication lag continuously and alert on it. Track the share of reads served by replicas, and
per-path staleness tolerance — documented, not assumed.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Query optimisation and indexing | Always first |
| Cache | Repeated identical reads; often cheaper than a replica |
| Read replica | Sustained primary load after optimisation, or reporting isolation |
| Partitioning | When writes, not reads, are the constraint |

## References

Summarised from the cited source.
