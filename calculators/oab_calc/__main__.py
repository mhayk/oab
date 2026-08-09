"""Command-line entry point for the OAB calculators.

    python3 -m oab_calc <calculator> [--key=value ...] [--json]
    python3 -m oab_calc --list

Emits the human-readable envelope by default, or JSON conforming to
schemas/capacity-result.schema.json with --json.

Run from the calculators/ directory, or with PYTHONPATH pointing at it.
"""

import argparse
import json
import sys

from . import bandwidth, cache, concurrency, connections, cost, queue, rps, storage

# Each entry: module, one-line summary, and the question it answers. The question is
# what an agent matches against when deciding which calculator to reach for.
CALCULATORS = {
    "rps": (rps, "Average and peak requests per second",
            "Is this actually high traffic?"),
    "storage": (storage, "Storage growth per day and per year",
                "When do we outgrow the disk or the plan?"),
    "bandwidth": (bandwidth, "Bandwidth and monthly egress",
                  "What does egress cost, and is it the biggest line?"),
    "concurrency": (concurrency, "Concurrent operations via Little's Law",
                    "How many in-flight requests, workers, or connections?"),
    "connections": (connections, "Database connection pool sizing",
                    "Will we exhaust the database, and do we need a pooler?"),
    "cache": (cache, "Cache working set and load relieved",
              "Does the cache fit, and what does it actually save?"),
    "queue": (queue, "Worker count and backlog drain time",
              "How many workers, and how long to recover from a spike?"),
    "cost": (cost, "Monthly infrastructure and operational cost",
             "What is the bill, and where does it concentrate?"),
}


def parse_value(raw: str):
    """Coerce a CLI string to the narrowest sensible type."""
    lowered = raw.lower()
    if lowered in ("true", "yes", "on"):
        return True
    if lowered in ("false", "no", "off"):
        return False
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        return raw


def list_calculators():
    width = max(len(name) for name in CALCULATORS)
    print("OAB calculators\n")
    for name, (_, summary, question) in CALCULATORS.items():
        print(f"  {name.ljust(width)}  {summary}")
        print(f"  {' ' * width}  → {question}\n")
    print("Run `python3 -m oab_calc <name> --help` for a calculator's inputs.")
    print("Formulas are documented in prose in calculators/README.md, which is the")
    print("fallback when this cannot be run.")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    if not argv or argv[0] in ("--list", "-l", "--help", "-h"):
        list_calculators()
        return 0

    name = argv.pop(0)
    if name not in CALCULATORS:
        print(f"unknown calculator: {name!r}\n", file=sys.stderr)
        list_calculators()
        return 2

    module = CALCULATORS[name][0]

    parser = argparse.ArgumentParser(
        prog=f"python3 -m oab_calc {name}",
        description=CALCULATORS[name][1],
        epilog=CALCULATORS[name][2],
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    module.add_arguments(parser)

    args = parser.parse_args(argv)
    kwargs = {k: v for k, v in vars(args).items() if k != "json" and v is not None}

    try:
        result = module.calculate(**kwargs)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(result.to_text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
