# OAB brand assets

Drop logo files here using these names. The README (#41) and the website (#42) reference
them from this directory, so nothing is duplicated.

| File | Format | Size | Used by |
| :-- | :-- | :-- | :-- |
| `oab-logo.svg` | SVG | scalable | Website header, docs |
| `oab-logo-light.svg` | SVG | scalable | Optional — for dark backgrounds |
| `oab-logo-dark.svg` | SVG | scalable | Optional — for light backgrounds |
| `oab-logo.png` | PNG, transparent | 512 px wide | README (safest for GitHub rendering) |
| `oab-icon.svg` | SVG, square | — | Favicon source, avatar |
| `oab-icon.png` | PNG, transparent | 512 × 512 | Favicon fallback, plugin listing |
| `oab-social-card.png` | PNG | 1280 × 640 | GitHub social preview, OpenGraph |

## Notes

- **README embedding:** use a relative path — `![OAB](assets/logo/oab-logo.png)`. Prefer the PNG
  in the README; GitHub's SVG handling in Markdown is less predictable across contexts.
- **GitHub social preview** is uploaded in repository Settings → General → Social preview. It is
  not read from this directory, so `oab-social-card.png` is kept here only as the source of truth.
- **Website** (#42) reads from here at build time. Do not keep a second copy in `website/public/`.
- **Dark/light variants:** only add them if the mark needs different colours per theme. A single
  logo that works on both backgrounds is preferable.

## Licensing

Brand assets are **not** covered by the Apache-2.0 licence that covers the rest of this
repository. The OAB name and logo identify the project; forks and derivative works may use the
code and knowledge freely but should not use the OAB name or logo in a way that implies
endorsement or official status.

This needs to be stated in `NOTICE` when issue #1 lands.
