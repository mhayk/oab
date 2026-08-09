"""Tests for the knowledge validator.

Each test builds a throwaway knowledge tree and asserts the validator's verdict. The point
is not coverage for its own sake: these tests defend the specific defects that would let the
knowledge base degrade quietly as contributions accumulate.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import validate_knowledge as vk  # noqa: E402


VALID = """---
id: cache-stampede
title: Cache Stampede
description: >-
  When a popular cache entry expires, concurrent requests all miss simultaneously and
  overwhelm the origin with duplicate work.
category: caching
subcategory: failure-modes
tags: [cache, thundering-herd]
maturity: stable
confidence: high
applies_at_stage: ["2", "3", "4", "5"]
complexity_cost: 1
trade_offs:
  - gains: "Bounded origin load when hot keys expire"
    costs: "Added coordination; a lock adds a failure mode of its own"
    when_worth_it: "Any cached item costing >100 ms to recompute and requested >10x/s"
failure_modes:
  - mode: "Synchronised expiry across many keys"
    symptom: "Periodic origin load spikes matching the TTL interval"
    detection: "Origin request rate showing periodicity at the TTL boundary"
    mitigation: "Randomised TTL jitter of plus or minus 10 to 20 percent"
references:
  - title: "Optimal Probabilistic Cache Stampede Prevention"
    type: paper
    accessed: 2026-08-09
last_reviewed: 2026-08-09
---

## What it is

A cache stampede happens when a frequently-requested entry expires and many concurrent
requests miss at the same instant.

## When it applies

When a single key exceeds roughly 10 requests per second and recomputation costs more
than about 100 ms.

## When it does not apply

Low-traffic systems. At one request per second for a key, a stampede is two duplicate
queries. Also does not apply where the cache already serves stale content while
revalidating, because the pattern is prevented by construction.

## Trade-offs

Coordination costs complexity.

## Failure modes

Synchronised expiry.

## References

Summarised from the cited paper.
"""


def write(tmp_path, name, content, category="caching"):
    directory = tmp_path / "knowledge" / category
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_text(content)
    return tmp_path / "knowledge"


def test_accepts_a_well_formed_unit(tmp_path, capsys):
    knowledge = write(tmp_path, "cache-stampede.md", VALID)
    assert vk.main(knowledge_dir=knowledge) == 0


def test_empty_tree_is_not_an_error(tmp_path):
    (tmp_path / "knowledge").mkdir()
    assert vk.main(knowledge_dir=tmp_path / "knowledge") == 0


@pytest.mark.parametrize(
    "field",
    ["id", "title", "description", "category", "maturity", "confidence",
     "applies_at_stage", "trade_offs", "failure_modes", "complexity_cost",
     "references", "last_reviewed"],
)
def test_rejects_missing_required_field(tmp_path, field, capsys):
    """Every required field must actually be enforced, not merely documented."""
    lines, skip = [], False
    for line in VALID.splitlines(keepends=True):
        if line.startswith(f"{field}:"):
            skip = True
            continue
        if skip:
            # Continuation lines of a multi-line value are indented or list items. The
            # closing --- also starts with '-', so match it before the list-item check.
            if line.strip() != "---" and line.startswith((" ", "-", "\t")):
                continue
            skip = False
        lines.append(line)
    knowledge = write(tmp_path, "unit.md", "".join(lines))
    assert vk.main(knowledge_dir=knowledge) == 1


def test_rejects_dangling_related_id(tmp_path, capsys):
    content = VALID.replace(
        "tags: [cache, thundering-herd]",
        "tags: [cache]\nrelated: [does-not-exist]",
    )
    knowledge = write(tmp_path, "unit.md", content)
    assert vk.main(knowledge_dir=knowledge) == 1
    assert "unknown id 'does-not-exist'" in capsys.readouterr().err


def test_rejects_prerequisites_cycle(tmp_path, capsys):
    a = VALID.replace("id: cache-stampede", "id: alpha").replace(
        "tags: [cache, thundering-herd]", "prerequisites: [beta]"
    )
    b = VALID.replace("id: cache-stampede", "id: beta").replace(
        "tags: [cache, thundering-herd]", "prerequisites: [alpha]"
    )
    write(tmp_path, "alpha.md", a)
    knowledge = write(tmp_path, "beta.md", b)
    assert vk.main(knowledge_dir=knowledge) == 1
    assert "cycle" in capsys.readouterr().err


def test_rejects_empty_references(tmp_path, capsys):
    content = VALID.replace(
        '''references:
  - title: "Optimal Probabilistic Cache Stampede Prevention"
    type: paper
    accessed: 2026-08-09''',
        "references: []",
    )
    knowledge = write(tmp_path, "unit.md", content)
    assert vk.main(knowledge_dir=knowledge) == 1


def test_rejects_category_that_does_not_match_directory(tmp_path, capsys):
    knowledge = write(tmp_path, "unit.md", VALID, category="databases")
    assert vk.main(knowledge_dir=knowledge) == 1
    assert "does not match directory" in capsys.readouterr().err


def test_rejects_duplicate_id(tmp_path, capsys):
    write(tmp_path, "one.md", VALID)
    knowledge = write(tmp_path, "two.md", VALID)
    assert vk.main(knowledge_dir=knowledge) == 1
    assert "already used by" in capsys.readouterr().err


def test_rejects_missing_body_section(tmp_path, capsys):
    content = VALID.replace("## When it does not apply", "## Something else")
    knowledge = write(tmp_path, "unit.md", content)
    assert vk.main(knowledge_dir=knowledge) == 1
    assert "When it does not apply" in capsys.readouterr().err


def test_rejects_near_empty_when_it_does_not_apply(tmp_path, capsys):
    """The section existing is not enough — it is the section that prevents overengineering."""
    content = VALID.replace(
        """## When it does not apply

Low-traffic systems. At one request per second for a key, a stampede is two duplicate
queries. Also does not apply where the cache already serves stale content while
revalidating, because the pattern is prevented by construction.""",
        """## When it does not apply

N/A.""",
    )
    knowledge = write(tmp_path, "unit.md", content)
    assert vk.main(knowledge_dir=knowledge) == 1
    assert "load-bearing" in capsys.readouterr().err


def test_warns_on_stale_review_date(tmp_path, capsys):
    content = VALID.replace("last_reviewed: 2026-08-09", "last_reviewed: 2020-01-01")
    knowledge = write(tmp_path, "unit.md", content)
    assert vk.main(knowledge_dir=knowledge) == 0          # warning only
    assert "over 18 months ago" in capsys.readouterr().err
    assert vk.main(strict=True, knowledge_dir=knowledge) == 1  # ...unless strict


def test_rejects_invalid_stage(tmp_path, capsys):
    content = VALID.replace('applies_at_stage: ["2", "3", "4", "5"]', 'applies_at_stage: ["9"]')
    knowledge = write(tmp_path, "unit.md", content)
    assert vk.main(knowledge_dir=knowledge) == 1


def test_rejects_unknown_frontmatter_field(tmp_path, capsys):
    """additionalProperties is false so a typo cannot silently do nothing."""
    content = VALID.replace("maturity: stable", "maturty: stable\nmaturity: stable")
    knowledge = write(tmp_path, "unit.md", content)
    assert vk.main(knowledge_dir=knowledge) == 1
