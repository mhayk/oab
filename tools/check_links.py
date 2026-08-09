#!/usr/bin/env python3
"""Verify that every relative link and image path in the repository's Markdown resolves.

Broken internal links are the most common documentation defect and the cheapest to catch.
External URLs are not fetched: network checks make CI flaky and slow, and a 404 on someone
else's site is not something a pull request can fix.

Usage:
    python3 tools/check_links.py [root]

Exit code is 1 if any link is broken.
"""

import re
import sys
from pathlib import Path

# [text](target) and ![alt](target), ignoring reference-style and autolinks.
LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", ".astro"}
SKIP_SCHEMES = ("http://", "https://", "mailto:", "tel:", "data:", "#")


def anchor_exists(path: Path, anchor: str) -> bool:
    """Check a #fragment against the GitHub-style slugs of the target file's headings."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return True  # not our business to validate binary or unreadable targets

    slugs = set()
    for line in text.splitlines():
        if not line.startswith("#"):
            continue
        heading = line.lstrip("#").strip()
        slug = heading.lower()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug).strip("-")
        if slug:
            slugs.add(slug)
    # Explicit HTML anchors, e.g. <a id="foo">
    slugs.update(re.findall(r'<a\s+(?:id|name)="([^"]+)"', text))
    return anchor.lower() in slugs


def check(root: Path) -> int:
    broken = []
    checked = 0

    for md in sorted(root.rglob("*.md")):
        if any(part in SKIP_DIRS for part in md.parts):
            continue
        try:
            content = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        # Strip fenced code blocks so example links are not treated as real ones.
        content = re.sub(r"```.*?```", "", content, flags=re.S)

        for target in LINK.findall(content):
            if target.startswith(SKIP_SCHEMES):
                continue
            checked += 1

            path_part, _, anchor = target.partition("#")
            if not path_part:
                continue

            resolved = (md.parent / path_part).resolve()
            if not resolved.exists():
                broken.append(f"{md.relative_to(root)}: missing target -> {target}")
                continue

            if anchor and resolved.suffix == ".md" and not anchor_exists(resolved, anchor):
                broken.append(f"{md.relative_to(root)}: missing anchor -> {target}")

    if broken:
        print(f"✗ {len(broken)} broken link(s) of {checked} checked:\n", file=sys.stderr)
        for item in broken:
            print(f"  {item}", file=sys.stderr)
        return 1

    print(f"✓ {checked} relative links resolve")
    return 0


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    sys.exit(check(root))
