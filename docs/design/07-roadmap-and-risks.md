# 07 — Milestones, Roadmap & Risks

Covers §26–§32 of the design brief.

---

## 26. M1 — The Smallest Credible First Milestone

### 26.1 The one-sentence definition

> **A developer installs the OAB plugin and, within five minutes, gets an architecture design or
> repository review that a Principal Engineer would recognise as competent — with real numbers,
> named rejected alternatives, and measurable revisit triggers.**

### 26.2 What ships

| Area | Scope |
| :-- | :-- |
| **Commands** | `/oab:design`, `/oab:review`, `/oab:capacity`, `/oab:adr`, plus the background `oab-principles` skill |
| **Frameworks** | discovery, architecture-design, architecture-review, capacity-planning, complexity-budget, evolution-triggers |
| **Knowledge** | **~40 units across 6 domains** — fundamentals, databases, caching, messaging, reliability, cost. Depth over breadth. |
| **Calculators** | The 8 from §17.3, stdlib Python, unit-tested, JSON output |
| **Schemas** | knowledge-unit, capacity-result, adr, evolution-trigger, design-output, review-output, repo-facts, reasoning-trace |
| **Templates** | ADR, architecture review, system design, capacity report |
| **Evaluations** | Tier 1 complete; Tier 2 with scenarios 1, 2, 3, 7, 8 |
| **Examples** | 3 committed end-to-end outputs (tiny startup, medium SaaS, repo review) |
| **Repo quality** | README, LICENSE, NOTICE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CHANGELOG, ROADMAP, issue/PR templates, CI |
| **Website** | Single landing page + link to GitHub docs |

### 26.3 Why 40 knowledge units and not 200

40 units covering the six domains that appear in nearly every system produce competent behaviour
across all M1 scenarios. 200 shallow units across 18 domains produce a directory listing.

The unit is also the contribution primitive — 40 well-made units establish the quality bar that the
next 200 must meet. Establishing that bar before opening the floodgates is the difference between a
knowledge base and a wiki.

### 26.4 What "done" means

M1 is complete when **all** of these hold:

1. `/plugin marketplace add mhayk/oab` → `/plugin install oab@oab` works on a clean machine.
2. `/oab:design` on the tiny-startup scenario produces an architecture with ≤4 complexity points,
   ≤£50/month, no Kubernetes/Kafka/Redis, ≥2 options with an explicit rejection, and ≥3 triggers.
3. `/oab:review` on a real third-party open-source repository produces findings that a senior
   engineer agrees with, with no scale-inappropriate findings.
4. `/oab:capacity` numbers are reproducible by hand from the printed formulas.
5. Tier 1 evaluations pass; Tier 2 scenarios 1, 2, 3, 7, 8 pass.
6. `claude plugin validate ./ --strict` passes in CI.
7. A person who has never seen the repository can add a knowledge unit using only
   `docs/contributing/knowledge.md`.

### 26.5 M1 non-goals (explicit)

MCP server · knowledge graph generation · additional integrations · web application · hosted
anything · accounts · telemetry · diagram rendering pipeline (Mermaid text is emitted; nothing
renders it) · load-test tool integration · LLM-judge gating · GOVERNANCE.md · more than 6 knowledge
domains · the remaining 8 commands.

---

## 27. M2 — The Logical Next Milestone

**Theme: depth, durability, and proof that OAB keeps earning its place after day one.**

| Area | Scope | Why now and not M1 |
| :-- | :-- | :-- |
| `/oab:evolve` | Check recorded triggers against current metrics; report expired decisions | Requires M1 designs to exist first. This is the retention feature. |
| `/oab:scale`, `/oab:performance`, `/oab:reliability`, `/oab:cost`, `/oab:security` | Focused analyses reusing M1 frameworks | Each is cheap once the frameworks exist; splitting them from `/oab:design` was premature before real usage showed which are wanted |
| Knowledge → ~150 units, 12 domains | Add distributed-systems, performance, observability, security, api-design, multi-tenancy | Growth after the quality bar is established |
| Knowledge graph | `tools/build_index.py` generating INDEX.md, index.json, Mermaid maps | Meaningful only past ~40 units |
| Calculators +2 | LLM token/inference cost, vector store sizing | Deferred from M1 on price volatility; revisit with a dated price table |
| Evaluation | Scenarios 4, 5, 6, 9; perturbation + holdout; Tier 3 advisory | Needs M1 behaviour to be stable first |
| Complexity budget calibration | Score ≥20 real projects; publish agreement rate; adjust weights | The honest follow-through on §04's stated limitation |
| Website | `/knowledge` and `/examples` rendered; browser-side search | Only worthwhile once there is knowledge to browse |
| Governance | `GOVERNANCE.md`, maintainer roles, RFC process | Only meaningful with >3 regular contributors |

---

## 28. Future Roadmap

Deliberately vaguer as it recedes — anything more precise would be fiction.

### M3 — Interoperability (conditional on demand)
- Second integration (Cursor or Codex), via `tools/build_integration.py`
- MCP server for calculators + knowledge search, **only if** §11.4's conditions are met
- GitHub Action: architecture gate on PRs (complexity delta, missing ADR)
- Load-testing tool emitters (k6/Gatling plan generation)

### M4 — Continuity
- Metrics adapters (Prometheus, Datadog, Grafana) so triggers evaluate against real telemetry
  instead of hand-entered numbers — this is the step that makes evolution triggers automatic
- Architecture drift detection between recorded ADRs and repository reality
- Multi-repo / platform-level review

### M5 — Ecosystem
- Community knowledge domains (fintech, healthcare, gaming, IoT, ML platforms)
- Organisation-specific knowledge overlays (internal standards layered over the open base)
- Federated knowledge: a mechanism for consuming a private knowledge pack alongside the public one

### Standing non-goals, at every milestone
Hosted OAB service · proprietary tiers · telemetry · a knowledge base gated behind an account ·
architecture *automation* (OAB advises; humans decide) · becoming a general coding agent.

---

## 29. Technical Risks

| # | Risk | Likelihood | Impact | Mitigation |
| :-- | :-- | :-: | :-: | :-- |
| T1 | **Behaviour is not reproducible.** Same input, different architecture across runs or models. | High | High | Deterministic calculators; explicit procedure with gates; structured artifact assertions rather than prose matching; multi-model Tier 2 runs. Accept residual variance in *prose*, require stability in *artifact fields*. |
| T2 | **Context budget.** Knowledge base outgrows what an agent can navigate. | High | High | Three-tier progressive disclosure (§10.4); generated per-domain indexes; skills name files and conditions explicitly. Measure: tokens consumed per `/oab:design` run, tracked per release. |
| T3 | **Plugin packaging behaviour differs from documentation** (§10.2 Option D). | Medium | Medium | Verified by real install in the first integration issue; Option A (release build) is a designed, pre-analysed fallback. Isolated blast radius. |
| T4 | **Claude Code plugin API changes.** | Medium | Medium | All client-specific surface confined to `integrations/claude-code/`. A breaking change is a one-directory fix. CI runs `claude plugin validate`. |
| T5 | **Knowledge rot.** Price tables, service limits, and version-specific figures go stale. | High | Medium | `last_reviewed` required; CI warns >18 months; prices dated and failing >12 months; figures carry their measurement basis. |
| T6 | **Complexity budget weights are wrong.** Systematically bad advice delivered with false confidence. | Medium | High | Weights are data in a YAML file, not code; documented as a heuristic in user-facing output; M2 calibration against real projects with a published agreement rate. |
| T7 | **Overfitting to the evaluation suite.** | Medium | High | Holdout scenarios; perturbation runs; property assertions rather than string matching. |
| T8 | **Python dependency unavailable** (notably Windows without Python). | Medium | Low | Stdlib-only; documented formulas printed alongside; graceful, announced fallback to model arithmetic. |
| T9 | **The agent ignores the procedure** under long-context pressure and reverts to pattern-matched output. | Medium | High | Short SKILL.md files; explicit gates; required artifact fields make skipping detectable; the artifact is emitted *before* the prose. |
| T10 | **Cost/pricing claims are wrong** and someone budgets on them. | Medium | Medium | Ranges not points; dated sources; a prominent "estimates, verify with your provider" statement in every cost output. |

---

## 30. Product Risks

| # | Risk | Mitigation |
| :-- | :-- | :-- |
| P1 | **"I can just ask Claude that."** The value is invisible until you compare outputs. | Lead with side-by-side comparison in the README and on the site: same prompt, generic vs OAB. The difference — numbers, rejected options, triggers, complexity budget — must be immediately visible, not argued. |
| P2 | **Nobody wants to be told no.** OAB's core value proposition is refusing complexity, and some users want permission for the exciting architecture. | Never moralise. Present the trigger: "Not yet — here is the exact measurement that changes this answer." That reframes refusal as a plan. |
| P3 | **Output is too long to read.** 25 sections of architecture document is a wall. | Adaptive output: executive summary first, ~1 page, then detail. Never generate a section that has no content for this system. Cap default output; detail on request. |
| P4 | **Wrong advice destroys trust permanently.** One confident, wrong recommendation outweighs ten good ones. | Confidence levels are mandatory and honest; low confidence recommends measurement before commitment; assumptions are always visible so a user can correct the input rather than distrust the tool. |
| P5 | **Discovery friction.** Plugin marketplaces are new; installation is a barrier. | Two-command install; submit to the community marketplace; make the repository useful even without installing (examples and knowledge are readable on GitHub and oab.run). |
| P6 | **Unclear who it is for.** "Architecture intelligence" is abstract. | Lead with the concrete tiny-startup example everywhere. The audience recognises itself in the £50/month problem. |
| P7 | **One-shot usage.** A user runs `/oab:design` once and never returns. | `/oab:evolve` (M2) is the retention mechanism: triggers give OAB a reason to be re-run quarterly. Design outputs are committed files that live in the user's repo. |

---

## 31. Open Source Risks

| # | Risk | Mitigation |
| :-- | :-- | :-- |
| O1 | **Bus factor of one.** A single-maintainer project stalls. | Everything is Markdown and schemas — low barrier to a second maintainer. Publish the review checklist so review is transferable. Actively recruit domain maintainers per knowledge area in M2. |
| O2 | **Knowledge quality erosion.** Contributions accumulate faster than review capacity; quality regresses to the mean of the internet. | Schema validation in CI; a published review checklist; `maturity: draft` as a holding state so a good-but-unreviewed contribution can land without claiming authority; agents down-weight `draft`. |
| O3 | **Copyright contamination.** A contributor pastes text from a book or paid course. | Explicit prohibition in CONTRIBUTING; mandatory `references`; reviewers check for verbatim phrasing; DCO sign-off establishes provenance. |
| O4 | **Contested knowledge becomes a flame war.** Architecture opinions are held strongly. | `confidence: low` exists precisely to record genuine disagreement. Knowledge units may present competing positions with evidence. The reviewer's question is "is this defensible and attributed", not "do I agree". |
| O5 | **Vendor capture.** A model vendor makes OAB de facto dependent on its client. | The neutrality CI check; the deletion test (§9.1); a second integration in M3 as a forcing function. |
| O6 | **Governance vacuum or premature bureaucracy.** | Start with BDFL + documented review checklist. `GOVERNANCE.md` and an RFC process arrive at M2, when >3 regular contributors make them necessary. Writing governance for a two-person project is itself overengineering. |
| O7 | **Trademark/name collision.** "OAB" is a short, contested acronym. | Confirm `oab.run` is held; check for conflicting marks in the developer-tools space before the first release announcement; the full name "Open Architecture Brain" is the primary identity. |
| O8 | **Contributor funnel is too narrow.** Only people who understand the whole system can contribute. | The knowledge path requires no code understanding: copy a template, fill it, PR. Good-first-issue labelling on individual knowledge units. |

---

## 32. Overengineering Review

*A critique of the founding brief, as requested. The brief asks OAB to prevent overengineering; the
brief is itself an example of it. Applying OAB's own principles to it is the first act of dogfooding.*

### 32.1 The core problem with the brief

It describes a five-year vision as if it were a specification, then asks for M1. Roughly **85% of
what it lists must not be built first.** The listed scope — 18 knowledge domains, 25 output
sections, 30+ calculators, 13 commands, a knowledge graph, an MCP server, six integrations, a
website, a governance model — is perhaps 30 engineer-months. As a first milestone it would produce
a large, shallow, untested artifact whose breadth conceals that none of it works well.

### 32.2 Cut from M1 — with reasons

| Item in the brief | Verdict | Reason |
| :-- | :-- | :-- |
| **18 knowledge domains** | Cut to 6 | 40 deep units beat 200 stubs. Breadth is a trap: it looks like progress and produces nothing usable. |
| **Knowledge graph generation** | Defer to M2 | Meaningless below ~40 nodes. A graph of 12 concepts is a picture, not a capability. |
| **MCP server** | Defer to M3, conditional | Solves no M1 problem. File reads already work. Adds a runtime, an install step, and a security surface for zero present benefit. |
| **13 commands** | Cut to 4 + 1 background skill | Nine of them are slices of `/oab:design` and `/oab:review`. Ship two well; let usage reveal which slices deserve their own entry point. |
| **25-section output template** | Cut to adaptive output | The brief itself warns against generating sections to satisfy a template, then supplies a 25-section template. Emit only sections with content. |
| **30+ calculators** | Cut to 8 | The listed set includes several that are the same formula with different labels. Eight cover the vast majority of real sizing. |
| **`integrations/` for codex, cursor, copilot, mcp** | Cut to Claude Code only | Empty directories are a promise, not an architecture. The abstraction that makes a second integration cheap is *client-agnostic frameworks*, which we have — not a directory tree. |
| **LLM-judge evaluation** | Advisory only, never gating | Non-deterministic CI is worse than no CI. |
| **`GOVERNANCE.md`** | Defer to M2 | Governance for two people is ceremony. The brief itself says "avoid overengineering governance during M1" and then lists ten governance artifacts. |
| **Full documentation site** | Cut to one landing page | GitHub renders Markdown. A docs framework before there are docs is backwards. |
| **Diagram rendering pipeline (PlantUML, C4, 10 diagram types)** | Cut to Mermaid text only | Mermaid renders natively in GitHub and in most agent clients. PlantUML adds a Java dependency. Two diagram types (context, container) cover the need; the brief's own §42 warns against diagrams that look impressive but cannot be justified. |
| **AI-systems knowledge domain** | Defer to M2 | Fastest-rotting knowledge in the set. Shipping stale token prices damages trust more than omitting the domain. |
| **Chaos engineering, distributed tracing depth, advanced consistency models** | Defer | Stage 4–5 concepts. Their absence cannot hurt an M1 user; their presence tempts stage-1 users toward stage-5 machinery. |

### 32.3 Where the brief is right, and should be defended

- **Proportionality as the central value.** Correct, and the genuine differentiator.
- **Evolution triggers.** The most original and most durable idea in the document. They should be
  more central than the brief makes them — they are what gives OAB a reason to be re-run.
- **Both over- and under-engineering must be caught.** Correct and rarely stated.
- **Vendor neutrality as structure, not intention.** Correct, and cheap if done from commit one.
- **"OAB must dogfood OAB."** The right constraint, and the reason this critique exists.
- **Operational complexity as a first-class cost.** Correct; the Complexity Budget is the attempt
  to make it operational rather than rhetorical.

### 32.4 Where the brief is internally inconsistent

1. **"Do not overengineer" + a 43-section specification.** Named here so the tension is resolved
   deliberately rather than silently.
2. **"Avoid unnecessary graph infrastructure initially"** followed by a full section specifying a
   knowledge graph. Resolved: derive the graph from frontmatter, generate it in M2.
3. **"Do not generate irrelevant sections merely to satisfy a template"** followed by a 25-section
   template. Resolved: adaptive output.
4. **"Deterministic tests preferred"** alongside a scope that is almost entirely subjective.
   Resolved: the structured output contract (§23.2), which is what makes determinism possible at all.
5. **Claude Code as "only the first client"** while every command is specified in Claude Code's
   idiom. Resolved: frameworks are client-agnostic; `integrations/` holds the idiom.

### 32.5 The one thing the brief under-specifies

**How the agent chooses which knowledge to read.** The brief assumes an agent with the knowledge
base available will use it well. It will not. Without an explicit, cheap selection mechanism it
will read nothing (and pattern-match as before) or attempt everything (and exhaust context).

This is the highest-risk unsolved problem in the project, and it is why §10.4's progressive
disclosure, the generated per-domain indexes, and the `applies_at_stage` filter are treated as core
architecture rather than as an implementation detail.
