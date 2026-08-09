# 04 — Reasoning Frameworks

Covers §16–§22 of the design brief.

A **framework** is a versioned, client-agnostic procedure: ordered steps, explicit inputs, decision
gates, and a required output artifact. Frameworks live in `frameworks/<name>/procedure.md` and are
the layer that integrations wrap.

---

## Complexity Budget

*Cross-cutting mechanism referenced by every framework below. It is the single most important
original construct in OAB, because it converts "don't overengineer" from advice into arithmetic.*

### The problem it solves

"Keep it simple" is unenforceable and unfalsifiable. Every individual component addition looks
reasonable in isolation; overengineering is an *accumulation* failure. A budget makes the
accumulation visible and forces an explicit trade rather than a silent slide.

### Complexity cost of a component

A component's cost is its **operational burden**: the probability it wakes someone up, multiplied by
how hard it is to understand when it does.

| Component class | Points |
| :-- | --: |
| Managed stateless service (PaaS app runtime, CDN, managed object storage) | 1 |
| Managed stateful service (managed Postgres, managed Redis, managed queue) | 1 |
| Each additional *distinct datastore technology* beyond the first | +1 |
| Each additional independently deployed service | +1 |
| Self-hosted stateless component (own reverse proxy, own worker fleet) | 2 |
| Self-hosted stateful component (own Postgres, own Kafka, own Elasticsearch) | 3 |
| Orchestration platform requiring cluster operation (self-managed Kubernetes) | 4 |
| Multi-region active-active for any stateful component | 4 |

Rationale for the weights: *state* is what makes operations hard (backup, restore, migration,
replication, failover), *self-hosting* transfers an entire operational domain to your team, and
*technology diversity* multiplies the amount your team must know. Managed services are cheap in
points and expensive in pounds — which is the correct trade for a small team, and the model says so.

### Available budget

```
budget = 4 + 1.5 × max(0, engineers − 2) + 4 × dedicated_ops_engineers
```

Floor of 3. Rounded down to the nearest integer.

| Team | Budget |
| :-- | --: |
| 2 developers, no ops | 4 |
| 5 developers, no ops | 8 |
| 12 developers, 1 SRE | 23 |
| 40 developers, 4 SRE | 73 |

The constant `4` is the complexity a two-person team can carry while still shipping product; the
`1.5` reflects that added engineers bring sub-linear operational capacity (coordination cost); the
`4` per dedicated ops engineer reflects that operational specialisation is what actually buys
complexity headroom.

### How it is used

1. Compute the budget from stated team facts.
2. Sum the complexity cost of every component in each candidate architecture.
3. **Over budget ⇒ the option is rejected by default.** It may only be selected with an explicit,
   written justification naming what will be dropped, who will operate it, or which engineer is
   being hired.
4. The spend is reported in the deliverable: `Complexity: 4 / 4 — no headroom. Adding Redis
   requires removing something or adding an engineer.`

### Honest limitations

This is a **heuristic and a conversation-forcing device, not a law of nature.** The weights are
judgement calibrated against experience, not measured from data. Three specific weaknesses:

- It does not model *coupling* — three tightly-coupled services are worse than three independent ones.
- It treats all managed services as equal, though managed Kafka is materially harder than managed S3.
- The constants are unvalidated.

Mitigations: the weights live in `frameworks/complexity-budget/weights.yaml` (data, not code, so
they can be argued about in a PR), the evaluation suite asserts against outcomes rather than
against the score itself, and calibration against real projects is an explicit M2 goal with its own
issue. Recorded as ADR-0005 with a revisit trigger: *revisit the weights when ≥20 real projects have
been scored and ≥25% disagree with practitioner judgement.*

---

## 16. Architecture Decision Framework

`frameworks/architecture-design/`

### 16.1 The decision object

Every significant decision is modelled as:

```
Decision
├── scope            what is being decided, and what is explicitly out of scope
├── requirements[]   functional + non-functional, each measurable or marked unmeasurable
├── constraints[]    budget, team, timeline, regulatory, existing-system, skills
├── options[]        ≥2, always including the simplest viable
│   ├── description
│   ├── complexity_cost
│   ├── monthly_cost_estimate (range)
│   ├── gains[] / costs[]
│   ├── failure_modes[]
│   └── reversibility: easy | moderate | hard | one-way
├── decision         the chosen option
├── rationale        why, referencing the numbers
├── trade_offs[]     what is accepted by choosing it — never empty
├── consequences[]   what becomes true, including what becomes harder
├── migration_path   how to get from here to there; how to get out
├── observability[]  what must be measured to know the decision is holding
├── triggers[]       measurable revisit conditions
└── confidence       high | medium | low
```

### 16.2 What makes it different from an ADR template

Three enforced properties:

1. **The simplest viable option is always present.** Not as a straw man — with a fair statement of
   why it might be enough. Most architecture failure is failing to consider "just use Postgres".
2. **Reversibility is a first-class field.** One-way doors deserve more analysis than two-way doors.
   A reversible decision made quickly is usually better than a perfect decision made slowly.
3. **`trade_offs[]` may not be empty.** An option with no downsides has not been understood.

### 16.3 Decision gates

The procedure refuses to proceed past a gate:

| Gate | Blocks until |
| :-- | :-- |
| G1 | Requirements exist and non-functional ones are quantified or explicitly marked unquantified |
| G2 | The stage and complexity budget are computed |
| G3 | ≥2 options exist, one of which is the simplest viable |
| G4 | The selected option is within budget, or an explicit override is written |
| G5 | ≥1 measurable trigger exists for the decision |

---

## 17. Capacity Planning Framework

`frameworks/capacity-planning/` + `calculators/`

### 17.1 Principle

Every capacity claim is reproducible: same inputs → same numbers, from a tested implementation.
This is where OAB earns trust fastest, because arithmetic is checkable and a wrong number is
immediately visible.

### 17.2 Output contract

Every calculation emits, in this order, without exception:

```
Assumptions   → each labelled: observed | stated | assumed, with a confidence
Formula       → the literal expression, so it can be disputed
Calculation   → substituted values, so it can be checked
Result        → with units, and a range if any input is low-confidence
Safety margin → the headroom applied, and why
Confidence    → high | medium | low
Sensitivity   → which single input most changes the result
```

`Sensitivity` is an addition to the brief's list and it is the most useful line in the report: it
tells the reader which assumption to go and measure first.

### 17.3 M1 calculator set

Eight calculators. Each is a pure function with unit tests. Chosen because together they answer
"does this design work and what does it cost" for the overwhelming majority of systems.

| Calculator | Formula | Answers |
| :-- | :-- | :-- |
| `rps` | `requests_per_day / 86400`; `peak = avg × peak_factor` | Is this actually high traffic? |
| `storage_growth` | `writes_per_day × avg_record_bytes × index_overhead`; ×365 | When do we outgrow the disk/plan? |
| `bandwidth` | `rps × avg_payload_bytes` → Mbps; egress GB/month | What does egress cost? (usually the shock) |
| `concurrency` | Little's Law: `L = λ × W` | How many in-flight requests / workers / connections? |
| `connection_pool` | `pool = ceil(L_db × safety)`; `total = instances × pool` vs `max_connections` | Will we exhaust the database? |
| `cache_sizing` | `working_set = hot_keys × avg_value_bytes × overhead`; hit-rate → origin load | Does the cache fit, and what does it actually save? |
| `queue_throughput` | `workers = ceil(arrival_rate × service_time / target_utilisation)`; backlog drain time | How many workers, and how long to recover from a spike? |
| `cost_estimate` | Σ(component × unit price × quantity) with a stated price table and date | What is the monthly bill, and where does it concentrate? |

Two more are **deliberately deferred to M2**: LLM token/inference cost, and vector-store sizing.
They are valuable and fashionable, but they are not on the critical path for the first credible
milestone, and their unit economics change monthly — shipping stale price data would damage trust
more than omitting the calculator.

### 17.4 On safety margins and false precision

- Default safety margin: **utilisation target 60–70%** for compute; **2× headroom** for peak
  estimates derived from assumed traffic shapes.
- Where an input is `assumed` with `low` confidence, the result is reported as a **range**, not a
  point, and the confidence propagates: a chain containing any low-confidence input cannot report
  high confidence.
- Never report more than 2 significant figures on a number derived from an assumption. `0.28 RPS`
  is honest; `0.2777 RPS` is a lie about precision.

### 17.5 Why the calculators are code, not prose

The trade-off is real and worth stating. Code adds a Python 3 dependency for full fidelity.
Against that: arithmetic is the one place where a language model's failure is silent and
confident, capacity numbers are the foundation every downstream decision rests on, and testable
arithmetic is what lets the evaluation suite be deterministic.

Mitigation: `calculators/` is **stdlib-only Python 3.9+**, importable as a library and runnable as
`python3 -m oab_calc <name> --key=value`, emitting JSON conforming to
`schemas/capacity-result.schema.json`. The skill instructs the agent to run it when `python3` is
available and to fall back to the documented formula — which is printed in the same file — when it
is not. Degradation is graceful, never silent.

---

## 18. Architecture Review Framework

`frameworks/architecture-review/`

### 18.1 The five phases

```
1 INVENTORY   What exists? (subagent, structured return)
2 CONTEXT     What scale does it actually operate at? ← the phase everyone skips
3 ANALYSE     Where are the risks, given that scale?
4 SEVERITY    How bad, given that scale?
5 REPORT      Findings, ranked, each with evidence and a remedy
```

### 18.2 Phase 1 — Inventory (deterministic where possible)

Detected from the repository, not guessed:

- Language, framework, dependency manifests, lockfiles
- Architecture style (single deployable / multi-service / serverless functions) inferred from
  build and deploy configuration
- Datastores, caches, queues, search engines (from dependencies, connection strings, compose files,
  IaC)
- External service calls (SDK imports, HTTP clients)
- Deployment topology (Dockerfile, compose, IaC, CI workflows, platform config)
- Entry points, background jobs, scheduled tasks
- Test presence and shape; migration tooling
- Observability: structured logging, tracing libraries, metrics, correlation IDs
- Configuration and secret handling

Output conforms to `schemas/repo-facts.schema.json`. **Facts only, no judgement** — this separation
is what lets the same inventory feed review, capacity, and evolution without re-scanning.

### 18.3 Phase 2 — Context (the phase that prevents nonsense)

Before any finding is generated, establish: current traffic, user count, team size, budget,
availability requirement, data sensitivity, deployment frequency, incident history.

Prefer observed evidence (analytics config, existing dashboards, README claims, git history
cadence). Ask at most 3 questions. Where unknown, **assume small** and label the assumption —
because assuming large is how a 100-user app gets told it needs multi-region.

### 18.4 Phase 4 — Severity, weighted by context

Severity is a function of *impact given actual scale and requirements*, not of pattern matching.

| Severity | Definition |
| :-- | :-- |
| CRITICAL | Data loss, security breach, or total outage is likely under conditions the system will meet soon |
| HIGH | Significant degradation under realistic near-term load, or a one-way door being closed badly |
| MEDIUM | Real risk, but conditions are not near, or a workaround exists |
| LOW | Suboptimal; cost is mostly future friction |
| INFORMATIONAL | Observation; no action implied |

Explicit anti-rules, each of which becomes an evaluation assertion:

- A single database instance is **not** a finding for a system with no stated availability target
  and 30 RPS. It may be an INFORMATIONAL observation with a trigger.
- "No Kubernetes", "no microservices", "no service mesh", "no multi-region" are **never** findings.
- Missing tests, missing backups, unbounded external calls, and missing timeouts are findings at
  **every** scale, because their failure is not proportional to traffic.
- Every finding must cite evidence: `file:line` or a named configuration fact. A finding without
  evidence is deleted, not softened.

### 18.5 Finding shape

```yaml
id: F-003
severity: HIGH
title: "Payment provider called synchronously in the request path with no timeout"
evidence: ["app/services/checkout.rb:88", "Gemfile:41"]
context: "Checkout is the primary revenue path; ~30 RPS peak; no circuit breaker present"
impact: "Provider latency propagates directly to users; a provider stall exhausts the
         web worker pool and takes down all endpoints, not just checkout"
knowledge: [timeouts, bulkhead, circuit-breaker]
remedy: "Set an explicit client timeout (2 s connect / 5 s read); isolate the call behind a
         bulkhead so provider degradation cannot consume the whole pool"
effort: S
trigger: "Revisit for async processing when checkout p95 exceeds 800 ms or provider
          error rate exceeds 1% over 1 hour"
```

---

## 19. Performance Framework

`frameworks/performance/`

### 19.1 Reasoning model

Performance analysis follows the causal chain, not a checklist:

```
Utilisation ──▶ Queueing ──▶ Latency ──▶ Tail latency ──▶ User experience
     │              │             │
     │              │             └── p50 vs p95 vs p99: different users, different causes
     │              └── queue depth grows non-linearly as ρ → 1
     └── ρ = λ / (c·μ)
```

The two facts that must be internalised and that OAB states in every performance analysis:

1. **Latency explodes non-linearly near saturation.** For an M/M/1 approximation,
   `W = W_service / (1 − ρ)`. At ρ=0.5, latency is 2× service time; at ρ=0.9, 10×; at ρ=0.95, 20×.
   This is why a target utilisation of 60–70% is not conservatism — it is the operating point where
   latency is stable.
2. **Averages hide the users you lose.** At 100 requests per page load, a p99 of 2 s means the
   *majority* of page loads contain a 2-second request. Tail latency is a median experience at fan-out.

### 19.2 Target setting

Targets are derived from user-facing requirements, then propagated down through the call graph as a
latency budget: if the page budget is 500 ms and it makes 4 sequential backend calls, each call's
budget is ~100 ms after overhead — and if any dependency cannot meet it, the design is wrong, not
the target.

### 19.3 Test plan generation

For a given target, OAB generates a plan with measurable acceptance criteria and a defined
saturation search — not "run a load test":

```
Load test — steady state
  Load:     2,000 RPS for 30 minutes, 5-minute ramp
  Pass:     p95 < 200 ms, p99 < 500 ms, error rate < 0.5%,
            CPU < 75%, DB connection utilisation < 80%
  Measure:  RPS, p50/p95/p99, error rate by class, CPU, memory,
            DB CPU, connection count, queue depth

Stress test — find the knee
  Method:   ramp 500 → 8,000 RPS in 500-RPS steps, 3 min per step
  Record:   the RPS at which p99 exceeds 2× its steady-state value (the knee)
  Pass:     knee ≥ 2× projected peak; degradation is graceful, not cliff-edged

Spike test — recovery
  Method:   10× step for 60 s
  Pass:     no data loss; error rate returns to baseline within 120 s;
            queue backlog drains within 300 s

Soak test — leaks and drift
  Method:   70% of knee for 8 hours
  Pass:     memory growth < 5% after warm-up; p95 drift < 10%;
            no connection or file-descriptor leak
```

The four questions every performance plan must answer: *maximum sustainable throughput; where it
saturates; how latency behaves near saturation; how it recovers.*

### 19.4 Scope

M1 generates targets and plans. It does **not** run tests, integrate with k6/Gatling/Locust, or
parse results. Tool integration is M3 and requires a real user asking for it.

---

## 20. Reliability Framework

`frameworks/reliability/`

### 20.1 Structured failure interrogation

For every component and every dependency edge, nine questions — mechanical, exhaustive, and
therefore reliable:

1. What if it fails completely?
2. What if it becomes slow but does not fail? *(usually worse — no signal, resources held)*
3. What if the network between us partitions?
4. What if a request is duplicated?
5. What if messages arrive out of order?
6. What if traffic increases 10×?
7. What if it returns wrong data?
8. What happens during its deployment?
9. What happens during *our* deployment?

Q2 is the one teams miss and it is where most real outages live: a healthy-looking dependency
holding connections open until the caller's pool is exhausted.

### 20.2 From availability target to architecture

Availability targets are translated into permitted downtime and then into required mechanisms —
and OAB refuses to accept a target the architecture cannot deliver:

| Target | Downtime/year | Downtime/month | Implies |
| :-- | :-- | :-- | :-- |
| 99% | 3.65 days | 7.3 h | Single instance, manual recovery, acceptable |
| 99.9% | 8.8 h | 43 min | Automated restart, monitoring, tested backups, deploy without extended downtime |
| 99.95% | 4.4 h | 22 min | Redundant instances, health-checked load balancing, DB failover |
| 99.99% | 53 min | 4.4 min | Multi-AZ, automated failover under 1 min, no manual step in recovery, deploy safety |
| 99.999% | 5.3 min | 26 s | Multi-region, no human in the recovery loop, very high cost |

**Consistency rule (an evaluation assertion):** if a stated target implies less downtime than a
single component's realistic recovery time, OAB must flag the inconsistency rather than produce an
architecture that pretends. A single VM with manual restart cannot be 99.99%, and saying so is the
job.

Dependency arithmetic: serial dependencies multiply. Three 99.9% dependencies in a request path
give a ceiling of 99.7% before your own code runs.

### 20.3 Mechanism selection

Every resilience mechanism is recommended only with its parameters, and never as a bare noun:

| Mechanism | Must specify | Common failure |
| :-- | :-- | :-- |
| Timeout | connect + read values, derived from the latency budget | Absent, or set longer than the caller's own timeout |
| Retry | max attempts, which errors, whether the operation is idempotent | Retrying non-idempotent writes; retry storms amplifying an outage |
| Backoff + jitter | base, multiplier, cap, jitter distribution | No jitter ⇒ synchronised retry waves |
| Circuit breaker | error threshold, window, open duration, half-open probe | Trips on the wrong signal; no fallback behind it |
| Bulkhead | pool sizes per dependency | One dependency starving all others |
| DLQ | retention, alerting, replay procedure | A queue nobody reads |
| Graceful degradation | which feature degrades, to what | Undefined, so it degrades to a 500 |

---

## 21. Cost Framework

`frameworks/cost/`

### 21.1 Two ledgers, always both

```
Total Cost of Architecture = Infrastructure Cost + Operational Cost
```

**Infrastructure cost** — compute, database, storage, egress, CDN, queues, observability, backups,
third-party APIs, AI inference. Estimated from a dated price table in
`knowledge/cloud/<provider>/pricing.md`, always with the date visible, always as a range.

**Operational cost** — the one that decides architectures and that nobody puts in the spreadsheet:

```
operational_cost_per_month ≈ complexity_points × hours_per_point × loaded_hourly_rate
```

Default `hours_per_point ≈ 4 h/month` (patching, upgrades, incidents, capacity checks, onboarding
the next engineer). At a loaded rate of £60/h, **each complexity point costs roughly £240/month**.

That single number reframes most small-system decisions correctly. Self-hosting Postgres to save
£25/month against a managed instance costs 3 points ≈ £720/month of engineering attention. The
managed service is 4× cheaper. OAB says this with arithmetic instead of preference.

### 21.2 Where cost concentrates (checked in this order)

1. **Egress** — routinely the largest and most surprising line at scale. Always computed.
2. **Observability** — log volume pricing is superlinear with traffic and is the classic
   unbudgeted cost.
3. **Idle compute** — over-provisioned instances at 5% utilisation.
4. **Cross-AZ / cross-region traffic** — invisible until the invoice arrives.
5. **Managed service minimums** — a £200/month floor on a service used at 2% of capacity.

### 21.3 Honesty rules

- Every price carries its source and date. Stale prices are labelled stale, and CI warns when a
  pricing file is older than 6 months.
- Costs are ranges, never point estimates.
- Currency is explicit (project default **GBP**, since the brief's constraints are in £; the
  calculator accepts a currency and a rate).
- Free tiers are noted but never assumed permanent.

---

## 22. Architecture Evolution Framework

`frameworks/evolution/`

### 22.1 Why triggers are the project's most durable idea

A design is a snapshot; a trigger is a **standing hypothesis with a falsification test**. Triggers
convert architecture from a document that rots into a system that tells you when it has expired.
They are also what make OAB useful on day 400, not just day 1.

### 22.2 Anatomy of a trigger

A trigger is only valid if it is **measurable today**. Full schema in
[§41](09-specifications.md#41-evolution-trigger-schema).

```yaml
id: db-cpu-sustained
decision: ADR-0007
metric: database.cpu.utilisation
source: "managed database metrics dashboard"     # if you can't name where it's read, it isn't a trigger
comparator: ">"
threshold: 70
unit: percent
window: "sustained over 3 consecutive days"
action: "Re-run /oab:capacity; evaluate read replica vs. query optimisation vs. vertical scale"
owner: "backend on-call"
verification: "monthly review"
status: armed
```

### 22.3 Validity rules (enforced by schema and review)

| Rule | Reason |
| :-- | :-- |
| The metric must be observable **now**, or the trigger includes the work to instrument it | Otherwise it never fires |
| A sustained window is required | Prevents reacting to spikes |
| The action must be a next step, not a solution | The right response is usually "re-analyse", not "add Kafka" |
| Thresholds must have headroom before the cliff | A trigger at 95% CPU fires during the incident, not before it |
| An owner is named | Unowned triggers are decoration |

### 22.4 Trigger library

`knowledge/**` units carry `triggers` in frontmatter, so the trigger library is generated, not
hand-maintained. Illustrative canonical set:

| Domain | Trigger | Threshold |
| :-- | :-- | :-- |
| Database | Sustained CPU | >70% for 3 days |
| Database | p95 query latency | > SLO for 1 day |
| Database | Connection pool saturation | >80% for 1 hour, recurring |
| Database | Replication lag | > RPO for 15 min |
| Storage | Capacity used | >60% of plan |
| Application | Instance CPU | >70% sustained at peak |
| Application | Deploy coupling | >2 teams blocked per week for a month |
| Caching | Repeated expensive reads | same query >100×/min at >50 ms |
| Queue | Backlog drain time | >15 min after a normal spike |
| Availability | Error budget | 50% consumed at mid-window |
| Cost | Monthly spend | >120% of budget for 2 months |
| Multi-region | Cross-region p95 | >150 ms for a material user segment |

### 22.5 Maturity stages — used as a filter, not a ladder

The stage model (0 Prototype → 5 Global) exists for exactly one purpose: to filter
`applies_at_stage` in knowledge retrieval, so stage-4 machinery is not offered to a stage-1 system.

It is explicitly **not** a roadmap, and OAB never recommends "moving to stage 3". Systems move when
a trigger fires. Many excellent systems stay at stage 2 permanently, and OAB must be comfortable
saying so. To keep this honest, the evaluation suite includes a scenario where the correct answer
is *"change nothing"* — a case most architecture tooling cannot produce at all.
