# Framework: Architecture Design

**Purpose.** Get from a framed problem to a decided, justified, trigger-bearing architecture.

**Inputs.** A problem description, and a repository where one exists.
**Output.** `design.md` (prose) and `design.json` conforming to `schemas/design-output.schema.json`.

**Emit the artifact before the prose.** A skipped step is then detectable as a missing field rather
than hidden inside readable text.

---

## The pipeline

```
 1 FRAME      What decision is actually being made?
 2 GATHER     Repository evidence + at most 5 questions          → frameworks/discovery
 3 ASSUME     Every gap becomes a labelled assumption            → frameworks/discovery
 4 QUANTIFY   Run the calculators                                → frameworks/capacity-planning
 5 CLASSIFY   Determine stage and complexity budget              → frameworks/complexity-budget
 6 RETRIEVE   Select knowledge filtered by applies_at_stage
 7 OPTION     Generate ≥2 options, always incl. the simplest
 8 CONSTRAIN  Apply the budget gate ──── over budget? ──┐
 9 DECIDE     Choose, with rationale and confidence     │
10 TRIGGER    Define measurable revisit conditions      │
11 RECORD     Emit design.json, then design.md          │
              ▲                                          │
              └──────────────────────────────────────────┘
                     back to 7: generate simpler options,
                     not forward to justify an expensive one
```

Steps 4, 5, 8 and 10 are what distinguish OAB from a well-written prompt. They are the steps a
model skips unless a procedure forces it, and they are the steps that produce proportionality.

---

## 1 — Frame

State the decision and its scope in one sentence, plus what is explicitly **out** of scope.

Watch for the common mis-frame: a request phrased as "design a scalable API" is usually "help me
choose a datastore and a deployment target for something small". Designing the stated question
instead of the real one is how a side project acquires a service mesh.

## 2–3 — Gather and assume

See `frameworks/discovery/procedure.md`. Cap at 5 questions. Apply the sensitivity test before
asking anything. Every gap becomes a labelled assumption, visible in the output.

## 4 — Quantify

See `frameworks/capacity-planning/procedure.md`. Peak for provisioning, average for volume and cost.

**Gate G1: do not proceed with unquantified scale and no assumption recorded.**

## 5 — Classify

Determine the maturity stage from the numbers and the context:

| Stage | Signals |
| :-- | :-- |
| 0 Prototype | Validating an idea; no real users; throwaway acceptable |
| 1 MVP | First real users; small team; low budget; velocity dominates |
| 2 Early production | Reliable operation matters; growing usage; monitoring justified |
| 3 Growth | Metrics justify horizontal scaling, replicas, dedicated queues |
| 4 Scale | Partitioning, event-driven, multi-service, autoscaling |
| 5 Global | Multi-region, geographic routing, regional isolation |

Then compute the complexity budget: `frameworks/complexity-budget/procedure.md`.

**The stage is a filter, not a target.** OAB never recommends "moving to stage 3". Systems move
when a trigger fires, and many excellent systems stay at stage 2 permanently.

## 6 — Retrieve knowledge

Read `knowledge/<domain>/README.md` for each domain the design touches, and select units where
`applies_at_stage` includes the system's stage.

**Name the file and the condition.** Not "consult the knowledge base" — that produces either
nothing or everything. For example:

- If the design involves a cache: read `knowledge/caching/README.md`, then
  `knowledge/caching/when-not-to-cache.md` before anything else in that domain.
- If it involves asynchronous work: read `knowledge/messaging/sync-vs-async-decision.md`.
- If an availability target was stated: read `knowledge/reliability/availability-targets.md`.

Record the ids used in `knowledge_used[]`.

**Rule R-F:** a stage-N system may not use stage-(N+2) machinery without a written override.

## 7 — Generate options

**At least two, and one of them must be the simplest viable option** — stated fairly, not as a
straw man.

Most architecture failure is failing to consider "just use the database you already have". The
simplest option must be described with a genuine account of why it might be enough, and if it is
rejected, rejected on a measurement.

Each option carries:

| Field | Requirement |
| :-- | :-- |
| Components | Generic kinds, not products |
| `complexity_cost` | From `weights.yaml` |
| `monthly_cost` | A range, with currency and a dated price table |
| `reversibility` | easy / moderate / hard / one-way |
| `trade_offs` | **Never empty.** An option with no downsides has not been understood. |
| `reason` (if rejected) | **The measurement that would change the answer**, not merely why it lost |

Reversibility deserves weight: a reversible decision made quickly usually beats a perfect decision
made slowly, and one-way doors justify more analysis than two-way doors.

## 8 — Constrain

Apply the complexity budget gate.

**Over budget ⇒ return to step 7 and generate simpler options.** Do not proceed to step 9 and
justify the expensive one. The loop is the mechanism; skipping it is how the budget becomes
decoration.

An override is permitted with both a justification and a mitigation naming what is dropped, who
operates the excess, or which engineer is being hired.

## 9 — Decide

State the decision, the rationale **referencing the numbers**, the trade-offs accepted, and an
honest confidence.

**Check the decision against every stated hard constraint, and record the result as a field.**

Where a budget was stated, compare the **high** end of the cost estimate against it and set
`cost.stated_budget` and `cost.within_budget`. When the range top exceeds the budget, set
`cost.within_budget: false` and write `cost.budget_note` — by how much, why, and what would bring
it inside.

A constraint the design might breach must be surfaced, not left for the reader to notice by
comparing two numbers. This is the same rule `availability.consistent` applies to an unreachable
availability target, and it exists because the first live run reasoned about the budget correctly
in prose while recording nothing an assertion could check.

Low confidence must recommend **measurement before commitment** rather than hedged prose.

Also record `rejected_components[]`: what was considered and refused, each with the measurement
that would change the answer. This is the most valuable part of an OAB design and the part a
generic assistant never produces.

## 10 — Triggers

See `frameworks/evolution-triggers/procedure.md`. **Gate G5: at least one measurable trigger.**

Where capacity analysis produced a sensitivity limit, that limit is a trigger. If the design holds
to 5,000 users, the trigger is 5,000 users.

## 11 — Record

Emit `design.json` first, then `design.md` from it.

### Adaptive output

Emit only sections that have content **for this system**. A stage-1 design does not get a
partitioning section, a multi-region section, or an event-streaming section. Generating empty
sections to satisfy a template is the failure this framework exists to prevent, and it makes the
output unreadable, which loses the reader before the useful part.

Always present:

```
Executive summary        ~1 page, first
Assumptions              with confidence
Capacity                 with formulas
Architecture             components + diagram
What was rejected        with the measurement that changes each answer
Complexity budget        spend vs available, stated plainly
Cost                     infrastructure and operational
Reliability              what the architecture actually delivers
Triggers                 measurable revisit conditions
Open questions
```

Present only when relevant: data architecture, API design, async processing, caching, scalability,
security specifics, observability detail, performance targets, load testing, failure scenarios,
evolution roadmap.

### Diagrams

Mermaid, capped at ~12 nodes. A system context diagram is almost always worth it. Anything more
must earn its place — a diagram that looks impressive but cannot be justified is the visual form of
overengineering.

---

## Gates

| Gate | Blocks until |
| :-- | :-- |
| G1 | Requirements exist; non-functional ones quantified or explicitly marked unquantified |
| G2 | Capacity computed with assumptions, formulas, and sensitivity |
| G3 | ≥2 options exist, one of which is the simplest viable |
| G4 | The selected option is within budget, or an override with a mitigation is written |
| G5 | ≥1 measurable trigger exists |

## The eight hard rules

| | Rule | Detectable as |
| :-- | :-- | :-- |
| R-A | No recommendation without a number, or a provisional label | `capacity` populated or explicitly null |
| R-B | Every assumption is in the output with a confidence | `assumptions[]` non-empty |
| R-C | The option set includes the simplest viable option | `options[]` ≥2 with a rejection |
| R-D | Every significant decision carries a measurable trigger | `triggers[]` non-empty |
| R-E | No component appears that was in no option | components ⊆ union of option components |
| R-F | No stage-(N+2) machinery without an override | `applies_at_stage` filter |
| R-G | Confidence stated honestly | `confidence` present |
| R-H | Knowledge ids cited | `knowledge_used[]` |

## Related

- `frameworks/discovery/`, `capacity-planning/`, `complexity-budget/`, `evolution-triggers/`
- `templates/system-design.md` — the prose skeleton
- `schemas/design-output.schema.json` — the artifact contract
- `evaluations/scenarios/` — what this framework is defended against
