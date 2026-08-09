# Scenario 02 — Growing SaaS

## What this guards against

**Under-provisioning**, and the mirror image of scenario 01: a tool that always says "one
server" would pass every overengineering guard and be useless. This scenario requires workers,
a real complexity budget, and modelled operational cost.

It also guards a specific overreach: at 21 writes/second and 2.3 jobs/second, **event streaming
is not justified** and a connection pooler is not justified — 6 instances at a pool of 5 is 30
connections against a limit of 100. Both must be rejected with the arithmetic shown.

## Why these assertions

- **`peak_rps` between 100 and 400** — 25k DAU × 3 sessions × 60 requests is 4.5M/day = 52 RPS
  average, ×4 peak factor = 208. Outside this band the arithmetic is wrong.
- **`complexity.available ≥ 10`** — eight engineers gives 13. A design that computes a small
  budget here has misread the team.
- **`cost.monthly_operational.low ≥ 1`** — the operational line must be modelled at all. For
  this team it exceeds the infrastructure line, which is the finding that decides
  managed-versus-self-hosted.
- **`must_reject_components: [event-stream]`** — refusing it silently is not enough; the
  rejection and its threshold must be recorded.
