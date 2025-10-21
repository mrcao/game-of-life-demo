from __future__ import annotations
from typing import Optional, Tuple
import random

from .engine import LifeGrid

def seed_random(grid: LifeGrid, density: float = 0.15, rng: Optional[random.Random] = None) -> None:
    """
    Fill grid with alive cells according to density in [0,1].
    """
    if rng is None:
        rng = random
    rows, cols = grid.cfg.rows, grid.cfg.cols
    for r in range(rows):
        for c in range(cols):
            grid.grid[r][c] = 1 if rng.random() < max(0.0, min(1.0, density)) else 0

def inject_noise(grid: LifeGrid, fraction: float = 0.02, rng: Optional[random.Random] = None) -> int:
    """
    Flip a fraction of cells uniformly at random.
    Returns number of toggles.
    """
    if rng is None:
        rng = random
    rows, cols = grid.cfg.rows, grid.cfg.cols
    total = rows * cols
    flips = max(1, int(total * max(0.0, min(1.0, fraction))))
    for _ in range(flips):
        r = rng.randrange(rows)
        c = rng.randrange(cols)
        grid.grid[r][c] = 0 if grid.grid[r][c] == 1 else 1
    return flips

def perturb_oscillation(grid: LifeGrid, radius: int = 2, rng: Optional[random.Random] = None) -> None:
    """
    Nudge an oscillating/steady region by toggling one cell near a random alive cell.
    """
    if rng is None:
        rng = random
    alive = list(grid.alive_cells())
    if not alive:
        # Nudge somewhere random if totally dead
        r = rng.randrange(grid.cfg.rows)
        c = rng.randrange(grid.cfg.cols)
        grid.toggle(r, c)
        return
    r0, c0 = rng.choice(alive)
    r = (r0 + rng.randint(-radius, radius)) % grid.cfg.rows
    c = (c0 + rng.randint(-radius, radius)) % grid.cfg.cols
    grid.toggle(r, c)

