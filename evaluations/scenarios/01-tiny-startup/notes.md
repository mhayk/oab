# Scenario 01 — Tiny startup

## What this guards against

**Overengineering** — the failure OAB exists to prevent, and the one generic assistants
reliably produce. Asked to design "a scalable API", an assistant typically returns an
orchestration platform, an event broker, a cache, and three services, for a product with
100 users and one developer.

## Why these assertions

- **`must_not_include_components`** checks the components array, not the prose. A framework
  can be tuned to produce reassuring words far more easily than the right structure.
- **`must_reject_components`** is the stronger check: silently omitting a cache is not the
  same as considering one and refusing it. Only the second gives the reader something to
  disagree with, and the assertion also requires `revisit_when` on each rejection.
- **`peak_rps ≤ 5`** — 100 users at 40 requests per session is 0.28 RPS. Even at 100% daily
  active with a 20× peak factor it is 1.9. Anything above 5 means the arithmetic is wrong.
- **`complexity.spent ≤ complexity.available`** — two developers have a budget of 4. The
  design must fit, without an override.
- **`triggers ≥ 3`** — a design with no expiry conditions cannot be revisited safely.

## What this scenario deliberately does not assert

The specific products chosen. OAB is vendor-neutral, so components are asserted by generic
kind. A design naming any particular managed database passes; one adding an orchestration
platform does not.
