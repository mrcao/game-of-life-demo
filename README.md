# Conway's Game of Life (Python + PyScript)

A robust, modular Python implementation of Conway's Game of Life with:
- Core engine (`life/`) that's framework-agnostic
- Local CLI demo (`examples/cli.py`)
- Browser UI via **PyScript** served from `/docs` (works on GitHub Pages)

## Features
- Play/Pause, Step, Speed slider
- Click-to-toggle cells
- Random seeding with density control
- "Anti-boringness" button (noise injector)
- Optional toroidal wrapping
- **Cycle/oscillation detection** with automatic gentle perturbation
- Clean, modern canvas UI

## Local quickstart

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
python examples/cli.py
```

## GitHub Pages (no server needed)
1. Push this repo to GitHub.
2. In Settings → Pages, select Source: Deploy from a branch, then Branch: main, Folder: /docs.
3. Wait for the green check, then open your Pages URL.
4. (Optional) Update the "View Repo" link in docs/index.html.

## Notes
- PyScript fetches modules from /docs/life. Keep those in sync with the root life/ package (copy when you change core logic).
- If the board gets stuck in a loop or still life, click Inject Noise, or keep Auto-perturb enabled.

## Architecture

### Core Engine (`life/engine.py`)
- `LifeGrid`: Main grid class with configurable toroidal wrapping
- `PatternMonitor`: Detects repetitive patterns/oscillations
- Efficient neighbor counting and state transitions
- Hashable state for cycle detection

### Utilities (`life/utils.py`)
- `seed_random()`: Initialize grid with configurable density
- `inject_noise()`: Add random entropy to break boring patterns
- `perturb_oscillation()`: Nudge stable/repetitive patterns

### Web UI (`docs/`)
- Pure PyScript + HTML Canvas implementation
- No server required—runs entirely in browser
- Interactive controls for all features
- Modern, accessible design

## Extension Ideas
- Preset pattern library (glider, pulsar, gosper glider gun)
- Export/import boards to JSON
- Different rule sets (B3/S23 variants)
- Heatmap visualization of cell age
- Statistics panel (population, generation count)

