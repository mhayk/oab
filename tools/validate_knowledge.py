#!/usr/bin/env python3
"""Validate every knowledge unit: frontmatter schema, referential integrity, body structure.

Checks performed:

  schema        frontmatter conforms to schemas/knowledge-unit.schema.json
  category      frontmatter category matches the directory the file lives in
  ids           ids are unique repo-wide, including aliases
  references    related / prerequisites / supersedes / superseded_by all resolve
  cycles        prerequisites form no cycle
  orphans       every unit has at least one inbound or outbound edge (warning)
  body          the mandatory heading skeleton is present, including
                "## When it does not apply" — the section that prevents a knowledge
                base from becoming a machine for producing overengineering
  staleness     last_reviewed within 18 months (warning)

Dev dependencies: PyYAML, jsonschema. These are CI and contributor tools, not runtime;
calculators/ remains standard-library only and is checked separately by check_stdlib_only.py.

    pip install -r requirements-dev.txt
    python3 tools/validate_knowledge.py [--strict] [--knowledge DIR]

--strict turns warnings into failures. --knowledge points at an alternative tree, used by
the test suite. Exit code is 1 on any error.
"""

import sys
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    sys.exit(
        "missing dev dependencies. Install them with:\n"
        "    pip install -r requirements-dev.txt"
    )

import json

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE = ROOT / "knowledge"
SCHEMA = ROOT / "schemas" / "knowledge-unit.schema.json"

REQUIRED_HEADINGS = [
    "## What it is",
    "## When it applies",
    "## When it does not apply",
    "## Trade-offs",
    "## Failure modes",
    "## References",
]

STALE_AFTER = timedelta(days=548)  # ~18 months


def split_frontmatter(text, path, errors):
    """Return the parsed YAML frontmatter and the remaining body."""
    if not text.startswith("---"):
        errors.append(f"{path}: no YAML frontmatter (file must start with ---)")
        return None, ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        errors.append(f"{path}: frontmatter is not terminated by a closing ---")
        return None, ""
    try:
        return yaml.safe_load(parts[1]) or {}, parts[2]
    except yaml.YAMLError as exc:
        errors.append(f"{path}: invalid YAML in frontmatter: {exc}")
        return None, ""


def collect(knowledge_dir):
    """Load every knowledge unit. Returns (units, errors) where units maps path -> (meta, body)."""
    units, errors = {}, []
    if not knowledge_dir.exists():
        return units, errors

    for md in sorted(knowledge_dir.rglob("*.md")):
        # README.md files are generated domain indexes, not knowledge units.
        if md.name == "README.md":
            continue
        rel = md.relative_to(knowledge_dir.parent)
        meta, body = split_frontmatter(md.read_text(encoding="utf-8"), rel, errors)
        if meta is not None:
            units[rel] = (meta, body)
    return units, errors


def to_json_types(value):
    """Convert YAML-native types to their JSON equivalents for schema validation.

    YAML parses an unquoted ISO date into a datetime.date; JSON has no date type, so the
    schema declares those fields as strings with format: date. Normalising here keeps the
    frontmatter natural to write (no quotes needed around dates) while still validating the
    format properly.
    """
    if isinstance(value, dict):
        return {k: to_json_types(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_json_types(v) for v in value]
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def parse_date(value):
    """Accept either a YAML date or an ISO string; return a date or None."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def check_cycles(graph):
    """Return a list of cycles found in a mapping of id -> [prerequisite ids]."""
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {node: WHITE for node in graph}
    cycles = []

    def visit(node, stack):
        colour[node] = GREY
        for nxt in graph.get(node, []):
            if nxt not in colour:
                continue
            if colour[nxt] == GREY:
                cycles.append(" -> ".join(stack[stack.index(nxt):] + [nxt]))
            elif colour[nxt] == WHITE:
                visit(nxt, stack + [nxt])
        colour[node] = BLACK

    for node in list(graph):
        if colour[node] == WHITE:
            visit(node, [node])
    return cycles


def main(strict=False, knowledge_dir=None):
    schema = json.loads(SCHEMA.read_text())
    # format_checker makes `format: date` and `format: uri` actually enforced rather than
    # annotation-only, which is the jsonschema default.
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    units, errors = collect(Path(knowledge_dir) if knowledge_dir else KNOWLEDGE)
    warnings = []

    if not units:
        # Errors are reported first: a tree whose only file failed to parse must not be
        # mistaken for an empty tree and silently pass.
        for error in errors:
            print(f"✗ {error}", file=sys.stderr)
        if errors:
            return 1
        print("no knowledge units yet — nothing to validate")
        return 0

    known_ids, prereqs, edges = {}, {}, {}

    for rel, (meta, body) in units.items():
        # --- schema ---------------------------------------------------------
        for err in sorted(validator.iter_errors(to_json_types(meta)), key=lambda e: e.path):
            loc = ".".join(str(p) for p in err.path) or "(root)"
            errors.append(f"{rel}: {loc}: {err.message}")

        uid = meta.get("id")
        if not uid:
            continue

        # --- id uniqueness --------------------------------------------------
        for name in [uid, *meta.get("aliases", [])]:
            if name in known_ids:
                errors.append(f"{rel}: id or alias '{name}' already used by {known_ids[name]}")
            known_ids[name] = rel

        # --- category matches directory -------------------------------------
        directory = rel.parts[1] if len(rel.parts) > 1 else ""
        if meta.get("category") and meta["category"] != directory:
            errors.append(
                f"{rel}: category '{meta['category']}' does not match directory '{directory}'"
            )

        prereqs[uid] = list(meta.get("prerequisites", []))
        linked = (
            list(meta.get("related", []))
            + prereqs[uid]
            + list(meta.get("supersedes", []))
            + ([meta["superseded_by"]] if meta.get("superseded_by") else [])
        )
        edges[uid] = linked

        # --- body skeleton --------------------------------------------------
        for heading in REQUIRED_HEADINGS:
            if heading not in body:
                errors.append(f"{rel}: body is missing the required section '{heading}'")

        # "When it does not apply" must actually say something.
        if "## When it does not apply" in body:
            section = body.split("## When it does not apply", 1)[1]
            section = section.split("\n## ", 1)[0].strip()
            if len(section) < 40:
                errors.append(
                    f"{rel}: '## When it does not apply' is empty or near-empty. This section is "
                    f"mandatory and load-bearing — it is what stops OAB recommending this concept "
                    f"to systems that do not need it."
                )

        # --- staleness ------------------------------------------------------
        reviewed = parse_date(meta.get("last_reviewed"))
        if reviewed and date.today() - reviewed > STALE_AFTER:
            warnings.append(f"{rel}: last_reviewed is {reviewed}, over 18 months ago")

    # --- referential integrity ---------------------------------------------
    for uid, targets in edges.items():
        for target in targets:
            if target not in known_ids:
                source = known_ids.get(uid, uid)
                errors.append(f"{source}: link to unknown id '{target}'")

    # --- cycles -------------------------------------------------------------
    for cycle in check_cycles(prereqs):
        errors.append(f"prerequisites cycle: {cycle}")

    # --- orphans ------------------------------------------------------------
    inbound = {t for targets in edges.values() for t in targets}
    for uid, targets in edges.items():
        if not targets and uid not in inbound:
            warnings.append(
                f"{known_ids.get(uid, uid)}: orphan — no inbound or outbound links. "
                f"Unreachable knowledge is knowledge an agent will never retrieve."
            )

    # --- report -------------------------------------------------------------
    for warning in warnings:
        print(f"⚠ {warning}", file=sys.stderr)
    for error in errors:
        print(f"✗ {error}", file=sys.stderr)

    if errors or (strict and warnings):
        print(
            f"\n{len(errors)} error(s), {len(warnings)} warning(s) across {len(units)} unit(s)",
            file=sys.stderr,
        )
        return 1

    print(f"✓ {len(units)} knowledge unit(s) valid ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    argv = sys.argv[1:]
    directory = None
    if "--knowledge" in argv:
        directory = argv[argv.index("--knowledge") + 1]
    sys.exit(main(strict="--strict" in argv, knowledge_dir=directory))
