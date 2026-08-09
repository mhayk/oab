---
id: transactional-outbox
title: Transactional Outbox
description: >-
  Writing a message into the same transaction as the business change, then relaying it, so
  that a database write and a published message cannot diverge.
category: messaging
tags: [outbox, dual-write, consistency]
maturity: stable
confidence: high
applies_at_stage: ["2", "3", "4", "5"]
prerequisites: [delivery-guarantees, idempotency]
related: [database-backed-queues, transactions-and-mvcc]
complexity_cost: 1
trade_offs:
  - gains: "Eliminates the dual-write problem; the message cannot exist without the write, or the write without the message"
    costs: "An outbox table, a relay process, and at-least-once delivery to handle downstream"
    when_worth_it: >-
      Whenever a database write must be reliably reflected in an external system and a
      broker is already in the architecture. If it is not, a database-backed queue gives
      the same atomicity for free.
failure_modes:
  - mode: "Relay publishes before the transaction commits"
    symptom: "Consumers see events for writes that were rolled back"
    detection: "Events referencing rows that do not exist"
    mitigation: "The relay reads committed rows only; never publish from inside the writing transaction"
  - mode: "Outbox table never pruned"
    symptom: "Unbounded growth; relay query slowing"
    detection: "Outbox table among the largest in the database"
    mitigation: "Delete or archive published rows on a retention schedule"
  - mode: "Ordering assumed across aggregates"
    symptom: "Consumers depend on a global order the outbox does not guarantee"
    detection: "Consumer logic sensitive to cross-entity ordering"
    mitigation: "Order per aggregate key; do not promise global ordering"
anti_patterns:
  - "Publishing to a broker inside the database transaction"
  - "Adding an outbox when a database-backed queue would give the same guarantee for free"
references:
  - title: "Transactional outbox pattern"
    type: engineering-blog
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

The **dual-write problem**: writing to a database and publishing to a broker are two operations that
cannot be made atomic. Either can succeed while the other fails, leaving the systems inconsistent
with no way to tell which happened.

The outbox solves it by making the message part of the database write:

```sql
BEGIN;
  UPDATE orders SET status = 'paid' WHERE id = ...;
  INSERT INTO outbox (topic, payload) VALUES ('order.paid', ...);
COMMIT;
```

A separate relay reads committed outbox rows and publishes them, marking them sent.

## When it applies

When a database write must be reliably reflected in an external system — a broker, a search index,
a third-party API — **and** the broker is already part of the architecture for other reasons.

## When it does not apply

**When a database-backed queue would do.** If the consumer is your own worker, put the job in the
jobs table and skip the broker entirely. You get the same atomicity with zero extra components. This
is the most common case, and reaching for an outbox first is a common overcomplication.

**When the message is genuinely optional.** If losing it is acceptable — a best-effort analytics
event — publish directly and accept the loss. An outbox for lossy data is unnecessary machinery.

**When change data capture is available and appropriate.** Reading the database's replication log
gives similar guarantees without an application-level table, at the cost of coupling consumers to
the schema.

**When global ordering across entities is required.** An outbox preserves order per aggregate, not
globally. Promising more will produce subtle consumer bugs.

## How it works

The relay must read only **committed** rows — publishing from inside the writing transaction
reintroduces the problem it solves, because consumers would see events for writes that later roll
back.

Delivery is at-least-once: the relay may publish and crash before marking the row sent. Consumers
must be idempotent, which is the standard requirement anyway.

The outbox table needs pruning. Published rows are dead weight, and an ever-growing table slows the
relay's own query.

## Trade-offs

One table, one relay process (1 complexity point), and at-least-once semantics downstream. In
exchange, the two systems cannot diverge.

## Failure modes

The ordering assumption is the subtle one: consumers that depend on seeing events across different
entities in a global order will work in testing and fail under concurrency.

## Measurement

Track outbox depth, oldest unpublished row age, and relay throughput. Rising age means the relay is
behind, which is the signal that matters — depth alone can be misleading during a burst.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Database-backed queue | Consumer is your own worker — same guarantee, zero components |
| Transactional outbox | A broker is already present and messages must not be lost |
| Change data capture | Consumers can couple to the schema; no application changes wanted |
| Direct publish | The message is genuinely optional |

## References

Summarised from the cited source.
