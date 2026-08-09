# Framework: Complexity Budget

**Purpose.** Convert "don't overengineer" from advice into arithmetic.

**Inputs.** Team size, dedicated operations headcount, a candidate list of components.
**Output.** An available budget, a spend, a verdict per option, and a headroom statement.
**Weights.** `weights.yaml` in this directory. Data, so they can be argued about in a pull request.

---

## Why this exists

"Keep it simple" is unenforceable and unfalsifiable. Every individual component addition looks
reasonable in isolation — the cache is justified, the queue is justified, the search engine is
justified — and overengineering happens as an **accumulation**, not as any single bad decision.

A budget makes the accumulation visible and forces an explicit trade rather than a silent slide.

It is not a scoring exercise. It is a device for producing one specific sentence:

> *"Complexity: 4 / 4 — no headroom. Adding a cache requires removing something or adding
> an engineer."*

---

## Step 1 — Compute the available budget

```
available = 4 + 1.5 × max(0, engineers − 2) + 4 × dedicated_ops_engineers
```

Floor of 3. Round down to the nearest integer.

| Team | Available |
| :-- | --: |
| 2 developers, no dedicated ops | 4 |
| 5 developers, no dedicated ops | 8 |
| 12 developers, 1 SRE | 23 |
| 40 developers, 4 SRE | 73 |

**Count people who will actually operate the system**, not headcount. A team of 10 where two are
designers and three work only on the mobile client is a team of 5 for this purpose. Contractors
who leave in three months do not raise the budget; they raise short-term capacity and lower
long-term operability.

If team size is unknown, **assume 2 and say so**. Assuming a large team is how a solo founder gets
told to run a cluster.

## Step 2 — Score the candidate architecture

Sum the cost of every component. Use `weights.yaml`:

| Component class | Points |
| :-- | --: |
| Managed stateless (app runtime, CDN, object storage) | 1 |
| Managed stateful (database, cache, queue) | 1 |
| Self-hosted stateless (own proxy, own worker fleet) | 2 |
| Self-hosted stateful (own database, broker, search cluster) | 3 |
| Self-managed orchestration platform | 4 |
| Multi-region active-active for any stateful component | 4 |

Then add the modifiers:

| Modifier | Points |
| :-- | --: |
| Each **additional datastore technology** beyond the first | +1 |
| Each **additional independently deployed service** | +1 |
| Each technology the team has **never operated** | +1 |

**Techniques cost nothing.** TTL jitter, timeouts, retries with backoff, request coalescing within
a process, a job queue on a database you already run — these change how existing components behave
and add no operational surface. They are free, and OAB should reach for them first.

### Worked example — two developers, £50/month

```
Application runtime (managed)          1
Relational database (managed)          1
Object storage (managed)               1
CDN (managed)                          1
                                      ──
                                       4    against an available budget of 4
```

No headroom. That is the finding, and it is what makes the next conversation honest: a cache is not
"nice to have later", it is a trade against something already in the design.

### Worked example — eight developers, no SRE

```
Application runtime                    1
Worker                                 1
Relational database (managed)          1
Read replica                           1
Cache (managed)                        1
  + additional datastore technology    1
Object storage                         1
CDN                                    1
Observability (managed)                1
                                      ──
                                       9    against an available budget of 13
```

Four points of headroom — enough to absorb one significant addition without a rethink.

## Step 3 — Apply the gate

| Spend vs available | Verdict |
| :-- | :-- |
| ≤ 50% | Comfortable. Note the headroom; do not spend it just because it exists. |
| ≤ 90% | Tight. Any addition needs a stated trade. |
| ≤ 100% | At budget. Report explicitly that there is no headroom. |
| > 100% | **Rejected by default.** |

An over-budget option may only be selected with a written override containing **both**:

1. **Justification** — why the excess complexity is unavoidable, referencing the requirement that
   forces it.
2. **Mitigation** — what is being dropped, who will operate the excess, or which engineer is being
   hired. An override without one of these is a wish, not a plan.

Both are required fields in `design-output.schema.json`. Going over budget is allowed. Going over
silently is not.

## Step 4 — Report it

The spend appears in the deliverable, always, in the form:

```
Complexity: 9 / 13 — 4 points of headroom.
```

And when at or over budget, with the consequence stated:

```
Complexity: 4 / 4 — no headroom. Adding a cache requires removing something
or adding an engineer.
```

---

## When the budget is not the binding constraint

At large scale the budget stops being interesting: a 40-engineer team with 4 SRE has 73 points and
a serious distributed architecture spends 25–30. **Say so and move on.** The binding constraints
there are cost and blast radius, not complexity.

A heuristic that binds where it matters and gets out of the way where it does not is working
correctly. One that produces a scolding at every scale is noise.

---

## Honest limitations

State these in user-facing output whenever the budget drives a rejection. A heuristic presented as
a law is worse than no heuristic.

- **The constants are judgement, not measurement.** `4`, `1.5`, `4`, and every component weight are
  calibrated against experience. Calibration against real projects is an M2 goal with a published
  agreement rate.
- **It does not model coupling.** Three tightly-coupled services are materially worse than three
  independent ones, and this model scores them identically.
- **It treats managed services as equal.** Managed event streaming is harder to operate well than
  managed object storage; both score 1.
- **It does not model team skill.** The `unfamiliar_technology` modifier is a crude proxy.
- **It says nothing about whether the architecture is correct** — only whether the team can carry
  it. An architecture can be within budget and still wrong.

## Failure modes of this framework

| Failure | Symptom | Mitigation |
| :-- | :-- | :-- |
| Gaming the score | Components merged or relabelled to fit | Score by operational surface, not by name. Two databases in one process are still two datastore technologies. |
| Budget treated as a target | Team spends headroom because it exists | Headroom is capacity for the next real requirement, not an allowance |
| Applied to a large team | Constant passing verdict, no signal | Report that complexity is not the binding constraint and stop |
| Blocking a genuine requirement | A necessary component rejected on points | The override path exists for exactly this; use it and record the mitigation |

## Related

- `knowledge/fundamentals/complexity-cost.md` — the underlying idea, and the ~£240/point/month
  operational cost model
- `frameworks/architecture-design/procedure.md` — where the gate is applied (G4)
- `calculators/oab_calc/cost.py` — turns points into money
