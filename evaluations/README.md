# OAB Evaluation

Every claim OAB makes — proportionality, rigour, "a Principal Engineer reviewed this" — is a claim
about **behaviour**. Behaviour claims without tests are marketing.

This suite catches **both** failure directions, which is unusual and is the point:

- **Overengineering** — an orchestration platform for 100 users. Common, expensive, and the reason
  OAB exists.
- **Underengineering** — no backups, no timeouts, 99.99% claimed on a single instance. Rarer in AI
  output, more dangerous.

A tool that only prevents overengineering is a tool that tells you to do nothing.

## Running

```bash
pip install -r ../requirements-dev.txt

python3 evaluations/runner/run_scenarios.py                 # Tier 1, all scenarios
python3 evaluations/runner/run_scenarios.py --perturb       # + magnitude sensitivity
python3 evaluations/runner/run_scenarios.py --scenario 01-tiny-startup -v

# Tier 2: assert against an artifact an agent actually produced
python3 evaluations/runner/run_scenarios.py \
    --scenario 01-tiny-startup --artifact .oab/design.json
```

## The two tiers

| | Source of the artifact | Runs | Blocking |
| :-- | :-- | :-- | :-- |
| **Tier 1** | Committed `baseline.json` per scenario | Every commit | ✅ |
| **Tier 2** | An artifact a real agent produced | Gated on a secret; nightly and on release | ✅ where it runs |

**The assertions are identical.** Only the source differs. Tier 1 is what stops a schema or
framework change silently invalidating a scenario's expectations; Tier 2 is what proves the agent
actually behaves this way.

Tier 2 is **skipped, not failed, on fork pull requests** — a suite that fails every external
contribution makes external contribution impossible.

## What makes this deterministic

Assertions run against **artifact fields**, never prose. That is the enabling design decision
behind the whole framework: `.oab/design.json` carries components, budget, options and triggers as
structured data, so "did OAB recommend an orchestration platform for 100 users" is a field check
rather than a string search.

It is also the anti-gaming property. A framework can be tuned to produce reassuring *words* far
more easily than the right *structure*, and a suite that checks strings teaches contributors to
write for the checker.

## The scenarios

| # | Scenario | Guards against |
| :-- | :-- | :-- |
| 01 | Tiny startup — 100 users, £50/month, 2 developers | Overengineering — the headline failure |
| 02 | Growing SaaS — 100k MAU, multi-tenant, 8 engineers | Under-provisioning; adopting streaming for queue-sized work |
| 03 | Large platform — 50,000 RPS, multi-region | **Refusing complexity the numbers justify** |
| 07 | Healthy system, nothing to change | The reflex to always recommend something |
| 08 | 99.99% on £50/month with one engineer | Producing an architecture that pretends |

Scenarios 07 and 08 are not in the founding brief. They were added during design because they are
the ones OAB is most likely to fail, and therefore the most valuable to hold from the start.

Numbering leaves gaps for the M2 scenarios: 04 financial transactions, 05 social feed, 06 AI SaaS,
09 legacy repository review.

## Anti-gaming

Scenario suites rot into overfitting: the framework grows a clause that recognises "100 users" and
emits the expected answer.

1. **Property assertions, not strings.** Component *kinds* from a closed enum, not prose.
2. **Perturbation** (`--perturb`). Capacity is scaled 100× and 0.01×; the assertions must break in
   at least one direction. A framework that recognised the specific numbers would survive both.
   Scenarios with no numeric capacity bounds report *not applicable* rather than a false alarm — a
   noisy guard is one people learn to ignore.
3. **Held-out scenarios** in `holdout/`, referenced by no framework, run only on release branches.
4. **Model diversity.** Tier 2 runs against more than one model family before a release; a
   framework that works with only one has encoded a model quirk, not knowledge.

## Adding a scenario

```
evaluations/scenarios/NN-name/
├── scenario.yaml     the input, and `guards:` naming the failure it protects against
├── assertions.yaml   must / must-not / numeric / structural
├── baseline.json     a schema-valid artifact representing the expected shape
└── notes.md          why this scenario exists, and how it could be gamed
```

Requirements:

- `guards:` must name a **specific failure**, not a topic.
- Assertions target artifact fields. If you find yourself matching prose, the artifact is missing a
  field — add it to the schema instead.
- `notes.md` explains what the scenario protects against and the tempting way to fail it.
- The baseline must validate against its schema; `tools/validate_artifacts.py` checks fixtures and
  CI validates the baselines.

## Assertion reference

| Assertion | Checks |
| :-- | :-- |
| `must_include_components` | Component *kinds* present |
| `must_not_include_components` | Component kinds absent — the overengineering guard |
| `must_reject_components` | Explicitly rejected **and** carrying `revisit_when` |
| `numeric` | `min`, `max`, `lte_field`, `gte_field`, `optional` |
| `structural` | `min_length`, `max_length`, `contains`, `not_contains`, `in`, `equals`, `exists` |

Field paths are dotted with `[*]` to project over a list: `options[*].verdict`.

`must_reject_components` is the strongest assertion in the set. Silently omitting a component is
not the same as considering one and refusing it — only the second gives a reader something to
disagree with, which is why it also requires the measurement that would reverse the rejection.
