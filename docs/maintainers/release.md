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

## Version pinning — verified behaviour

`version` **pins** the plugin, and the cache is frozen **per version, not per commit**.

- `claude plugin marketplace update <name>` is what fetches new content — and only when `version`
  changed.
- `claude plugin install` reports *"already installed"* either way. That message is about
  enablement, not content, so it is not a signal that the update did or did not arrive.
- Verify by reading the cache, not the message:
  `grep <a-string-from-your-change> ~/.claude/plugins/cache/<mkt>/<plugin>/<version>/...`

Both failure modes were observed in one session. A fix pushed to `main` under an unchanged version
never reached the installed plugin; and 0.1.1, fetched between two commits, froze the earlier
content so a later fix under the same version never arrived either.

**Bump the version on every change that must reach users, and confirm against the cache.** A
release without a bump is a no-op, however green CI is.

To force a local refresh while developing, use `claude --plugin-dir ./` rather than the installed
copy.

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
