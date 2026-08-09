# Live review — linkding, 2026-08-09

The first real `/oab:review` of a third-party repository: [sissbruecker/linkding](https://github.com/sissbruecker/linkding)
at commit `0f72293`, run headless with the plugin via `--plugin-dir` and the artifact hook active.
Both files are unedited output.

linkding was chosen **because it is the trap**: a small, correct, self-hosted Django app with
SQLite as the default datastore and a single-container deploy. A reviewer pattern-matching against
large-scale practice fails here loudly — "SQLite is not production-ready", "single instance is a
SPOF", "no HA". The release criterion was zero scale-inappropriate findings.

## Verification performed (release condition 3 of [#43](https://github.com/mhayk/oab/issues/43))

**Every finding read; every evidence citation checked against the code. 8 of 8 match**, including
the citation of the *correct* pattern elsewhere in the same codebase (`website_loader.py:102`,
`timeout=10`) used to argue the fix.

**Zero anti-rule violations.** No orchestration, multi-region, microservice, HA or SPOF findings.
SQLite is *praised* as the correct choice, WAL noted. The verdict's first sentence is that the
architecture is appropriate.

**Severity is proportionate.** 0 CRITICAL, 0 HIGH, 1 MEDIUM, 2 LOW, 2 INFORMATIONAL — and the one
MEDIUM is the scale-independent class the framework refuses to discount: two outbound HTTP calls
with no timeout (`favicon_loader.py:73`, `preview_image_loader.py:38`) on a 2-thread background
pool, so two hung connections silently halt all background work. The remedy is two one-line
changes matching the codebase's own pattern. A finding worth reporting upstream.

**The review can say no.** F-002 (synchronous scrape) and F-003 (SSRF surface) both conclude
"no change needed now" for the actual deployment model, each with a measurable trigger for when
that changes. F-005 checked `bootstrap.sh` before judging the committed dev SECRET_KEY and
downgraded it to INFORMATIONAL because deployed instances never use it — receipts-checking, not
pattern-matching.

**Context honesty.** The run noticed the shallow clone (one commit, one author visible) and
reduced its confidence in the team-size estimate accordingly.

## Known gap

`summary.complexity` is null in the artifact while the prose discusses the complexity spend. The
schema permits null, so the hook stayed silent. If complexity scoring should be mandatory in
reviews, that is a schema tightening for M2 — noted, not hidden.
