# OAB brand

Extracted from the concept boards in `logo.png` and `branding.png`. Colour values are the
declared palette from the board; sampled pixel values differ by 1–3% due to render noise and
the declared values are canonical.

## Palette

| Role | Hex | Notes |
| :-- | :-- | :-- |
| Background, deepest | `#0B0F14` | Primary dark surface |
| Background, raised | `#141A22` | Cards, panels on dark |
| Foreground, muted | `#E6E6E6` | Body text on dark |
| Foreground, primary | `#FFFFFF` | Headings, the wordmark on dark |
| Accent | `#00D1FF` | Cyan. The only accent — use sparingly |

The accent appears in the mark as small cubes and a dotted vertical axis, and in the wordmark on
the word **ARCHITECTURE**. Highlights in the render reach `#2AE7F3`; that is a glow, not a
separate palette entry.

### Accessibility check

- `#FFFFFF` on `#0B0F14` — contrast ratio ≈ 18.9:1. Passes AAA.
- `#E6E6E6` on `#0B0F14` — ≈ 16.1:1. Passes AAA.
- `#00D1FF` on `#0B0F14` — ≈ 10.4:1. Passes AAA for text.
- `#00D1FF` on `#FFFFFF` — ≈ 1.8:1. **Fails.** Never use the cyan for text on a light
  background; on light surfaces it is a fill or stroke colour only, or it must be darkened.

## Typography

| Role | Options (in preference order) |
| :-- | :-- |
| Primary / wordmark | Sora · Exo 2 · Space Grotesk |
| Secondary / body | Inter · Manrope · DM Sans |

All six are open-licensed (SIL OFL) and available on Google Fonts, so the website can self-host
them without a third-party request at runtime — which matters, because the site must not call an
external service to render (see `docs/design/06-documentation-and-website.md` §25.3).

**Pick one primary and one secondary before the website is built (#42).** Listing three options
each is a concept-board convention, not a decision.

## Wordmark composition

```
OAB
OPEN ARCHITECTURE BRAIN        ← letterspaced, "ARCHITECTURE" in accent cyan
─────────── • ───────────
ARCHITECTURE INTELLIGENCE
FOR AI CODING AGENTS           ← optional tagline lockup
```

The tagline lockup is for the site hero and social card only. Use the compact horizontal lockup
(mark + `OAB` + `OPEN ARCHITECTURE BRAIN`) everywhere else.

## Status

✅ **The mark is resolved.** `oab-mark.svg` is the canonical asset — true vector, drawn from
isometric geometry, theme-aware via `currentColor`. `oab-icon.svg` is its optically simplified
counterpart for small sizes. All rasters are exported from these two files.

The concept boards (`concept-board-1.png`, `concept-board-2.png`) are kept as reference only. They
are AI-generated and the mark is drawn differently in every panel — the isometric geometry, stroke
weight, and construction of the `B` are inconsistent across panels 01, 02, 03, and 05. They were
direction, not artwork, and the accompanying `.svg` files shipped with them were raster PNGs in an
`<image>` wrapper rather than real vectors, so they were discarded.

⚠️ **The wordmark is still open**, and it blocks nothing today but should be closed before the
website ships (#42):

1. Choose one primary and one secondary typeface from the lists above.
2. Set `OAB` and `OPEN ARCHITECTURE BRAIN` in it and convert to outlines.
3. Combine with `oab-mark.svg` into a real `oab-logo.svg`.

Until then use the mark plus a text heading rather than the raster lockup. See `README.md` in this
directory.
