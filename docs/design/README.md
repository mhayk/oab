# OAB Design Proposal

> Status: **Proposed** — design only, no implementation.
> Date: 2026-08-09
> Author: Mhayk Whandson

This directory contains the founding design proposal for **OAB — Open Architecture Brain**,
an open, vendor-neutral architecture intelligence layer for AI coding agents.

Nothing here is code. This is the reasoning that must be settled *before* code, so that the
first 5,000 lines of OAB are not an accident.

## How to read this

| Document | Covers | Read it if you want to know |
| :-- | :-- | :-- |
| [01 — Vision & Positioning](01-vision.md) | §1–8 | What OAB is, why it exists, who it's for, and what it is *not* |
| [02 — Repository & Integrations](02-repository-and-integration.md) | §9–11 | The repo layout, the Claude Code plugin design, how other agents plug in |
| [03 — Knowledge System](03-knowledge-system.md) | §12–15 | How knowledge is stored, schema'd, linked, and consumed by a reasoning agent |
| [04 — Frameworks](04-frameworks.md) | §16–22 | Decisions, capacity, review, performance, reliability, cost, evolution |
| [05 — Evaluation](05-evaluation.md) | §23 | How we prove OAB reasons well — and detect over- *and* under*-engineering |
| [06 — Documentation & oab.run](06-documentation-and-website.md) | §24–25 | Docs architecture and the smallest useful website |
| [07 — Roadmap & Risks](07-roadmap-and-risks.md) | §26–32 | M1, M2, roadmap, risks, and a blunt overengineering critique of the brief |
| [08 — Technology & Worked Examples](08-technology-and-worked-examples.md) | §33–36 | Tech choices with justification; three end-to-end reasoning walkthroughs |
| [09 — Specifications](09-specifications.md) | §37–42 | Repo tree, commands, knowledge schema, ADR schema, trigger schema, system diagram |
| [10 — M1 Execution Plan](10-m1-execution-plan.md) | §43 | Sequenced, independently reviewable GitHub issues with acceptance criteria |

## The three sentences that matter

1. **OAB turns system design knowledge into executable, auditable reasoning** — assumptions, formulas, numbers, trade-offs, and a decision, not vibes.
2. **OAB's primary job is saying "no"** — refusing complexity that the measured problem does not justify is the feature, and it is the one thing generic assistants reliably get wrong.
3. **OAB must obey its own advice** — Markdown, YAML, JSON Schema, one small stdlib script, no server. If OAB needs a database to give architecture advice, OAB has failed its own review.

## Design constraints accepted for M1

- Apache-2.0, 100% open source, no hosted dependency for any core capability.
- Claude Code is the **first client**, never the platform. Every Claude-specific artifact lives under `integrations/claude-code/`.
- Deterministic over probabilistic wherever the choice exists.
- Nothing enters M1 that cannot be tested or demonstrated on day one.

## What we deliberately deferred

The brief proposes far more than a credible first milestone can carry. The full critique is in
[§32 Overengineering Review](07-roadmap-and-risks.md#32-overengineering-review). Summary of what is
**cut from M1**: MCP server, knowledge-graph generation, 18 knowledge domains, LLM-judge evaluation,
the 25-section output template, `GOVERNANCE.md`, a documentation site framework, and every
integration other than Claude Code.
