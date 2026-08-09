---
id: graceful-degradation
title: Graceful Degradation
description: >-
  Deciding in advance which features degrade and to what, so that a partial failure produces
  a reduced service rather than an error page.
category: reliability
tags: [degradation, fallback, resilience]
maturity: stable
confidence: high
applies_at_stage: ["2", "3", "4", "5"]
prerequisites: [timeouts]
related: [circuit-breakers, bulkheads, availability-targets]
complexity_cost: 0
trade_offs:
  - gains: "Partial failures stay partial; the core journey survives a non-critical dependency outage"
    costs: "Each fallback is a second code path that must be maintained and exercised"
    when_worth_it: >-
      When a non-critical dependency sits in a critical path. Not worth it for dependencies
      whose absence makes the feature meaningless.
failure_modes:
  - mode: "Degradation is undefined, so it degrades to a 500"
    symptom: "A recommendations service outage takes down the product page"
    detection: "Error pages caused by non-essential dependencies"
    mitigation: "Define the degraded behaviour per dependency, in advance"
  - mode: "Fallback path never exercised"
    symptom: "The fallback itself fails during the incident it was built for"
    detection: "Fallback code with no tests and no production traffic"
    mitigation: "Exercise it deliberately, in tests and periodically in production"
  - mode: "Silent degradation"
    symptom: "Users see stale or missing data with no indication; support cannot explain it"
    detection: "No metric distinguishing degraded from normal responses"
    mitigation: "Emit a metric and, where it matters to the user, say so in the response"
anti_patterns:
  - "Treating every dependency as critical, so any failure is total"
  - "Falling back to a cache with no bound on staleness"
references:
  - title: "Site Reliability Engineering: graceful degradation"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

Deciding, before the incident, what each feature does when a dependency it uses is unavailable —
so the answer is a designed behaviour rather than whatever the exception handler does.

## When it applies

Wherever a **non-critical** dependency sits inside a **critical** path. Typical decisions:

| Dependency fails | Degraded behaviour |
| :-- | :-- |
| Recommendations | Show the page without them |
| Search ranking service | Fall back to simple relevance ordering |
| Avatar or media service | Placeholder image |
| Analytics | Drop the event; never block the request |
| Rate limiter store | Fail open, and alert |
| Session store | Force re-login rather than 500 |

The rate limiter case is worth stating explicitly: failing *closed* on a rate limiter outage
converts a limiter problem into a total outage.

## When it does not apply

**When the dependency is genuinely essential.** Without the primary database, a write endpoint has
nothing to degrade to. Say so plainly rather than inventing a fallback that misleads.

**When degrading is worse than failing.** In payments, ledger, or authorisation paths, a degraded
answer can be dangerous. An explicit error is correct there — and "fail closed" is the right choice
for anything that grants access.

**When the fallback cannot be maintained.** A second code path that is never exercised will not
work during the incident it was built for. If you cannot test it, do not rely on it.

## How it works

For each dependency in a path, answer three questions in advance: is it essential; if not, what
does the feature do without it; and how does anyone know degradation is happening.

The third is the one most often skipped, and it is what turns a good design into an
unexplainable support ticket.

## Trade-offs

Every fallback is a second code path. It costs maintenance and it must be exercised, or it becomes
a liability that fails at the worst moment.

## Failure modes

Silent degradation is the subtle one: users see stale or missing data, nobody is alerted, and the
system reports itself healthy while delivering a reduced service for days.

## Measurement

Emit a metric per degraded response, labelled by which dependency caused it. Alert on sustained
degradation — the whole point is that users do not notice, which means monitoring must.

Exercise fallbacks deliberately: in tests, and periodically in production.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Defined degraded behaviour | Non-critical dependency in a critical path |
| Explicit failure | Payments, authorisation, ledger — where a wrong answer is worse than none |
| Full redundancy | When the dependency is essential and downtime is unacceptable |

## References

Summarised from the cited source.
