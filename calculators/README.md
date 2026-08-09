# OAB Calculators

Deterministic arithmetic for architecture sizing. Same inputs, same numbers, every time.

Arithmetic is the one place where a language model's failure is silent and confident, and every
downstream architecture decision rests on it. So it is code, it is tested, and its output is a
fixed envelope you can check by hand.

## Running

```bash
cd calculators
python3 -m oab_calc --list                    # what is available
python3 -m oab_calc rps --requests-per-day=2400 --peak-factor=10
python3 -m oab_calc rps --requests-per-day=2400 --json   # schema-conforming JSON
```

**Standard library only.** No install step, no dependencies, Python 3.9+. This is enforced in CI
by `tools/check_stdlib_only.py`, because the promise that OAB works from a git clone is only worth
anything if nothing quietly breaks it.

## The output envelope

Every calculation emits the same seven things, in the same order:

| | |
| :-- | :-- |
| **Assumptions** | every input, labelled `observed` / `stated` / `assumed` / `calculated`, with a confidence |
| **Formula** | the literal expression, so it can be disputed without the numbers |
| **Calculation** | the expression with values substituted, so it can be checked by hand |
| **Result** | with units, and a range whenever any input is uncertain |
| **Safety margin** | the headroom applied, and why |
| **Confidence** | propagated from the inputs, never asserted |
| **Sensitivity** | which single input most changes the result |

**Sensitivity is the most useful line.** It tells you which assumption to go and measure first.

It also carries `decision_is_insensitive`, which records something stronger than any individual
number: that the conclusion holds across the entire plausible input range. When that is true, low
confidence in the inputs does not mean low confidence in the decision, and OAB says so.

### Confidence propagation

A chain containing any low-confidence input cannot report high confidence. This is computed from
the assumptions, not chosen — so it cannot be talked up.

### Precision

Results derived from an assumed input are rounded to **2 significant figures**. `0.28 RPS` is
honest; `0.2777 RPS` is a lie about precision, and a confident-looking wrong number does more
damage than an obviously approximate one.

---

## The formulas

Documented in prose so that an agent can compute them by hand when Python is unavailable. If you
are doing that, say so in the output — a silent fallback is exactly the failure these calculators
exist to prevent.

### `rps` — average and peak requests per second

```
requests_per_day = users × dau_share × sessions_per_day × requests_per_session
avg_rps          = requests_per_day / 86400
peak_rps         = avg_rps × peak_factor
```

Peak factors, when unmeasured. They fall as traffic spreads across time zones:

| Traffic shape | Factor |
| :-- | --: |
| Single-timezone consumer app (evening concentration) | 10 |
| Single-timezone business tool (working hours) | 4 |
| Multi-region service | 2 |
| Global consumer service | 1.5 |

### `storage` — growth per day and per year

```
bytes_per_day  = writes_per_day × avg_record_bytes × index_overhead
bytes_per_year = bytes_per_day × 365
```

`index_overhead` (default **2.5**) turns row size into stored size: indexes, tuple headers, page
fill factor, and dead-tuple slack before vacuum. Counts **inserts only** — updates consume space
until reclaimed, which is a performance concern rather than a growth one.

With a retention policy, storage plateaus at `bytes_per_day × retention_days` instead of growing.

### `bandwidth` — bandwidth and monthly egress

```
bytes_per_second = rps × avg_payload_bytes
egress_per_month = bytes_per_second × 2,592,000
cost             = origin_gb × price_per_gb + edge_gb × cdn_price_per_gb
```

Uses **average** RPS, not peak: egress is billed on volume.

Egress is routinely the largest and most surprising line on an infrastructure invoice, and it is
almost never computed during design. At scale it can exceed the entire compute bill, which makes
edge offload the highest-value decision available — an arithmetic result, not a fashion.

### `concurrency` — Little's Law

```
L           = arrival_rate × service_time_seconds
provisioned = L / target_utilisation
```

Holds for any stable system regardless of arrival distribution or service order.

Takes **milliseconds** explicitly and converts, because mixing milliseconds with requests/second
produces an answer 1000× wrong that still looks plausible.

Little's Law uses the **mean**. Size pools against the tail, not this number alone.

### `connections` — pool sizing, and whether a pooler is justified

```
concurrent        = query_rate × query_time_seconds
pool_per_instance = max(min_pool, ceil(concurrent / instances × safety))
total             = instances × pool_per_instance
```

Defaults: `safety` 4, `min_pool` 5. The floor exists because a pool sized to the mean queues on
connection acquisition during any burst — the arithmetic tells you when a pool is too small, not
that a pool of one is ever a real configuration.

Reports an explicit verdict on whether a connection pooler is justified, at a threshold of **80%
of `max_connections`**. A pooler is a real component with real operational cost, and it is
routinely added before it solves anything.

### `cache` — working set, and what the cache actually saves

```
working_set = hot_keys × avg_value_bytes × overhead
origin_reads = read_rate × (1 − hit_rate)
relieved     = read_rate − origin_reads
```

`overhead` (default **1.3**) covers key storage, per-entry metadata, allocator slack, and
replication headroom.

Given `--origin-query-rate`, it reports the relieved load as a **share of origin load** and flags a
marginal benefit explicitly. "Improves read performance" and "removes 4 queries/second from a
database doing 300" are very different justifications, and only the second is checkable.

### `queue` — workers, and backlog drain time

```
workers    = ceil(arrival_rate × service_time_seconds / target_utilisation)
capacity   = workers / service_time_seconds
drain_time = backlog / (capacity − arrival_rate)
```

When capacity does not exceed the arrival rate, it reports **NEVER DRAINS** rather than a negative
number. A queue that never drains is an outage with a delay on it.

Drain time is the number teams skip, and it is the one that matters during an incident.

### `cost` — infrastructure plus operational

```
infrastructure = Σ(quantity × unit_price)
operational    = complexity_points × hours_per_point × loaded_hourly_rate
total          = infrastructure + operational
```

Defaults: **4 engineer-hours per complexity point per month**, **60 currency units per hour** — so
each complexity point costs roughly **240/month**.

That figure reframes most small-system decisions correctly. Self-hosting a database to save 25/month
costs 3 complexity points, or about 720/month of engineering attention: the managed service is
roughly 4× cheaper. OAB says this with arithmetic instead of preference.

The operational line exceeding the infrastructure line is normal for a small team, invisible in
every cloud calculator, and the reason a cheaper option is often the more expensive architecture.

Prices are **inputs, not built in**. Price tables live in `knowledge/cost/` with their date
attached, because undated prices rot and a stale number stated confidently is worse than no number.

---

## Testing

```bash
pip install -r ../requirements-dev.txt
python3 -m pytest tests -q
```

Three kinds of test:

1. **Worked examples** — each calculator reproduces the numbers published in
   `docs/design/08-technology-and-worked-examples.md`, so the documentation cannot drift from the
   implementation.
2. **Properties** — relationships that hold for any input: peak never below average, doubling
   writes doubles storage, Little's Law is unit-consistent.
3. **Edges and errors** — zero, fractional, very large, and invalid input. A calculator that
   returns a plausible number for nonsense input is worse than one that raises.

## Adding a calculator

Each module exposes exactly two functions:

```python
def add_arguments(parser): ...        # argparse arguments
def calculate(**kwargs) -> CalcResult: ...
```

Then register it in `oab_calc/__main__.py` with a one-line summary and **the question it answers** —
that question is what an agent matches against when deciding which calculator to reach for.

Requirements for a new calculator:

- Standard library only.
- Raise `ValueError` on invalid input rather than returning a plausible number.
- Label every assumption with a source and a confidence.
- Provide a `Sensitivity` naming the input to measure first.
- Add a worked example test tied to a documented scenario.
- Document the formula in this file.
