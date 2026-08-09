# Live run — 2026-08-09

**The first real `/oab:design` output**, produced by the installed plugin (v0.1.0) running headless
against the tiny-startup brief. Unedited.

```bash
claude plugin marketplace add mhayk/oab
claude plugin install oab@oab
claude -p "/oab:design Recipe-sharing web app: ... 100 registered users, 2 developers,
           £50/month infrastructure budget ..." --permission-mode acceptEdits
```

## What it got right

- **0.28 peak requests/second**, matching the design documents exactly.
- **4 / 4 complexity**, at budget with no headroom, stated plainly.
- **12 components rejected**, each with the measurement that reverses it — against 5 in the
  hand-authored baseline.
- **13 triggers, 14 assumptions.**
- It **rejected the CDN** on arithmetic: 3.9 GB/month of egress against a threshold of a few
  hundred, "0.4% of the ~1 TB/month threshold", noting that *"a photo-sharing brief makes a CDN
  feel mandatory"*. The hand-authored baseline **included** a CDN. The live run was less
  overengineered than the reference artifact.
- Its open questions are sharper than the baseline's — the connection-limit one identifies the
  resource most likely to force a plan upgrade, ahead of CPU or storage.

## What it got wrong, and what changed because of it

It recorded £50/month as a quantified requirement and produced an infrastructure estimate of
**£16–56** — a worst case £6 over a hard constraint — with **no field saying so**.

The schema had `availability.consistent` precisely so an unreachable availability target cannot be
stated silently. Cost had no equivalent, so a budget the design might breach was left for the
reader to notice by comparing two numbers.

Fixed in the same commit as this file:

- `design-output.schema.json` gains `cost.stated_budget`, `cost.within_budget`, and
  `cost.budget_note`, with `budget_note` conditionally required when `within_budget` is false.
- `frameworks/architecture-design/procedure.md` step 9 now requires the comparison.
- Scenario 01 asserts `cost.within_budget` exists, and checks the **low** end against the budget
  rather than the high end — the expected case must fit, and a price range whose top exceeds the
  budget is acceptable only if the design says so.

This artifact therefore **fails** the current scenario, on exactly one assertion:
`cost.within_budget is missing`. It is kept as-is rather than patched, because a corrected
sample would hide the finding that produced the fix.

Note that the *prose* did reason about the budget — it states that reaching 99.9% would cost
"three to five times the stated budget". The gap was that nothing in the **artifact** recorded it,
so no assertion could check it. That is the whole argument for the structured output contract in
one example.

## Also verified

- `version` pins the plugin: the fix above was invisible to the installed copy until the version
  was bumped. Recorded in `docs/maintainers/release.md`.
- `claude plugin details` reports `Agents (0)` for an agent declared through a manifest path, but
  the agent **does** load — `oab:repo-scanner` is available as an agent type. A reporting quirk,
  not a defect in the plugin.

---

## Four runs, one unfixed defect

`cost.within_budget` was absent from **every** live run, under escalating enforcement:

| Version | Enforcement added | Result |
| :-- | :-- | :-- |
| 0.1.0 | none — the field did not exist | missing |
| 0.1.2 | required by the framework procedure | missing |
| 0.1.3 | added to the skill; schema made it required | missing — run exhausted its turns before validating |
| 0.1.4 | validation moved **before** the prose; 80 turns | **missing**, with turns to spare |

Run 5 wrote both files and was not truncated. The instruction was in the framework, in the skill,
ahead of the prose, and the schema rejects the artifact without it. The agent still did not emit it.

**Prompt-level instruction does not reliably guarantee a field appears in an artifact.** That is
risk T9 from the design — "the agent ignores the procedure under context pressure" — now measured
rather than hypothesised, and it is the single most important thing learned from installing this
plugin.

The design deliberately excluded hooks from M1: *"Deliberately not used in M1: hooks, MCP servers,
LSP servers…  None solves an M1 problem."* That judgement was wrong. A `PostToolUse` hook that
validates `.oab/design.json` on write and returns the schema error to the agent is a **mechanism**
rather than more words, and it is the only approach tried or proposed that could close this. See
[#44](https://github.com/mhayk/oab/issues/44).

Until then, treat schema-required fields as **aspirational for agent output** and enforced only in
CI. The artifacts here are committed unpatched so the gap stays visible.
