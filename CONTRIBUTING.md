# Contributing to OAB

Thank you for considering a contribution. OAB is a knowledge project first and a software project
second, and the most valuable contributions are usually not code.

This document routes you to the right place. It is deliberately short.

## Which kind of contributor are you?

### I want to add or correct architecture knowledge

**This is the highest-value contribution to OAB, and it requires no understanding of the codebase.**

You need: experience with a system-design topic, and the ability to edit a Markdown file.

→ Read **[docs/contributing/knowledge.md](docs/contributing/knowledge.md)**

In short: copy `templates/knowledge-unit.md`, fill it in, run the validator, open a pull request.
Issues labelled [`area:knowledge` + `good first issue`](https://github.com/mhayk/oab/issues?q=is%3Aopen+label%3A%22good+first+issue%22+label%3Aarea%3Aknowledge)
name specific units we want.

### I want to work on frameworks, calculators, schemas, or evaluations

→ Read **[docs/contributing/engine.md](docs/contributing/engine.md)**

### I want to add support for another AI coding agent

→ Read **[docs/contributing/engine.md](docs/contributing/engine.md)**, section "Integrations".

Note the hard rule: integrations contain no knowledge and no reasoning. If you find yourself
writing architecture guidance inside `integrations/`, it belongs in `frameworks/` or `knowledge/`.

### I want to add an evaluation scenario

Scenarios are how OAB's behaviour is defended against regression, and they are a genuinely useful
contribution — especially ones that guard against **under**-building, which are the harder half.

→ Read **[evaluations/README.md](evaluations/README.md)**

A scenario is four files: the input, the assertions, a schema-valid baseline artifact, and a
`notes.md` saying what failure it protects against and how it could be gamed.

### I want to improve the site or the translations

The site is three static pages sharing one stylesheet — no build step, no framework.

→ Read **[website/README.md](website/README.md)**

**English is canonical, and translations are updated in the same change as the original.** That
applies to `README.md` → `README.pt-BR.md` / `README.es.md`, and to `website/index.html` →
`website/pt/` / `website/es/`. Each translated file carries a sync-date comment at the top. Three
copies that drift silently are worse than one honest language.

### I found a bug or want to propose a change

Open an issue first for anything larger than a typo. A short discussion before the pull request
saves everyone time.

## Rules that apply to every contribution

### 1. Vendor neutrality in the core

No AI vendor or model name (Claude, Anthropic, OpenAI, GPT, Codex, Cursor, Copilot, Gemini, …) may
appear in the **client-agnostic core**: `knowledge/`, `frameworks/`, `calculators/`, `schemas/`,
`templates/`, `evaluations/`. `tools/check_neutrality.py` enforces it.

The test behind the rule: **deleting `integrations/` must leave a complete, coherent, useful
project.**

It deliberately does **not** police project documentation. A README that cannot say which agents
OAB works with is not neutral, it is unhelpful — so `README.md`, `docs/`, `ROADMAP.md` and
`website/` may name clients freely.

A line containing `neutrality-ok` is exempt from the check. Use it with a stated reason, so every
exemption is visible in review.

Naming a cloud provider or database product as *factual comparative data* inside a knowledge unit
is fine. Recommending one as a default is not.

### 2. No verbatim copyrighted text

Summarise concepts in your own words and cite the source in `references`. Do not paste from books,
paid courses, or articles. A knowledge project that launders copyrighted text has a shutdown date.

### 3. No new runtime dependencies

**`calculators/` is standard-library Python only**, and CI enforces it. Those calculators run on a
user's machine through their agent; a user must be able to `git clone` and get exact arithmetic
without installing anything.

`tools/` and tests may use the dev dependencies in `requirements-dev.txt` (PyYAML, jsonschema,
pytest). They run in CI and on a contributor's machine, where two well-known packages are a
reasonable cost for real schema validation rather than a hand-rolled YAML parser.

### 4. Quantify

OAB's entire value is that its advice carries numbers. "Use a cache when reads are high" is not a
contribution. "Use a cache when a single key exceeds ~10 requests/second and recomputation costs
more than ~100 ms" is.

### 5. Say when *not* to do something

Every knowledge unit needs a `## When it does not apply` section, and it is the section reviewers
scrutinise hardest. A knowledge base that only says when to use things is a machine for producing
overengineering.

## Commits and pull requests

### Sign-off (DCO)

Every commit must be signed off, certifying you have the right to submit it under Apache-2.0:

```bash
git commit -s -m "your message"
```

This appends a `Signed-off-by:` line. We use the [Developer Certificate of Origin](https://developercertificate.org/)
rather than a CLA: it establishes provenance without assigning rights to any single entity, which
matters for a project that claims vendor neutrality.

### Commit messages

Conventional style, imperative mood:

```
knowledge: add cache stampede unit
calculators: fix peak RPS rounding at fractional inputs
frameworks: require reversibility on every option
```

Explain **why** in the body when the change is not self-evident. Do not add co-author trailers.

### Pull requests

- One logical change per pull request. If it exceeds ~400 lines of substantive change, split it.
- Update documentation in the same pull request as the behaviour it describes.
- CI must be green: schema validation, neutrality guard, tests.
- Fill in the pull request template. It is short and every line is load-bearing.

## Running checks locally

CI runs all of these. Running them before you push is faster than a round trip.

```bash
pip install -r requirements-dev.txt          # once

# contracts and content
python3 tools/validate_knowledge.py          # frontmatter, links between units, body structure
python3 tools/validate_artifacts.py          # schema fixtures, both directions
python3 tools/build_index.py --check         # generated knowledge indexes are current
python3 tools/check_price_staleness.py       # price tables are not stale

# structural guarantees
python3 tools/check_neutrality.py            # core is client-agnostic
python3 tools/check_stdlib_only.py           # calculators import stdlib only
python3 tools/check_links.py                 # every relative link and heading anchor resolves

# behaviour
python3 evaluations/runner/run_scenarios.py --perturb
python3 -m pytest calculators/tests -q
python3 -m pytest tools/tests -q
```

Regenerate the knowledge indexes after adding or editing a unit — CI fails if they are stale:

```bash
python3 tools/build_index.py
```

### Trying the plugin from your checkout

```bash
claude --plugin-dir ./     # loads this working tree, not the installed copy
/reload-plugins            # after editing a skill
```

Use `--plugin-dir` rather than the marketplace-installed copy while developing: it tests what you
have actually changed, and it is also the only path where the artifact-validation hook currently
runs ([#45](https://github.com/mhayk/oab/issues/45)).

### Demos

`demo/` holds VHS tapes; the GIFs are generated artifacts. **Nothing in them is staged** — the
install tape genuinely removes and reinstalls the plugin. Re-render with `./demo/render.sh` when
the demoed behaviour changes, and look at every GIF before committing.

## Code of conduct

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Licence

Contributions are licensed under [Apache-2.0](LICENSE). See [NOTICE](NOTICE) for trademark terms,
which are separate.
