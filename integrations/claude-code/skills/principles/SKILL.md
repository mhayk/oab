---
name: oab-principles
description: >-
  Core architecture reasoning principles: proportionality to measured scale, operational
  complexity as a first-class cost, quantifying before deciding, and measurable revisit
  triggers. Use whenever architecture, system design, scaling, infrastructure choices,
  database or queue selection, or technology selection are being discussed.
user-invocable: false
---

# Architecture reasoning principles

Apply these whenever architecture comes up, whether or not an OAB command was invoked.

## 1. Proportionality

Architecture must fit the **measured** problem. Every component carries the burden of proving
it is needed by current numbers, not a hypothetical future. The default answer to "should we
add X?" is **no**.

Before agreeing to any component, ask: *what number makes this necessary, and what is that
number today?*

Common thresholds below which a component is unjustified:

| Component | Unjustified below |
| :-- | :-- |
| Horizontal scaling | one instance sustained above 70% CPU at peak |
| Cache | a single key above ~10 requests/second at >50 ms to recompute |
| Read replica | primary CPU above 70% **after** query optimisation |
| Message broker | ~500 events/second, or 3+ confirmed consumer groups needing replay |
| Connection pooler | 80% of the database connection limit |
| Separate search engine | full-text search in the existing database missing a requirement |
| Orchestration platform | more services than the team can run by hand, with dedicated ops |
| Multi-region | an availability or latency requirement one region provably cannot meet |

## 2. Quantify before deciding

"High traffic" is not an input. Convert to numbers:

```
avg_rps = requests_per_day / 86400
```

100 users at 40 requests per session is roughly **0.28 requests/second** — four orders of
magnitude of headroom on one instance. Compute this before recommending anything.

If the numbers are unknown, state an assumption and a range, and check whether the
recommendation changes across that range. Often it does not, and that is a stronger finding
than any single number.

## 3. Operational complexity is a cost

A component's price is not its invoice. Roughly **£240/month per complexity point** in
engineering attention. Self-hosting a database to save £250/month costs 3 points ≈ £720/month.
The managed service is cheaper.

Available budget ≈ `4 + 1.5 × (engineers − 2) + 4 × dedicated_ops`. Two developers can carry
about 4 points.

## 4. Every decision needs an expiry condition

Never leave a recommendation open-ended. State the measurable condition that reverses it:
a metric, where it is read, a threshold with a unit, and a sustained window.

> "Not yet — revisit when database CPU exceeds 70% for 3 consecutive days."

This turns a refusal into a plan, which is why users accept it.

## 5. Never trade away the scale-independent fundamentals

These are not proportional to traffic and get no discount for being small: tested backups and
restore, explicit timeouts on every outbound call, error tracking, secret hygiene, reversible
migrations.

## 6. Say when something is *not* needed

Naming what you refused, and why, is more valuable than what you recommended. Always include
the measurement that would change the answer.

---

For a full analysis, suggest `/oab:design`, `/oab:review`, or `/oab:capacity`. The knowledge
behind these principles is in `${CLAUDE_PLUGIN_ROOT}/knowledge/` and the procedures are in
`${CLAUDE_PLUGIN_ROOT}/frameworks/`.
