---
id: sync-vs-async-decision
title: Synchronous versus Asynchronous
description: >-
  Deciding whether work belongs in the request path, based on whether the caller needs the
  result and whether the work can fail independently.
category: messaging
tags: [async, queues, latency, decision-making]
maturity: stable
confidence: high
applies_at_stage: ["1", "2", "3", "4", "5"]
related: [database-backed-queues, delivery-guarantees, when-you-need-streaming, timeouts]
complexity_cost: 0
trade_offs:
  - gains: "Moving work out of the request path bounds latency and isolates failure"
    costs: "The caller no longer knows the outcome; status must be communicated some other way"
    when_worth_it: >-
      When the caller does not need the result to proceed, and the work either takes longer
      than the latency budget or depends on something that can fail independently.
failure_modes:
  - mode: "Async chosen for work the user is waiting for"
    symptom: "Polling, spinners, and a status model nobody wanted"
    detection: "Client polling immediately after submitting"
    mitigation: "If the caller needs the result now, keep it synchronous"
  - mode: "Sync call to a third party in a critical path"
    symptom: "Third-party latency becomes your latency; a stall exhausts the worker pool"
    detection: "External calls without timeouts in request handlers"
    mitigation: "Timeouts and bulkheads at minimum; move out of the path where possible"
  - mode: "Fire-and-forget without durability"
    symptom: "Work silently lost on restart"
    detection: "Background work started in-process with no persistence"
    mitigation: "Persist the intent before returning to the caller"
anti_patterns:
  - "Sending email synchronously during signup"
  - "Making everything asynchronous because asynchronous sounds scalable"
references:
  - title: "Enterprise Integration Patterns"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

The decision of whether work happens inside the request the user is waiting on, or afterwards.

## When it applies

Three questions decide it:

1. **Does the caller need the result to proceed?** If yes, synchronous. No amount of scalability
   argument changes this.
2. **Does the work fit in the latency budget?** If not, asynchronous.
3. **Can it fail independently without the request being wrong?** If yes, asynchronous is safer —
   a failed email should not fail a signup.

| Work | Usually |
| :-- | :-- |
| Validating and persisting the user's input | Synchronous |
| Sending a confirmation email | Asynchronous |
| Generating a report | Asynchronous with status |
| Charging a card at checkout | Synchronous — the user needs the outcome |
| Updating a search index | Asynchronous |
| Third-party webhook delivery | Asynchronous with retries |

## When it does not apply

**When the user is waiting for the answer.** Making a fast operation asynchronous adds a status
model, polling, and a worse experience in exchange for nothing.

**When the added durability is not real.** Fire-and-forget in a background thread is not
asynchronous processing; it is work that disappears on restart. If you move work out of the request
path, persist the intent first.

**When the operation must be atomic with the request.** Splitting it introduces the dual-write
problem, which then needs an outbox — often more complexity than keeping it synchronous.

**At very low volume where the sync path is comfortably within budget.** A 200 ms operation inside a
1-second budget does not need a queue.

## How it works

The transition from synchronous to asynchronous changes the contract: the caller receives an
acknowledgement rather than a result. That means designing how the outcome is communicated —
status endpoint, webhook, notification, or nothing at all if the caller genuinely does not care.

Skipping that design is what produces systems where work silently fails and nobody notices.

## Trade-offs

Asynchronous bounds request latency and isolates failure, at the cost of eventual consistency and a
status model. It also adds a place where work can queue up invisibly.

## Failure modes

A synchronous third-party call in a critical path is the highest-value finding in most reviews: the
provider's latency becomes yours, and a stall exhausts the worker pool, taking down endpoints that
have nothing to do with it.

## Measurement

Track time spent in the request path per operation class, and the share attributable to external
calls. Anything above a third of the latency budget spent waiting on a dependency is a candidate to
move out.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Synchronous | Caller needs the result; work fits the budget |
| Database-backed queue | Default asynchronous mechanism below a few hundred jobs/second |
| Managed queue | Isolation from database load, or elastic consumer scaling |
| Event stream | Multiple independent consumers needing replay |

## References

Summarised from the cited source.
