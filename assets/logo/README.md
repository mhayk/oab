# OAB brand assets

Colours, typography, and accessibility notes are in [`BRAND.md`](BRAND.md).

## Files

| File | What it is | Use for |
| :-- | :-- | :-- |
| `oab-mark.svg` | **Canonical mark.** True vector, 1.6 KB. Frame is `currentColor`, accent is fixed cyan | Anywhere. Inherits the surrounding text colour, so one file works in both themes |
| `oab-icon.svg` | Favicon / app tile. Dark rounded square, optically simplified | Favicon, app icon, plugin listing |
| `oab-icon.png` | 512 × 512, exported from `oab-icon.svg` | Where SVG is not accepted |
| `oab-mark-on-dark.png` | 512 px, white mark, transparent | Raster fallback on dark surfaces |
| `oab-mark-on-light.png` | 512 px, dark mark, transparent | Raster fallback on light surfaces |
| `oab-logo-on-dark.png` | 1200 × 512 lockup with wordmark, transparent | README banner **on dark only** — see the limitation below |
| `oab-social-card.png` | 1280 × 640, opaque dark | GitHub social preview, OpenGraph |
| `concept-board-1.png`, `concept-board-2.png` | The original AI-generated concept boards | Reference only. **Not assets** — the mark is drawn differently in every panel |

## The mark

An exploded isometric cube on a vertical axis: a cube between two planes, threaded by a dotted
cyan spine with a node at each plane. It is drawn from true isometric geometry — hexagon radius
56, width `√3 × R` — not traced over a raster.

The composition reads 1:1.6 (134 × 214 of usable area). The floating planes are 1.28× the cube's
half-width: wide enough to read as planes the cube sits between, not so wide that they overpower it.

`oab-icon.svg` is **optically simplified**, not merely scaled: the floating planes are dropped, the
dotted axis becomes solid, and the strokes thicken. Dots and fine strokes disappear below roughly
48 px, so a straight downscale of the mark would produce mush. This is standard practice, and it is
why the icon and the mark are two files rather than one.

## Known limitations

**The wordmark is not vectorised.** `oab-logo-on-dark.png` is the AI-generated lockup, kept because
it looks good on dark surfaces. It is white-only, and its baked-in drop shadow shows as a grey
smudge on light backgrounds. Until the typeface is chosen (see `BRAND.md`) and the wordmark is set
as outlines, prefer `oab-mark.svg` plus a Markdown or HTML heading over the raster lockup.

**16 px favicons are weak.** A wireframe mark cannot hold at 16 px; the internal edges collapse.
It is legible from 32 px up, and most browsers now render the 32 px asset. Accept it, or commission
a dedicated 16 px glyph later.

## Using the mark in Markdown

`currentColor` does not apply inside a GitHub `<img>`, so use the two raster variants with a
`<picture>` element rather than a single transparent PNG:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo/oab-mark-on-dark.png">
  <img src="assets/logo/oab-mark-on-light.png" alt="OAB" width="96">
</picture>
```

Inline SVG in a web page can use `oab-mark.svg` directly and colour it with CSS.

## Regenerating the rasters

Every PNG except `oab-logo-on-dark.png` and `oab-social-card.png` is exported from the SVGs.
Never edit them by hand.

```bash
rsvg-convert -w 512 -h 512 oab-icon.svg -o oab-icon.png
sed 's|<svg |<svg style="color:#FFFFFF" |' oab-mark.svg | rsvg-convert -w 512 -o oab-mark-on-dark.png
sed 's|<svg |<svg style="color:#0B0F14" |' oab-mark.svg | rsvg-convert -w 512 -o oab-mark-on-light.png
```

## Licensing

Brand assets are **not** covered by the Apache-2.0 licence that covers the rest of this repository.
The OAB name and logo identify the project; forks may use the code and knowledge freely but should
not use the name or logo in a way that implies endorsement or official status. This is to be stated
in `NOTICE` when issue #1 lands.
