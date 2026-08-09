---
id: timeouts
title: Timeouts
description: >-
  Every outbound call needs an explicit connect and read timeout derived from the caller's
  own latency budget; a dependency that becomes slow without failing is the usual cause of
  a total outage.
category: reliability
tags: [timeouts, resilience, latency]
maturity: stable
confidence: high
applies_at_stage: ["0", "1", "2", "3", "4", "5"]
related: [retries-backoff-jitter, circuit-breakers, bulkheads, failure-mode-analysis]
complexity_cost: 0
trade_offs:
  - gains: "Bounded resource holding; a slow dependency degrades one call path instead of exhausting the process"
    costs: "Requests that would have succeeded slowly are failed; the timeout value must be chosen"
    when_worth_it: >-
      Always. This is scale-independent: the absence of a timeout is a defect at 1 request
      per second and at 50,000.
failure_modes:
  - mode: "No timeout set, so the client library default applies"
    symptom: "Worker pool exhausted while the dependency is merely slow, taking down unrelated endpoints"
    detection: "Rising in-flight request count with flat throughput; connections held for minutes"
    mitigation: "Set explicit connect and read timeouts on every client"
  - mode: "Timeout longer than the caller's own timeout"
    symptom: "Caller has already given up while resources are still held downstream"
    detection: "Timeout values that increase rather than decrease down the call chain"
    mitigation: "Derive from a latency budget; each hop's timeout must be shorter than its caller's"
  - mode: "Timeout without a defined behaviour"
    symptom: "Timeout produces an unhandled exception and a 500"
    detection: "Error responses whose cause is a timeout rather than a decision"
    mitigation: "Define the fallback: cached value, degraded response, or explicit error contract"
anti_patterns:
  - "Relying on client library defaults, which are often minutes or unbounded"
  - "One global timeout value applied to every dependency regardless of its latency profile"
references:
  - title: "Release It! Stability patterns"
    author: "Michael T. Nygard"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

A timeout bounds how long a caller will wait. Without one, a dependency that becomes slow — but
does not fail — holds the caller's threads, connections, and memory until the caller dies.

Two values, and they are different:

- **Connect timeout** — establishing the connection. Short: 1–3 seconds. A host that will not
  accept a connection quickly is unavailable.
- **Read timeout** — waiting for the response. Derived from the latency budget.

## When it applies

**Every outbound call, without exception**: HTTP, database, cache, queue, DNS, and anything else
that leaves the process. This is a scale-independent fundamental.

Deriving the value from a budget rather than convention:

```
page budget 500 ms
  → 4 sequential backend calls
  → ~100 ms each after overhead
  → read timeout ~200 ms (2x the budget, not 30 s)
```

A timeout much larger than the budget is not protection; it is a delayed failure.

## When it does not apply

**For deliberately long-running operations** — a report generation, a large upload, a streaming
response. These still need a timeout, but one derived from the operation rather than a request
budget. The rule is that the timeout is *chosen*, not that it is small.

**For background work with no waiting caller**, where the bound should come from job-level
supervision rather than a per-call timeout. Still bound it — an unbounded background call holds a
worker forever.

## How it works

The failure that matters is not "the dependency is down". A down dependency fails fast and is
obvious. The dangerous case is **slow but healthy-looking**: connections stay open, health checks
pass, and the caller's pool drains until unrelated endpoints start failing. Timeouts convert that
into a bounded, attributable failure.

## Trade-offs

A timeout fails requests that might have succeeded. That is the point: a failed request is
recoverable, an exhausted process is not.

Setting values too tight causes spurious failures under normal variance. Derive from measured p99,
not from p50.

## Failure modes

The most common is no timeout at all, because the client library's default is minutes or unbounded
and nobody looked. The second is timeouts that grow down the call chain, so downstream work
continues after the caller has given up.

## Measurement

Record timeout occurrences per dependency as a distinct error class — not merged into generic
errors. A rising timeout rate is an early signal that a dependency is degrading, well before it
starts returning errors.

Set values from the dependency's measured p99, not from a round number.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Explicit connect + read timeouts | Always, unconditionally |
| Deadline propagation across a call chain | Multi-hop systems where the budget must be shared |
| Timeout + circuit breaker | When the dependency fails often enough that retrying is wasteful |

## References

Summarised from the cited source.
