# Examples

Reference artifacts showing the shape and rigour of OAB output.

> ⚠️ **These are reference artifacts, not live agent runs.**
>
> They are the schema-valid `design.json` documents the evaluation suite asserts against —
> hand-authored to define what correct output looks like, and used as the deterministic
> baseline for Tier 1 evaluation.
>
> Replacing them with **real, unedited** output from an installed plugin is condition 2 of the
> M1 definition of done ([#43](https://github.com/mhayk/oab/issues/43)), and has not happened
> yet. Saying so plainly matters more than a convincing-looking sample.

## What to notice

Read `rejected_components` first in each file. That array — what was considered, refused, and
**the measurement that would reverse the refusal** — is the part a generic assistant never
produces, and it is where OAB's value concentrates.

| Example | Scale | The point |
| :-- | :-- | :-- |
| [`tiny-startup/`](tiny-startup/design.json) | 100 users, £50/month, 2 developers | 0.28 requests/second. Four components, 4/4 complexity points, no headroom — stated plainly. An orchestration platform, a cache, an event stream, a read replica and a search engine each rejected with their threshold. |
| [`medium-saas/`](medium-saas/design.json) | 100k MAU, 8 engineers, multi-tenant | 208 peak RPS. Workers, a replica and a cache are justified — the cache on **shared state across instances**, not load relief, because the load-relief case is marginal and saying so is the honest answer. Event streaming and a connection pooler rejected with arithmetic. |
| [`inconsistent-requirements/`](inconsistent-requirements/design.json) | 99.99% on £50/month, 1 engineer | `availability.consistent: false`. OAB refuses to produce an architecture that pretends, states what the design *does* deliver (~99.5%), and puts the contradiction in front of the user. |

## The three things to compare against a generic answer

1. **Numbers before components.** Every component carries a justification referencing a measured
   or assumed figure.
2. **Rejections with thresholds.** `revisit_when` on every refusal, so a "no" is a plan rather
   than an opinion.
3. **The complexity budget, reported plainly.** `4 / 4 — no headroom` is a sentence that changes
   the next conversation.
