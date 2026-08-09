# <system> — Architecture

<!-- ADAPTIVE OUTPUT. Emit only sections that have content FOR THIS SYSTEM.
     A stage-1 design has no partitioning, multi-region, or streaming section.
     Generating empty sections to satisfy a template is the failure this exists to prevent. -->

## Executive summary
~1 page, first. The recommendation, the numbers behind it, and the headline trade-off.

## Assumptions
Every one, with a confidence and the impact if wrong. Visible so the reader can correct an
input rather than distrust the analysis.

## Capacity
Formulas, substituted values, results, and the sensitivity statement.

## Architecture
Components with a justification each — referencing the numbers. Mermaid diagram, ≤12 nodes.

## What was rejected, and when to revisit
Each rejected component with **the measurement that would change the answer**. This is the
most valuable section and the part a generic assistant never produces.

## Complexity budget
`Complexity: N / M` stated plainly, with the consequence when at or over budget.

## Cost
Infrastructure and operational, as ranges, with the price table date.

## Reliability
What this architecture actually delivers. If a stated target exceeds it, say so.

## Evolution triggers
Measurable conditions, each with a source, window, action, and owner.

## Open questions

<!-- Emit only if relevant: data architecture · API design · async processing · caching ·
     scalability · security · observability · performance targets · load testing ·
     failure scenarios · evolution roadmap -->
