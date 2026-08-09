---
id: delivery-guarantees
title: Delivery Guarantees
description: >-
  At-most-once, at-least-once, and effectively-once — and why at-least-once plus
  idempotency is almost always the right choice.
category: messaging
tags: [delivery, semantics, correctness]
maturity: stable
confidence: high
applies_at_stage: ["2", "3", "4", "5"]
prerequisites: [idempotency]
related: [transactional-outbox, dead-letter-queues, database-backed-queues]
complexity_cost: 0
trade_offs:
  - gains: "Explicit semantics remove a whole class of correctness argument"
    costs: "At-least-once requires idempotent consumers, which is work at every consumer"
    when_worth_it: >-
      Always be explicit. At-least-once plus idempotency is the right default; exactly-once
      end-to-end across systems is not available and claiming it is a mistake.
failure_modes:
  - mode: "At-least-once assumed, consumers not idempotent"
    symptom: "Duplicate side effects during redelivery after a failure"
    detection: "Duplicates correlating with consumer restarts or timeouts"
    mitigation: "Idempotency keys or natural unique constraints at the consumer"
  - mode: "Exactly-once believed to be available end to end"
    symptom: "No deduplication anywhere, because the broker was trusted"
    detection: "Architecture documents claiming exactly-once across system boundaries"
    mitigation: "Treat broker exactly-once as within-broker only; deduplicate at the edge"
anti_patterns:
  - "At-most-once for work that matters"
  - "Relying on a broker's exactly-once semantics to cover an external side effect"
references:
  - title: "Designing Data-Intensive Applications: stream processing guarantees"
    author: "Martin Kleppmann"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

| Guarantee | Means | Cost |
| :-- | :-- | :-- |
| **At-most-once** | Delivered zero or one times; may be lost | Cheapest; acceptable only when loss is acceptable |
| **At-least-once** | Delivered one or more times; never lost | Requires idempotent consumers |
| **Effectively-once** | At-least-once delivery plus deduplication, so effects happen once | The practical target |

**Exactly-once delivery does not exist** across a network. What is achievable is at-least-once
delivery with idempotent processing — which produces exactly-once *effects*, which is what anyone
actually wanted.

## When it applies

Every messaging design must state which guarantee it provides and which it requires. Most defects in
asynchronous systems come from these two being different and nobody noticing.

**At-least-once plus idempotency is the right default.** It is what queues naturally provide, and
the idempotency requirement is work that pays for itself in retry safety.

## When it does not apply

**At-most-once is acceptable** for genuinely lossy data: sampled metrics, non-billing analytics
events, cache-warming hints. Say so explicitly — an unexamined at-most-once path is a data loss bug
waiting to be discovered.

**Within a single broker with transactional semantics**, exactly-once processing can be genuine for
reads and writes confined to that broker. It does **not** extend to external side effects: sending
an email or charging a card is outside the transaction, and no broker can make that exactly-once.

## How it works

At-least-once arises naturally from acknowledgement: the consumer processes a message and then
acknowledges. A crash between the two means redelivery. Acknowledging first would give at-most-once
and lose work on a crash.

Since redelivery is unavoidable, the consumer must be idempotent. That is the whole design.

## Trade-offs

At-least-once shifts work to the consumer, which must be idempotent. That work is not wasted: the
same mechanism makes retries safe throughout the system.

## Failure modes

The dangerous belief is that a broker's exactly-once guarantee covers external side effects. It does
not, and a system built on that assumption has no deduplication where it most needs it.

## Measurement

Track redelivery rate and duplicate detection rate at consumers. A rising redelivery rate signals
consumer failures or timeouts too tight for the work.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| At-least-once + idempotent consumers | Default |
| At-most-once | Genuinely lossy data, stated explicitly |
| Broker transactional processing | Reads and writes confined to one broker |
| Transactional outbox | Atomicity between a database write and a message |

## References

Summarised from the cited source.
