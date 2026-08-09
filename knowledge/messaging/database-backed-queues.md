---
id: database-backed-queues
title: Database-Backed Queues
description: >-
  Using the database you already run as a job queue, which removes the dual-write problem
  by construction and costs no additional component.
category: messaging
tags: [queues, jobs, async]
maturity: stable
confidence: high
applies_at_stage: ["1", "2", "3"]
prerequisites: [sync-vs-async-decision]
related: [transactional-outbox, dead-letter-queues, when-you-need-streaming, transactions-and-mvcc]
complexity_cost: 0
trade_offs:
  - gains: "Zero new components; enqueue is atomic with the business write; jobs are inspectable with SQL"
    costs: "Consumes database connections and I/O; a throughput ceiling in the low thousands per second"
    when_worth_it: >-
      Below roughly 500 to 1000 jobs per second, which covers the overwhelming majority of
      systems. It is the correct default asynchronous mechanism.
failure_modes:
  - mode: "Long-running job holding a transaction"
    symptom: "Table bloat, blocked cleanup, connection exhaustion"
    detection: "Transactions open for the duration of job execution"
    mitigation: "Claim and execute in separate transactions"
  - mode: "Polling too aggressively"
    symptom: "Constant database load from empty queue checks"
    detection: "Query volume uncorrelated with job volume"
    mitigation: "Backoff when empty, or use a notification mechanism"
  - mode: "Completed jobs never removed"
    symptom: "Queue table growing without bound; queries slowing"
    detection: "Table size growing while queue depth is flat"
    mitigation: "Archive or delete completed jobs on a retention schedule"
triggers:
  - metric: "queue.throughput_jobs_per_second"
    comparator: ">"
    threshold: 500
    unit: "jobs/second"
    window: "sustained at peak over 1 week"
    action: "Re-run capacity analysis for the async subsystem; evaluate a dedicated broker against measured demand"
anti_patterns:
  - "Adopting a broker before measuring job volume"
  - "Holding a database transaction across the whole job execution"
references:
  - title: "SELECT FOR UPDATE SKIP LOCKED"
    type: official-docs
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

A jobs table in the existing database, with workers claiming rows using `SELECT ... FOR UPDATE SKIP
LOCKED`, which lets concurrent workers take different rows without blocking each other.

## When it applies

Below roughly 500–1,000 jobs/second, which covers the overwhelming majority of systems. The
decisive advantage is usually not throughput but **atomicity**:

```sql
BEGIN;
  INSERT INTO orders ...;
  INSERT INTO jobs (type, payload) VALUES ('send_confirmation', ...);
COMMIT;
```

The job cannot exist without the order, and the order cannot exist without the job. An external
broker reintroduces the dual-write problem, which then needs a transactional outbox — adding back
the complexity the broker was supposed to avoid.

Secondary advantages: jobs are inspectable with SQL during an incident, and existing backup and
monitoring already cover them.

## When it does not apply

**Above roughly 500–1,000 jobs/second sustained.** The queue competes with application queries for
connections and I/O.

**When multiple independent consumer groups need to replay the same stream.** That is what event
streaming is for; a job queue deletes work once it is done.

**When the database is already the bottleneck.** Adding queue load to a saturated database is the
wrong direction.

**Very long-running jobs**, where a claim held for minutes complicates visibility timeouts and
retries. Workable, but a purpose-built system handles it better.

## How it works

Claim and execute in **separate transactions**. Claim the row, commit, execute, then mark complete.
Holding a transaction across execution blocks version cleanup for the duration of the job and is the
most common way this pattern goes wrong.

Poll with backoff when the queue is empty, or use a database notification mechanism, so an idle
system is not generating constant load.

Completed jobs need a retention policy. A queue table that only grows will eventually slow the
claiming query.

## Trade-offs

Zero complexity points and no dual-write problem, against a throughput ceiling and shared capacity
with application queries. For most systems the trade is overwhelmingly favourable — and OAB's
default recommendation.

## Failure modes

Holding a transaction across job execution is the recurring operational failure, and its symptoms —
bloat, blocked cleanup — appear unrelated to the queue.

## Measurement

Track queue depth, oldest job age, throughput, failure rate, and dead-letter depth. Oldest job age is
the most useful single metric: it rises before depth does when workers are undersized.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Database-backed queue | Default below ~500 jobs/second |
| Managed queue service | Isolation from database load; elastic consumers; +2 points |
| Event stream | Multiple independent consumer groups with replay; +3–4 points |
| In-process background work | Never for anything that must not be lost |

## References

Summarised from the cited documentation.
