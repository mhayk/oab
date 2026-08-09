---
name: review
description: >-
  Review the architecture of the current repository. Inventories what exists, establishes the
  system's actual operating scale, and reports findings weighted by that scale — never
  theoretical problems.
argument-hint: "[optional: path or area to focus on]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob
---

# Architecture review

Scope: **$ARGUMENTS** (whole repository if empty)

Follow `${CLAUDE_PLUGIN_ROOT}/frameworks/architecture-review/procedure.md`. Read it now.

## The governing rule

> **Do not report theoretical problems.** A single database instance is not a finding for a
> system with no availability target and 30 requests per second.

A reviewer who flags every deviation from large-scale practice produces a document the team
correctly ignores — and loses the ability to be heard about what matters.

## 1. Inventory

Delegate to the `oab:repo-scanner` agent. It returns facts only, conforming to
`${CLAUDE_PLUGIN_ROOT}/schemas/repo-facts.schema.json`. Keeping the scan out of this context
keeps the review readable.

## 2. Context — a blocking gate

**No finding before this is established.** Prefer observed evidence: analytics configuration,
existing dashboards, README claims, commit cadence, distinct authors in the last 6 months.

Then ask **at most 3** questions. Where unknown, **assume small and say so** — assuming large
is how a 100-user application gets told it needs multiple regions.

Record every context assumption with a confidence, so a reader who disagrees with the scale
can discount the findings rather than the tool.

## 3. Analyse

**Always, at every scale** — their failure is not proportional to traffic:

- Backups exist **and restore has been tested**
- Every outbound call has an explicit timeout
- Errors are visible (error tracking present)
- Secrets are not committed
- Migrations are reversible or expand/contract
- Deploys do not need extended downtime

**Given the measured scale**: bottlenecks against the actual numbers, single points of failure
whose failure exceeds the stated availability requirement, synchronous work a latency budget
says should be async, security boundaries, observability gaps, and **unnecessary complexity** —
components with no measured problem to solve.

## 4. Severity — the anti-rules

Never findings: "no orchestration platform" · "not microservices" · "no service mesh" ·
"single region" · "no event streaming" · "not on the latest framework version" (absent a known
vulnerability).

**Downgrade check** before any HIGH or CRITICAL: *would this still be HIGH if the system stays
exactly this size for two more years?* If not, it is MEDIUM with a trigger.

**A finding without `file:line` evidence is deleted, not softened.**

## 5. Report

Write `.oab/review.json` conforming to
`${CLAUDE_PLUGIN_ROOT}/schemas/review-output.schema.json`, then `docs/architecture/review.md`
using `${CLAUDE_PLUGIN_ROOT}/templates/architecture-review.md`.

**Zero findings is a valid and valuable outcome:**

> "No findings. The architecture is proportional to its measured scale and the operational
> fundamentals are in place. Watch these triggers rather than changing anything now."

Summary first, one page. If the architecture is appropriate, say so in the first sentence.
