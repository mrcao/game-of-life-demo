import time
import os
import sys
from pathlib import Path

# Add parent directory to path to import 'life' module
sys.path.insert(0, str(Path(__file__).parent.parent))

from life import LifeGrid, seed_random, inject_noise

def render_ascii(g: LifeGrid):
    chars = []
    for r in range(g.cfg.rows):
        row = ''.join('█' if g.grid[r][c] else ' ' for c in range(g.cfg.cols))
        chars.append(row)
    return '\n'.join(chars)

if __name__ == "__main__":
    g = LifeGrid(24, 48, toroidal=True)
    seed_random(g, density=0.2)
    try:
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(render_ascii(g))
            time.sleep(0.08)
            g.step()
    except KeyboardInterrupt:
        pass

