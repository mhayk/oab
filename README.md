<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo/oab-logo-on-dark.png">
  <img src="assets/logo/oab-logo-on-light.png" alt="OAB — Open Architecture Brain" width="420">
</picture>

**Your agent knows what big systems look like. Not what yours needs.**

> Open knowledge. Open reasoning. Open architecture.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Scenarios](https://img.shields.io/badge/scenarios-5%2F5%20passing-brightgreen.svg)](evaluations/)
[![Release](https://img.shields.io/badge/release-v0.1.7%20·%20M1-brightgreen.svg)](https://github.com/mhayk/oab/releases/tag/v0.1.7)

**English** · [Português (BR)](README.pt-BR.md) · [Español](README.es.md)

---

## The problem

Ask a coding agent to "design a scalable API" and you will usually get Kubernetes, Kafka, Redis and
three microservices — for a product with 100 users and one developer.

The agent learned the *aesthetics* of system design from conference talks and blog posts, drawn
almost entirely from the largest 0.1% of systems. It did not learn the *economics*.

**100 users at 40 requests per session is 0.28 requests per second.** A single instance has four
orders of magnitude of headroom. OAB computes that, says so, and names the exact measurement that
would change the answer.

## What OAB does

| Command | What you get |
| :-- | :-- |
| `/oab:design` | An architecture with the capacity numbers behind it, the components it refused, and the threshold that would change each answer |
| `/oab:review` | Findings weighted by the scale your repository actually runs at — not a checklist borrowed from a system a thousand times larger |
| `/oab:capacity` | What a change costs before you make it: requests/second, storage growth, egress, cost, with the formula printed so you can check it |
| `/oab:adr` | A decision recorded with the options you weighed and the metric that would send you back to it |

A background skill also loads automatically, so ordinary architecture conversation gets the same
proportionality — not only these four commands.

## Install

```
/plugin marketplace add mhayk/oab
/plugin install oab@oab
```

![Installing OAB — real, unstaged](demo/out/install.gif)

Verified end to end: fresh clone 0.8 s / 8.1 MB, and the committed examples include a live
`/oab:design` run that passes every scenario assertion and a live third-party review with all
evidence citations checked ([`examples/live-run/`](examples/live-run/),
[`examples/live-review/`](examples/live-review/)). One caveat: artifact-validation hooks did not
fire for marketplace-installed plugins in headless sessions ([#45](https://github.com/mhayk/oab/issues/45));
skill-level validation is the fallback until that is resolved.

## What the output looks like

The deterministic heart — same inputs, same numbers, checkable by hand
([`demo/`](demo/) holds the tapes; nothing is staged):

![The capacity envelope: assumptions, formula, calculation, sensitivity](demo/out/calculator.gif)

And from [`examples/tiny-startup/`](examples/tiny-startup/) — 100 users, £50/month, two developers:

```
## Complexity: 4 / 4  — no headroom

| Component                    | Kind                  | Cost | Why                                    |
| Application instance         | application-runtime   |    1 | 0.28 peak RPS against a single          |
|                              |                       |      | instance leaves ~4 orders of magnitude  |
|                              |                       |      | of headroom.                            |
| Managed relational database  | relational-database   |    1 | 0.66 GB/year. Managed for tested        |
|                              |                       |      | point-in-time recovery, which a         |
|                              |                       |      | two-person team will not build.         |
```

**What was rejected, and when to revisit**

> **`cache`** — At 0.24 peak reads/second there is no measured read pressure to relieve.
> *Revisit when: a single query exceeds 10 requests/second at over 50 ms, or database CPU is
> sustained above 60% for 3 days.*

> **`orchestration-platform`** — Three times the complexity budget and four times the money
> budget for a system with four orders of magnitude of headroom on one instance.
> *Revisit when: more than 4 independently deployable services exist and a dedicated operations
> engineer is on the team.*

That second section — what was considered, refused, and **the measurement that reverses it** — is
the part a generic assistant never produces.

## How it decides

Every component costs **complexity points**, and every team has a budget:

```
available = 4 + 1.5 × (engineers − 2) + 4 × dedicated_ops
```

Two developers get 4 points. A managed database costs 1; a self-managed orchestration platform
costs 4. Over budget is **rejected by default**, and an override must name what is being dropped or
who will operate the excess.

At roughly **£240 per point per month** in engineering attention, self-hosting a database to save
£250/month costs about £720/month. The managed service is cheaper — and OAB says so with arithmetic
rather than preference.

It is a calibrated heuristic, not a law, and the output says that too.

## Not anti-complexity — anti-*unjustified* complexity

Kubernetes, Kafka and Redis are the right answer for plenty of systems. The question is whether
they are the right answer for *this* one, and OAB fails its own tests if it gets that wrong in
either direction.

Scenario 03 in [`evaluations/`](evaluations/) describes a platform at 50,000 requests/second across
three regions. Its assertions **require** the machinery a small system would be refused:

```yaml
must_include_components: [cdn, cache, event-stream, application-runtime]
numeric:
  - { field: "capacity.peak_rps",             min: 40000 }
  - { field: "capacity.egress_gb_per_month",  min: 100000 }   # egress must be computed
  - { field: "complexity.available",          min: 50 }
```

The suite fails if OAB refuses event streaming at 7,500 events/second with three independent
consumer groups, or omits a CDN against 1.04 PB/month of egress — where 85% offload saves roughly
$35,000/month, the largest single cost lever in that design.

**Two of the five scenarios guard against under-building; three against over-building.** A tool
that only prevented over-building would be a tool that tells you to do nothing.

## Proof, not claims

Every claim OAB makes is about behaviour, and behaviour claims without tests are marketing.

| | |
| :-- | --: |
| Scenarios passing | **5 / 5** |
| — guards against building too much | 3 / 3 |
| — guards against building too little | 2 / 2 |
| Calculator tests | 43 |
| Schema fixtures (both directions) | 33 |
| Knowledge units | 37 |

![The scenario suite with magnitude perturbation](demo/out/evaluation.gif)

Assertions run against **artifact fields**, never prose — a framework can be tuned to produce
reassuring words far more easily than the right structure. Scenarios are also perturbed 100× and
0.01× to prove they respond to magnitude rather than recognising specific numbers.

Scenario 07 is *"nothing needs to change"*, and scenario 08 is *"these requirements are
inconsistent"*. Those are the answers an eager assistant never gives.

## What is not built yet

Honest list: no MCP server · no knowledge graph generation · no second integration ·
`/oab:evolve` and the other nine commands are M2 · no website beyond a landing page · 6 knowledge
domains, not 18.

See [ROADMAP.md](ROADMAP.md), and [§32 of the design](docs/design/07-roadmap-and-risks.md#32-overengineering-review)
for a critique of our own founding brief.

## Contributing

**The highest-value contribution is architecture knowledge, and it requires no understanding of the
codebase** — copy a template, fill it in, open a pull request.

→ [docs/contributing/knowledge.md](docs/contributing/knowledge.md)

Engine, integrations and evaluation: [CONTRIBUTING.md](CONTRIBUTING.md).

## Support

OAB is free, local-first, and has no hosted service to monetise. If it earns a place in your
workflow, [sponsoring](https://github.com/sponsors/mhayk) funds the unglamorous part: keeping 37
knowledge units reviewed and current, evaluation runs, and the domain.

## Licence

[Apache-2.0](LICENSE). The OAB name and logo are trademarks and are not covered by that licence —
see [NOTICE](NOTICE).

[oab.run](https://oab.run) · [Design proposal](docs/design/) · [Examples](examples/)
