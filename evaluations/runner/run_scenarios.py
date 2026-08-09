#!/usr/bin/env python3
"""Run OAB scenarios and report which assertions failed.

Two tiers, deliberately separated:

  Tier 1  Deterministic. Applies assertions to a committed baseline artifact per scenario.
          No model, no network, runs on every commit, blocking. This is what stops a
          framework or schema change silently invalidating a scenario's expectations.

  Tier 2  Model in the loop. Applies the same assertions to an artifact an agent actually
          produced. Needs a run against a real agent, so it is gated and skipped on forks
          rather than failing them — otherwise external contribution is impossible.

The assertions are identical in both tiers. Only the source of the artifact differs.

    python3 evaluations/runner/run_scenarios.py                    # Tier 1, all scenarios
    python3 evaluations/runner/run_scenarios.py --scenario 01-tiny-startup
    python3 evaluations/runner/run_scenarios.py --artifact .oab/design.json --scenario 01-tiny-startup

Exit code is 1 if any assertion fails.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from assertions import evaluate  # noqa: E402

try:
    import yaml
except ImportError:
    sys.exit("missing PyYAML. Install with: pip install -r requirements-dev.txt")

ROOT = Path(__file__).resolve().parent.parent.parent
SCENARIOS = ROOT / "evaluations" / "scenarios"
HOLDOUT = ROOT / "evaluations" / "holdout"


def load_scenario(directory):
    scenario = yaml.safe_load((directory / "scenario.yaml").read_text())
    assertions = yaml.safe_load((directory / "assertions.yaml").read_text())
    baseline = directory / "baseline.json"
    return scenario, assertions, baseline if baseline.exists() else None


def perturb(artifact, factor):
    """Scale the capacity figures in a copy of an artifact."""
    scaled = json.loads(json.dumps(artifact))
    capacity = scaled.get("capacity") or {}
    for key, value in list(capacity.items()):
        if isinstance(value, (int, float)):
            capacity[key] = value * factor
    return scaled


def bounds_capacity(assertions):
    """Whether a scenario constrains capacity numerically at all.

    Scenarios that assert on availability, findings, or cost rather than on capacity cannot
    be perturbed this way, and reporting them as insensitive would be a false alarm — which
    is worse than no check, because a noisy guard is one people learn to ignore.
    """
    return any(str(rule.get("field", "")).startswith("capacity.")
               and ("min" in rule or "max" in rule)
               for rule in assertions.get("numeric", []))


def perturbation_check(directory):
    """Scale capacity up AND down; the assertions must break in at least one direction.

    A framework that recognises a scenario's specific numbers rather than reasoning about
    magnitude passes the scenario and survives both perturbations. Scaling only upward is
    not enough: a scenario with a lower bound (a large-scale case) is unaffected by
    multiplication and would be reported as insensitive when it is not.

    Returns True (sensitive), False (insensitive), or None (not applicable).
    """
    scenario, assertions, baseline = load_scenario(directory)
    if baseline is None or not bounds_capacity(assertions):
        return None
    artifact = json.loads(baseline.read_text())
    return any(evaluate(perturb(artifact, factor), assertions) for factor in (100, 0.01))


def run_one(directory, artifact_path=None, verbose=False):
    scenario, assertions, baseline = load_scenario(directory)
    name = scenario.get("id", directory.name)

    source = Path(artifact_path) if artifact_path else baseline
    if source is None:
        print(f"  ~ {name}: no baseline artifact and none supplied — skipped")
        return None

    artifact = json.loads(Path(source).read_text())
    failures = evaluate(artifact, assertions)

    if failures:
        print(f"  ✗ {name}  ({len(failures)} failure(s))")
        for failure in failures:
            print(f"      {failure}")
        if scenario.get("guards"):
            print(f"      guards against: {scenario['guards']}")
        return False

    detail = f"  [{source.relative_to(ROOT)}]" if verbose else ""
    print(f"  ✓ {name}{detail}")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", help="run one scenario directory by name")
    parser.add_argument("--artifact", help="artifact to assert against instead of the baseline")
    parser.add_argument("--holdout", action="store_true",
                        help="also run held-out scenarios (release branches only)")
    parser.add_argument("--perturb", action="store_true",
                        help="verify assertions break when capacity magnitude changes")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    roots = [SCENARIOS] + ([HOLDOUT] if args.holdout and HOLDOUT.exists() else [])
    directories = []
    for root in roots:
        if not root.exists():
            continue
        directories += sorted(d for d in root.iterdir()
                              if d.is_dir() and (d / "scenario.yaml").exists())

    if args.scenario:
        directories = [d for d in directories if d.name == args.scenario]
        if not directories:
            sys.exit(f"no scenario named {args.scenario!r}")

    if not directories:
        print("no scenarios yet — nothing to run")
        return 0

    print(f"Running {len(directories)} scenario(s)\n")
    results = [run_one(d, args.artifact, args.verbose) for d in directories]

    perturbation_failures = []
    if args.perturb:
        print("\nPerturbation: capacity scaled 100x and 0.01x — assertions must break\n")
        for directory in directories:
            scenario, _, _ = load_scenario(directory)
            name = scenario.get("id", directory.name)
            verdict = perturbation_check(directory)
            if verdict is None:
                print(f"  ~ {name}: no numeric capacity bounds — not applicable")
            elif verdict:
                print(f"  ✓ {name}: correctly breaks when magnitude changes")
            else:
                perturbation_failures.append(name)
                print(f"  ✗ {name}: assertions survive a 100x and 0.01x change in capacity — "
                      f"they are not sensitive to magnitude")

    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    skipped = sum(1 for r in results if r is None)

    print(f"\n{passed} passed, {failed} failed, {skipped} skipped")
    if perturbation_failures:
        print(f"{len(perturbation_failures)} scenario(s) insensitive to magnitude")

    return 1 if failed or perturbation_failures else 0


if __name__ == "__main__":
    sys.exit(main())
