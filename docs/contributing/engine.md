# Contributing to the engine

> **Status: not yet written.**
> This guide lands with [issue #39](https://github.com/mhayk/oab/issues/39).
> Until then, the design documents below describe the intended shape.


Read in the meantime:

- [Repository architecture](../design/02-repository-and-integration.md) — the layering rule and why
  dependencies point downward only
- [The reasoning frameworks](../design/04-frameworks.md) — decisions, capacity, review, performance,
  reliability, cost, evolution
- [Evaluation](../design/05-evaluation.md) — how a reasoning change is defended against regression

## The deletion test

The structural claim that makes OAB vendor-neutral is testable:

> **Deleting `integrations/` must leave a complete, coherent, useful project.**

If a change would break that test, it is in the wrong directory. Architecture knowledge and
reasoning live in `knowledge/` and `frameworks/`; `integrations/` contains only the mapping onto a
specific client's extension model.

CI enforces the mechanical form of this with `tools/check_neutrality.py`: no AI vendor or model
name inside the client-agnostic core — `knowledge/`, `frameworks/`, `calculators/`, `schemas/`,
`templates/`, `evaluations/`.

It deliberately does not police project documentation. A README that cannot say which agents OAB
works with is not neutral, it is unhelpful.

A line containing `neutrality-ok` is exempt. Use it with a stated reason so every exemption is
visible in review.

`tools/check_stdlib_only.py` enforces the other half: `calculators/` imports nothing outside the
standard library, because those calculators run on a user's machine through their agent.

## Integrations

An integration consumes three things and adds nothing to them:

1. `frameworks/<name>/procedure.md` — client-agnostic procedures
2. `knowledge/**/*.md` plus the generated indexes
3. `schemas/*.json` — the artifact contracts

If you are writing architecture guidance inside `integrations/`, it belongs upstream.
