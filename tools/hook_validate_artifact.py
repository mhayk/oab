#!/usr/bin/env python3
"""PostToolUse hook: validate an OAB artifact the moment it is written.

Four live runs of /oab:design omitted `cost.within_budget` despite the field being required
by the framework, by the skill, ahead of the prose, and by the schema. Prompt-level
instruction does not reliably guarantee a field appears in an artifact — see issue #44.

This is the mechanism rather than more words. It reads the PostToolUse payload on stdin,
and when the written file is an OAB artifact it validates it and returns the specific
missing fields to the agent as `additionalContext`, which appears alongside the tool result.

Design constraints, in priority order:

1. **Never block a write.** A hook that errors must not stop the user working. Every failure
   path exits 0 with no output.
2. **Work with zero dependencies.** The critical contract checks are standard library, so the
   guarantee holds on a machine with nothing installed — the same promise the calculators
   make. Full schema validation runs additionally when jsonschema is present.
3. **Be specific.** "Invalid artifact" is not actionable. The message names each missing
   field and what it means.

Wired up in hooks/hooks.json.
"""

import json
import os
import sys

# Fields that carry a HARD STATED CONSTRAINT. Their absence is not a schema technicality:
# it means a constraint the user gave was not checked, or was checked only in prose where
# nothing can verify it. Kept in standard library so the check survives a bare machine.
CRITICAL = {
    "design.json": [
        (("cost", "stated_budget"),
         "the budget the user stated, or null if none was — required so within_budget is checkable"),
        (("cost", "within_budget"),
         "false when the HIGH end of the estimate exceeds a stated budget"),
        (("complexity", "available"), "the team's complexity budget"),
        (("complexity", "spent"), "the complexity this design spends"),
        (("assumptions",), "every assumption, with a confidence — never empty"),
        (("options",), "at least two options, at least one rejected"),
        (("triggers",), "at least one measurable revisit condition"),
    ],
    "review.json": [
        (("context", "assumptions"),
         "the scale assumptions that produced the severities — never empty"),
        (("summary", "verdict"), "the verdict, stated plainly"),
    ],
}

EMPTY_IS_MISSING = {("assumptions",), ("options",), ("triggers",), ("context", "assumptions")}


def get(data, path):
    for key in path:
        if not isinstance(data, dict) or key not in data:
            return None, False
        data = data[key]
    return data, True


def critical_failures(artifact, name):
    failures = []
    for path, meaning in CRITICAL.get(name, []):
        value, present = get(artifact, path)
        label = ".".join(path)
        if not present:
            failures.append(f"`{label}` is missing — {meaning}")
        elif path in EMPTY_IS_MISSING and not value:
            failures.append(f"`{label}` is empty — {meaning}")
    return failures


def schema_failures(artifact, name):
    """Full schema validation. Additive: absence of jsonschema is not a failure."""
    try:
        from jsonschema import Draft202012Validator, FormatChecker
        from referencing import Registry, Resource
    except ImportError:
        return []

    root = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))
    schemas = os.path.join(root, "schemas")
    stem = {"design.json": "design-output", "review.json": "review-output",
            "capacity.json": "capacity-result"}.get(name)
    target = os.path.join(schemas, f"{stem}.schema.json")
    if not stem or not os.path.exists(target):
        return []

    try:
        registry = Registry()
        for entry in os.listdir(schemas):
            if entry.endswith(".schema.json"):
                with open(os.path.join(schemas, entry)) as fh:
                    loaded = json.load(fh)
                if "$id" in loaded:
                    registry = registry.with_resource(loaded["$id"],
                                                      Resource.from_contents(loaded))
        with open(target) as fh:
            schema = json.load(fh)
        validator = Draft202012Validator(schema, registry=registry,
                                         format_checker=FormatChecker())
        out = []
        for err in sorted(validator.iter_errors(artifact), key=lambda e: list(e.path))[:8]:
            where = ".".join(str(p) for p in err.path) or "(root)"
            out.append(f"`{where}`: {err.message}")
        return out
    except Exception:
        return []


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # malformed payload is not the user's problem

    path = (payload.get("tool_input") or {}).get("file_path") or ""
    name = os.path.basename(path)

    # Only OAB artifacts, and only inside a .oab directory, so a file merely named
    # design.json elsewhere is left alone.
    if name not in CRITICAL or os.path.basename(os.path.dirname(path)) != ".oab":
        return 0

    try:
        with open(path) as fh:
            artifact = json.load(fh)
    except json.JSONDecodeError as exc:
        emit(f"`{name}` is not valid JSON: {exc}. Rewrite it before continuing.")
        return 0
    except OSError:
        return 0

    failures = critical_failures(artifact, name)
    extra = [f for f in schema_failures(artifact, name)
             if not any(f.split("`")[1] in c for c in failures)]

    if not failures and not extra:
        return 0

    lines = [f"The OAB artifact `{name}` you just wrote does not satisfy its output contract.",
             ""]
    if failures:
        lines.append("**Required fields missing or empty:**")
        lines += [f"- {f}" for f in failures]
        lines.append("")
    if extra:
        lines.append("**Schema errors:**")
        lines += [f"- {f}" for f in extra]
        lines.append("")
    lines.append(
        "Fix the artifact now, before writing any prose. A field that is absent cannot be "
        "checked by anyone — reasoning about a constraint in prose is not the same as "
        "recording whether it was met."
    )
    emit("\n".join(lines))
    return 0


def emit(message):
    print("oab hook_validate_artifact: contract violations found, feeding back to the agent",
          file=sys.stderr)
    json.dump({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": message,
        },
        "suppressOutput": True,
    }, sys.stdout)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # A hook must never break the session it is trying to help — but a silent
        # failure is indistinguishable from a pass, which made issue #44 undiagnosable.
        # stderr is logged by the harness and never reaches the model, so this is free.
        import traceback
        print("oab hook_validate_artifact crashed:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(0)
