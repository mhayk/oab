# 01 — Vision, Mission, Positioning

Covers §1–§8 of the design brief.

---

## 1. Vision

> **A world where every software system has access to a Principal Engineer's judgment — and that judgment is open, inspectable, and free.**

Long-term, OAB aims to be the **shared architecture reasoning layer of the AI coding era**: the
place where the industry's system design knowledge is written down in a form that machines can
execute and humans can audit.

Three properties define success in five years:

1. **Vendor-neutral.** The knowledge and reasoning are usable by any agent, in any IDE, in any CI
   pipeline, under Apache-2.0. No OAB capability requires a proprietary model or a hosted service.
2. **Executable.** Knowledge is not prose to be read; it is procedures, formulas, schemas, and
   assertions that produce a specific recommendation for a specific system with specific numbers.
3. **Accountable.** Every recommendation carries its assumptions, arithmetic, confidence, and a
   measurable condition under which it must be revisited. Architecture stops being an opinion and
   becomes a hypothesis with a falsification test.

The success metric is not stars. It is: *how often does an OAB-produced architecture survive
contact with production, and how often does an OAB revisit trigger fire before an incident does?*

## 2. Mission (what OAB does today)

> **Give an AI coding agent the ability to size, design, and critique a software system with the
> proportionality and rigour of an experienced Principal Engineer — and to justify every choice
> with numbers.**

Concretely, in the near term OAB must let a developer, from inside their existing agent:

- Turn a vague product description into quantified requirements and explicit assumptions.
- Compute capacity — RPS, storage, bandwidth, concurrency, connections, cost — deterministically.
- Receive an architecture *proportional* to those numbers, with named rejected alternatives.
- Have an existing repository reviewed for architectural risk, weighted by its actual scale.
- Produce ADRs whose revisit conditions are measurable metrics, not adjectives.

Everything else — knowledge graphs, MCP servers, additional clients — is downstream of doing that
well once.

## 3. Problem Statement

AI coding agents have become excellent at **local** software engineering: writing a function,
fixing a test, refactoring a module. They remain unreliable at **global** software engineering:
deciding what the system should be.

Four failure modes recur, and they compound:

### 3.1 Pattern-matching instead of sizing

Asked to "design a scalable API", an agent produces Kubernetes, Kafka, Redis, a service mesh, and
three microservices — for a product with 100 users and one developer. The agent has learned the
*aesthetics* of system design from conference talks, blog posts, and interview prep material, all
of which are drawn from the largest 0.1% of systems. It has not learned the *economics*.

This is not a small error. It is the single most expensive mistake in early-stage software: an
architecture that costs more in operational attention than the product earns in revenue, imposed
before the product has proven it should exist.

### 3.2 Adjectives instead of arithmetic

"High traffic", "large scale", "many users" are inputs that cannot produce an engineering decision.
Yet almost every architecture conversation with an agent runs on them. Nobody computes that
`2,400 requests/day = 0.028 RPS` and that a £5 VM has four orders of magnitude of headroom.

### 3.3 Decisions with no expiry date

Architecture advice is delivered as permanent truth. Nothing states *when it stops being true*.
So systems either ossify — running an architecture that outgrew itself two years ago — or churn,
rewritten on the basis of a conference talk rather than a metric.

### 3.4 Unaccountable reasoning

The developer receives a conclusion and cannot inspect the chain that produced it. Which
assumptions? Which numbers? What was considered and rejected? How confident? Without that chain,
the developer cannot disagree intelligently, and the recommendation is either accepted on faith or
discarded on instinct.

### 3.5 The knowledge itself is trapped

The knowledge that would fix all four problems exists — in books, papers, engineering blogs, and
the heads of senior engineers. It is unstructured, unversioned, uncontestable, and unusable by
machines. Every agent vendor re-derives it privately and imperfectly inside a model, where nobody
can read it, fix it, or version it.

**OAB exists to make that knowledge open, structured, quantitative, and executable.**

## 4. Project Positioning

> **OAB is an open architecture intelligence layer for software engineering agents.**

### How OAB differs from adjacent things

| Compared with | Their shape | OAB's difference |
| :-- | :-- | :-- |
| **Generic AI prompts** ("act as a principal engineer") | A paragraph of persona instruction; behaviour varies per model, per session, per phrasing | Versioned, testable procedures and a knowledge base under source control. Behaviour is a reviewable artifact with a git history, not a lucky prompt. |
| **Claude-specific plugins** | Bind knowledge and client together; die with the client | Knowledge, formulas, schemas and frameworks are client-agnostic files. `integrations/claude-code/` is a thin adapter over them and can be deleted without losing OAB. |
| **Architecture documentation collections** (awesome-lists, System Design Primer, DDIA notes) | Human reading material; ends at "here is the concept" | Ends at "here is your number, here is your decision, here is the trigger that invalidates it". Every knowledge unit carries machine-readable trade-offs, failure modes, and thresholds. |
| **Static system-design interview repos** | Optimised for whiteboard performance and the largest systems on earth | Optimised for real systems, most of which are small. OAB's most common correct answer is "one server and a managed Postgres". |
| **MCP servers** | A transport/tool protocol — *how* an agent calls capabilities | OAB is *what* the agent should know and how it should reason. MCP is one possible delivery mechanism for OAB, considered for M3, and never a requirement. |
| **AI coding assistants** (Copilot, Cursor, Codex, Claude Code) | Clients that write code | OAB is a knowledge and reasoning payload those clients consume. OAB competes with none of them; it makes all of them better at the one thing they are worst at. |
| **Cloud well-architected frameworks** | Vendor-authored, vendor-shaped, prose checklists, biased toward vendor services | Vendor-neutral, quantitative, and willing to conclude "you don't need this cloud service". |
| **IaC / policy-as-code** (Terraform, OPA, Checkov) | Enforce rules on infrastructure that already exists | Reasons about what infrastructure *should* exist, before it is written. Complementary, upstream. |

### The positioning sentence to defend

> **Claude Code is the first OAB client, not the OAB platform.**

Operationally this means a specific, testable rule, enforced in CI:

- No file outside `integrations/` may mention Claude, Anthropic, or any model name.
- Deleting `integrations/claude-code/` must leave a complete, useful, self-describing project.

## 5. Core Principles

These are ordered. When two conflict, the higher one wins.

### P1 — Proportionality

Architecture must be proportional to the measured problem. Every component must justify its
existence against the current numbers, not against a hypothetical future. **The default answer to
"should we add X?" is no**, and the burden of proof is on X.

### P2 — Quantify before deciding

No architectural recommendation without numbers. If the numbers are unknown, state a range and a
confidence level, and label the recommendation as provisional pending measurement. Adjectives are
not inputs.

### P3 — Operational complexity is a first-class cost

A component's price is not its invoice. It is invoice + on-call surface + upgrade burden +
failure modes + the engineer-hours to understand it. A system that saves £100/month and costs
half an engineer is the more expensive system. OAB budgets complexity explicitly
(see [Complexity Budget](04-frameworks.md#complexity-budget)).

### P4 — Every decision has an expiry condition

A decision without a revisit trigger is a decision nobody can safely revisit. Triggers must be
**measurable**: a metric, a source, a comparator, a threshold, and a sustained window. "When we
grow" is not a trigger. "When p95 write latency exceeds 100 ms for 3 consecutive days" is.

### P5 — Reasoning is a deliverable

The chain — assumptions → evidence → formula → calculation → options → trade-off → decision →
confidence → trigger — is part of the output, not scaffolding discarded before delivery. A
developer must be able to disagree with a specific link.

### P6 — Deterministic where possible, probabilistic where necessary

Arithmetic, schema validation, threshold checks and repository facts are code. Judgement, framing
and synthesis are the model. Never let the model do arithmetic that a script can do exactly, and
never let a script pretend to have judgement.

### P7 — Local-first, no required service

Everything core runs from a git checkout with no network, no account, and no telemetry. Any
network dependency is an optional adapter.

### P8 — Vendor neutrality is structural, not aspirational

Enforced by directory boundaries and a CI check, not by good intentions.

### P9 — OAB dogfoods OAB

OAB's own architecture must pass an OAB review. Markdown, YAML, JSON Schema, one small
stdlib-only script, GitHub. No database, no server, no queue, until a measured requirement
demands one — at which point we write the ADR.

### P10 — Contestable knowledge

Every knowledge unit is attributed, dated, and challengeable by pull request. Where the industry
genuinely disagrees, OAB records the disagreement rather than pretending consensus.

## 6. Open Source Strategy

### 6.1 Why Apache-2.0 is the right licence

| Requirement | Apache-2.0 |
| :-- | :-- |
| Commercial adoption inside proprietary developer tooling | Permitted; no copyleft reach into the consuming product |
| Patent protection for contributors and users | §3 grants patent rights; §3's retaliation clause deters patent aggression — a real concern given the volume of patent activity around agent tooling |
| Corporate legal acceptance | Apache-2.0 is on virtually every enterprise allowlist; GPL-family and SSPL are not |
| Attribution and provenance | §4 requires preserving notices — important for knowledge attribution |
| Compatibility | Compatible with MIT/BSD; GPLv3-compatible one-way |

Alternatives considered and rejected:

- **MIT** — simpler, but no explicit patent grant. For a project whose output is *engineering
  methodology* consumed by commercial agent vendors, the patent grant is worth the extra text.
- **CC-BY-SA for knowledge, Apache-2.0 for code** — a defensible split, but dual-licensing a
  repository where a single Markdown file is simultaneously documentation *and* an executable
  instruction to an agent creates a boundary nobody can locate. One licence for everything.
  This decision is recorded as ADR-0002 and is revisited if a knowledge contributor's employer
  objects to Apache-2.0 for prose.
- **BUSL / SSPL / open-core** — incompatible with the stated 100%-open-source commitment and
  fatal to the vendor-neutrality claim, which is the entire differentiator.

`NOTICE` will carry project attribution. A `DCO` (Developer Certificate of Origin) sign-off is
preferred over a CLA: lower friction, sufficient provenance, and no assignment of rights to a
single entity — which matters for a project claiming neutrality.

### 6.2 Contribution model

Two distinct contributor paths, deliberately separated so that a distributed-systems expert who
does not write Python can contribute the most valuable thing in the project:

| Path | Who | What they touch | Review bar |
| :-- | :-- | :-- | :-- |
| **Knowledge contribution** | Engineers with domain experience | `knowledge/**/*.md` | Schema-valid; claims attributed; trade-offs and failure modes present; at least one maintainer approval |
| **Engine contribution** | Tooling contributors | `frameworks/`, `calculators/`, `schemas/`, `evaluations/`, `integrations/` | Tests; no vendor leakage; evaluation suite green |

Knowledge contributions are the primary growth vector and must have the lowest possible friction:
copy a template, fill it in, open a PR, CI validates the schema.

### 6.3 Knowledge ownership

Contributors retain copyright; the Apache-2.0 grant covers use. Source attribution is mandatory
(`references:` in frontmatter) and **verbatim copying of copyrighted material is prohibited** —
knowledge units summarise concepts in original prose and cite the source. This is a hard CI-adjacent
review rule, stated in `CONTRIBUTING.md`, because a knowledge project that launders copyrighted text
is a project with a shutdown date.

### 6.4 Structural vendor neutrality

1. `knowledge/`, `frameworks/`, `schemas/`, `calculators/`, `evaluations/` contain **zero** vendor
   or model names outside of factual, comparative technology entries (e.g. a knowledge unit on
   "managed Postgres options" may name RDS and Cloud SQL as data).
2. A CI check greps for agent-vendor names outside `integrations/` and fails the build.
3. Cloud-specific facts (pricing, service limits) live in `knowledge/cloud/<provider>/` as
   clearly-dated *data*, never as a default recommendation.
4. The evaluation suite runs against the client-agnostic frameworks, not through any one client.

## 7. Target Users

**Primary (drives every M1 decision): the technically-capable builder with no architect.**
A solo founder, a two-person startup, a senior developer who has become the de-facto architect,
or a small in-house team. They can implement anything but have nobody to argue with about *what*
to implement, and they are the population most damaged by overengineering advice.

**Secondary:**

| User | Need |
| :-- | :-- |
| Staff/Principal engineers | A rigorous second opinion and an ADR generator that does the tedious parts; a shared vocabulary for review |
| Engineering managers / CTOs | Cost and complexity visibility; an evidence trail for architecture spend |
| Platform / DevEx teams | An architecture review standard embeddable in CI and internal developer platforms |
| Consultancies & agencies | Fast, defensible, client-ready architecture assessments |
| Educators & learners | A quantitative, non-cargo-cult path into system design |
| Agent tooling vendors | A neutral knowledge payload they can ship rather than re-derive |

**Explicit non-users for M1:** enterprise architecture governance (TOGAF-shaped compliance),
regulated-industry certification, and FinOps platform replacement.

## 8. Use Cases

Nine concrete scenarios. The first four are M1 scope; the rest inform the architecture so they can
be added without redesign.

### UC-1 — Greenfield sizing *(M1)*
A founder describes a marketplace app. OAB asks four questions that actually change the answer,
states assumptions, computes 0.4 peak RPS and 1.2 GB/year, and recommends a single application
instance, one managed Postgres, object storage, and a CDN — explicitly rejecting Redis,
Kubernetes, and a queue, each with the measurement that would change the answer.

### UC-2 — Existing repository review *(M1)*
A developer runs a review on a two-year-old Rails monolith. OAB detects a synchronous third-party
payment call in the request path with no timeout, N+1 queries on the highest-traffic endpoint, no
correlation IDs, and a single point of failure in a cron-driven job runner — and rates each by
severity *weighted by the app's actual 30 RPS*, so it does not report "no multi-region" as a finding.

### UC-3 — Capacity planning *(M1)*
An engineer needs to know whether the current database survives a marketing campaign expected to
5× traffic for 48 hours. OAB computes the projected peak RPS, connection demand via Little's Law,
storage delta, and cost delta, with a stated safety margin and confidence, and identifies the
first component to saturate.

### UC-4 — Decision capture *(M1)*
A team is choosing between a database-backed job queue and a managed queue service. OAB produces
an ADR with options, trade-offs, a decision, a migration path, the observability required to know
the decision is holding, and revisit conditions expressed as metrics.

### UC-5 — Scaling diagnosis *(M2)*
Latency is degrading. OAB reasons from the symptom through queueing theory and utilisation to a
ranked list of candidate causes, and specifies the measurement that discriminates between them.

### UC-6 — Evolution check *(M2)*
Quarterly, OAB re-evaluates recorded revisit triggers against current metrics and reports which
architectural decisions have expired. This is the capability that makes OAB *keep* earning its place.

### UC-7 — Cost and complexity audit *(M2)*
OAB maps the architecture to an estimated monthly cost and a complexity score, and identifies
components whose combined cost exceeds their justification.

### UC-8 — CI architecture gate *(M3)*
A pull request adds a new datastore. A CI job runs an OAB review and comments with the complexity
delta and the missing ADR.

### UC-9 — Neutral knowledge payload for other agents *(M3)*
Cursor, Codex, or an in-house agent consumes the same `knowledge/` and `frameworks/` directories
through a thin adapter, with no fork of the core.
