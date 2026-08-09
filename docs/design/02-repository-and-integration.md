# 02 — Repository Architecture & Agent Integration

Covers §9–§11 of the design brief.

---

## 9. Repository Architecture

### 9.1 The organising idea

OAB is layered strictly, and dependencies point **downward only**:

```
integrations/     ← client adapters (Claude Code, later: Codex, Cursor, MCP)
       │  may read everything below
       ▼
frameworks/       ← procedures: how to reason (discovery, design, review, capacity…)
       │  may read knowledge, schemas, calculators, templates
       ▼
knowledge/        ← facts: what is true about systems (+ machine-readable metadata)
calculators/      ← arithmetic: deterministic, tested, no judgement
schemas/          ← contracts: JSON Schema for every structured artifact
templates/        ← output shapes: ADR, review, capacity report
       │
       ▼
evaluations/      ← proof: scenarios + assertions that OAB reasons correctly
```

Two rules make the layering real rather than decorative, and both are CI-enforced:

- **R1 — No upward references.** Nothing in `knowledge/` or `frameworks/` may reference
  `integrations/`.
- **R2 — No vendor leakage.** No agent-vendor or model name (Claude, Anthropic, OpenAI, Codex,
  Cursor, Copilot, GPT, Gemini…) may appear outside `integrations/`.

If `integrations/` is deleted, OAB is still a complete, coherent, useful project. That is the test.

### 9.2 Directory rationale

| Directory | Exists because | Consumed by |
| :-- | :-- | :-- |
| `knowledge/` | The durable asset. Concepts, trade-offs, failure modes, thresholds — as Markdown with YAML frontmatter so both humans and agents read the same file. | Frameworks, agents, humans |
| `frameworks/` | Knowing facts ≠ reasoning well. Frameworks are the *procedures*: ordered steps, decision gates, required outputs. This is what makes OAB reasoning reproducible rather than emergent. | Integrations |
| `calculators/` | Arithmetic must be exact and testable. The one place code is unambiguously better than a model. | Frameworks, evaluations, CI |
| `schemas/` | Every structured artifact (knowledge unit, capacity result, ADR, trigger, review finding) has a JSON Schema. This is what turns "the agent wrote something" into "the agent produced a validatable artifact" — and it is the foundation of deterministic evaluation. | CI, evaluations, integrations |
| `templates/` | Consistent output shape without a code generator. Markdown skeletons, cheap and forkable. | Frameworks |
| `evaluations/` | The project's credibility. Scenarios + assertions catching both over- and under-engineering. Without this, OAB is a vibe. | CI |
| `integrations/` | The only vendor-aware zone. Thin adapters mapping OAB frameworks onto a specific client's extension model. | Users |
| `examples/` | Real end-to-end outputs, committed. They document capability better than any README and double as regression fixtures. | Users, docs |
| `docs/` | Design, contribution, and knowledge-authoring guidance. Sources for the website. | Humans |
| `tools/` | Repo maintenance: schema validation, link checking, neutrality lint, index generation. Never user-facing. | CI |
| `website/` | The `oab.run` static site. Deliberately last and deliberately small. | Adoption |

### 9.3 A deliberate rejection: no `src/`

There is no application. OAB M1 is content + schemas + one small calculator CLI. Creating a `src/`
tree, a package manifest, a build system, and a dependency graph before there is anything to build
would be exactly the overengineering OAB exists to prevent. `calculators/` holds a single-purpose
stdlib-only Python package; `tools/` holds stdlib-only scripts. When (if) OAB needs a real
application, that gets an ADR.

### 9.4 Why one repository

A monorepo, not a constellation. Rationale:

- Knowledge, frameworks and evaluations change together; splitting them creates version-skew
  between a framework and the knowledge it cites.
- A single `git clone` is the entire product — it directly serves the local-first principle.
- Claude Code's marketplace can serve a plugin whose `source` is the repository root, so one repo
  is simultaneously the marketplace, the plugin, and the knowledge base (see §10.2). Splitting
  would force a build-and-publish step on day one.

**Revisit condition:** if the repository exceeds ~500 MB, or if a second integration needs an
independent release cadence, split `integrations/*` into their own repos consuming OAB as a git
submodule or archive.

The full tree is in [§37 Repository Tree](09-specifications.md#37-repository-tree).

---

## 10. Claude Code Integration

> Designed against the **current** official documentation (code.claude.com/docs, verified August 2026),
> not from memory. Key change from older material: **custom commands have merged into skills.**
> `.claude/commands/foo.md` and `skills/foo/SKILL.md` both produce `/foo`; skills additionally
> support a directory of supporting files, richer frontmatter, and model-invocation control.

### 10.1 What the platform actually gives us

| Capability | Mechanism | OAB uses it for |
| :-- | :-- | :-- |
| Namespaced commands | `skills/<name>/SKILL.md` in a plugin named `oab` → `/oab:<name>` | The user-facing commands |
| Bundled supporting files | Any file in the skill directory; `SKILL.md` links to them and Claude loads on demand | **Progressive disclosure of knowledge** — the single most important mechanism for OAB |
| Path to plugin contents | `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_SKILL_DIR}` | Reaching `knowledge/`, `frameworks/`, `calculators/` from a skill body |
| Arguments | `$ARGUMENTS`, `$0..$N`, named `arguments:` frontmatter | `/oab:capacity`, `/oab:adr <title>` |
| Inline shell injection | `` !`command` `` in skill body | Cheap repo facts (file counts, dependency manifests) without burning tool calls |
| File references | `@path` | Pulling a specific file into context |
| Tool pre-approval | `allowed-tools:` frontmatter (accepts `${CLAUDE_SKILL_DIR}` substitution) | Letting the capacity calculator run without a permission prompt |
| Invocation control | `disable-model-invocation`, `user-invocable` | Heavy workflows are user-triggered; background principles are model-only |
| Subagents | `agents/*.md`; frontmatter `name, description, model, effort, maxTurns, tools, disallowedTools, skills, memory, background, isolation` | Isolating the repo-scanning phase of a review so it doesn't flood the main context |
| Forked execution | `context: fork` on a skill | Considered for `review`; deferred (see 10.6) |
| Distribution | `.claude-plugin/marketplace.json` + `/plugin marketplace add mhayk/oab` | Installation |
| Validation | `claude plugin validate ./ --strict` | A CI job |
| Local dev | `claude --plugin-dir ./`, `/reload-plugins` | Contributor workflow |

Deliberately **not** used in M1: hooks, MCP servers, LSP servers, monitors, output styles,
`userConfig`, plugin `settings.json`. None solves an M1 problem.

### 10.2 The packaging decision (the one that constrains everything)

**Problem.** OAB's value is in `knowledge/` and `frameworks/` at the repository root. A skill can
only reach files *inside the plugin root*. If the plugin were `integrations/claude-code/` and the
marketplace entry used `"source": "./integrations/claude-code"`, then `${CLAUDE_PLUGIN_ROOT}` would
resolve to that subdirectory and **the knowledge base would not ship with the plugin**.

**Options considered.**

| Option | Mechanism | Verdict |
| :-- | :-- | :-- |
| A. Build step copies `knowledge/` into the plugin dir at release | Script + release automation | Rejected for M1. Introduces a build pipeline and a drift class (published plugin ≠ repo) before there is any need. |
| B. Duplicate knowledge inside the integration | Copy | Rejected. Two sources of truth is a defect generator. |
| C. Git submodule | Submodule in plugin dir | Rejected. Submodules are a well-known contributor-hostile trap for a project courting first-time contributors. |
| **D. Plugin root = repository root** | Marketplace entry with `"source": "./"` and explicit `skills` paths | **Chosen.** |

**Chosen design.** The repository is simultaneously the marketplace and the plugin.
`.claude-plugin/` at the repo root contains both `marketplace.json` and `plugin.json`. The plugin
entry uses `"source": "./"` and points `skills` at the integration directory:

```jsonc
// .claude-plugin/marketplace.json
{
  "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
  "name": "oab",
  "owner": { "name": "OAB Maintainers", "url": "https://oab.run" },
  "description": "Open Architecture Brain — architecture intelligence for AI coding agents",
  "plugins": [
    {
      "name": "oab",
      "source": "./",
      "description": "Architecture intelligence: sizing, design, review, ADRs — proportional to your actual scale",
      "license": "Apache-2.0",
      "homepage": "https://oab.run",
      "repository": "https://github.com/mhayk/oab",
      "category": "development",
      "keywords": ["architecture", "system-design", "capacity-planning", "adr", "scalability"],
      "skills": ["./integrations/claude-code/skills"],
      "agents": ["./integrations/claude-code/agents"]
    }
  ]
}
```

This relies on a documented behaviour: for a marketplace entry whose `source` resolves to the
marketplace root, the listed `skills` paths are the complete set for that entry (replacing the
default `skills/` scan). `${CLAUDE_PLUGIN_ROOT}` then resolves to the repository root, so a skill
body can reference `${CLAUDE_PLUGIN_ROOT}/knowledge/...` and `${CLAUDE_PLUGIN_ROOT}/frameworks/...`.

**Trade-off:** the user's plugin cache holds the whole repository, including `docs/` and
`evaluations/`. At M1 that is a few megabytes of Markdown — immaterial. **Revisit condition:** if
the repository exceeds 50 MB, or if `git clone` of the plugin takes more than ~5 s on a normal
connection, switch to Option A (a release build that packages a slim plugin). Recorded as ADR-0003.

**Verification requirement (must be part of the first integration issue):** this behaviour is
confirmed end-to-end by an actual install (`/plugin marketplace add`, then `/plugin install`), not
by reading docs. If it does not behave as documented, fall back to Option A immediately — the rest
of the design is unaffected because it depends only on "skills can read the knowledge base", not on
how that is achieved.

### 10.3 Plugin manifest

```jsonc
// .claude-plugin/plugin.json
{
  "$schema": "https://json.schemastore.org/claude-code-plugin-manifest.json",
  "name": "oab",
  "displayName": "OAB — Open Architecture Brain",
  "version": "0.1.0",
  "description": "Architecture intelligence for AI coding agents: capacity planning, proportional system design, architecture review, and ADRs with measurable revisit triggers.",
  "author": { "name": "OAB Maintainers", "url": "https://oab.run" },
  "homepage": "https://oab.run",
  "repository": "https://github.com/mhayk/oab",
  "license": "Apache-2.0",
  "keywords": ["architecture", "system-design", "capacity-planning", "scalability", "adr", "sre"],
  "skills": ["./integrations/claude-code/skills"],
  "agents": ["./integrations/claude-code/agents"]
}
```

`name: "oab"` is what produces the `/oab:` namespace. `version` is set explicitly so users receive
updates only on a deliberate bump.

### 10.4 Skill architecture — progressive disclosure

The defining constraint of a knowledge-heavy plugin is **context economics**. OAB's knowledge base
will reach hundreds of files. Loading it is impossible and pointless. The architecture is therefore
a three-tier disclosure chain, which maps exactly onto the platform's own design:

```
Tier 1  SKILL.md            ~100–200 lines. The procedure. Always loaded when invoked.
        │                   Contains: steps, decision gates, required outputs,
        │                   and pointers naming exactly which Tier-2 files to read when.
        ▼
Tier 2  frameworks/*.md     The full procedure detail for one phase. Read on demand.
        │                   e.g. frameworks/capacity-planning/procedure.md
        ▼
Tier 3  knowledge/**/*.md   Individual concepts. Read only when a decision depends on them.
                            e.g. knowledge/caching/cache-stampede.md
```

The rule written into every SKILL.md: **name the file and the condition.** Not "consult the
knowledge base" (which produces either nothing or everything) but "if the design includes a cache,
read `${CLAUDE_PLUGIN_ROOT}/knowledge/caching/README.md` and follow its `related` links".

`knowledge/<domain>/README.md` acts as the domain index — a short, cheap file listing every unit in
that domain with a one-line summary, so the agent can select precisely. This index is generated by
`tools/build_index.py` from frontmatter, so it cannot drift.

### 10.5 M1 skills

Four commands. Each is one directory under `integrations/claude-code/skills/`.

| Command | Frontmatter posture | Why |
| :-- | :-- | :-- |
| `/oab:design` | `disable-model-invocation: true` | Long, interactive, writes files. Must never fire spontaneously. |
| `/oab:review` | `disable-model-invocation: true`, `allowed-tools: Read Grep Glob` | Long, scans the repo. Pre-approving read-only tools removes prompt friction. |
| `/oab:capacity` | model-invocable | Cheap, read-only, high value when Claude notices a sizing question. |
| `/oab:adr` | model-invocable, `argument-hint: [decision title]` | Cheap, produces one file, natural for Claude to offer. |

Plus one non-command skill:

| Skill | Frontmatter | Why |
| :-- | :-- | :-- |
| `oab-principles` | `user-invocable: false` | Background priors — proportionality, complexity cost, "quantify before deciding". Claude loads it automatically whenever architecture comes up, so OAB improves *ordinary* conversation, not only explicit commands. This is the highest-leverage, lowest-cost element of the whole integration. |

Full specifications in [§38 Claude Commands](09-specifications.md#38-claude-commands-m1).

### 10.6 Subagent usage

One agent in M1: `oab:repo-scanner` (`integrations/claude-code/agents/repo-scanner.md`).

Repository inspection is high-token and low-signal-density — hundreds of file reads producing a
one-page summary. Running it in the main context poisons the remaining review with irrelevant
detail. A subagent with `tools: Read, Grep, Glob, Bash` and a strict structured return contract
(the `repo-facts` schema) keeps the main thread clean.

`context: fork` on the review skill was considered as a lighter alternative and **deferred**: it
would fork the entire review, not just the scan, losing the interactive clarification step that
makes the review useful. Revisit if review sessions routinely exhaust context.

### 10.7 Installation UX

```bash
# One-time
/plugin marketplace add mhayk/oab
/plugin install oab@oab

# Use
/oab:design      # new system
/oab:review      # existing repository
/oab:capacity    # sizing
/oab:adr "Choose a job queue"
```

Contributor loop: `claude --plugin-dir ./` then `/reload-plugins` after edits.
CI runs `claude plugin validate ./ --strict`.

---

## 11. Future Agent Integrations

### 11.1 The stable contract

Future clients are cheap **only if** the core exposes a stable, client-agnostic contract. That
contract is three things, and nothing else:

1. **Frameworks** — `frameworks/<name>/procedure.md`: an ordered procedure in plain Markdown with
   explicit inputs, steps, decision gates, and required outputs. No client-specific syntax.
2. **Knowledge** — `knowledge/**/*.md` with schema-valid frontmatter, plus generated indexes
   (`knowledge/INDEX.md`, `knowledge/index.json`).
3. **Artifacts** — JSON Schemas in `schemas/` defining every structured output.

An integration is then a *mapping* from that contract to a client's extension model, plus whatever
prompt glue that client requires. It contains no knowledge and no reasoning.

### 11.2 Anticipated shapes

| Client | Likely mechanism | Adapter work |
| :-- | :-- | :-- |
| **Claude Code** *(M1)* | Plugin: skills + agents | Skill wrappers around frameworks |
| **Cursor / Copilot / generic IDE agents** *(M3)* | Rules/instruction files (`.cursor/rules`, `.github/copilot-instructions.md`) | A generator emitting the client's file format from the same framework sources |
| **OpenAI Codex / CLI agents** *(M3)* | `AGENTS.md` + prompt files | Same generator, different emitter |
| **MCP** *(M3, conditional)* | An MCP server exposing `oab.capacity`, `oab.knowledge.search`, `oab.review` as tools | A thin server over `calculators/` and the knowledge index |
| **CI / bots** *(M3)* | The calculator CLI + schema validation in a GitHub Action | Action wrapper |

### 11.3 The generator principle

Rather than hand-maintaining N copies of every procedure, `tools/build_integration.py` emits
client-specific artifacts from the framework sources. Integration directories then contain a small
amount of hand-written client glue plus generated content, with generated files marked and
CI-checked for staleness.

**This generator is explicitly M3.** Building it for one client is speculative infrastructure —
precisely what OAB tells users not to do. M1 hand-writes the Claude Code skills. The *second*
integration is what justifies the generator, and the design constraint we accept now is only that
frameworks must be written as client-agnostic Markdown so the generator remains possible.

### 11.4 On MCP specifically

MCP is a genuine fit for two OAB capabilities — deterministic calculators and knowledge search —
because both are stateless, well-typed request/response operations.

It is a poor fit for the rest. `/oab:design` is a long, interactive, context-dependent procedure;
expressing it as a tool call would produce a worse experience than a skill, because the value is in
the agent *following a procedure inside the conversation*, not in calling a remote function.

Therefore: **no MCP server in M1.** The conditions under which we build one, recorded as an
evolution trigger:

- A second client requests programmatic access to calculators or knowledge search, **and**
- that client cannot consume the repository directly (no filesystem access), **or**
- ≥3 users request an MCP interface with a stated use case.

Until then, an MCP server would be a runtime, an install step, a security surface, and a support
burden in exchange for capability that a file read already provides.
