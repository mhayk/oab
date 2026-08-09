# Principles

Ordered. When two conflict, the higher one wins.

## 1. Proportionality

Architecture must fit the **measured** problem. Every component carries the burden of proving it
is needed by current numbers, not a hypothetical future. The default answer to "should we add X?"
is **no**, and X carries the argument.

## 2. Quantify before deciding

No recommendation without a number. If the numbers are unknown, state a range and a confidence and
label the recommendation provisional. Adjectives are not inputs — "high traffic" usually turns out
to be a fraction of a request per second.

## 3. Operational complexity is a first-class cost

A component's price is not its invoice. It is invoice + on-call surface + upgrade burden + failure
modes + the hours every engineer spends learning why it exists. Roughly **£240 per complexity point
per month**. A system that saves £100/month and costs half an engineer is the more expensive system.

## 4. Every decision has an expiry condition

A decision without a revisit trigger is one nobody can safely revisit. Triggers must be
**measurable**: a metric, a named source, a threshold with a unit, and a sustained window. "When we
grow" is not a trigger.

## 5. Reasoning is a deliverable

Assumptions → evidence → formula → calculation → options → trade-off → decision → confidence →
trigger. The chain is part of the output, not scaffolding discarded before delivery. You must be
able to disagree with a specific link.

## 6. Deterministic where possible, probabilistic where necessary

Arithmetic, schema validation, and threshold checks are code. Framing, judgement and synthesis are
the model. The model is never asked to multiply, and code is never asked to have taste.

## 7. Local-first, no required service

Everything core runs from a git checkout with no network, no account, and no telemetry.

## 8. Vendor neutrality is structural

Enforced by directory boundaries and a CI check, not by good intentions. Deleting `integrations/`
must leave a complete, useful project.

## 9. OAB dogfoods OAB

Markdown, YAML, JSON Schema, one stdlib script, GitHub. No database, no server, no queue — until a
measured requirement demands one, at which point it gets an ADR. If OAB needed a database to give
architecture advice, OAB would have failed its own review.

## 10. Contestable knowledge

Every knowledge unit is attributed, dated, and challengeable by pull request. Where the industry
genuinely disagrees, OAB records the disagreement rather than pretending consensus.

---

## What these rule out

- Recommending a technology because it is modern, or because a larger company published a post
  about it
- Designing for a growth curve nobody has committed to
- Reporting theoretical problems in a review of a small system
- Claiming an availability target the architecture cannot deliver
- Precision the inputs do not justify

## What they never trade away

Some things are **not proportional to traffic**, and a small system gets no discount: tested
backups and restore, explicit timeouts on every outbound call, error tracking, secret hygiene, and
reversible migrations. Their failure is total at any scale.
