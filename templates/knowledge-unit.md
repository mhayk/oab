---
# Copy this file to knowledge/<category>/<id>.md and fill it in.
# Validate with: python3 tools/validate_knowledge.py
# Full field reference: schemas/knowledge-unit.schema.json

id: your-concept-id                    # kebab-case, unique repo-wide, never changes
title: Your Concept
description: >-
  One sentence stating what this concept is. Used in indexes and by an agent deciding
  whether to read the file, so describe the thing, not why it is interesting.

category: databases                    # must match the directory this file lives in
subcategory: ""                        # optional
tags: []                               # optional, kebab-case

maturity: draft                        # draft | reviewed | stable — draft is fine for a first PR
confidence: high                       # high | medium | low — low means the industry genuinely disagrees

# THE OVERENGINEERING GUARD. Retrieval filters on this, so a stage-4 concept cannot
# surface in a stage-1 design. Listing every stage is almost always wrong unless the
# concept is genuinely scale-independent (tested backups, timeouts).
#   0 Prototype  1 MVP  2 Early production  3 Growth  4 Scale  5 Global
applies_at_stage: ["2", "3"]

prerequisites: []                      # ids of concepts needed to understand this one
related: []                            # peer ids — cross-domain links are the most valuable

# Operational burden in complexity points if adopted. 0 = a technique, not a component.
# See frameworks/complexity-budget/weights.yaml.
complexity_cost: 1

trade_offs:
  - gains: "What you get."
    costs: "What it costs — operationally, not just financially."
    when_worth_it: "Quantified condition. This field is what turns knowledge into a decision."

failure_modes:
  - mode: "How it breaks."
    symptom: "What an operator observes, not what happens internally."
    detection: "The specific signal or metric. 'Monitoring' is not detection."
    mitigation: "What to do about it."

# Optional. Measurable conditions that make this concept relevant; these generate the
# trigger library, so they must be observable metrics rather than narrative conditions.
triggers:
  - metric: "database.cpu.utilisation"
    comparator: ">"
    threshold: 70
    unit: percent
    window: "sustained over 3 consecutive days"
    action: "Re-run capacity analysis; evaluate query optimisation before adding infrastructure"

anti_patterns: []

references:
  - title: "Source title"
    author: "Author, if known"
    url: "https://example.com"
    type: paper                        # paper | book | rfc | standard | official-docs |
                                       # engineering-blog | talk | measurement | other
    accessed: 2026-08-09

last_reviewed: 2026-08-09
---

## What it is

Two or three sentences. Assume the reader is a competent engineer who has not met this
concept. Do not define it by listing what uses it.

## When it applies

The conditions and **thresholds** under which this concept is relevant. Numbers, not
adjectives. If you cannot give a number, give a ratio, an order of magnitude, or a
qualitative condition that can be checked against a real system.

State the conditions as a conjunction where they genuinely are one:

1. Condition with a number.
2. Condition with a number.
3. Condition with a number.

## When it does not apply

**Mandatory, and the section reviewers scrutinise hardest.**

A knowledge base that only says when to use things is a machine for producing
overengineering. Be specific and be generous: most systems, most of the time, do not
need most concepts.

- The scale below which this is not worth the complexity.
- The simpler alternative that is usually sufficient.
- The case where adopting this makes things actively worse.

## How it works

The mechanism. Enough that a reader can reason about failure, not just recite the name.

## Trade-offs

Prose expansion of the structured `trade_offs` field. What you give up, and to whom the
cost falls — operations, on-call, the next engineer to join.

## Failure modes

Prose expansion of the structured `failure_modes` field. Prefer real failure patterns
over theoretical ones.

## Measurement

What to instrument to know whether this is working, and what the numbers should look
like when it is. A recommendation you cannot verify is a recommendation you cannot
revisit.

## Alternatives

| Approach | Complexity | When to prefer |
| :-- | --: | :-- |
| The simplest thing | 0 | Almost always, until a stated threshold |
| This concept | 1 | When the conditions above hold |
| The heavier option | 3 | When a further stated threshold holds |

## References

Summarise sources in your own words and cite them. **Do not paste copyrighted text.**
