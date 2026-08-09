# Contributing architecture knowledge

> **Status: not yet written.**
> This guide lands with [issue #20](https://github.com/mhayk/oab/issues/20).
> Until then, the design documents below describe the intended shape.

Read in the meantime:

- [Knowledge representation and unit schema](../design/03-knowledge-system.md) — the format, the
  required frontmatter fields, and why Markdown with YAML frontmatter was chosen over a graph or
  vector database
- [A complete worked example](../design/09-specifications.md#39-knowledge-schema-example) — a full
  knowledge unit, frontmatter and body
- [The rules that apply to every contribution](../../CONTRIBUTING.md#rules-that-apply-to-every-contribution)

The two things reviewers will check hardest:

1. **`## When it does not apply` is non-empty.** A knowledge base that only says when to use things
   is a machine for producing overengineering.
2. **Claims are quantified.** "Use a cache when reads are high" is not a contribution.

