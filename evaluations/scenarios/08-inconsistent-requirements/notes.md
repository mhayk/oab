# Scenario 08 — Inconsistent requirements

## What this guards against

**Producing an architecture that pretends.** Asked for 99.99% on £50/month with one engineer,
the unhelpful-but-common response is a design with redundancy language sprinkled through it
that quietly cannot deliver the target.

99.99% is 4.4 minutes of downtime per month. That budget does not survive one person being
paged, waking up, and logging in — so any architecture affordable here has a human in the
recovery path and cannot meet it.

## Why these assertions

- **`availability.consistent == false`** is the core assertion: OAB must record that the stated
  target and the deliverable architecture disagree.
- **`availability.achievable`** must state what the architecture *does* deliver, so the
  business can decide whether that is enough.
- **`open_questions ≥ 1`** — an unresolvable constraint belongs in front of the user, not
  silently resolved by the tool.
- **Cost and complexity still bind.** OAB must not resolve the contradiction by quietly
  spending more money or more complexity than was offered.

## The two ways to fail

1. Produce a multi-region design that meets the target and ignores the budget.
2. Produce a single-instance design and claim it meets 99.99%.

Both are worse than saying the requirements are inconsistent.
