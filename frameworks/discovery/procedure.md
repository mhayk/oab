# Framework: Discovery

**Purpose.** Establish what must be known before designing anything — while asking as few questions
as possible.

**Inputs.** A problem description, and a repository where one exists.
**Output.** `inputs[]` and `assumptions[]` conforming to `schemas/reasoning-trace.schema.json`.

---

## The governing rule

> **Ask only questions whose answers materially change the architecture.**
> Hard cap: **5 questions.** Infer everything else, and label what you inferred.

A long questionnaire is not thoroughness. It is a way of transferring the analytical work back to
the person who came for help, and most of its answers would not have changed the recommendation.

Before asking anything, apply the **sensitivity test** (Step 4). It frequently removes the need to
ask at all.

---

## Step 1 — Infer from the repository first

Where a repository exists, these are observations, not questions. Use `repo-facts` from the
inventory phase of `frameworks/architecture-review/`.

| Fact | Where it comes from |
| :-- | :-- |
| Language, framework, dependencies | Manifests and lockfiles |
| Architecture style | Build and deploy configuration |
| Datastores, caches, queues | Dependencies, connection strings, compose files, IaC |
| External services in the request path | SDK imports and HTTP clients |
| Deployment topology | Dockerfile, IaC, CI workflows, platform config |
| Team size (approximate) | Distinct commit authors in the last 6 months |
| Development cadence | Commit and release frequency |
| Existing observability | Logging, tracing, metrics libraries |

Team size from git history is an estimate, not a fact — record it as `source: assumed`.

## Step 2 — Infer from what was already said

Read the problem description for facts the person has already given you implicitly. Asking for
something they just told you is the fastest way to lose their confidence.

| Signal in the description | Inference |
| :-- | :-- |
| "internal tool", "for our team" | Small user count; working-hours traffic shape (peak factor ≈ 4) |
| "marketplace", "social", "consumer" | Public traffic; evening concentration (peak factor ≈ 10) |
| "£X/month budget" | Budget stated; also implies stage and team size |
| "we", "our team" with no size | Small; assume 2–5 and say so |
| "regulated", "healthcare", "financial", "PCI" | Compliance constraints exist and must be asked about |
| "MVP", "prototype", "validating" | Stage 0–1; optimise for velocity and reversibility |
| "customers are complaining about speed" | Existing system; performance analysis, not greenfield design |

## Step 3 — Rank what remains by decision impact

Only these six change the architecture materially. Ask at most five, in this order.

| # | Question | Why it changes the answer |
| --: | :-- | :-- |
| 1 | **How many users, and how active?** | Sets every capacity number. Everything downstream depends on it. |
| 2 | **How many engineers will operate this?** | Sets the complexity budget. A two-person team cannot carry what a twenty-person team can. |
| 3 | **What is the monthly infrastructure budget?** | Hard constraint that eliminates whole classes of architecture immediately. |
| 4 | **What breaks the business if it fails or is wrong?** | Separates the parts needing consistency and durability from the parts that can be eventually consistent, retried, or lost. |
| 5 | **What availability do you actually need?** | Drives redundancy, failover, and cost — and is frequently overstated until the cost of each nine is shown. |
| 6 | **Any compliance, residency, or data-sensitivity constraints?** | One-way doors. Cheap to ask, extremely expensive to discover late. |

Questions deliberately **not** asked, because the answer rarely changes the design at the stage
most systems are at: preferred language, preferred cloud, preferred database, expected growth rate
in three years, whether the team likes microservices.

Growth rate is the notable omission. It is excluded because it is almost always speculative, and
designing for speculative growth is the failure mode OAB exists to prevent. Growth is handled by
**triggers**, not by pre-building.

## Step 4 — The sensitivity test (do this before asking)

Compute the result at the **extremes** of the plausible range for the unknown input. If the
recommendation does not change, **do not ask** — state the assumption and the range, and move on.

Worked example. Users unknown, described as "a small side project":

```
Assume 100 users,  30% daily active, 10x peak  ->  0.28 requests/second
Assume 100 users, 100% daily active, 20x peak  ->  1.9  requests/second
```

Both are a single instance with enormous headroom. The question would have cost a round-trip and
changed nothing, so instead:

> *Assuming under ~5,000 users. At 100 users this is 0.28 requests/second, and even at 100% daily
> active with a 20× peak it is 1.9 — the recommendation is the same across the whole range. If you
> are above 5,000 users, say so and I will re-run this.*

This is recorded as `decision_is_insensitive: true` in the capacity result. It is a **stronger**
finding than any individual number: it says the conclusion is robust, not merely computed.

## Step 5 — Turn every remaining gap into a labelled assumption

Every gap becomes an explicit assumption with a confidence and a stated impact. Assumptions are
**visible in the deliverable**, never hidden — a user who can see the assumption can correct the
input instead of distrusting the tool.

```yaml
assumptions:
  - text: "30% of registered users are daily active"
    confidence: low
    impact: "±3x on RPS"
  - text: "No compliance constraints, as none were mentioned"
    confidence: medium
    impact: "would change data residency and audit requirements entirely"
```

**When unknown, assume small.** Assuming large is how a 100-user application gets told it needs
multiple regions. The cost of assuming small and being wrong is one re-run; the cost of assuming
large and being wrong is an architecture the team cannot operate.

---

## Discovery areas, for reference

Not a questionnaire. This is the space from which the six questions are drawn, and the checklist
for what to infer.

**Product** — what it does; who uses it; the critical journeys; which operations may fail
temporarily and which may not; what is synchronous today that could be asynchronous.

**Scale** — users; active share; requests per day; read/write ratio; payload sizes; storage volume
and growth; geographic distribution.

**Reliability** — availability target; recovery time and recovery point objectives; what "down"
means to this business.

**Performance** — latency expectations at p50/p95/p99; throughput; concurrency.

**Financial** — infrastructure budget now and expected; engineering cost; tolerance for operational
complexity.

**Team** — size; experience; dedicated operations capacity; on-call reality; expected maintenance
capacity.

---

## Gate

**G1 — Discovery is complete when:**

- Scale is quantified, or a labelled assumption with a range exists.
- Team size is known or assumed, so a complexity budget can be computed.
- Non-functional requirements are quantified or explicitly marked unquantified.
- Every gap appears in `assumptions[]` with a confidence.

Do not proceed to design with unquantified scale and no assumption recorded. That is how adjectives
become architecture.

## Related

- `frameworks/capacity-planning/procedure.md` — consumes these inputs
- `frameworks/complexity-budget/procedure.md` — consumes team size
- `schemas/reasoning-trace.schema.json` — the output contract
