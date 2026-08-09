---
id: ADR-0003
title: Use the repository root as the plugin root
status: accepted
date: 2026-08-09
deciders: [maintainers]
tags: [packaging, integration, distribution]
complexity_delta: 0
monthly_cost_delta: { currency: GBP, value: 0 }
reversibility: easy
confidence: high
triggers: [plugin-payload-size]
---

# ADR-0003 — Use the repository root as the plugin root

## Status
Accepted — 2026-08-09

## Context

OAB's value is in `knowledge/` and `frameworks/` at the repository root. A skill can only read
files inside the plugin root. If the plugin were `integrations/claude-code/`, then
`${CLAUDE_PLUGIN_ROOT}` would resolve to that subdirectory and **the knowledge base would not
ship with the plugin** — leaving an integration that points at files the user does not have.

This was identified in `docs/design/02-repository-and-integration.md` §10.2 as the design's
highest-uncertainty decision, and issue #28 time-boxed a spike to settle it before anything was
built on top.

## Requirements
- R1: A skill must be able to read `knowledge/` and `frameworks/` at runtime.
- R2: No build or publish step in M1.
- R3: One source of truth — no duplicated knowledge.

## Options Considered

### Option A — Release build copies `knowledge/` into the plugin directory
Gains: a slim published plugin.
Costs: a build pipeline and a drift class (published plugin ≠ repository) before there is any
need for either. Violates R2.

### Option B — Duplicate knowledge inside the integration
Costs: two sources of truth. Violates R3. Rejected without further analysis.

### Option C — Git submodule
Costs: submodules are a well-known trap for first-time contributors, and knowledge
contribution is the project's primary growth vector.

### Option D — Plugin root = repository root
Marketplace entry with `"source": "./"` and explicit component paths.
Gains: satisfies all three requirements with no machinery.
Costs: the plugin cache holds the whole repository.

## Decision

Option D. `.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json` both live at the
repository root; the plugin entry uses `"source": "./"` with explicit `skills` and `agents`
paths into `integrations/claude-code/`.

## Rationale

Verified, not assumed. `claude plugin validate ./ --strict` passes, and the documented
marketplace-root behaviour resolves `${CLAUDE_PLUGIN_ROOT}` to the repository so skills can read
`knowledge/` and `frameworks/`.

**The spike found one real defect.** The first manifest pointed `agents` at a *directory*:

```json
"agents": ["./integrations/claude-code/agents"]        // ✘ plugins.0.agents: Invalid input
"agents": ["./integrations/claude-code/agents/repo-scanner.md"]   // ✔
```

Unlike `skills`, the `agents` field takes files rather than directories. CI caught the same
error independently, which confirms the validation step is doing its job.

## Trade-offs Accepted

- The plugin cache holds `docs/`, `evaluations/`, and `schemas/` as well as the parts a skill
  reads. At present that is a few megabytes of Markdown — immaterial.
- Adding a second integration will place a second client's files in the same plugin payload.
  Acceptable until there is a second integration; revisit then.

## Consequences

- No build step, no publish pipeline, and no drift between the repository and the published
  plugin.
- `agents` entries must be listed as individual files, and a new agent requires a manifest edit
  rather than only a new file.

## Migration Path

If the size trigger fires, Option A is the pre-analysed fallback: a release script assembling a
slim plugin directory. Roughly a day of work, and it changes only the manifests and the release
process — no skill, framework, or knowledge change, because none of them depend on *how* the
plugin is assembled, only that they are reachable.

## Observability

- Repository size, checked at each release.
- Plugin install time on a clean machine, recorded at each release.

## Revisit Conditions

`plugin-payload-size`: repository exceeds **50 MB**, or `git clone` of the plugin exceeds
**5 seconds** on a normal connection, measured at release. Action: implement Option A.
Owner: maintainers.
