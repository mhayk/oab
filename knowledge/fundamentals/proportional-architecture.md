---
id: proportional-architecture
title: Proportional Architecture
description: >-
  Architecture must be proportional to the measured problem; every component carries
  the burden of proving it is needed by current numbers, not a hypothetical future.
category: fundamentals
tags: [principles, overengineering, decision-making]
maturity: stable
confidence: high
applies_at_stage: ["0", "1", "2", "3", "4", "5"]
related: [complexity-cost, maturity-stages, utilisation-and-queueing]
complexity_cost: 0
trade_offs:
  - gains: "Systems a team can actually operate; money and attention spent on the product"
    costs: "Some rework later when a threshold is genuinely crossed"
    when_worth_it: >-
      Almost always. Rework at a known trigger is cheap and scoped; carrying unnecessary
      operational load is a continuous tax paid whether or not the growth arrives.
failure_modes:
  - mode: "Applied as dogma rather than as a threshold test"
    symptom: "Genuine requirements refused; the system fails under load it was told about"
    detection: "A rejected component whose rejection reason cites no measurement"
    mitigation: "Every rejection names the number that would reverse it"
  - mode: "Used to justify skipping scale-independent fundamentals"
    symptom: "No backups, no timeouts, no error tracking, because the system is small"
    detection: "Absence of the fundamentals listed below at any scale"
    mitigation: "Treat those as unconditional; they are not proportional to traffic"
anti_patterns:
  - "Adopting a component because a larger company published a post about it"
  - "Designing for a growth curve nobody has committed to"
  - "Rejecting a component the measurements justify, out of a preference for simplicity"
references:
  - title: "The Fallacy of Premature Optimization"
    author: "Randall Hyde"
    type: paper
    accessed: 2026-08-09
  - title: "Choose Boring Technology"
    author: "Dan McKinley"
    type: talk
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

Architecture should be sized to the problem that has been measured, not to the largest problem
imaginable. Every component must justify its existence against current numbers, and the default
answer to "should we add X?" is **no** until X has a measurement behind it.

This is not a preference for small systems. It is a rule about **burden of proof**: complexity is
a cost paid continuously, so the party proposing it carries the argument.

## When it applies

Every architectural decision, at every stage. The test is mechanical:

1. What number makes this component necessary?
2. What is that number today?
3. If the answer to (2) is far below (1), the component is not justified yet — and the gap becomes
   a trigger.

Concrete thresholds that recur:

| Component | Typically unjustified below |
| :-- | :-- |
| Horizontal scaling | one instance sustained above 70% CPU at peak |
| Cache | a single key above ~10 requests/second at >50 ms to recompute |
| Read replica | primary CPU sustained above 70% after query optimisation |
| Message broker | ~500 events/second, or 3+ independent consumer groups needing replay |
| Connection pooler | 80% of the database's connection limit |
| Separate search engine | full-text search in the existing database missing a stated requirement |
| Multi-region | an availability or latency requirement that one region provably cannot meet |
| Orchestration platform | more deployable services than the team can run by hand, with dedicated operations capacity |

## When it does not apply

Three important exceptions, and getting them wrong is how this principle becomes harmful.

**Scale-independent fundamentals are unconditional.** Their failure is not proportional to traffic,
so a small system gets no discount: tested backups and restore, explicit timeouts on outbound calls,
error tracking, secret hygiene, reversible migrations. Never trade these away for simplicity.

**One-way doors deserve more analysis than their current numbers justify.** A data model, a tenancy
model, an identifier scheme, or a public API contract is expensive to reverse. Spend more thought
there than the present scale implies — the asymmetry is in reversibility, not in load.

**Known, committed, imminent load counts as measured.** A contract that starts in six weeks with
stated volumes is a number, not speculation. Proportionality is about refusing *speculative* future
load, not about ignoring known future load.

## How it works

Complexity is not paid once at adoption. It is paid every month, in on-call surface, upgrade
burden, incident diagnosis, and the time each new engineer spends learning why the component exists.
A component that will be needed in two years costs two years of that tax to avoid one scoped
migration.

The migration is also cheaper than it looks, because by the time the trigger fires you know things
you do not know now: the real access patterns, the real hot spots, and which of today's assumptions
were wrong.

## Trade-offs

The genuine cost is rework. When a trigger fires you will do work that could have been done
up-front. The trade is favourable because the rework is **scoped and informed**, while the avoided
cost is **continuous and uninformed** — and because most speculative growth never arrives.

The trade becomes unfavourable when the change is a one-way door, which is why reversibility is a
first-class field in every option.

## Failure modes

The dangerous failure is dogma: refusing a component the numbers justify because simplicity has
become an aesthetic. The guard is that every rejection must name the measurement that reverses it.
A rejection without a number is as unprincipled as an adoption without one.

## Measurement

Instrument the numbers in the threshold table for the components you have deliberately excluded.
A rejected component with no corresponding metric means nobody will notice when the rejection stops
being correct.

## Alternatives

| Approach | When it is preferred |
| :-- | :-- |
| Proportional architecture | Default |
| Design for projected scale | Load is contractually committed with stated volumes and dates |
| Design for maximum imaginable scale | Effectively never; this is the failure mode, not an option |

## References

Summarised from the cited sources; the threshold table is drawn from the domain knowledge units in
this repository rather than from any single source.
