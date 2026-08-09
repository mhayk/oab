# Architecture Review — <repository>

<!-- Emit only sections with content. Findings are weighted by ACTUAL scale. -->

## Summary
One page. State the verdict in the first sentence. If the architecture is appropriate, say
so plainly rather than burying it under minor observations.

| Severity | Count |
| :-- | --: |

Complexity: N / M points.

## Context
Established **before** any finding. Traffic, users, team, budget, availability requirement.
Every assumption listed with a confidence — where unknown, assume small and say so.

## Findings
Ranked most severe first. Each with: evidence (`file:line`), context, impact, remedy,
effort, and a trigger where deliberately not actioned now.

A finding without evidence is deleted, not softened.

## What is appropriate
What the system gets right at its scale. Absence of large-scale machinery is not a defect.

## Triggers to watch
Measurable conditions that would change the findings above.
