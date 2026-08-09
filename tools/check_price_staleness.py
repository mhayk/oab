#!/usr/bin/env python3
"""Fail when a price table has gone stale.

Prices rot faster than any other content in the knowledge base, and a stale number stated
confidently does more damage than no number: someone budgets on it.

Any Markdown file under knowledge/ containing a line matching `Checked: YYYY-MM-DD` is
treated as a price table.

    warn  after 6 months
    fail  after 12 months

    python3 tools/check_price_staleness.py [--strict]
"""

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE = ROOT / "knowledge"

CHECKED = re.compile(r"Checked:\s*(\d{4}-\d{2}-\d{2})")
WARN_DAYS = 183
FAIL_DAYS = 365


def main(strict=False):
    if not KNOWLEDGE.exists():
        print("no knowledge/ yet — nothing to check")
        return 0

    warnings, errors, found = [], [], 0
    today = date.today()

    for path in sorted(KNOWLEDGE.rglob("*.md")):
        match = CHECKED.search(path.read_text(encoding="utf-8"))
        if not match:
            continue
        found += 1
        rel = path.relative_to(ROOT)
        try:
            checked = date.fromisoformat(match.group(1))
        except ValueError:
            errors.append(f"{rel}: unparseable Checked date {match.group(1)!r}")
            continue

        age = (today - checked).days
        if age > FAIL_DAYS:
            errors.append(f"{rel}: prices checked {checked} ({age} days ago) — over 12 months")
        elif age > WARN_DAYS:
            warnings.append(f"{rel}: prices checked {checked} ({age} days ago) — over 6 months")

    for warning in warnings:
        print(f"⚠ {warning}", file=sys.stderr)
    for error in errors:
        print(f"✗ {error}", file=sys.stderr)

    if errors or (strict and warnings):
        return 1
    if found == 0:
        print("no price tables found")
        return 0
    print(f"✓ {found} price table(s) current ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main(strict="--strict" in sys.argv))
