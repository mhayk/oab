## What and why

<!-- What changes, and what problem it solves. Link the issue: Closes #NN -->

## Type

- [ ] Knowledge unit (new or corrected)
- [ ] Framework / reasoning change
- [ ] Calculator or schema
- [ ] Integration
- [ ] Documentation
- [ ] Tooling / CI

## Checklist

- [ ] Commits are signed off (`git commit -s`) — see [DCO](https://developercertificate.org/)
- [ ] No AI vendor or model name added outside `integrations/`
- [ ] No new runtime dependency in `calculators/` or `tools/`
- [ ] Documentation updated in this pull request, if behaviour or a contract changed
- [ ] CI is green

### If this adds or changes a knowledge unit

- [ ] Frontmatter validates (`python3 tools/validate_knowledge.py`)
- [ ] Has a non-empty `## When it does not apply` section
- [ ] Claims are quantified, or explicitly marked as unquantified
- [ ] Sources attributed in `references`; **no verbatim copyrighted text**
- [ ] `applies_at_stage` is deliberate — a stage-4 concept must not surface in a stage-1 design

### If this changes how OAB reasons

- [ ] An evaluation scenario covers the change
- [ ] I have stated whether this guards against over- or under-engineering
