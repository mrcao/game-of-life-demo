# Quick Start Guide

## Running Locally (Python)

### 1. Simple CLI Demo

The easiest way to see the Game of Life in action locally:

```bash
python3 examples/cli.py
```

This will show an animated ASCII version in your terminal. Press `Ctrl+C` to stop.

### 2. Interactive Python Session

You can also experiment interactively:

```python
from life import LifeGrid, seed_random, inject_noise, perturb_oscillation

# Create a 30x50 grid with toroidal wrapping
grid = LifeGrid(30, 50, toroidal=True)

# Seed with 20% density
seed_random(grid, density=0.2)

# Toggle a specific cell
grid.toggle(15, 25)

# Run one generation
grid.step()

# Count alive cells
alive_count = len(list(grid.alive_cells()))
print(f"Alive cells: {alive_count}")

# Inject some random noise (2% of cells)
inject_noise(grid, fraction=0.02)

# Get grid state hash for comparison
state = grid.state_hash()
```

### 3. Pattern Detection

The `PatternMonitor` class detects repetitive patterns:

```python
from life import LifeGrid, seed_random, PatternMonitor

grid = LifeGrid(40, 60)
seed_random(grid, density=0.15)

monitor = PatternMonitor(window=64, min_repeats=3)

for generation in range(100):
    h = grid.state_hash()
    period = monitor.observe(h)
    
    if period:
        print(f"Detected oscillation with period {period} at generation {generation}")
        # Perturb to break the cycle
        from life.utils import perturb_oscillation
        perturb_oscillation(grid)
    
    grid.step()
```

## Deploying to GitHub Pages

### Step 1: Create GitHub Repository

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: Game of Life with PyScript"

# Connect to GitHub
git remote add origin https://github.com/YOUR_USERNAME/game-of-life.git
git branch -M main
git push -u origin main
```

### Step 2: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under "Source", select:
   - **Branch**: `main`
   - **Folder**: `/docs`
4. Click **Save**
5. Wait 1-2 minutes for the site to build

### Step 3: Access Your Live Site

Your Game of Life will be live at:
```
https://YOUR_USERNAME.github.io/game-of-life/
```

### Optional: Update the Repository Link

Edit `docs/index.html` and update this line:

```html
<a href="https://github.com/YOUR_USERNAME/game-of-life" target="_blank">View Repo</a>
```

## Web UI Features

Once deployed (or by opening `docs/index.html` locally in a modern browser):

- **Play/Pause**: Control simulation
- **Step**: Advance one generation at a time
- **Speed slider**: Adjust ms between generations (10-600ms)
- **Click cells**: Toggle individual cells alive/dead
- **Randomize**: Generate new random seed with density control
- **Inject Noise**: Add entropy to break boring patterns
- **Auto-perturb**: Automatically detect and break repetitive cycles
- **Toroidal wrapping**: Toggle edge behavior (wrap vs. fixed boundary)
- **Cell size**: Adjust visualization scale

## Troubleshooting

### "Module not found" in browser

Make sure:
- `docs/life/engine.py` and `docs/life/utils.py` exist
- They're identical to the versions in `life/` directory
- Your browser supports PyScript (Chrome, Firefox, Safari, Edge are fine)

### PyScript loading slowly

- First load downloads PyScript runtime (~5MB)
- Subsequent loads are cached and faster
- Consider adding a loading message if needed

### Grid appears frozen

- This is normal! Many patterns stabilize or loop
- Use "Inject Noise" button to add chaos
- Enable "Auto-perturb detected loops" checkbox

## Next Steps

Consider adding:
- **Preset patterns**: Glider, pulsar, gosper glider gun dropdown
- **Statistics panel**: Show generation count, population over time
- **Export/Import**: Save interesting patterns as JSON
- **Color schemes**: Different visualizations
- **Rule variations**: B3/S23 is standard, but try other rule sets
- **Cell history**: Show age of cells with color gradients

Enjoy exploring cellular automata! 🎮

