# Scenario 03 — Large platform

## What this guards against

**Refusing complexity the numbers justify.** Proportionality is symmetric: recommending an
event stream to a 100-user application and refusing one to a platform doing 7,500 events/second
across three independent consumer groups are the same error in opposite directions.

A tool biased toward simplicity would pass scenarios 01, 07 and 08 while being useless here.

## Why these assertions

- **`egress_gb_per_month ≥ 100,000`** — 50,000 RPS at 8 KB is roughly 1 PB/month. Egress must
  be *computed*, because at this scale it is the largest line on the invoice: about $52k/month
  origin-served, falling to $17k with 85% edge offload. That single calculation is worth more
  than the entire compute fleet of scenario 02.
- **`cdn` required** — it is the largest cost lever available, and it is an arithmetic result
  rather than an architectural fashion.
- **`complexity.available ≥ 50`** — 40 engineers with 4 SRE gives 77. At this scale the budget
  stops being the binding constraint, and a design that reports it as binding has misapplied
  the heuristic. Cost and blast radius are the real constraints here.
- **`availability.consistent == true`** — unlike scenario 08, the target is achievable and the
  architecture must actually deliver it.

## What this scenario does not assert

An orchestration platform. Even at this scale it is a choice, not a requirement, and asserting
it would encode a preference rather than a threshold.
