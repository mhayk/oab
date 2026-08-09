---
id: indexing-fundamentals
title: Indexing Fundamentals
description: >-
  Indexes trade write cost and storage for read speed; column order in a composite index
  determines which queries it can serve.
category: databases
tags: [indexes, query-performance]
maturity: stable
confidence: high
applies_at_stage: ["1", "2", "3", "4", "5"]
related: [relational-vs-document, connection-pooling, read-replicas]
complexity_cost: 0
trade_offs:
  - gains: "Orders of magnitude on selective reads"
    costs: "Every index is maintained on every write, and consumes storage and memory"
    when_worth_it: >-
      When a query is on a hot path and is selective. An index on a low-cardinality column
      the planner will ignore is pure write cost.
failure_modes:
  - mode: "Composite index column order wrong for the query"
    symptom: "Index exists, planner ignores it"
    detection: "Sequential scan in the query plan despite a matching index"
    mitigation: "Equality columns first, then range, then ordering"
  - mode: "Index on a low-cardinality column"
    symptom: "Planner prefers a scan; write cost paid for nothing"
    detection: "Index with near-zero usage in statistics"
    mitigation: "Drop it; consider a partial index instead"
  - mode: "Unused indexes accumulating"
    symptom: "Write throughput degrading as indexes multiply"
    detection: "Index usage statistics showing zero scans"
    mitigation: "Review usage quarterly and drop what is unused"
triggers:
  - metric: "p95 query latency on a hot path"
    comparator: ">"
    threshold: 100
    unit: milliseconds
    window: "sustained over 1 day"
    action: "Examine the query plan before adding capacity; missing or wrong indexes are the usual cause"
anti_patterns:
  - "Indexing every column that appears in a WHERE clause"
  - "Adding hardware before reading the query plan"
references:
  - title: "Use The Index, Luke"
    author: "Markus Winand"
    type: engineering-blog
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

An index is a sorted structure the planner can use to avoid scanning a whole table. It costs write
amplification — every insert, update, and delete maintains every affected index — plus storage and
memory.

## When it applies

Index when a query is **on a hot path** and **selective** (returns a small fraction of rows).

Composite index column order follows the query, not intuition:

```
equality columns first → range columns → ordering columns
```

An index on `(tenant_id, created_at)` serves `WHERE tenant_id = ? ORDER BY created_at`. Reversed, it
does not.

Before adding capacity for a slow query, read the plan. Missing or misordered indexes are the most
common cause of a database that looks overloaded.

## When it does not apply

**Low-cardinality columns.** An index on a boolean or a three-value status column will usually be
ignored, because a scan is cheaper than the index lookup plus the row fetches. A **partial** index
on the rare value is often the right answer instead.

**Small tables.** Below a few thousand rows a scan is fast, and the planner will prefer it.

**Write-dominated tables** where reads are rare or non-selective. Every index is a tax on every
write.

**When the real problem is the query.** An unbounded result set or an N+1 pattern is not fixed by
an index.

## How it works

The planner chooses between an index and a scan using table statistics. It will ignore an index it
believes is not selective enough — which is usually correct, and means the fix is a different index
or a different query, not forcing the planner's hand.

## Trade-offs

Read speed against write cost and storage. On a read-heavy table with selective queries the trade is
overwhelming. On a write-heavy log table it can be negative.

## Failure modes

Unused indexes accumulating is the slow failure: nobody notices write throughput degrading because
each addition was individually small.

## Measurement

Track index usage statistics, index size against table size, and p95 latency per query class. Any
index with zero scans over a month is pure cost.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| B-tree index | Default for equality and range |
| Partial index | Selective predicate on a low-cardinality column |
| Covering index | When the index alone can answer the query |
| No index | Small tables, write-heavy tables, non-selective predicates |

## References

Summarised from the cited source.
