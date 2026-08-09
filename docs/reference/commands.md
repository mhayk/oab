# Command reference

| Command | Invocation | Writes |
| :-- | :-- | :-- |
| `/oab:design` | user only | `docs/architecture/design.md`, `.oab/design.json` |
| `/oab:review` | user only | `docs/architecture/review.md`, `.oab/review.json` |
| `/oab:capacity` | user or agent | `.oab/capacity.json` |
| `/oab:adr` | user or agent | `docs/adr/NNNN-*.md` |
| `oab-principles` | agent only | — |

`design` and `review` are user-invoked only: they are long, they write files, and they must never
fire spontaneously. `capacity` and `adr` are cheap and read-only enough for the agent to reach for.

## `/oab:design [description]`

Runs the eleven-step pipeline in `frameworks/architecture-design/procedure.md`: frame, gather,
assume, quantify, classify, retrieve, option, constrain, decide, trigger, record.

Asks at most 5 questions. Emits `.oab/design.json` **before** the prose, so a skipped step is
detectable as a missing field.

Output is adaptive — only sections with content for your system are emitted.

## `/oab:review [optional scope]`

Five phases: inventory (delegated to the `repo-scanner` subagent), context, analyse, severity,
report. Context is a **blocking gate**: no finding is produced before the system's actual scale is
established.

Never reports absence of large-scale machinery as a finding. Every finding carries `file:line`
evidence — one without evidence is deleted, not softened.

## `/oab:capacity [what to size]`

Runs the calculators and reports the full envelope. Falls back to the documented formulas when
Python is unavailable, and **says so**.

## `/oab:adr [title]`

Auto-numbers into `docs/adr/`. Refuses to complete with fewer than two options or without at least
one measurable trigger.

## `oab-principles`

A background skill the agent loads automatically whenever architecture comes up. It improves
ordinary conversation, not only explicit commands — the highest-leverage element of the
integration.

## Deferred to M2

`scale` · `performance` · `reliability` · `security` · `cost` · `diagram` · `evolve` · `explain` ·
`knowledge`. Each is a slice of the four above. Shipping nine thin commands before two good ones is
how a plugin becomes a menu nobody understands; usage decides which are promoted.

`/oab:evolve` — checking recorded triggers against current metrics — is the most likely first
addition, because it is the retention mechanism.
