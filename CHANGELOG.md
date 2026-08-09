# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Because OAB's behaviour is its interface, a change to a framework procedure that materially changes
the architecture OAB recommends is treated as a **breaking change**, the same as a schema change.

## [Unreleased]

Everything below is built and green in CI. The release is held pending the three manual
verification steps in `docs/maintainers/release.md` that cannot be automated — a clean-machine
install, a real `/oab:design` run asserted with the evaluation runner, and a real `/oab:review`
of a third-party repository.

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

**Project**
- Founding design proposal (`docs/design/`), including a critique of its own founding brief.
- Brand assets: mark and icon as true SVG from isometric geometry, wordmark generated from Sora
  outlines by `tools/build_wordmark.py`.
- Apache-2.0 with a `NOTICE` carving out the name and mark as trademarks.
- Seven CI guards: schema validation, referential integrity, vendor neutrality, stdlib-only
  calculators, price staleness, link resolution, and index freshness.
- One static landing page for oab.run, with no build step and no runtime external request.

[Unreleased]: https://github.com/mhayk/oab/commits/main
