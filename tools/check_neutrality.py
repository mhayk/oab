#!/usr/bin/env python3
"""Fail if an AI vendor or model name appears in OAB's client-agnostic core.

OAB's central structural claim is that its first client is a client, not the platform.
That claim decays into marketing unless something enforces it, so this check is the
mechanical form of the deletion test:

    Deleting integrations/ must leave a complete, coherent, useful project.

SCOPE. The rule applies to the core — knowledge, reasoning procedures, arithmetic,
contracts, output shapes, and the evaluation suite. It deliberately does NOT apply to
project documentation: a README that cannot say which agents OAB works with is not
neutral, it is unhelpful. Naming supported clients in ROADMAP, CHANGELOG, or the website
is normal and expected.

Naming a *cloud provider* or *database product* as factual comparative data inside a
knowledge unit is also fine. This check is about AI agent vendors and models, which are
the ones that would couple the core to a single client.

ESCAPE HATCH. A line containing `neutrality-ok` is skipped. Use it sparingly and with a
reason, so every exemption is visible in review:

    # neutrality-ok: this list is the check's own subject matter

    python3 tools/check_neutrality.py

Exit code is 1 on any violation.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The client-agnostic core. Everything outside this is out of scope by design.
GUARDED_DIRS = [
    "knowledge",
    "frameworks",
    "calculators",
    "schemas",
    "templates",
    "evaluations",
]

# Unambiguous product and vendor names: matched case-insensitively.
UNAMBIGUOUS = [
    "claude", "anthropic", "openai", "chatgpt", "copilot", "gemini", "ollama",
    "gpt-3", "gpt-4", "gpt-5", "github copilot",
]

# Names that are also ordinary English or common identifiers. Matched case-SENSITIVELY on
# the capitalised form, so a `cursor` variable or the word "opus" in prose does not trip
# the check while the product name still does. Getting this wrong in the noisy direction
# would train contributors to ignore the guard.
AMBIGUOUS = ["Cursor", "Codex", "Sonnet", "Opus", "Haiku", "Llama", "Mistral"]

SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2",
                 ".ttf", ".otf", ".zip", ".pdf", ".webp"}

ESCAPE = "neutrality-ok"

PATTERN_ANY = re.compile(r"\b(" + "|".join(re.escape(t) for t in UNAMBIGUOUS) + r")\b", re.I)
PATTERN_CAP = re.compile(r"\b(" + "|".join(re.escape(t) for t in AMBIGUOUS) + r")\b")


def main() -> int:
    violations = []
    scanned = 0

    for directory in GUARDED_DIRS:
        base = ROOT / directory
        if not base.exists():
            continue

        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() in SKIP_SUFFIXES:
                continue
            rel = path.relative_to(ROOT)
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            scanned += 1

            for lineno, line in enumerate(text.splitlines(), 1):
                if ESCAPE in line:
                    continue
                for pattern in (PATTERN_ANY, PATTERN_CAP):
                    for match in pattern.finditer(line):
                        violations.append((rel, lineno, match.group(0), line.strip()[:100]))

    if violations:
        print(
            f"✗ {len(violations)} vendor reference(s) in the client-agnostic core.\n"
            f"  Knowledge and reasoning must work for any agent. Move the client-specific "
            f"part into integrations/, or rewrite it generically (\"the agent\", \"the "
            f"client\"). If the reference is genuinely necessary, add `{ESCAPE}` to the "
            f"line with a reason.\n",
            file=sys.stderr,
        )
        for rel, lineno, term, line in violations:
            print(f"  {rel}:{lineno}: '{term}' — {line}", file=sys.stderr)
        return 1

    guarded = ", ".join(d for d in GUARDED_DIRS if (ROOT / d).exists()) or "none yet"
    print(f"✓ core is client-agnostic ({scanned} files scanned in: {guarded})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
