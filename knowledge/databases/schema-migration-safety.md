---
id: schema-migration-safety
title: Schema Migration Safety
description: >-
  Expand-contract migrations that keep old and new code working simultaneously, so a schema
  change never requires downtime or a synchronised deploy.
category: databases
tags: [migrations, deployment, schema]
maturity: stable
confidence: high
applies_at_stage: ["1", "2", "3", "4", "5"]
related: [transactions-and-mvcc, backup-restore-and-pitr]
complexity_cost: 0
trade_offs:
  - gains: "Schema changes without downtime, and each step is independently reversible"
    costs: "Several deploys instead of one, and a period where both shapes must be supported"
    when_worth_it: >-
      Whenever the deploy is rolling rather than atomic, which is any system with more than
      one instance. Below that, a short maintenance window may genuinely be simpler.
failure_modes:
  - mode: "Column dropped or renamed in one step"
    symptom: "Old instances error during the rolling deploy window"
    detection: "Errors referencing a missing column during deploy"
    mitigation: "Expand, migrate, switch, then contract in a later release"
  - mode: "Blocking DDL on a large table"
    symptom: "Table locked; every query on it queues; effective outage"
    detection: "Lock waits during migration"
    mitigation: "Concurrent index creation; batched backfills; short lock timeouts on DDL"
  - mode: "Backfill in one statement"
    symptom: "Long transaction, replication lag, bloat"
    detection: "Single UPDATE touching millions of rows"
    mitigation: "Batch with a bounded rate and commit between batches"
anti_patterns:
  - "Renaming a column in a single migration"
  - "Adding a NOT NULL column with a default to a large table without checking whether it rewrites"
references:
  - title: "Zero-downtime schema migrations"
    type: engineering-blog
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

**Expand-contract**: make the schema tolerate both old and new code, migrate, switch, then remove
the old shape in a later release.

```
1 Expand    add the new column, nullable; old code unaffected
2 Backfill  populate in bounded batches
3 Dual-write both shapes written; reads still from old
4 Switch    reads move to new
5 Contract  remove the old column, a release later
```

Renaming a column becomes five safe steps instead of one unsafe one.

## When it applies

Any system where deploys are rolling rather than atomic — which is any system with more than one
instance. During the rolling window, old and new code run simultaneously against one schema.

Also applies to a single instance where the deploy is not instantaneous, and to any change on a
table large enough that DDL takes a noticeable lock.

## When it does not apply

**Genuinely additive changes.** Adding a nullable column that no old code touches is one safe step.
Do not ceremonially expand-contract everything.

**When a maintenance window is genuinely acceptable.** For an internal tool with a stated 99%
target, a two-minute window is cheaper than five deploys, and choosing it deliberately is fine.

**Before real users exist.** At prototype stage, recreate the schema. Expand-contract on a database
with no users is process for its own sake.

## How it works

The constraint is the rolling window: for some minutes, both versions of the code are live. Every
migration step must be compatible with the version before it and the version after it.

Backfills need bounded batches with commits between them. One statement touching millions of rows is
a long transaction, and long transactions cause the problems described in `transactions-and-mvcc`.

## Trade-offs

More deploys and a period of dual-shape support, in exchange for no downtime and independently
reversible steps. The reversibility is the underrated part: each step can be rolled back alone.

## Failure modes

Blocking DDL on a large table is the one that becomes an incident: an `ALTER` that takes a full lock
queues every query behind it, which is an outage regardless of how quickly it completes.

## Measurement

Track migration duration, lock wait time during migration, and replication lag during backfills. Set
a short lock timeout on DDL so a migration fails fast rather than blocking traffic.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Expand-contract | Default for rolling deploys |
| Single additive migration | Genuinely additive, no old-code interaction |
| Maintenance window | Small systems with an accepted downtime budget |
| Online schema change tooling | Very large tables where native DDL is unsafe |

## References

Summarised from the cited source.
