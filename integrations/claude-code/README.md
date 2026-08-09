# OAB — agent integration

This directory is the **only** vendor-aware zone in the repository. It contains no knowledge
and no reasoning: the skills here are thin wrappers that point at `frameworks/`, `knowledge/`,
`calculators/`, `schemas/`, and `templates/` at the repository root.

The structural test: **deleting this directory must leave a complete, coherent project.**
`tools/check_neutrality.py` enforces the mechanical half of that in CI.

## Install

```
/plugin marketplace add mhayk/oab
/plugin install oab@oab
```

## Commands

| Command | What it does | Invocation |
| :-- | :-- | :-- |
| `/oab:design` | Design a system proportional to its measured scale | user only |
| `/oab:review` | Review this repository's architecture, weighted by actual scale | user only |
| `/oab:capacity` | Capacity planning with reproducible arithmetic | user or agent |
| `/oab:adr` | Create an ADR with measurable revisit triggers | user or agent |
| `oab-principles` | Background priors, loaded automatically when architecture comes up | agent only |

`design` and `review` are user-invoked only: they are long, they write files, and they must
never fire spontaneously. `capacity` and `adr` are cheap and safe for the agent to reach for.

`oab-principles` is the highest-leverage element here — it improves **ordinary** architecture
conversation, not only explicit commands.

## Agents

`repo-scanner` inventories a repository and returns structured facts. It runs as a subagent so
that hundreds of file reads do not flood the review's context, and it is forbidden from forming
opinions — inventory is separated from analysis so the scan cannot pre-judge scale.

## Packaging

The repository root **is** the plugin root: the marketplace entry uses `"source": "./"` so
`${CLAUDE_PLUGIN_ROOT}` resolves to the repository, and skills can read `knowledge/` and
`frameworks/`. If the plugin were this subdirectory, the knowledge base would not ship with it.

Trade-off: the plugin cache holds the whole repository. At a few megabytes of Markdown that is
immaterial. **Revisit** if the repository exceeds 50 MB — see ADR-0003, and
`docs/design/02-repository-and-integration.md` §10.2 for the analysed fallback.

## Local development

```bash
claude --plugin-dir ./          # load from a checkout
/reload-plugins                 # after editing a skill
claude plugin validate ./ --strict
```

## Adding a command

1. Write the procedure in `frameworks/<name>/procedure.md` — client-agnostic, no vendor names.
2. Add a thin skill here that points at it.

If you are writing architecture guidance inside this directory, it belongs upstream.
