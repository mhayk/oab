---
id: connection-pooling
title: Connection Pooling
description: >-
  Reusing database connections across requests, and the arithmetic that decides whether a
  separate connection pooler is justified yet.
category: databases
tags: [connections, pooling, capacity]
maturity: stable
confidence: high
applies_at_stage: ["1", "2", "3", "4", "5"]
prerequisites: [little-law]
related: [read-replicas, utilisation-and-queueing]
complexity_cost: 1
trade_offs:
  - gains: "Connection establishment cost removed from the request path; bounded load on the server"
    costs: "In-process pooling is free; a separate pooler is a component, a hop, and a failure mode"
    when_worth_it: >-
      In-process pooling always. A separate pooler only above roughly 80 percent of the
      server connection limit.
failure_modes:
  - mode: "Pool sized from mean concurrency"
    symptom: "Latency spikes under burst with no corresponding database load"
    detection: "Connection acquisition wait time in traces"
    mitigation: "Apply a tail multiplier of about 4x and a practical floor of about 5"
  - mode: "Pool larger than the server can serve"
    symptom: "Connection refused errors under load; server memory pressure"
    detection: "instances x pool_size approaching max_connections"
    mitigation: "Size total connections against the server limit, not per instance in isolation"
  - mode: "Connections held across a long-running operation"
    symptom: "Pool exhausted by a few slow requests"
    detection: "Long-lived transactions in the server's activity view"
    mitigation: "Acquire late, release early; never hold a connection across an external call"
triggers:
  - metric: "database.connections.used / max_connections"
    comparator: ">"
    threshold: 80
    unit: percent
    window: "sustained 1 hour, recurring"
    action: "Evaluate a connection pooler against the measured concurrency"
anti_patterns:
  - "Adding a separate pooler before measuring connection demand"
  - "One connection per request with no pooling at all"
references:
  - title: "PostgreSQL connection management"
    type: official-docs
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

A pool keeps connections open and hands them to requests, removing per-request handshake cost and
bounding how many connections the server must serve.

```
concurrent        = query_rate × query_time_seconds     (Little's Law)
pool_per_instance = max(5, ceil(concurrent / instances × 4))
total             = instances × pool_per_instance
```

## When it applies

In-process pooling: always. Every mainstream framework has one; use it.

A **separate** pooler is a different question, and the arithmetic usually says no:

> 312 queries/second at 4 ms is 1.25 concurrent queries. Six instances with a pool of 5 is 30
> connections against a limit of 100 — 30%. A pooler would add a hop, a process, and a failure
> mode in exchange for nothing.

Justified above roughly **80% of `max_connections`**, or where instance count is elastic and can
spike beyond what the server can serve.

## When it does not apply

**Serverless or per-request runtimes** where the process does not persist. There, an external
pooler is required rather than optional, because there is nowhere to keep a pool.

**When the real problem is a slow query.** A pool exhausted by 2-second queries is a query problem.
Enlarging the pool moves the queue from the application to the database.

**Very low traffic.** Below a few queries per second, connection cost is not measurable.

## How it works

Little's Law gives the mean concurrency. Pools must absorb the tail, hence the multiplier — and a
practical floor, because a pool of 1 queues on acquisition during any burst.

Idle connections are not free: each costs memory on the server, which is why total connections
matter more than per-instance comfort.

## Trade-offs

In-process pooling is free. A separate pooler costs one component and adds a hop; in exchange it
decouples instance count from server connection count, which matters when instances autoscale.

## Failure modes

Holding a connection across an external HTTP call is the most damaging pattern: a handful of slow
requests exhausts the pool while the database is idle.

## Measurement

Track connections used against the server limit, connection acquisition wait time, and pool
utilisation per instance. Acquisition wait appearing in traces means the pool is too small — or a
query is too slow.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| In-process pool | Always |
| Separate pooler | Above 80% of the connection limit, or elastic instance counts |
| Serverless-mode pooler | Per-request runtimes |

## References

Summarised from the cited documentation.
