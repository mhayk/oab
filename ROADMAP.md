# Roadmap

OAB is pre-release. Nothing below is a commitment with a date; it is the order we intend to build
in, and why.

The reasoning behind this sequencing is in [`docs/design/07-roadmap-and-risks.md`](docs/design/07-roadmap-and-risks.md).

## Status today

| Area | State |
| :-- | :-- |
| Design proposal | ✅ Complete |
| Brand assets | ✅ Complete |
| Repository foundation and CI | ✅ Complete |
| Schemas and contracts | ✅ Complete — 9 schemas, 33 fixtures |
| Calculators | ✅ Complete — 8 calculators, 43 tests |
| Frameworks | ✅ Complete — 6 procedures |
| Knowledge | ✅ Complete — 37 units, 6 domains |
| Agent integration | ✅ Built — manifest validates |
| Evaluation suite | ✅ Complete — 5 scenarios passing |
| Docs, examples, website | ✅ Complete |
| **v0.1.0 release** | 🚧 **Held on manual verification** |

**42 of 43 M1 issues are closed.** What remains cannot be automated: a clean-machine install, a
real `/oab:design` run asserted against the scenario, and a real `/oab:review` of a third-party
repository. See [#43](https://github.com/mhayk/oab/issues/43) and
`docs/maintainers/release.md`.

Until those pass, treat the committed examples as **reference artifacts** rather than as evidence
of live behaviour.

## M1 — Prove the idea

> A developer installs the plugin and, within five minutes, gets an architecture design or a
> repository review that a Principal Engineer would recognise as competent — with real numbers,
> named rejected alternatives, and measurable revisit triggers.

- Four commands: `/oab:design`, `/oab:review`, `/oab:capacity`, `/oab:adr`, plus a background
  principles skill that improves ordinary architecture conversation
- Six reasoning frameworks, including the complexity budget
- ~40 knowledge units across 6 domains — depth over breadth
- 8 deterministic calculators, unit-tested
- 8 JSON Schemas defining every structured artifact
- Evaluation suite catching both over- and under-engineering
- Three committed end-to-end examples

**Explicitly not in M1:** MCP server, knowledge graph generation, additional integrations, hosted
anything, accounts, telemetry, diagram rendering, load-test tool integration, governance documents,
or more than six knowledge domains. See
[§32 Overengineering Review](docs/design/07-roadmap-and-risks.md#32-overengineering-review) for the
reasoning — including a critique of our own founding brief.

## M2 — Depth and durability

The milestone that proves OAB keeps earning its place after day one.

- `/oab:evolve` — check recorded triggers against current metrics and report which architectural
  decisions have expired. This is the retention feature.
- Focused commands split out of `/oab:design`: `scale`, `performance`, `reliability`, `cost`,
  `security` — promoted based on actual usage, not speculation
- Knowledge grows to ~150 units across 12 domains
- Knowledge graph generation and rendering
- Calculators for LLM inference cost and vector store sizing
- Complexity budget calibrated against ≥20 real projects, with the agreement rate published
- `oab.run` renders the knowledge base and examples
- Governance: maintainer roles and an RFC process, once there are more than three regular
  contributors

## M3 — Interoperability

Conditional on demand, not built speculatively.

- A second integration (Cursor or Codex) via a generator that emits client artifacts from the same
  framework sources
- An MCP server exposing calculators and knowledge search — **only** if a client cannot consume the
  repository directly, or three or more users request it with a stated use case
- A GitHub Action: architecture gate on pull requests, reporting complexity delta and missing ADRs
- Load-test plan emitters for k6 and Gatling

## M4 — Continuity

- Metrics adapters so evolution triggers evaluate against real telemetry instead of hand-entered
  numbers. This is the step that makes triggers automatic rather than manual.
- Architecture drift detection between recorded ADRs and repository reality
- Multi-repository and platform-level review

## M5 — Ecosystem

- Community knowledge domains: fintech, healthcare, gaming, IoT, ML platforms
- Organisation-specific knowledge overlays layered on the open base
- A mechanism for consuming a private knowledge pack alongside the public one

## Standing non-goals

At every milestone, OAB will not have:

- A hosted service that any core capability depends on
- Proprietary tiers or an open-core model
- Telemetry
- A knowledge base gated behind an account
- Architecture *automation* — OAB advises; humans decide
- Ambitions to become a general-purpose coding agent
