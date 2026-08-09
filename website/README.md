# oab.run

One static page. No build step, no framework, no external requests at runtime — which is the
project's own principle applied to itself.

```bash
python3 -m http.server -d website 8000
```

## Deploying

GitHub Pages, via `.github/workflows/pages.yml`: on any push touching `website/`, the directory is
uploaded as-is — there is nothing to build.

`oab.run` is set as the custom domain in the repository's Pages settings. DNS is on Cloudflare
**with the proxy enabled**, so TLS terminates at Cloudflare's edge and HTTP→HTTPS is enforced by a
Cloudflare Redirect Rule ("Redirect from HTTP to HTTPS"), not by GitHub's Enforce HTTPS — that
setting cannot activate behind the proxy, because GitHub never sees its own IPs and never
provisions its certificate. SSL mode must stay **Full** (not *strict*: GitHub serves the
`*.github.io` certificate to the origin connection, which strict would reject; not *Flexible*,
which would downgrade the origin hop to HTTP).

Assets are copied from `assets/logo/` rather than duplicated as sources:

```bash
cp assets/logo/oab-logo-on-dark.png assets/logo/oab-logo-on-light.png \
   assets/logo/oab-icon.png assets/logo/oab-social-card.png website/
```

## Deliberately not here

Search · a docs framework · an interactive calculator · analytics beyond aggregate page views ·
accounts · anything the plugin calls at runtime.

`/docs`, `/knowledge` and `/examples` as rendered pages are M2. GitHub renders that Markdown today,
and a documentation site before there is traffic to it is the overengineering this project exists
to prevent.

## Fonts

Sora (headings) and Inter (body) are the decided typefaces — see `assets/logo/BRAND.md`. The page
currently uses the system stack. When they are added they must be **self-hosted as WOFF2**: linking
to a font CDN would make the site call an external service to render, which contradicts the
principle the page is advertising.
