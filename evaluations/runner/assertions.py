"""Assertion primitives for OAB scenario evaluation.

Assertions operate on **artifact fields**, never on prose. That is the anti-gaming property:
a framework can be tuned to produce the right words far more easily than the right structure,
and a scenario suite that checks strings teaches contributors to write for the checker.

Field paths use dots and support `[*]` to project over a list:

    capacity.peak_rps
    options[*].verdict
    components[*].kind

Standard library only; the runner is a dev tool but shares the calculators' discipline.
"""

from numbers import Number

MISSING = object()


def resolve(data, path):
    """Resolve a dotted path, returning a list when the path projects over a list.

    Returns MISSING when any segment is absent, which assertions distinguish from a
    present-but-empty value — "the field is not there" and "the field is empty" are
    different failures.
    """
    current = data
    for segment in path.split("."):
        projecting = segment.endswith("[*]")
        key = segment[:-3] if projecting else segment

        if isinstance(current, list):
            collected = []
            for item in current:
                value = item.get(key, MISSING) if isinstance(item, dict) else MISSING
                if value is not MISSING:
                    collected.extend(value if projecting and isinstance(value, list) else [value])
            current = collected
            continue

        if not isinstance(current, dict) or key not in current:
            return MISSING
        current = current[key]
        if projecting:
            if not isinstance(current, list):
                return MISSING
    return current


def as_list(value):
    if value is MISSING:
        return []
    return value if isinstance(value, list) else [value]


# --------------------------------------------------------------------------- components

def component_kinds(artifact):
    """The set of component KINDS present.

    Matching is exact against `kind`, never a substring and never against `name`. Names are
    free text: "CDN / edge cache" contains "cache" but a CDN is not the cache component a
    scenario forbids. Substring matching produced exactly that false positive, which is why
    the schema constrains `kind` to a closed enum in the first place.
    """
    return {str(k).lower() for k in as_list(resolve(artifact, "components[*].kind"))}


def must_not_include_components(artifact, kinds):
    """The overengineering guard. Checks the components list, not the prose."""
    present = component_kinds(artifact)
    return [
        f"component kind '{kind}' is present but this scenario forbids it "
        f"(kinds present: {sorted(present)})"
        for kind in kinds
        if str(kind).lower() in present
    ]


def must_include_components(artifact, kinds):
    present = component_kinds(artifact)
    return [
        f"component kind '{kind}' is required but absent (kinds present: {sorted(present)})"
        for kind in kinds
        if str(kind).lower() not in present
    ]


def must_reject_components(artifact, kinds):
    """A rejection must be recorded explicitly, with the measurement that reverses it.

    Silently omitting a component is not the same as considering and refusing it: only the
    second gives the reader something to disagree with.
    """
    rejected = {str(k).lower() for k in as_list(resolve(artifact, "rejected_components[*].kind"))}
    failures = []
    for kind in kinds:
        if str(kind).lower() not in rejected:
            failures.append(
                f"component kind '{kind}' should be explicitly rejected, but is not listed "
                f"(rejected: {sorted(rejected)})"
            )
    for entry in as_list(resolve(artifact, "rejected_components")):
        if isinstance(entry, dict) and not entry.get("revisit_when"):
            failures.append(
                f"rejected component '{entry.get('kind')}' has no revisit_when — a rejection "
                f"without the measurement that reverses it is an opinion"
            )
    return failures


# ------------------------------------------------------------------------------ numeric

def numeric(artifact, rule):
    field = rule["field"]
    value = resolve(artifact, field)
    if value is MISSING or value is None:
        if rule.get("optional"):
            return []
        return [f"{field} is missing"]
    if not isinstance(value, Number):
        return [f"{field} is {value!r}, not a number"]

    failures = []
    if "max" in rule and value > rule["max"]:
        failures.append(f"{field} is {value}, above the maximum {rule['max']}")
    if "min" in rule and value < rule["min"]:
        failures.append(f"{field} is {value}, below the minimum {rule['min']}")
    if "lte_field" in rule:
        other = resolve(artifact, rule["lte_field"])
        if isinstance(other, Number) and value > other:
            failures.append(
                f"{field} is {value}, above {rule['lte_field']} ({other})"
            )
    if "gte_field" in rule:
        other = resolve(artifact, rule["gte_field"])
        if isinstance(other, Number) and value < other:
            failures.append(f"{field} is {value}, below {rule['gte_field']} ({other})")
    return failures


# --------------------------------------------------------------------------- structural

def structural(artifact, rule):
    field = rule["field"]
    value = resolve(artifact, field)

    if "exists" in rule:
        present = value is not MISSING and value is not None
        if present != rule["exists"]:
            return [f"{field} " + ("is missing" if rule["exists"] else "should be absent")]
        return []

    if value is MISSING:
        return [f"{field} is missing"]

    failures = []
    if "min_length" in rule and len(as_list(value)) < rule["min_length"]:
        failures.append(
            f"{field} has {len(as_list(value))} item(s), fewer than the required "
            f"{rule['min_length']}"
        )
    if "max_length" in rule and len(as_list(value)) > rule["max_length"]:
        failures.append(f"{field} has {len(as_list(value))} item(s), more than {rule['max_length']}")
    if "contains" in rule and rule["contains"] not in as_list(value):
        failures.append(f"{field} does not contain {rule['contains']!r} (got {as_list(value)})")
    if "not_contains" in rule and rule["not_contains"] in as_list(value):
        failures.append(f"{field} contains {rule['not_contains']!r} but should not")
    if "in" in rule and value not in rule["in"]:
        failures.append(f"{field} is {value!r}, not one of {rule['in']}")
    if "equals" in rule and value != rule["equals"]:
        failures.append(f"{field} is {value!r}, expected {rule['equals']!r}")
    return failures


def evaluate(artifact, assertions):
    """Apply every assertion, returning a flat list of human-readable failures."""
    failures = []
    failures += must_not_include_components(artifact, assertions.get("must_not_include_components", []))
    failures += must_include_components(artifact, assertions.get("must_include_components", []))
    failures += must_reject_components(artifact, assertions.get("must_reject_components", []))
    for rule in assertions.get("numeric", []):
        failures += numeric(artifact, rule)
    for rule in assertions.get("structural", []):
        failures += structural(artifact, rule)
    return failures
