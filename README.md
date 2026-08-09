<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo/oab-logo-on-dark.png">
  <img src="assets/logo/oab-logo-on-light.png" alt="OAB — Open Architecture Brain" width="420">
</picture>

**Architecture intelligence for AI coding agents.**

> Open knowledge. Open reasoning. Open architecture.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-pre--release-orange.svg)](ROADMAP.md)

---

> ⚠️ **Pre-release. Nothing is installable yet.**
> The design is complete and the build is in progress — follow the
> [M1 milestone](https://github.com/mhayk/oab/milestone/1).
> This README is replaced with the real one, including sample output, in
> [#41](https://github.com/mhayk/oab/issues/41).

## What is OAB?

An open, vendor-neutral **architecture intelligence layer** for AI coding agents. It turns system
design knowledge into executable, auditable reasoning: assumptions, formulas, numbers, trade-offs,
and a decision — with a measurable condition under which that decision must be revisited.

Ask a coding agent to "design a scalable API" and you will usually get Kubernetes, Kafka, Redis and
three microservices — for a product with 100 users and one developer. The agent learned the
*aesthetics* of system design from material drawn almost entirely from the largest 0.1% of systems.
It did not learn the *economics*.

OAB's primary job is to compute that 100 users at 40 requests per session is **0.28 requests per
second**, that a single instance has four orders of magnitude of headroom, and to say so — while
naming the exact measurement that would change the answer.

## Where things stand

- 📐 [**Design proposal**](docs/design/) — the complete reasoning behind the project
- 🗺️ [**Roadmap**](ROADMAP.md) — what is being built, and what is deliberately not
- 🧭 [**Execution plan**](docs/design/10-m1-execution-plan.md) — 43 issues, sequenced

## Contributing

The most valuable contribution is **architecture knowledge**, and it requires no understanding of
the codebase — see [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

[Apache-2.0](LICENSE). The OAB name and logo are trademarks and are not covered by that licence —
see [NOTICE](NOTICE).

[oab.run](https://oab.run)
