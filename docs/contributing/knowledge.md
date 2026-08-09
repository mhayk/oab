# Contributing architecture knowledge

**This is the highest-value contribution to OAB, and it requires no understanding of the codebase.**

You need one thing: real experience with a system-design topic. If you have operated something in
production and learned when it helps and when it hurts, you can contribute.

---

## What a knowledge unit is

One file, one concept. It is not documentation — it is an **instruction to a reasoning agent**, so
it must be specific enough to change a decision.

The test: *could an agent use this to decide whether to include a component in a specific
architecture, given specific numbers?*

| Not a knowledge unit | A knowledge unit |
| :-- | :-- |
| "Caches improve read performance" | "A cache is justified when a single key exceeds ~10 requests/second and recomputation costs more than ~100 ms" |
| "Kafka is good for event streaming" | "A broker earns its complexity above ~500 events/second, or when 3+ independent consumer groups must replay the same stream" |
| "Use timeouts" | "Set connect and read timeouts derived from the caller's latency budget; a timeout longer than the caller's own is not a timeout" |

## The five-minute version

```bash
git clone https://github.com/mhayk/oab && cd oab
pip install -r requirements-dev.txt

cp templates/knowledge-unit.md knowledge/<domain>/<your-concept-id>.md
# fill it in

python3 tools/validate_knowledge.py     # checks schema, links, structure
python3 tools/build_index.py            # regenerates the domain index
git commit -s -m "knowledge: add <concept>"
```

Domains available today: `fundamentals`, `databases`, `caching`, `messaging`, `reliability`, `cost`.
More arrive in M2 — if your concept does not fit, open an issue before writing.

---

## The four things reviewers check hardest

### 1. `## When it does not apply` is real

**Mandatory, and enforced — the validator rejects a section under 40 characters.**

A knowledge base that only says when to use things is a machine for producing overengineering. This
section is where OAB's central value lives, so be specific and be generous: most systems, most of
the time, do not need most concepts.

Good content for this section:

- The scale below which the concept is not worth its complexity — with a number.
- The simpler alternative that is usually sufficient.
- The case where adopting it makes things actively worse.

### 2. Claims are quantified

Numbers, ratios, or orders of magnitude. Where you genuinely cannot give a number, give a condition
that can be checked against a real system.

If a figure is version- or hardware-specific, say which. `"about 5,000 writes/second on an indexed
table, measured on 4 vCPU with 16 GB in 2025"` is useful; `"about 5,000 writes/second"` rots
invisibly.

### 3. `applies_at_stage` is deliberate

```yaml
applies_at_stage: ["3", "4"]
```

This is **the primary overengineering guard**. Retrieval filters on it, so a stage-4 concept cannot
surface in a stage-1 design.

| Stage | Shape |
| :-- | :-- |
| 0 | Prototype — validating the idea |
| 1 | MVP — first real users |
| 2 | Early production — reliable operation, growing usage |
| 3 | Growth — horizontal scaling where metrics justify it |
| 4 | Scale — partitioning, event-driven, multi-service |
| 5 | Global — multi-region, geographic routing |

Listing every stage is almost always wrong. The exceptions are genuinely scale-independent concepts
— tested backups, timeouts, error tracking — whose failure is not proportional to traffic.

### 4. Sources are attributed and text is original

At least one entry in `references`. **Never paste from books, paid courses, or articles.** Summarise
in your own words and cite. A knowledge project that launders copyrighted text has a shutdown date.

Preferred sources: papers, RFCs, standards, official documentation, published measurements,
reputable engineering writing. Your own production experience is a valid source — record it as
`type: measurement` and say what you measured.

---

## Structured fields that matter

Beyond the prose, three frontmatter fields carry weight in OAB's reasoning:

**`trade_offs`** — each entry needs `gains`, `costs`, and `when_worth_it`. The last one is the field
that turns knowledge into a decision, so quantify it. An entry with no costs means the concept has
not been understood.

**`failure_modes`** — each needs `mode`, `symptom`, `detection`, `mitigation`. `symptom` is what an
operator *observes*, not what happens internally. `detection` is a specific signal — "monitoring" is
not detection.

**`complexity_cost`** — 0–5 points of operational burden if adopted. 0 means a technique rather than
a component (TTL jitter is 0; a distributed cache is 2). This feeds the complexity budget directly,
so it changes what OAB recommends. See `frameworks/complexity-budget/weights.yaml`.

**`triggers`** — optional but valuable. Measurable conditions that make the concept relevant. These
generate the trigger library, so they must be observable metrics with a sustained window, not
narrative conditions.

---

## Reviewing your own unit before opening a pull request

1. Does it change a decision, or does it only explain a thing?
2. Could someone follow `## When it does not apply` and correctly *not* adopt this?
3. Are the numbers checkable, and do they carry their basis?
4. Is `applies_at_stage` narrow enough that a small system will not see it?
5. Does `## Measurement` say what to instrument to know it is working? A recommendation you cannot
   verify is one you cannot revisit.
6. Is every claim yours, or attributed?

## What happens next

CI validates the schema, referential integrity, prerequisite cycles, and the body structure. A
maintainer reviews for the four things above.

`maturity: draft` is a legitimate landing state. A good but unreviewed unit can merge as `draft` —
agents treat draft content as provisional and flag it as such — and be promoted to `reviewed` or
`stable` later. It is better to land useful knowledge marked honestly than to hold it for perfect.

## Related

- [`templates/knowledge-unit.md`](../../templates/knowledge-unit.md) — the file you copy
- [`schemas/knowledge-unit.schema.json`](../../schemas/knowledge-unit.schema.json) — the full field reference
- [Knowledge representation](../design/03-knowledge-system.md) — why Markdown with frontmatter, and not a graph or vector database
- [A complete worked example](../design/09-specifications.md#39-knowledge-schema-example)
- [Rules for every contribution](../../CONTRIBUTING.md#rules-that-apply-to-every-contribution)
