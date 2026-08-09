# 06 — Documentation Architecture & oab.run

Covers §24–§25 of the design brief.

---

## 24. Documentation Architecture

### 24.1 Four audiences, four paths

Documentation fails when it serves one audience and pretends to serve four. OAB splits explicitly.

| Audience | Question | Entry point | Success |
| :-- | :-- | :-- | :-- |
| **User** | "How do I get an architecture review in the next five minutes?" | `README.md` → `docs/getting-started.md` | First useful output within 5 minutes of install |
| **Knowledge contributor** | "How do I add what I know about idempotency?" | `docs/contributing/knowledge.md` | First knowledge PR without reading any code |
| **Engine contributor** | "How do I add a calculator / framework / integration?" | `CONTRIBUTING.md` → `docs/contributing/engine.md` | Tests pass locally on first try |
| **Maintainer** | "How do I review, release, and govern?" | `docs/maintainers/` | Consistent review bar; reproducible releases |

### 24.2 Layout

```
README.md                       Hero, why, install, first run, sample output, contribute
CONTRIBUTING.md                 Routing document — sends each contributor type to their path
CODE_OF_CONDUCT.md              Contributor Covenant 2.1
SECURITY.md                     Reporting, scope, response expectations
CHANGELOG.md                    Keep a Changelog format, semver
ROADMAP.md                      M1 / M2 / beyond, honest about what is not built
LICENSE, NOTICE                 Apache-2.0

docs/
├── getting-started.md          Install → first review → reading the output
├── principles.md               The 10 core principles, in user-facing language
├── design/                     This proposal (the "why" of OAB itself)
├── architecture/               OAB's own architecture + its own ADRs (dogfooding, visibly)
├── contributing/
│   ├── knowledge.md            Knowledge unit authoring guide + schema walkthrough
│   ├── engine.md               Frameworks, calculators, schemas, evaluations
│   ├── style.md                Voice: precise, quantitative, no hype, no hedging
│   └── review-checklist.md     What a reviewer checks, so review is predictable
├── knowledge-map/              Generated index + Mermaid graphs (M2)
├── frameworks/                 One page per framework: inputs, procedure, outputs
├── reference/
│   ├── commands.md             Every command, arguments, outputs
│   ├── schemas.md              Generated from JSON Schema
│   └── calculators.md          Formulas, assumptions, worked examples
└── maintainers/
    ├── release.md              Version bump → changelog → tag → marketplace verify
    ├── governance.md           Decision-making, roles, RFC process (M2)
    └── knowledge-review.md     The bar for accepting knowledge

examples/                       Real committed outputs — the best documentation there is
```

### 24.3 Documentation principles

1. **Examples over explanation.** A committed `examples/tiny-startup/` containing the real
   `design.md` and `design.json` teaches more than three pages of prose, and is regression-tested.
2. **Generated where derivable.** Command reference, schema reference, and knowledge index are
   generated from source. Hand-maintained duplicates drift within two releases.
3. **Honest about gaps.** A `Status: not implemented` banner is better than documentation for a
   feature that does not exist. Aspirational docs are the fastest way to lose a first-time user.
4. **No documentation framework in M1.** Markdown in git, rendered by GitHub. A docs site is added
   when the volume justifies it (see §25).

### 24.4 The README is the product

For an open-source project of this kind, the README *is* the adoption funnel. Required structure:

1. Hero — name, one-line positioning, manifesto line
2. The problem, in three sentences, with the Kubernetes-for-100-users example
3. What OAB does — four commands, one line each
4. Install — two commands
5. **A real, unedited output excerpt** — the capacity numbers and the rejected options. This is the
   moment a reader decides whether OAB is serious.
6. How it avoids overengineering — the Complexity Budget, briefly
7. What is *not* built yet
8. Contributing — with the knowledge path first, because that is the growth vector
9. Licence, website

Point 5 is non-negotiable. Projects in this space are judged on whether their sample output looks
like something a senior engineer wrote.

---

## 25. oab.run

### 25.1 Purpose

The website exists for **adoption and documentation**. Nothing else. It is not a product, not a
SaaS, not a dashboard, and it stores no user data.

Three jobs, in order:

1. Convince a sceptical senior engineer, in under 60 seconds, that OAB is rigorous.
2. Get them installed.
3. Let them read the knowledge base and the docs without cloning.

### 25.2 M1 site — five pages

| Page | Content | Purpose |
| :-- | :-- | :-- |
| `/` | Hero, the problem, the four commands, **a real output sample**, install, links | Conversion |
| `/docs` | Getting started, principles, command reference (rendered from repo Markdown) | Onboarding |
| `/knowledge` | Browsable knowledge base rendered from `knowledge/` | Proves the substance is real |
| `/examples` | The three worked examples, rendered | Proves the output quality |
| `/contributing` | How to add knowledge; link to templates and open issues | Growth |

Plus `/adr` (OAB's own ADRs) once there are more than three — dogfooding in public is a
credibility asset specific to this project.

### 25.3 Technology

**Static site, generated from the repository's Markdown, deployed on push.**

| Choice | Rationale |
| :-- | :-- |
| Astro (or Eleventy) | Content-first, zero client JS by default, Markdown-native, trivial to render the existing tree |
| No CMS, no database, no accounts, no analytics beyond aggregate | P7 local-first, P9 dogfooding, and no privacy surface to defend |
| Deployed via Cloudflare Pages / GitHub Pages | Free, static, no infrastructure to operate — complexity cost 1 |
| `website/` in the same repository | Single source of truth; docs cannot drift from the site |

**Explicitly rejected for M1:** search infrastructure (browser-side index at this size is
sufficient; the whole knowledge base is smaller than one React bundle), interactive calculators in
the browser (duplicates `calculators/` in a second language — a maintenance trap), user accounts,
a plugin directory, telemetry, and a blog.

An interactive capacity calculator on the site is genuinely attractive for demonstration. It is
deferred to M2 and, when built, must be generated from or compiled from the same Python source —
never reimplemented, because two implementations of the same formula will disagree.

### 25.4 What the site must never become

- A gate in front of the knowledge (everything remains in git)
- A service the plugin calls at runtime (P7)
- A place where documentation lives that the repository does not have
