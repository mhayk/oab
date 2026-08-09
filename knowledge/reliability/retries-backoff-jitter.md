---
id: retries-backoff-jitter
title: Retries, Backoff and Jitter
description: >-
  Retrying only idempotent operations, with exponential backoff and randomised jitter, so
  that recovery attempts do not amplify the outage they are responding to.
category: reliability
tags: [retries, backoff, jitter, resilience]
maturity: stable
confidence: high
applies_at_stage: ["1", "2", "3", "4", "5"]
prerequisites: [timeouts]
related: [idempotency, circuit-breakers, cache-stampede]
complexity_cost: 0
trade_offs:
  - gains: "Transient failures become invisible to the user"
    costs: "Load multiplied exactly when the dependency is least able to serve it; duplicate side effects if the operation is not idempotent"
    when_worth_it: >-
      When the failure is genuinely transient and the operation is idempotent. Never retry
      a non-idempotent write without an idempotency key.
failure_modes:
  - mode: "Retry storm"
    symptom: "A brief dependency blip becomes a sustained outage as retries multiply load"
    detection: "Request rate to the dependency rising while its success rate falls"
    mitigation: "Exponential backoff, a low attempt cap, and a circuit breaker above it"
  - mode: "Synchronised retries"
    symptom: "Load arrives in waves at regular intervals matching the backoff schedule"
    detection: "Periodicity in the request rate during recovery"
    mitigation: "Full jitter: sleep a random value in [0, computed_backoff]"
  - mode: "Retrying a non-idempotent write"
    symptom: "Duplicate charges, duplicate records, duplicate emails"
    detection: "Duplicates correlating with timeout events"
    mitigation: "Idempotency keys, or do not retry"
  - mode: "Retries at every layer"
    symptom: "3 retries at 4 layers becomes 81 attempts"
    detection: "Attempt count far above what any single layer configured"
    mitigation: "Retry at one layer only, usually the outermost that can act on failure"
anti_patterns:
  - "Retrying on a 4xx response, which will not succeed on repetition"
  - "Fixed-interval retries with no jitter"
  - "Unbounded retry loops"
references:
  - title: "Exponential Backoff And Jitter"
    type: engineering-blog
    accessed: 2026-08-09
  - title: "Release It! Stability patterns"
    author: "Michael T. Nygard"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

Retrying a failed operation after a delay that grows exponentially, with randomness added so that
concurrent clients do not retry in unison.

```
delay = random(0, min(cap, base × 2^attempt))     # full jitter
```

## When it applies

Three conditions, all required:

1. The failure is plausibly **transient** — timeout, connection reset, 429, 503.
2. The operation is **idempotent**, or carries an idempotency key.
3. There is a **bounded attempt count**, typically 3.

Not all of them present means do not retry.

## When it does not apply

**On 4xx responses other than 429.** A malformed request will be malformed again. Retrying wastes
capacity and hides the bug.

**On non-idempotent writes without an idempotency key.** A payment that timed out may have
succeeded. Retrying it charges the customer twice.

**When the caller has already given up.** If the overall deadline has passed, an in-flight retry is
work nobody will use.

**At more than one layer.** Retries compose multiplicatively: 3 attempts at 4 layers is up to 81
requests. Choose one layer — usually the outermost that can do something useful with the failure —
and make the others fail fast.

**During a sustained outage.** That is what circuit breakers are for. Retrying into a dependency
that is down converts your outage into their prolonged one.

## How it works

Jitter is the part most often omitted and the part that matters most under load. Without it, every
client that failed at the same moment retries at the same moment, producing waves of load precisely
when the dependency is trying to recover.

Full jitter — a random value in `[0, backoff]` — is the simplest variant that works and is the
right default.

## Trade-offs

Retries convert a transient failure into invisible latency. They also multiply load exactly when the
dependency is least able to serve it. The attempt cap and the circuit breaker are what stop the
trade going bad.

## Failure modes

The retry storm is the one that turns an incident into an outage: a two-second blip becomes twenty
minutes because every client is now generating three times its normal load against a dependency
that is trying to restart.

## Measurement

Track attempts separately from requests, and the retry rate as a share of total. A retry rate above
a few percent sustained is a signal about the dependency, not about the retry policy.

Alert on retry rate, not just error rate — retries hide errors from users, which is their purpose
and also why they hide degradation from you.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Retry with full jitter, cap 3 | Default for idempotent transient failures |
| Fail fast, no retry | Non-idempotent operations without idempotency keys |
| Circuit breaker above retries | Dependencies that fail in sustained episodes |
| Queue and retry asynchronously | When the caller does not need the result now |

## References

Summarised from the cited sources.
