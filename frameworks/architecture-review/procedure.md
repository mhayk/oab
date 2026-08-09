# Framework: Architecture Review

**Purpose.** Inspect an existing repository and produce findings weighted by the system's **actual**
operating scale.

**Inputs.** A repository.
**Output.** `review.md` (prose) and `review.json` conforming to `schemas/review-output.schema.json`.

---

## The governing rule

> **Do not report theoretical problems.**
> A single database instance is not a finding for a system with no availability target and 30
> requests per second. Context decides severity.

This is the rule that makes a review trustworthy. A reviewer who flags every deviation from
large-scale practice produces a document the team correctly ignores, and loses the ability to be
heard about the findings that matter.

---

## The five phases

```
1 INVENTORY   What exists?                      → facts only, no judgement
2 CONTEXT     What scale does it actually run at?  ← the phase everyone skips
3 ANALYSE     Where are the risks, given that?
4 SEVERITY    How bad, given that?
5 REPORT      Ranked findings, each with evidence and a remedy
```

## Phase 1 — Inventory

Detected from the repository, not guessed. Output conforms to `schemas/repo-facts.schema.json`:
**facts only, no severity, no recommendation.** Separating inventory from analysis is what lets the
same scan feed review, capacity, and evolution — and it stops the scanner forming opinions before
scale is known.

Detect: languages and frameworks; architecture style from build and deploy configuration;
deployables; datastores, caches, queues, search; external services and whether they sit in the
request path; deployment topology; background work; tests; migrations; observability;
configuration and secret handling; repository age and contributor count.

**Report what could not be determined** in `undetermined[]`. An omission reads as an absence, and
"no metrics found" must not be confused with "metrics not detectable from the repository". Where
a fact cannot be established, say `null` and list it — never guess, because a guess here drives a
wrong finding.

## Phase 2 — Context

**A blocking gate. No finding is generated before this is established.**

Determine: current traffic, user count, team size, budget, availability requirement, data
sensitivity, deployment frequency, incident history.

Prefer observed evidence — analytics configuration, existing dashboards, README claims, git cadence,
distinct commit authors. Then ask **at most 3 questions**.

**Where unknown, assume small and label the assumption.** Assuming large is how a 100-user
application gets told it needs multiple regions.

Record every context assumption in `context.assumptions[]` with a confidence. The weighting that
produced the severities must be visible, so a reader who disagrees with the scale can discount the
findings rather than the tool.

## Phase 3 — Analyse

Work through these, in this order. The first three are scale-independent and are checked at every
size.

### Always, regardless of scale

Their failure is not proportional to traffic, so a small system gets no discount:

- **Backups exist and restore is tested.** An untested restore is not a backup.
- **Outbound calls have explicit timeouts.** A dependency that becomes slow without failing is the
  most common cause of a total outage.
- **Errors are visible.** No error tracking means failures are discovered by users.
- **Secrets are not committed.**
- **Migrations are reversible or expand/contract.**
- **Deployment does not require extended downtime** — unless the business genuinely accepts it.

### Given the measured scale

- Bottlenecks against the actual numbers: N+1 queries on hot paths, missing indexes on filtered
  columns, unbounded result sets.
- Single points of failure **whose failure exceeds the stated availability requirement**.
- Synchronous work that a measured latency budget says should be asynchronous.
- Caching where repeated expensive reads dominate, and only where they do.
- Security: authentication and authorisation boundaries, input validation on trust boundaries,
  dependency currency, tenant isolation where multi-tenant.
- Observability gaps that would prevent diagnosing the failures identified above.
- **Unnecessary complexity**: components with no measured problem to solve. This is a finding too,
  and a common one.

## Phase 4 — Severity

Severity is a function of **impact given actual scale and requirements**, never of pattern matching.

| Severity | Definition |
| :-- | :-- |
| CRITICAL | Data loss, security breach, or total outage is likely under conditions the system will meet soon |
| HIGH | Significant degradation under realistic near-term load, or a one-way door being closed badly |
| MEDIUM | Real risk, but conditions are not near, or a workaround exists |
| LOW | Suboptimal; the cost is mostly future friction |
| INFORMATIONAL | Observation; no action implied |

### Anti-rules

Each of these is an evaluation assertion, not a guideline:

- A **single database instance** is not a finding for a system with no stated availability target
  and low traffic. It may be INFORMATIONAL with a trigger.
- **"No orchestration platform", "not microservices", "no service mesh", "single region", "no event
  streaming"** are **never** findings. Absence of large-scale machinery is not a defect.
- **"Not using the latest framework version"** is not a finding unless there is a known
  vulnerability or a concrete blocked capability.
- **Low test coverage** is a finding; *"coverage below 80%"* is not. Report what is untested and
  why it matters.
- A finding **without evidence is deleted, not softened**.

### Downgrade check

Before assigning HIGH or CRITICAL, ask: *would this still be HIGH if the system stays exactly this
size for two more years?* If not, it is MEDIUM with a trigger.

## Phase 5 — Report

Ranked most severe first. Every finding carries:

```yaml
id: F-003
severity: HIGH
title: "Payment provider called synchronously in the request path with no timeout"
evidence: ["app/services/checkout.rb:88", "Gemfile:41"]
context: "Checkout is the primary revenue path; ~30 RPS peak; no circuit breaker present"
impact: "Provider latency propagates directly to users. A provider stall exhausts the
         web worker pool and takes down all endpoints, not just checkout."
knowledge: [timeouts, bulkheads, circuit-breakers]
remedy: "Set an explicit client timeout (2 s connect / 5 s read); isolate the call behind
         a bulkhead so provider degradation cannot consume the whole pool"
effort: S
trigger: "Revisit for async processing when checkout p95 exceeds 800 ms or provider
          error rate exceeds 1% over 1 hour"
scale_independent: true
```

### Zero findings is a valid outcome

> *"No findings. The architecture is proportional to its measured scale and the operational
> fundamentals are in place. Watch these triggers rather than changing anything now."*

This is the most useful answer a reviewer can give and the one an eager assistant never gives. A
review that always finds something is a review that finds nothing.

### The summary

One page, first. State the verdict plainly, then the counts, then the complexity spend. If the
architecture is appropriate, say so in the first sentence rather than burying it under a list of
minor observations.

---

## Gates

| Gate | Blocks until |
| :-- | :-- |
| G-R1 | Inventory is complete and contains no judgement |
| G-R2 | Context is established, with assumptions recorded |
| G-R3 | Every finding cites evidence |
| G-R4 | Every HIGH or CRITICAL has passed the downgrade check |
| G-R5 | No finding is on the anti-rules list |

## Related

- `schemas/repo-facts.schema.json`, `schemas/review-finding.schema.json`,
  `schemas/review-output.schema.json`
- `frameworks/complexity-budget/procedure.md` — for scoring what exists
- `templates/architecture-review.md`
