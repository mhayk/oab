#!/usr/bin/env python3
"""Validate OAB artifact fixtures against their JSON Schemas — in both directions.

Every schema in schemas/ may have a fixture directory at schemas/fixtures/<schema-stem>/
containing:

    valid-*.json      MUST validate. These are the worked examples from the design
                      documents, so a schema change that breaks a documented example
                      fails CI rather than silently invalidating the docs.
    invalid-*.json    MUST NOT validate. A schema that accepts everything is not a
                      contract, and the usual way that happens is a required field
                      quietly dropped. Negative fixtures catch that.

Also usable on real output:

    python3 tools/validate_artifacts.py                       # check all fixtures
    python3 tools/validate_artifacts.py .oab/design.json      # check one artifact

Exit code is 1 on any failure.
"""

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from referencing import Registry, Resource
except ImportError:
    sys.exit(
        "missing dev dependencies. Install them with:\n"
        "    pip install -r requirements-dev.txt"
    )

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas"
FIXTURES = SCHEMAS / "fixtures"


def load_registry():
    """Build a registry of every local schema so cross-schema $refs resolve offline."""
    registry = Registry()
    for path in sorted(SCHEMAS.glob("*.schema.json")):
        schema = json.loads(path.read_text())
        if "$id" in schema:
            registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    return registry


def validator_for(schema_path, registry):
    schema = json.loads(schema_path.read_text())
    return Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())


def describe(errors):
    for err in errors:
        loc = ".".join(str(p) for p in err.path) or "(root)"
        yield f"{loc}: {err.message}"


def check_fixtures():
    registry = load_registry()
    failures, checked = [], 0

    for schema_path in sorted(SCHEMAS.glob("*.schema.json")):
        stem = schema_path.name.replace(".schema.json", "")
        directory = FIXTURES / stem
        if not directory.exists():
            continue
        validator = validator_for(schema_path, registry)

        for fixture in sorted(directory.glob("valid-*.json")):
            checked += 1
            errors = sorted(validator.iter_errors(json.loads(fixture.read_text())),
                            key=lambda e: e.path)
            if errors:
                rel = fixture.relative_to(ROOT)
                for message in describe(errors):
                    failures.append(f"{rel}: should be VALID but {message}")

        for fixture in sorted(directory.glob("invalid-*.json")):
            checked += 1
            data = json.loads(fixture.read_text())
            if validator.is_valid(data):
                rel = fixture.relative_to(ROOT)
                failures.append(
                    f"{rel}: should be INVALID but the schema accepted it — "
                    f"the constraint this fixture guards has been lost"
                )

    return failures, checked


def check_file(target: Path):
    """Validate one artifact, choosing the schema from its filename."""
    registry = load_registry()
    mapping = {
        "design.json": "design-output",
        "review.json": "review-output",
        "capacity.json": "capacity-result",
    }
    stem = mapping.get(target.name)
    if not stem:
        return [f"{target}: no schema mapped for this filename"], 1

    schema_path = SCHEMAS / f"{stem}.schema.json"
    if not schema_path.exists():
        return [f"{target}: schema {schema_path.name} does not exist yet"], 1

    validator = validator_for(schema_path, registry)
    errors = sorted(validator.iter_errors(json.loads(target.read_text())), key=lambda e: e.path)
    return [f"{target}: {m}" for m in describe(errors)], 1


def main(argv):
    if argv:
        failures, checked = check_file(Path(argv[0]))
    else:
        failures, checked = check_fixtures()

    if failures:
        print(f"✗ {len(failures)} schema failure(s):\n", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1

    if checked == 0:
        print("no artifact fixtures yet — nothing to validate")
        return 0

    print(f"✓ {checked} fixture(s) validate as expected")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
