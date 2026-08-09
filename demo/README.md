# Demos

Demos as code: the `.tape` files are the source of truth, the GIFs in `out/` are generated
artifacts, and **nothing is staged** — `install.tape` genuinely removes and reinstalls the plugin,
and the calculator and evaluation tapes run the real tools. Rendered with
[VHS](https://github.com/charmbracelet/vhs), themed to the palette in `assets/logo/BRAND.md`.

| Tape | Shows |
| :-- | :-- |
| `install.tape` | The two-command install, really executed against GitHub |
| `calculator.tape` | The full capacity envelope: assumptions with confidences, the literal formula, the substituted calculation, and the sensitivity line |
| `evaluation.tape` | The scenario suite — both failure-direction guards — plus the magnitude perturbation check |

## Re-rendering

```bash
brew install vhs        # pulls ttyd and ffmpeg
./demo/render.sh
```

The script creates a local `.venv` for the evaluation tape's dev dependencies, and removes the
`oab` marketplace before rendering so the install tape shows a genuine install — a trap restores
the installed state even if a render fails.

Renders are not byte-deterministic (font rasterisation, network timing), so there is no CI
freshness check. Re-render when the demoed behaviour changes, and **eyeball every GIF before
committing** — extract the last frame with
`ffmpeg -sseof -0.5 -i demo/out/x.gif -frames:v 1 frame.png` if in doubt.

## What is deliberately not recorded

A `/oab:design` session in the agent TUI. It runs for ~10–12 minutes, its output varies per run,
and every re-render would spend real model tokens to produce a different GIF — a non-reproducible
demo of a non-deterministic process. The real, unedited output of those sessions is committed as
text in [`examples/live-run/`](../examples/live-run/) and
[`examples/live-review/`](../examples/live-review/), which is both cheaper and more honest than a
recording. Revisit if a demo-stable replay mechanism ever exists.
