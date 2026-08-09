# Framework: Capacity Planning

**Purpose.** Turn discovery inputs into reproducible numbers, and numbers into architectural
constraints.

**Inputs.** `inputs[]` and `assumptions[]` from discovery.
**Output.** One or more `capacity-result` artifacts conforming to
`schemas/capacity-result.schema.json`.
**Implementation.** `calculators/` — run it; do not do this arithmetic by hand if you can avoid it.

---

## The governing rule

> **Every capacity claim is reproducible.** Same inputs, same numbers, from a tested
> implementation — and printed so a reader can check them by hand.

This is where OAB earns trust fastest, because arithmetic is checkable and a wrong number is
immediately visible. It is also where a language model fails most dangerously: silently, and with
confidence.

---

## Step 1 — Run the calculators

```bash
cd calculators
python3 -m oab_calc --list
python3 -m oab_calc rps --users=100 --dau-share=0.3 --sessions-per-day=2 \
                        --requests-per-session=40 --peak-factor=10
```

Order matters — later calculators consume earlier results:

```
rps ──┬──▶ bandwidth        (needs average RPS)
      ├──▶ concurrency      (needs peak RPS)
      │      └──▶ connections   (needs query rate and concurrency)
      ├──▶ cache            (needs read rate)
      └──▶ queue            (needs job arrival rate)
storage ─────▶ cost         (needs volumes)
complexity ──▶ cost         (needs points, for the operational line)
```

**Peak for provisioning, average for volume.** Compute instances and pools against peak RPS;
compute egress, storage, and cost against average. Using peak for a monthly bill overstates it by
the peak factor.

### When the calculators cannot run

If `python3` is unavailable, compute from the formulas printed in `calculators/README.md` and
**say so in the output**:

> *Computed from the documented formulas; the calculator was not available in this environment.*

A silent fallback is precisely the failure the calculators exist to prevent.

## Step 2 — Emit the full envelope

Never a bare number. Every calculation reports, in this order:

```
Assumptions   each labelled observed | stated | assumed | calculated, with a confidence
Formula       the literal expression
Calculation   the expression with values substituted
Result        with units, and a range if any input is uncertain
Safety margin the headroom applied, and why
Confidence    propagated from the inputs
Sensitivity   which single input most changes the result
```

A reader must be able to dispute one line rather than the whole conclusion.

## Step 3 — Apply safety margins

| Quantity | Default margin | Why |
| :-- | :-- | :-- |
| Compute utilisation | Size for **60–70%** | Latency grows non-linearly near saturation: at ρ=0.9 it is roughly 10× service time, at ρ=0.95 roughly 20×. This is an operating point, not conservatism. |
| Peak from assumed traffic shape | **2×** headroom | Peak factor is the least reliable input in most estimates |
| Connection pools | **4×** mean concurrency | Little's Law gives the mean; pools must absorb the tail |
| Storage | **2.5×** logical size | Indexes, page overhead, dead-tuple slack |
| Worker pools | Size for **70%** utilisation | Queue depth grows without bound as utilisation approaches 1 |

Every margin carries its reason. A margin without a reason is superstition.

## Step 4 — Report honestly

**Precision.** At most **2 significant figures** on any number derived from an assumed input.
`0.28 RPS` is honest; `0.2777 RPS` is a lie about precision, and a confident-looking wrong number
does more damage than an obviously approximate one.

**Ranges, not points**, whenever any input has low confidence.

**Confidence propagates.** A chain containing a low-confidence input cannot report high confidence
in the *number*. It can still report high confidence in the *decision* when the sensitivity
analysis shows the conclusion holds across the whole plausible range — and that distinction must
be stated explicitly, not blurred.

## Step 5 — Sensitivity: name the input to measure first

The most useful line in the report.

Compute the result at the extremes of the plausible range for each uncertain input. Report:

- **Which single input dominates** — the one to go and measure first.
- **Whether the decision changes** across that range.

When it does not change, say so plainly:

> *Even at 100% daily active users and a 20× peak factor this is 1.9 requests/second. The
> recommendation does not change anywhere in the plausible input range.*

That is a stronger finding than the point estimate, and it converts an apparently shaky set of
assumptions into a confident decision.

## Step 6 — Turn numbers into constraints

Numbers are not the deliverable. The deliverable is what they rule in and out.

| Finding | Architectural consequence |
| :-- | :-- |
| Peak RPS under ~10 | A single instance has orders of magnitude of headroom. Horizontal scaling, load balancing, and caching have no measured problem to solve. |
| Writes/second under ~100 | Any relational database handles this. Partitioning, sharding, and specialised write stores are unjustified. |
| Reads/second above ~1,000 with a hot working set | A cache may now have a measurable problem to solve. Compute what it relieves before adding it. |
| Connections above 80% of the server limit | A connection pooler is justified. Below that it adds a hop and a process for nothing. |
| Egress above ~1 TB/month | Compute the cost. Edge offload is frequently the largest single saving available. |
| Storage above 60% of the plan | Plan retention and archival now, not at 95%. |
| Worker backlog that never drains | Capacity is below arrival rate. This is an outage with a delay on it. |

## Step 7 — Attach triggers

Every capacity figure that constrains a decision gets a trigger, so the decision expires when the
number does. See `frameworks/evolution-triggers/procedure.md`.

---

## Gate

**G2 — Capacity planning is complete when:**

- Peak and average RPS are computed, or explicitly marked as unquantified.
- Storage growth is projected for at least 12 months.
- Egress is computed where any material payload is served.
- Every result carries assumptions, formula, calculation, confidence, and sensitivity.
- The dominant uncertain input is named.

## Common errors this framework prevents

| Error | Guard |
| :-- | :-- |
| Sizing from adjectives | No recommendation without a number or a provisional label |
| Mixing units (ms with requests/second) | Calculators take milliseconds explicitly and convert |
| Provisioning at 100% utilisation | Default target 60–70%, with the queueing reason stated |
| Billing egress at peak rate | Volume calculations use average, provisioning uses peak |
| False precision | 2 significant figures on assumption-derived numbers |
| Point estimates from uncertain inputs | Ranges required when any input is low confidence |
| Presenting a shaky estimate as authoritative | Confidence propagates from the weakest input |

## Related

- `calculators/README.md` — every formula in prose, and the fallback when Python is unavailable
- `frameworks/discovery/procedure.md` — supplies the inputs
- `knowledge/fundamentals/little-law.md`, `knowledge/fundamentals/utilisation-and-queueing.md`
