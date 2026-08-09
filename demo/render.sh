#!/usr/bin/env bash
# Re-render the demo GIFs from the committed tapes.
#
# Demos are code: the .tape files are the source of truth, the GIFs are generated artifacts,
# and nothing here is faked — install.tape genuinely removes and reinstalls the plugin, and
# the calculator and evaluation tapes run the real tools.
#
# Requires: vhs (brew install vhs), claude, python3. Renders are not byte-deterministic
# (font rasterisation, timing), so there is no CI freshness check — re-render when the
# demoed behaviour changes, and eyeball the result before committing.
set -euo pipefail
cd "$(dirname "$0")/.."

command -v vhs >/dev/null || { echo "vhs is required: brew install vhs" >&2; exit 1; }

# Evaluation tape needs the dev dependencies in a repo-local venv (gitignored).
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements-dev.txt
fi

# install.tape must show a genuine install, not "already installed". Removing the
# marketplace uninstalls the plugin; the tape itself re-adds and reinstalls, so a
# successful render restores the initial state. The trap restores it even on failure.
restore() {
  claude plugin marketplace add mhayk/oab >/dev/null 2>&1 || true
  claude plugin install oab@oab >/dev/null 2>&1 || true
}
trap restore EXIT
claude plugin marketplace remove oab >/dev/null 2>&1 || true

for tape in demo/tapes/*.tape; do
  echo "rendering $tape"
  vhs "$tape"
done

# Optimise if gifsicle is available; skip silently if not.
if command -v gifsicle >/dev/null; then
  for gif in demo/out/*.gif; do
    gifsicle -O3 --lossy=40 -o "$gif.tmp" "$gif" && mv "$gif.tmp" "$gif"
  done
fi

ls -la demo/out/
