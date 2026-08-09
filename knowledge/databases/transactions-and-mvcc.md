---
id: transactions-and-mvcc
title: Transactions and MVCC
description: >-
  Atomicity and isolation, how multi-version concurrency control lets readers avoid blocking
  writers, and why long-running transactions are operationally expensive.
category: databases
tags: [transactions, isolation, mvcc, concurrency]
maturity: stable
confidence: high
applies_at_stage: ["1", "2", "3", "4", "5"]
related: [relational-vs-document, schema-migration-safety, idempotency]
complexity_cost: 0
trade_offs:
  - gains: "Atomic multi-row changes and a defined isolation level, which removes whole classes of concurrency bug"
    costs: "Locks and version retention; long transactions block cleanup and can exhaust resources"
    when_worth_it: >-
      Whenever a logical operation touches more than one row and partial application would be
      incorrect. Keep them short.
failure_modes:
  - mode: "Long-running transaction"
    symptom: "Table bloat, blocked cleanup, connection exhaustion"
    detection: "Transactions open for minutes in the server activity view"
    mitigation: "Never hold a transaction across an external call or user think-time"
  - mode: "Isolation level assumed rather than known"
    symptom: "Lost updates or phantom reads under concurrency"
    detection: "Concurrency bugs that reproduce only under load"
    mitigation: "State the required isolation level explicitly per operation"
  - mode: "Deadlock under concurrent multi-row updates"
    symptom: "Intermittent deadlock errors"
    detection: "Deadlock counters in server statistics"
    mitigation: "Acquire locks in a consistent order; keep transactions short; retry on deadlock"
anti_patterns:
  - "Wrapping an entire request in one transaction, including external calls"
  - "Relying on read-modify-write without an appropriate isolation level or a conditional update"
references:
  - title: "Designing Data-Intensive Applications: transactions"
    author: "Martin Kleppmann"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

A transaction makes a set of changes atomic: all applied or none. **MVCC** lets each transaction see
a consistent snapshot, so readers do not block writers and writers do not block readers — at the
cost of retaining old row versions until no transaction needs them.

## When it applies

Whenever one logical operation touches more than one row and partial application would leave the
system incorrect: transferring a balance, creating an order with its lines, enqueueing a job in the
same transaction as the write that caused it.

That last case is significant: an in-database job queue eliminates the dual-write problem by
construction, which is often a stronger argument than throughput.

## When it does not apply

**For single-row operations.** Those are already atomic; an explicit transaction adds nothing.

**Across service or network boundaries.** A distributed transaction is a different and much harder
problem; use an outbox, a saga, or idempotent retries instead.

**Around external calls.** Holding a transaction while waiting on an HTTP request is the most
damaging pattern in this document: it holds locks and blocks version cleanup for the duration of
someone else's latency.

**As a substitute for idempotency.** A transaction that is retried after a timeout may commit twice
if the caller cannot tell whether the first attempt succeeded.

## How it works

MVCC keeps multiple versions of a row. Old versions can only be reclaimed once no open transaction
might need them — which is why one long-running transaction can cause table bloat across the whole
database, not just in the tables it touched.

Isolation levels trade correctness for concurrency, and the default varies by database. State the
level you need per operation rather than inheriting whatever the default is.

## Trade-offs

Correctness against concurrency and cleanup. Short transactions make the trade cheap; long ones make
it expensive in ways that show up far from their cause.

## Failure modes

The long-running transaction is the operationally significant one, because its symptoms — bloat,
blocked cleanup, connection exhaustion — appear unrelated to the code that caused it.

## Measurement

Track the longest open transaction age, deadlock rate, and table bloat. An oldest-transaction age
above a minute in an OLTP system warrants investigation.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Short transaction | Default |
| Conditional update with a version column | Read-modify-write without holding a transaction |
| Transactional outbox | Atomicity between a write and a downstream message |
| Saga | Multi-service operations where a distributed transaction is not available |

## References

Summarised from the cited source.
