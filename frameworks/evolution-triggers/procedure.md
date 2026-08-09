# Framework: Evolution Triggers

**Purpose.** Give every significant decision a measurable expiry condition.

**Inputs.** A decision, its capacity numbers, and the metrics the system already emits.
**Output.** `triggers[]` conforming to `schemas/evolution-trigger.schema.json`.

---

## Why this is the most durable idea in OAB

A design is a snapshot. A trigger is a **standing hypothesis with a falsification test**.

Architecture advice is normally delivered as permanent truth, and nothing states when it stops
being true. So systems either ossify — running an architecture that outgrew itself two years ago —
or churn, rewritten on the basis of a conference talk rather than a metric.

Triggers also give OAB a reason to exist on day 400, not only day 1.

---

## Anatomy

```yaml
id: db-cpu-sustained
decision: ADR-0007
metric: database.cpu.utilisation
source: "managed database metrics dashboard"
comparator: ">"
threshold: 70
unit: percent
window: "sustained over 3 consecutive days"
action: "Re-run capacity analysis; evaluate query optimisation before a read replica"
owner: "backend on-call"
verification: "monthly"
status: armed
```

## The five validity rules

A trigger failing any of these is not a trigger. The schema enforces the mechanical ones; the
reviewer enforces the rest.

### 1. The metric must be observable **today**

If nobody can read this number right now, the trigger will never fire.

Where the metric does not exist yet, the trigger **includes the work to instrument it**, and that
work is part of the decision:

> *This trigger requires per-key cache hit rate, which is not currently emitted. Instrumenting it
> is a prerequisite of this decision, not a follow-up.*

### 2. `source` must name where it is read

A named dashboard, tool, query, or review. "Monitoring" is not a source.

If you cannot say where the number is read, you have written a hope.

### 3. A sustained window is required

Instantaneous triggers fire on spikes, get ignored, and train the team to ignore the next one —
which is worse than having no trigger at all.

| Metric type | Typical window |
| :-- | :-- |
| Utilisation (CPU, memory, connections) | sustained 1–3 days |
| Latency percentiles | sustained 1 day, or 2 occurrences in a week |
| Error rates | sustained 1 hour |
| Queue depth or age | after a normal spike has passed, twice in a month |
| Cost | 2 consecutive months |
| Structural (team, requirement, tenant count) | confirmed, not projected |

### 4. The action is a **next step**, not a solution

| Bad | Good |
| :-- | :-- |
| "Add a message broker" | "Re-run capacity analysis for the async subsystem; evaluate broker options against measured demand" |
| "Migrate to microservices" | "Re-examine service boundaries against the deployment coupling that is blocking teams" |
| "Add a cache" | "Identify the dominant query; evaluate query optimisation before adding a component" |

A trigger that pre-decides the outcome makes the future analysis ceremonial. The right response to
a fired trigger is almost always *re-analyse with current numbers* — because the numbers that fired
it may point somewhere unexpected.

### 5. An owner is named

A person, role, or team. Unowned triggers are decoration.

---

## Setting thresholds

**Fire with time to act, not during the incident.**

A trigger at 95% CPU fires while you are already paged. Set it where there is still runway:

```
threshold = the level at which you would want to START the analysis,
            not the level at which the system is in trouble
```

Rules of thumb:

| Situation | Threshold |
| :-- | :-- |
| Utilisation metrics | 70% — latency is still linear here, and there is time to act |
| Capacity limits (connections, storage) | 60–80% of the hard limit |
| Latency against an SLO | at the SLO, not above it |
| Growth against an assumption | the point at which the assumption stops holding, from the sensitivity analysis |
| Structural thresholds | one step before the pain, e.g. 3 consumer groups rather than 5 |

Where capacity analysis produced a sensitivity figure, use it. If the design holds up to 5,000
users, the trigger is 5,000 users — not a round number chosen for comfort.

## Canonical triggers by domain

Generated from knowledge frontmatter as the knowledge base grows. Starting set:

| Domain | Trigger | Threshold |
| :-- | :-- | :-- |
| Database | Sustained CPU | >70% for 3 days |
| Database | p95 query latency | > SLO for 1 day |
| Database | Connection pool utilisation | >80% for 1 hour, recurring |
| Database | Replication lag | > RPO for 15 minutes |
| Storage | Capacity used | >60% of plan |
| Application | Instance CPU at peak | >70% sustained |
| Application | Deployment coupling | >2 teams blocked per week for a month |
| Caching | Repeated expensive reads | one query >100/min at >50 ms |
| Queue | Backlog drain time | >15 minutes after a normal spike |
| Availability | Error budget | 50% consumed at mid-window |
| Cost | Monthly spend | >120% of budget for 2 months |
| Multi-region | Cross-region p95 | >150 ms for a material user segment |
| Product | Users | past the sensitivity limit of the current design |

## Lifecycle

```
armed ──▶ fired ──▶ resolved
  │                    │
  └────── retired ◀────┘
```

`fired_at` is **retained** after resolution rather than cleared. The history of when an architecture
actually strained is more valuable than a clean record, and it is the evidence base for calibrating
future thresholds.

A trigger is `retired` when the decision it guards is superseded, or when the metric stops being
meaningful. Retiring is a deliberate act with a reason, not deletion.

## Verification

Triggers rot. The dashboard named in `source` gets retired; the metric gets renamed; the threshold
stops being meaningful as the system changes.

Set `verification` to how often someone confirms the metric is still emitted and the threshold
still means what it meant. Monthly for critical decisions, quarterly otherwise.

---

## Gate

**G5 — A decision is complete when:**

- At least one trigger exists.
- Every trigger has an observable metric, a named source, a sustained window, a numeric threshold
  with a unit, an action that is a next step, and an owner.
- Where a metric does not exist yet, instrumenting it is part of the decision.

## Failure modes of this framework

| Failure | Symptom | Mitigation |
| :-- | :-- | :-- |
| Trigger never fires | Metric was never instrumented | Rule 1: observable today, or the work is in scope |
| Trigger fires constantly | No sustained window, or threshold too tight | Rule 3, and thresholds set from measurement |
| Fired trigger ignored | No owner, or the action was ceremonial | Rules 4 and 5 |
| Trigger fires during the incident | Threshold set at the cliff | Set it where analysis can still start |
| Trigger set and forgotten | No verification cadence | `verification` field, reviewed on a schedule |

## Related

- `schemas/evolution-trigger.schema.json` — the contract
- `frameworks/architecture-design/procedure.md` — where triggers are attached
- `docs/design/09-specifications.md#41-evolution-trigger-schema` — worked examples
