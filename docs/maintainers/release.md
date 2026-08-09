# Release process

## Before tagging

```bash
python3 tools/validate_knowledge.py --strict
python3 tools/validate_artifacts.py
python3 tools/check_neutrality.py
python3 tools/check_stdlib_only.py
python3 tools/check_price_staleness.py --strict
python3 tools/check_links.py
python3 tools/build_index.py --check
python3 evaluations/runner/run_scenarios.py --perturb --holdout
cd calculators && python3 -m pytest tests -q && cd ..
python3 -m pytest tools/tests -q
npx --yes @anthropic-ai/claude-code plugin validate ./ --strict
```

Then, and this is the part that cannot be automated:

1. **Install on a clean machine.** `/plugin marketplace add mhayk/oab` →
   `/plugin install oab@oab`. Record install time and repository size against the ADR-0003
   revisit threshold (50 MB, 5 s).
2. **Run `/oab:design` on the tiny-startup scenario** and assert the real output with
   `run_scenarios.py --artifact`.
3. **Run `/oab:review` on a real third-party repository** and read every finding. Any
   scale-inappropriate finding blocks the release.

## Tagging

1. Bump `version` in `.claude-plugin/plugin.json` **and** the marketplace entry — they must match.
2. Move `CHANGELOG.md` `[Unreleased]` into a dated version section.
3. `git tag -a vX.Y.Z -m "..."` and push.
4. Create the GitHub release from the changelog section.

## Publish the numbers

Every release publishes the **scenario pass rate**, split into overengineering-guard and
underengineering-guard, in the README.

Publish the failures too. A project that claims architecture rigour and hides its own evaluation
results has failed its own review.

## Versioning

Semantic versioning, with one project-specific rule: **a framework change that materially changes
the architecture OAB recommends is a breaking change**, the same as a schema change. Behaviour is
the interface.
