# 05 — Evaluation Framework

Covers §23 of the design brief.

---

## 23. Evaluation Framework

### 23.1 Why this is not optional

Every claim OAB makes — proportionality, rigour, "a Principal Engineer reviewed this" — is a claim
about *behaviour*. Behaviour claims without tests are marketing. The evaluation suite is what
separates OAB from a well-written prompt, and it must exist from M1, not be retrofitted.

It must catch **both** failure directions, which is unusual and is the point:

- **Overengineering** — Kubernetes for 100 users. Common, expensive, and the reason OAB exists.
- **Underengineering** — no backups, no timeouts, 99.99% claimed on a single VM. Rarer in AI output
  but more dangerous.

A tool that only prevents overengineering is a tool that tells you to do nothing.

### 23.2 The enabling design decision: a structured output contract

Deterministic evaluation of prose is impossible. Therefore **every OAB deliverable emits a
machine-readable artifact alongside the human document**:

| Command | Human output | Machine artifact | Schema |
| :-- | :-- | :-- | :-- |
| `/oab:design` | `docs/architecture/design.md` | `.oab/design.json` | `design-output.schema.json` |
| `/oab:review` | `docs/architecture/review.md` | `.oab/review.json` | `review-output.schema.json` |
| `/oab:capacity` | inline report | `.oab/capacity.json` | `capacity-result.schema.json` |
| `/oab:adr` | `docs/adr/NNNN-*.md` | frontmatter in the same file | `adr.schema.json` |

The artifact contains the reasoning trace from §15.3: stage, complexity budget and spend,
components with their costs, assumptions, options with verdicts, knowledge ids used, triggers, and
confidence.

This one decision makes everything downstream possible: assertions become field checks, regressions
become diffs, and a user can pipe OAB output into their own tooling. It also serves users directly —
`.oab/design.json` is a durable, diffable record of what was decided and why.

### 23.3 Three test tiers

```
Tier 1 — Unit (pure, fast, no model)
         calculators, schema validation, index integrity, neutrality lint
         Runs on every commit. Must be 100% green. ~seconds.

Tier 2 — Scenario assertions (model in the loop, deterministic checks)
         Fixed scenario input → OAB artifact → assertions on artifact fields.
         The core of the suite. Runs on PRs touching frameworks/ or knowledge/.

Tier 3 — Judged quality (model as judge, advisory only)
         Rubric scoring of prose clarity and reasoning coherence.
         Never gates a merge. Tracked as a trend.
```

Tier 3 is advisory **by design**. An LLM judge gating CI makes the build non-deterministic and
teaches contributors to write for the judge. It reports; it does not block.

### 23.4 Scenario format

Each scenario is a directory: input, expected properties, forbidden properties.

```
evaluations/scenarios/01-tiny-startup/
├── scenario.yaml      # the input: product, scale, team, budget, constraints
├── assertions.yaml    # must / must-not / numeric-range assertions on the artifact
└── notes.md           # why this scenario exists and what it protects against
```

```yaml
# scenario.yaml
id: tiny-startup
description: "Recipe-sharing web app, pre-revenue"
input:
  product: "Users publish recipes, browse, comment, and upload photos"
  users_total: 100
  dau_estimate: unknown
  team: { engineers: 2, dedicated_ops: 0 }
  budget_gbp_month: 50
  availability_target: unstated
  compliance: none
```

```yaml
# assertions.yaml
must_not_include_components:
  [kubernetes, kafka, elasticsearch, service-mesh, cassandra, multi-region,
   microservices, redis, read-replica]
must_include_components: [application-runtime, relational-database]
numeric:
  - { field: "capacity.peak_rps",          max: 5 }
  - { field: "cost.monthly_gbp.high",      max: 50 }
  - { field: "complexity.spent",           max: 4 }
  - { field: "complexity.spent",           lte_field: "complexity.available" }
structural:
  - { field: "assumptions",                min_length: 1 }
  - { field: "options",                    min_length: 2 }
  - { field: "triggers",                   min_length: 3 }
  - { field: "options[*].verdict",         contains: "rejected" }
  - { field: "confidence",                 in: [high, medium, low] }
semantic:                                   # Tier 3, advisory
  - "The rejection of a cache is justified by measured or estimated read volume, not by cost alone"
```

### 23.5 Scenario suite

Six from the brief, plus three that the brief omits and that are strictly necessary:

| # | Scenario | Guards against |
| :-- | :-- | :-- |
| 1 | Tiny startup — 100 users, £50/mo, 2 devs | Overengineering (the headline failure) |
| 2 | Growing SaaS — 100k users, multi-tenant | Under-provisioning; missing tenant isolation |
| 3 | Large platform — 50k RPS, multi-region | Under-engineering; refusing justified complexity |
| 4 | Financial transactions | Missing idempotency, audit trail, consistency reasoning |
| 5 | Social feed | Naive fan-out; ignoring hot users and read amplification |
| 6 | AI SaaS | Ignoring token cost, rate limits, inference latency, fallback |
| **7** | **Healthy system, no change needed** | **The "always recommend something" reflex** |
| **8** | **Inconsistent requirements** (99.99% on £50/month, one VM) | **Producing an architecture that pretends to meet an impossible target** |
| **9** | **Legacy repo review, deliberately small scale** | **Reporting theoretical problems as findings** |

Scenarios 7 and 8 are the ones I would most expect OAB to fail early, and therefore the most
valuable to have from the start. Scenario 7 in particular tests whether the tool can say "your
architecture is appropriate; here are the triggers to watch" — the single most useful answer a
consultant can give and the one an eager assistant never gives.

### 23.6 Deterministic checks that need no model at all

Highest-value, lowest-cost tests. All Tier 1:

| Check | Implementation |
| :-- | :-- |
| Calculator correctness | Unit tests with hand-verified expected values, including edge cases (zero, very large, fractional RPS) |
| Formula self-consistency | Property tests: `peak_rps ≥ avg_rps`; doubling `writes_per_day` doubles storage growth; Little's Law is dimensionally consistent |
| Artifact validity | Every emitted artifact validates against its JSON Schema |
| Knowledge integrity | Frontmatter schema-valid; all `related`/`prerequisites` ids resolve; no cycles; no orphans; `references` non-empty |
| Availability consistency | A stated target ≥99.99% with a single-instance component and no automated failover fails |
| Complexity budget arithmetic | Recomputed independently from the components list; must match the reported spend |
| Vendor neutrality | No agent-vendor/model name outside `integrations/` |
| Price staleness | Any `pricing.md` older than 6 months warns; older than 12 months fails |

### 23.7 Anti-gaming

Scenario suites rot into overfitting: the framework grows a clause that recognises "100 users" and
emits the expected answer.

Countermeasures:

1. **Held-out scenarios.** A subset lives in `evaluations/holdout/`, is not referenced by any
   framework, and is run only on release branches.
2. **Perturbation runs.** Scenarios are re-run with inputs scaled (10×, 0.1×) and assertions
   flipped accordingly. A framework that recognises the *number* rather than the *magnitude* fails.
3. **Assertions target properties, not strings.** `must_not_include_components` checks the
   components list in the artifact, not the presence of a word in prose.
4. **Model diversity where feasible.** Tier 2 runs against at least two model families before a
   release; a framework that only works with one has encoded a model quirk, not knowledge.

### 23.8 CI wiring

| Trigger | Tier 1 | Tier 2 | Tier 3 |
| :-- | :-- | :-- | :-- |
| Every push / PR | ✅ blocking | — | — |
| PR touching `frameworks/`, `calculators/`, `schemas/` | ✅ | ✅ blocking | — |
| PR touching `knowledge/` | ✅ | ✅ (subset) | — |
| Nightly on `main` | ✅ | ✅ full | ✅ advisory |
| Release branch | ✅ | ✅ full + holdout + perturbation | ✅ advisory |

Tier 2 and 3 require model access, so they run in a workflow gated on a repository secret and are
skipped (not failed) on fork PRs — otherwise external contribution becomes impossible. A maintainer
re-runs them on the merge queue.

### 23.9 Success metric for the project itself

The number to publish and track in the README:

> **Scenario pass rate**, broken out as *overengineering-guard* pass rate and
> *underengineering-guard* pass rate, on a fixed suite, per release.

Publishing the failures is part of the credibility. A project that claims architecture rigour and
hides its own evaluation results has failed its own review.
