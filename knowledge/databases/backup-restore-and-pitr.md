---
id: backup-restore-and-pitr
title: Backup, Restore and Point-in-Time Recovery
description: >-
  An untested restore is not a backup; recovery objectives, not backup frequency, are what
  determine whether the strategy is adequate.
category: databases
tags: [backup, restore, disaster-recovery, rpo, rto]
maturity: stable
confidence: high
applies_at_stage: ["0", "1", "2", "3", "4", "5"]
related: [managed-vs-self-hosted, availability-targets, schema-migration-safety]
complexity_cost: 0
trade_offs:
  - gains: "Recoverable data; a bounded worst case for the most unrecoverable class of failure"
    costs: "Storage, and the discipline to test restores"
    when_worth_it: >-
      Always, at every scale. This is scale-independent: data loss is not proportional to
      traffic, and it is the one failure with no workaround.
failure_modes:
  - mode: "Backups run, restores never tested"
    symptom: "Restore fails or takes far longer than assumed, discovered during the incident"
    detection: "No record of a restore test"
    mitigation: "Test quarterly; record the elapsed time as the real RTO"
  - mode: "Backups stored only alongside the primary"
    symptom: "The event that destroys the database destroys the backups"
    detection: "Backups in the same account, region, or credential scope as the primary"
    mitigation: "Separate the failure domain and the credential scope"
  - mode: "Logical corruption within the retention window"
    symptom: "Corruption propagated to every backup before it was noticed"
    detection: "Retention shorter than the time to detect a subtle bug"
    mitigation: "Retention longer than your realistic detection time; PITR to a chosen moment"
anti_patterns:
  - "Trading backups away because the system is small"
  - "Assuming a managed service means recovery is not your responsibility"
references:
  - title: "PostgreSQL continuous archiving and point-in-time recovery"
    type: official-docs
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

Three distinct things, often conflated:

| | Answers |
| :-- | :-- |
| **Backup** | Can the data be reconstructed? |
| **Restore** | How long does reconstruction take, and has anyone done it? |
| **PITR** | Can we recover to a *specific moment*, before a bad deploy or a bad migration? |

Sized by two objectives: **RPO** (how much data may be lost) and **RTO** (how long recovery may
take).

## When it applies

Every system with data anyone would miss, at every stage. This is one of the fundamentals that is
**not proportional to traffic** — a 100-user application losing its database is as total a failure
as a large one.

PITR specifically matters where the realistic disaster is **logical**: a bad migration, a wrong
`DELETE`, an application bug corrupting rows. Restoring last night's snapshot loses a day; PITR
loses minutes.

## When it does not apply

**Where the data is genuinely reconstructible** from an authoritative source — a read-only cache,
a derived search index, a materialised view. Back up the source; document how the derivative is
rebuilt, and how long that takes.

**For ephemeral prototype data** nobody would miss. Say so explicitly rather than leaving it
implicit, because "prototype" data has a habit of becoming production data.

## How it works

Snapshots plus continuous write-ahead log archiving allow recovery to any moment in the retention
window. Managed services usually provide this; self-hosted requires configuring and verifying it.

The number that matters is not backup frequency. It is **measured restore time**, because that is
the actual RTO — and it is almost always longer than assumed, since restoring a large database is
bounded by I/O rather than by intention.

## Trade-offs

Storage cost and the discipline of testing. Both are small against the alternative, which has no
workaround.

## Failure modes

The one that recurs: backups that run successfully for two years and a restore nobody has
attempted. The second: backups in the same failure domain and credential scope as the primary, so
the event that destroys one destroys both.

## Measurement

Record for each database: RPO target versus actual, **measured** restore time from a real test,
date of the last successful restore test, and retention window.

A restore test older than a quarter should be treated as no restore test.

## Alternatives

| Approach | When to prefer |
| :-- | :-- |
| Managed automated backup + PITR | Default; the main reason to prefer a managed database |
| Snapshot only | Where an RPO of hours is genuinely acceptable |
| Replica as a backup | **Not a backup.** Replicas faithfully replicate `DELETE` too |

## References

Summarised from the cited documentation.
