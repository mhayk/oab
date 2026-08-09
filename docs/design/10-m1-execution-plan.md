# 10 — M1 Execution Plan

Covers §43 of the design brief.

---

## 43. Sequenced Implementation Plan

### 43.1 Principles for the issue breakdown

1. **One issue = one reviewable pull request.** If a PR would exceed ~400 lines of substantive
   change, the issue is too big.
2. **Contracts before consumers.** Schemas land before the things that emit them, so nothing is
   built against a moving target.
3. **Maximise parallelism after the contracts land.** Knowledge units and calculators are
   independent and are the natural entry point for new contributors.
4. **Each issue states its acceptance criteria as checkable facts**, not intentions.
5. **The riskiest unknown is de-risked first** — the plugin packaging spike (#28) runs early,
   because a negative result changes the integration approach and nothing else.

### 43.2 Waves and dependencies

```
Wave 0  Foundation        #1 #2 #3                     ── no dependencies
Wave 1  Contracts         #4 #5 #6 #7                  ── depends on Wave 0
        Guards            #8
        Spike             #28  ⚡ run in parallel with Wave 1 — de-risks the integration
Wave 2  Calculators       #9 → #10 #11 #12 #13         ── #10–13 parallel after #9
        Knowledge setup   #20                          ── depends on #4
Wave 3  Frameworks        #14 #15 #16 #17 #18 #19      ── #14–16 parallel; #17 #18 depend on #14 #16
        Knowledge         #21 #22 #23 #24 #25 #26      ── all parallel after #20
        Templates         #27
Wave 4  Integration       #29 → #30 #31 #32 #33 → #34 #35
Wave 5  Evaluation        #36 → #37 #38
Wave 6  Ship              #39 #40 #41 #42 #43
```

**Critical path:** `#1 → #4 → #20 → #21 → #17 → #35 → #37 → #43`
Everything else can be worked around it.

**Best parallel entry points for additional contributors:** the six knowledge issues (#21–#26) and
the four calculator issues (#10–#13). Both require reading one guide and nothing else.

### 43.3 The issues

All 43 issues exist in the tracker under the **M1 — First Milestone** milestone, numbered to match
this table: <https://github.com/mhayk/oab/issues>. Full acceptance criteria live there; this is the
map.

Labels: `area:*` (foundation, schemas, calculators, frameworks, knowledge, integration, evaluation,
docs, website) · `wave:0-foundation` … `wave:6-ship` · `parallel-safe` · `good first issue` · `spike`.

Summary:

| # | Title | Wave | Depends on | Parallel-safe |
| --: | :-- | :-: | :-- | :-: |
| 1 | Repository foundation files | 0 | — | ✅ |
| 2 | GitHub issue/PR templates and labels | 0 | — | ✅ |
| 3 | Base CI workflow | 0 | — | ✅ |
| 4 | Knowledge unit schema, template, and validator | 1 | #1 #3 | ✅ |
| 5 | Capacity result and reasoning trace schemas | 1 | #1 #3 | ✅ |
| 6 | ADR and evolution trigger schemas | 1 | #1 #3 | ✅ |
| 7 | Design, review, finding, and repo-facts schemas | 1 | #5 | |
| 8 | Vendor-neutrality and stdlib-only CI guards | 1 | #3 | ✅ |
| 9 | Calculator package skeleton, result envelope, CLI | 2 | #5 | |
| 10 | Calculators: RPS, storage growth, bandwidth | 2 | #9 | ✅ |
| 11 | Calculators: concurrency and connection pool | 2 | #9 | ✅ |
| 12 | Calculators: cache sizing and queue throughput | 2 | #9 | ✅ |
| 13 | Calculator: cost estimate with dated price table | 2 | #9 | ✅ |
| 14 | Framework: complexity budget + weights.yaml | 3 | #1 | ✅ |
| 15 | Framework: discovery | 3 | #1 | ✅ |
| 16 | Framework: capacity planning | 3 | #9 | ✅ |
| 17 | Framework: architecture design | 3 | #14 #15 #16 | |
| 18 | Framework: architecture review | 3 | #7 #14 | |
| 19 | Framework: evolution triggers | 3 | #6 | ✅ |
| 20 | Knowledge authoring guide and domain index generator | 2 | #4 | |
| 21 | Knowledge: fundamentals (6 units) | 3 | #20 | ✅ |
| 22 | Knowledge: databases (8 units) | 3 | #20 | ✅ |
| 23 | Knowledge: caching (5 units) | 3 | #20 | ✅ |
| 24 | Knowledge: messaging (7 units) | 3 | #20 | ✅ |
| 25 | Knowledge: reliability (7 units) | 3 | #20 | ✅ |
| 26 | Knowledge: cost (4 units) | 3 | #20 | ✅ |
| 27 | Output templates: ADR, review, design, capacity | 3 | #6 #7 | ✅ |
| 28 | **SPIKE:** verify plugin packaging end-to-end | 1 | #1 | ✅ |
| 29 | Plugin manifest and marketplace manifest | 4 | #28 | |
| 30 | Skill: `oab-principles` | 4 | #29 #14 | ✅ |
| 31 | Skill: `/oab:capacity` | 4 | #29 #16 | ✅ |
| 32 | Skill: `/oab:adr` | 4 | #29 #19 #27 | ✅ |
| 33 | Agent: `repo-scanner` | 4 | #29 #7 | ✅ |
| 34 | Skill: `/oab:review` | 4 | #33 #18 | |
| 35 | Skill: `/oab:design` | 4 | #31 #17 | |
| 36 | Evaluation runner and assertion library | 5 | #7 | |
| 37 | Scenarios 01, 07, 08 (over-engineering + consistency guards) | 5 | #36 #35 | ✅ |
| 38 | Scenarios 02, 03 (scale guards) | 5 | #36 #35 | ✅ |
| 39 | Docs: getting started, principles, contributing | 6 | #35 | ✅ |
| 40 | Examples: three committed end-to-end outputs | 6 | #35 #34 | ✅ |
| 41 | README with real output sample | 6 | #40 | |
| 42 | Website: oab.run landing page | 6 | #41 | ✅ |
| 43 | Release v0.1.0 | 6 | all | |

### 43.4 Standard acceptance criteria

Every issue inherits these in addition to its own:

- CI green (schema validation, neutrality guard, tests).
- No vendor or model name introduced outside `integrations/`.
- No third-party runtime dependency introduced.
- Documentation updated in the same PR where behaviour or contracts changed.
- Commits authored as `hi@mhayk.com`, no co-author trailers.

### 43.5 Definition of done for M1

The seven conditions in [§26.4](07-roadmap-and-risks.md#264-what-done-means), verified on a clean
machine, plus a tagged `v0.1.0` release and a working
`/plugin marketplace add mhayk/oab` → `/plugin install oab@oab`.

### 43.6 Sequencing advice

- **Do not start knowledge (#21–#26) before #20.** Six contributors writing units against six
  interpretations of the schema is the fastest way to a knowledge base that needs rewriting.
- **Do not start #35 (`/oab:design`) before #17.** The skill is a thin wrapper; writing the wrapper
  before the procedure inverts the whole architecture and will pull reasoning into the
  vendor-specific layer, which is the one structural mistake this design exists to prevent.
- **Run #28 immediately.** It is a one-hour spike whose outcome changes #29 and nothing else. A
  negative result is cheap in week one and expensive in week six.
- **Write scenario assertions (#37) before tuning the frameworks.** Otherwise the frameworks are
  tuned to whatever they happened to produce, and the evaluation suite ratifies the status quo.
