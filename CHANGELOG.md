# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Because OAB's behaviour is its interface, a change to a framework procedure that materially changes
the architecture OAB recommends is treated as a **breaking change**, the same as a schema change.

## [Unreleased]

Nothing yet.

## [0.1.7] — 2026-08-09

**The M1 release.** Planned as v0.1.0; the version counter was consumed by live-run iterations
(0.1.0 → 0.1.7), each bump required to reach the installed plugin — the per-version cache freeze
documented in `docs/maintainers/release.md`. Reusing an earlier string would collide with stale
caches, so the milestone ships under the number it reached.

All three manual verification steps passed with live, unedited evidence:

- **Install**: marketplace add + install from GitHub on this machine; fresh clone 0.8 s, 8.1 MB —
  well inside the ADR-0003 thresholds (5 s, 50 MB).
- **`/oab:design`**: run 7 passes every scenario-01 assertion and full schema validation
  (`examples/live-run/`). Six earlier runs without an executing hook all failed the same
  assertion; the mechanism, not more instructions, closed it.
- **`/oab:review`**: linkding reviewed; all 8 evidence citations verified against the code, zero
  scale-inappropriate findings, SQLite praised as the correct choice (`examples/live-review/`).

Known caveat: hooks from **marketplace-installed** plugins did not execute in headless sessions,
while the identical hook via `--plugin-dir` did (#45). The evaluation harness uses `--plugin-dir`;
skill-level validation instructions remain as the fallback layer for installed plugins.

### Added

**Reasoning**
- Six client-agnostic frameworks with blocking gates: discovery, capacity planning, complexity
  budget, architecture design, architecture review, evolution triggers.
- The complexity budget: `available = 4 + 1.5 × (engineers − 2) + 4 × dedicated_ops`, with weights
  as data in `frameworks/complexity-budget/weights.yaml` and its limitations stated in the
  procedure itself.

**Knowledge**
- 37 units across fundamentals, databases, caching, messaging, reliability and cost. Every unit
  carries a non-empty `When it does not apply` section, quantified thresholds, structured
  trade-offs and failure modes, and attributed references.
- Generated per-domain indexes carrying stage and complexity cost, so an agent can select
  precisely rather than reading everything.

**Arithmetic**
- Eight standard-library calculators — RPS, storage, bandwidth, concurrency, connections, cache,
  queue, cost — with 43 tests including worked examples tied to the design documents.
- Confidence is computed from the inputs rather than asserted, and results derived from
  assumptions round to two significant figures.

**Contracts**
- Nine JSON Schemas and 33 fixtures validating in both directions.
- `design-output` and `review-output` are what make deterministic evaluation possible.

**Evaluation**
- Runner, assertion library, and five scenarios: three overengineering guards and two
  underengineering guards. Assertions target artifact fields, never prose.
- Perturbation at 100× and 0.01× proves scenarios respond to magnitude rather than to specific
  numbers.

**Integration**
- Plugin manifests, four commands, a background principles skill, and a repository-scanner
  subagent. `claude plugin validate ./ --strict` passes.
- A `PostToolUse` hook that validates OAB artifacts the moment they are written and returns the
  missing fields to the agent. Six live runs proved prompt-level instruction cannot guarantee a
  field appears in an artifact; the first run with the hook executing passed every scenario
  assertion. Caveat: fires via `--plugin-dir` but not for marketplace-installed plugins in
  headless sessions (#45).

**Project**
- Founding design proposal (`docs/design/`), including a critique of its own founding brief.
- Brand assets: mark and icon as true SVG from isometric geometry, wordmark generated from Sora
  outlines by `tools/build_wordmark.py`.
- Apache-2.0 with a `NOTICE` carving out the name and mark as trademarks.
- Seven CI guards: schema validation, referential integrity, vendor neutrality, stdlib-only
  calculators, price staleness, link resolution, and index freshness.
- One static landing page for oab.run, with no build step and no runtime external request.

[Unreleased]: https://github.com/mhayk/oab/compare/v0.1.7...HEAD
[0.1.7]: https://github.com/mhayk/oab/releases/tag/v0.1.7
