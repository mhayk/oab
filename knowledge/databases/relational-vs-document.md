---
id: relational-vs-document
title: Relational versus Document Databases
description: >-
  Choosing a datastore from workload characteristics — access patterns, relationships, and
  consistency needs — rather than from preference or familiarity.
category: databases
tags: [datastore-selection, relational, document]
maturity: stable
confidence: high
applies_at_stage: ["0", "1", "2", "3", "4", "5"]
related: [indexing-fundamentals, transactions-and-mvcc, partitioning-and-sharding]
complexity_cost: 0
trade_offs:
  - gains: "Relational gives joins, constraints, and transactions across entities; document gives schema flexibility and locality for whole-object access"
    costs: "Relational needs schema migrations; document pushes integrity and joins into application code"
    when_worth_it: >-
      Relational is the correct default for systems with related entities and unknown future
      query patterns. Document wins when access is genuinely by whole document and the shape varies.
failure_modes:
  - mode: "Document store chosen for schema flexibility, then queried relationally"
    symptom: "Application-side joins, N+1 fetches, growing consistency bugs"
    detection: "Multiple round trips to assemble one view"
    mitigation: "Model by access pattern, or move to relational"
  - mode: "Relational schema modelled as a document"
    symptom: "Large JSON columns queried with path expressions instead of indexed columns"
    detection: "Queries filtering inside JSON on hot paths"
    mitigation: "Promote queried fields to columns with indexes"
anti_patterns:
  - "Choosing by team familiarity when access patterns clearly indicate otherwise"
  - "Adopting a second datastore before the first has a measured limitation"
references:
  - title: "Designing Data-Intensive Applications: data models and query languages"
    author: "Martin Kleppmann"
    type: book
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

Relational stores normalise entities into tables and join at query time. Document stores keep
related data together and retrieve it in one read.

## When it applies

Choose from the workload:

| Signal | Points to |
| :-- | :-- |
| Entities with meaningful relationships | Relational |
| Query patterns not fully known yet | Relational — joins let you ask new questions without remodelling |
| Transactions spanning entities | Relational |
| Reporting and ad-hoc analysis | Relational |
| Access is always the whole document by id | Document |
| Shape varies genuinely per record | Document |
| Very high write throughput on independent records | Document or wide-column |

**Relational is the correct default** for most systems, primarily because it does not require you
to know your query patterns in advance — and at the point of choosing, you do not.

## When it does not apply

**When the choice is already made.** An existing system with a working datastore needs a measured
limitation before migration, not a preference.

**When both work.** Below significant scale, either handles the load. Then the decision should be
made on team familiarity and operational maturity, and saying so is more honest than manufacturing
a technical justification.

**For genuinely specialised workloads** — time-series, graph traversal, full-text ranking — where
neither general-purpose option is the right shape.

## How it works

The real question is where the join happens. Relational joins in the database, with the optimiser's
knowledge of statistics and indexes. Document stores join in application code, or avoid joins by
duplicating data — which then needs keeping consistent.

## Trade-offs

Relational costs schema migrations and, at extreme scale, harder horizontal partitioning. Document
costs application-side integrity, and remodelling when access patterns change.

## Failure modes

The recurring one is a document store chosen for flexibility, then queried relationally: N+1
fetches, application-side joins, and consistency bugs that a foreign key would have prevented.

## Measurement

Track queries per request and whether hot paths need application-side assembly. Rising round trips
per view is the signal that the model no longer matches the access pattern.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Relational | Default |
| Document | Whole-document access with genuinely variable shape |
| Relational with JSON columns | Mostly structured with a variable region — usually the best of both |
| Two datastores | Only with a measured limitation; costs an extra complexity point |

## References

Summarised from the cited source.
