---
id: dead-letter-queues
title: Dead-Letter Queues
description: >-
  A destination for messages that cannot be processed, which is only useful if someone is
  alerted and a replay procedure exists.
category: messaging
tags: [dlq, failure-handling, operations]
maturity: stable
confidence: high
applies_at_stage: ["2", "3", "4", "5"]
prerequisites: [delivery-guarantees]
related: [database-backed-queues, retries-backoff-jitter, idempotency]
complexity_cost: 0
trade_offs:
  - gains: "A poison message stops blocking the queue; failed work is retained rather than lost"
    costs: "Another place to monitor, and a replay path to build and maintain"
    when_worth_it: >-
      Whenever a queue exists. The cost is small; the alternative is either infinite retries
      blocking the queue or silent data loss.
failure_modes:
  - mode: "A queue nobody reads"
    symptom: "Thousands of failed messages accumulated unnoticed over months"
    detection: "No alert on dead-letter depth"
    mitigation: "Alert on ANY growth, not on a threshold"
  - mode: "No replay path"
    symptom: "Messages are retained but cannot be reprocessed after the bug is fixed"
    detection: "No documented or tested replay procedure"
    mitigation: "Build replay when the dead-letter queue is created, not during the incident"
  - mode: "Poison message retried forever"
    symptom: "One malformed message blocks the queue indefinitely"
    detection: "Rising redelivery count on a single message"
    mitigation: "Bounded attempt count, then dead-letter"
triggers:
  - metric: "dead_letter.depth"
    comparator: ">"
    threshold: 0
    unit: messages
    window: "any growth"
    action: "Investigate the failure class before it accumulates; any dead-lettered message is a defect signal"
anti_patterns:
  - "Alerting on dead-letter depth only above a threshold"
  - "Creating a dead-letter queue with no replay tooling"
references:
  - title: "Enterprise Integration Patterns: dead letter channel"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

A separate destination for messages that failed processing after a bounded number of attempts. It
removes the poison message from the main queue so the rest of the work continues.

## When it applies

Wherever a queue exists. Without one, a message that always fails is retried forever — blocking the
queue if processing is ordered, or consuming capacity indefinitely if not.

Attempt count before dead-lettering: typically 3–5. Enough to survive transient failures, few enough
that a genuinely broken message is set aside quickly.

## When it does not apply

**When the message is genuinely disposable.** For lossy analytics events, dropping and counting is
simpler than retaining. Be explicit about it.

**When failure means the work must stop.** Some pipelines must halt on error rather than skip and
continue — financial reconciliation, for example. Dead-lettering there silently continues past a
problem that should block.

**When you will not build the replay path.** A dead-letter queue with no way to reprocess is a
retention mechanism pretending to be a recovery mechanism. Either build replay or accept the loss
honestly.

## How it works

Three things make it useful, and all three are needed:

1. **Alerting on any growth.** Not on a threshold — a threshold means the first messages are
   invisible. Any dead-lettered message is a defect signal.
2. **Enough context to diagnose.** The original message, the failure reason, the attempt count, and
   a timestamp.
3. **A tested replay path.** After the bug is fixed, the messages must be reprocessable — and
   consumers must be idempotent, because replay is another delivery.

## Trade-offs

Small cost, large benefit. The real cost is operational discipline: it must be watched, or it
becomes an archive of failures nobody knew about.

## Failure modes

"A queue nobody reads" is the classic, and it is worse than having none: the team believes failures
are being captured while thousands of messages accumulate unnoticed.

## Measurement

Alert on any growth. Track messages by failure class — one class dominating indicates a systematic
bug rather than transient failures.

Track replay success rate when replay is used; a replay that fails the same way means the fix was
incomplete.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Dead-letter queue with alerting and replay | Default wherever a queue exists |
| Halt on error | Pipelines where skipping is incorrect |
| Drop and count | Genuinely disposable messages, stated explicitly |

## References

Summarised from the cited source.
