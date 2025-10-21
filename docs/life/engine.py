from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Tuple, Optional, List
import random
import hashlib
from collections import deque

Coord = Tuple[int, int]

@dataclass
class LifeConfig:
    rows: int
    cols: int
    toroidal: bool = True

class LifeGrid:
    """
    Core, framework-agnostic Game of Life grid & rules.

    - Efficient neighbor counting
    - Optional toroidal wrapping
    - Hashable state for cycle detection
    """
    def __init__(self, rows: int, cols: int, toroidal: bool = True):
        self.cfg = LifeConfig(rows=rows, cols=cols, toroidal=toroidal)
        self.grid = [[0]*cols for _ in range(rows)]

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.cfg.rows and 0 <= c < self.cfg.cols

    def get(self, r: int, c: int) -> int:
        if self.cfg.toroidal:
            r %= self.cfg.rows
            c %= self.cfg.cols
            return self.grid[r][c]
        return self.grid[r][c] if self.in_bounds(r, c) else 0

    def set(self, r: int, c: int, val: int) -> None:
        if self.cfg.toroidal:
            r %= self.cfg.rows
            c %= self.cfg.cols
            self.grid[r][c] = 1 if val else 0
        else:
            if self.in_bounds(r, c):
                self.grid[r][c] = 1 if val else 0

    def toggle(self, r: int, c: int) -> None:
        self.set(r, c, 0 if self.get(r, c) == 1 else 1)

    def clear(self) -> None:
        for r in range(self.cfg.rows):
            for c in range(self.cfg.cols):
                self.grid[r][c] = 0

    def alive_cells(self) -> Iterable[Coord]:
        for r in range(self.cfg.rows):
            for c in range(self.cfg.cols):
                if self.grid[r][c] == 1:
                    yield (r, c)

    def neighbors(self, r: int, c: int) -> int:
        cnt = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                cnt += self.get(r+dr, c+dc)
        return cnt

    def step(self) -> None:
        rows, cols = self.cfg.rows, self.cfg.cols
        nxt = [[0]*cols for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                n = self.neighbors(r, c)
                if self.grid[r][c] == 1:
                    nxt[r][c] = 1 if (n == 2 or n == 3) else 0
                else:
                    nxt[r][c] = 1 if n == 3 else 0
        self.grid = nxt

    def state_hash(self) -> str:
        # Compact, stable hash of grid state
        flat_bytes = bytearray()
        bits = 0
        b = 0
        for r in range(self.cfg.rows):
            for c in range(self.cfg.cols):
                b = (b << 1) | (self.grid[r][c] & 1)
                bits += 1
                if bits == 8:
                    flat_bytes.append(b)
                    bits, b = 0, 0
        if bits:  # flush remaining
            flat_bytes.append(b << (8 - bits))
        return hashlib.sha256(flat_bytes).hexdigest()

class PatternMonitor:
    """
    Lightweight repetition detector.
    - Keeps a window of recent hashes.
    - If a pattern repeats with a detected period and passes a threshold count,
      signals that we should perturb to avoid boring loops.
    """
    def __init__(self, window: int = 64, min_repeats: int = 3):
        self.window = window
        self.min_repeats = min_repeats
        self.hashes = deque(maxlen=window)

    def observe(self, h: str) -> Optional[int]:
        """
        Record hash h. If a period is detected that has occurred >= min_repeats times,
        return the detected period (int). Otherwise return None.
        """
        self.hashes.append(h)
        # Try to find a period p where current hash equals hash[-1-p], -1-2p, ...
        # Limit p up to half the buffer to be safe.
        L = len(self.hashes)
        if L < 6:
            return None
        max_p = min(L // 2, 20)  # keep cheap
        for p in range(1, max_p+1):
            ok = True
            repeats = 1
            idx = -1
            while True:
                prev = idx - p
                if -L <= prev:
                    if self.hashes[idx] == self.hashes[prev]:
                        repeats += 1
                        idx = prev
                        if repeats >= self.min_repeats:
                            return p
                    else:
                        ok = False
                        break
                else:
                    break
            if ok and repeats >= self.min_repeats:
                return p
        return None

