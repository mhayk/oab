#!/usr/bin/env python3
"""Fail if calculators/ imports anything outside the Python standard library.

The calculators run on a user's machine, invoked by their agent. If they needed a pip
install, the promise that OAB works from a git clone with nothing installed would be
false — and the fallback path (the agent doing the arithmetic itself) is exactly the
silent-wrong-number failure mode the calculators exist to prevent.

This is a real risk, not a theoretical one: adding `import requests` to fetch live
pricing is a natural-looking change that would quietly break the guarantee.

tools/ and tests are exempt. They run in CI and on a contributor's machine, where
requirements-dev.txt is a reasonable ask.

    python3 tools/check_stdlib_only.py

Exit code is 1 on any violation.
"""

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUARDED = ROOT / "calculators"

# sys.stdlib_module_names exists from Python 3.10. Below that, fall back to a list
# covering what a calculator could plausibly need, so the check still runs on 3.9.
STDLIB = getattr(sys, "stdlib_module_names", None) or frozenset({
    "abc", "argparse", "collections", "dataclasses", "datetime", "decimal", "enum",
    "fractions", "functools", "io", "itertools", "json", "math", "os", "pathlib",
    "re", "statistics", "sys", "textwrap", "typing", "unittest", "warnings",
})


def top_level(name: str) -> str:
    return name.split(".", 1)[0]


def main() -> int:
    if not GUARDED.exists():
        print("calculators/ does not exist yet — nothing to check")
        return 0

    violations = []
    checked = 0

    for path in sorted(GUARDED.rglob("*.py")):
        rel = path.relative_to(ROOT)
        # The calculators' own test suite may use pytest.
        if "tests" in rel.parts:
            continue
        checked += 1
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(rel))
        except SyntaxError as exc:
            violations.append((rel, exc.lineno or 0, f"syntax error: {exc.msg}"))
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = top_level(alias.name)
                    if module not in STDLIB:
                        violations.append((rel, node.lineno, f"import {alias.name}"))
            elif isinstance(node, ast.ImportFrom):
                # level > 0 is a relative import within the package: always fine.
                if node.level == 0 and node.module:
                    module = top_level(node.module)
                    if module not in STDLIB:
                        violations.append((rel, node.lineno, f"from {node.module} import ..."))

    if violations:
        print(
            f"✗ {len(violations)} non-stdlib import(s) in calculators/.\n"
            f"  The calculators must run on a user's machine with nothing installed. "
            f"If you need this dependency, it belongs in tools/ instead — or the "
            f"capability belongs somewhere other than a calculator.\n",
            file=sys.stderr,
        )
        for rel, lineno, detail in violations:
            print(f"  {rel}:{lineno}: {detail}", file=sys.stderr)
        return 1

    print(f"✓ calculators/ is standard-library only ({checked} module(s) checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
