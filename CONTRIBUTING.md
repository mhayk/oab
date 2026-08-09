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

### I found a bug or want to propose a change

Open an issue first for anything larger than a typo. A short discussion before the pull request
saves everyone time.

## Rules that apply to every contribution

### 1. Vendor neutrality

No AI vendor or model name (Claude, Anthropic, OpenAI, GPT, Codex, Cursor, Copilot, Gemini, …)
may appear outside `integrations/`. CI enforces this.

The test: **deleting `integrations/` must leave a complete, coherent, useful project.**

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

```bash
pip install -r requirements-dev.txt      # once

python3 tools/validate_knowledge.py      # frontmatter + referential integrity
python3 tools/check_neutrality.py        # no vendor names outside integrations/
python3 tools/check_stdlib_only.py       # no third-party imports in calculators/
python3 -m pytest calculators/tests      # calculator unit and property tests
```

## Code of conduct

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Licence

Contributions are licensed under [Apache-2.0](LICENSE). See [NOTICE](NOTICE) for trademark terms,
which are separate.
