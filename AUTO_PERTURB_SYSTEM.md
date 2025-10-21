# Sophisticated Auto-Perturb System

## Overview

Implemented an elegant cell-level pattern tracking system that detects and perturbs "boring" regions of the grid. Unlike the previous system which detected whole-grid repetition, this tracks individual cells for static and periodic behavior.

---

## ✨ Key Features

### 1. **Cell-Level Tracking**
Each cell is independently monitored for:
- **Static behavior**: Cell hasn't changed for N consecutive steps
- **Periodic patterns**: Cell oscillates with period 2, 3, or 4

### 2. **Configurable Perturb Rate**
- UI slider: 0-100% 
- Controls what fraction of "boring" cells get toggled
- Higher rate = more aggressive perturbation

### 3. **Pattern Detection**
Tracks three types of boring behavior:
- **Static cells**: Same state for 5+ consecutive steps
- **Period-2**: Oscillates A→B→A for 10+ steps (5 cycles × 2)
- **Period-3**: Oscillates A→B→C→A for 15+ steps (5 cycles × 3)
- **Period-4**: Oscillates A→B→C→D→A for 20+ steps (5 cycles × 4)

---

## 🏗️ Architecture

### CellTracker Class

```python
class CellTracker:
    """Tracks per-cell patterns to detect static and periodic behavior"""
    
    # Data structures:
    history[r][c]           # List of recent states (0/1) for cell (r,c)
    static_count[r][c]      # Consecutive steps cell hasn't changed
    period_counts[p][r][c]  # Cycles of period p detected
```

**Methods**:
- `update(grid)`: Update all tracking after grid step
- `get_boring_cells()`: Return list of cells that need perturbation
- `reset()`: Clear all tracking data

---

## 📊 How It Works

### Step-by-Step Process

**1. Before Each Generation**:
```python
cell_tracker.update(grid)  # Update cell histories
```

**2. Pattern Detection**:
For each cell:
- Add current state to history
- Check if state matches previous state (static count++)
- Check if state matches state N steps ago (period count++)
- Reset counters when patterns break

**3. Identify Boring Cells**:
```python
boring_cells = cell_tracker.get_boring_cells()
# Returns: [(r1, c1), (r2, c2), ...]
```

Cells are "boring" if:
- `static_count >= 5` (static too long)
- `period_counts[2] >= 10` (period-2 for 5 cycles)
- `period_counts[3] >= 15` (period-3 for 5 cycles)
- `period_counts[4] >= 20` (period-4 for 5 cycles)

**4. Apply Perturbation**:
```python
num_to_perturb = len(boring_cells) * perturb_rate
cells_to_toggle = random.sample(boring_cells, num_to_perturb)
for r, c in cells_to_toggle:
    grid.toggle(r, c)
    # Reset tracking for this cell
```

---

## 🎯 Example Scenarios

### Scenario 1: Still Life (Blinkers)
```
Grid has region:
███
███
███
(static block)

After 5 steps:
- All 9 cells marked as boring (static_count = 5)
- With perturb_rate = 0.3:
  → Toggle ~3 cells (30% of 9)
  → Block disrupted, new patterns emerge
```

### Scenario 2: Blinker (Period-2)
```
Step 0: ███    Step 1:  █     Step 2: ███
        ·       ·       █      ·       ·
        ·       ·       █      ·       ·

After 10 steps (5 cycles):
- All cells marked boring (period-2 count = 10)
- Perturb rate 0.3 → toggle 1-2 cells
- Pattern broken, evolution continues
```

### Scenario 3: Complex Oscillator (Period-3)
```
After 15 steps (5 cycles of period-3):
- Cells in oscillator marked boring
- Random perturbation introduces asymmetry
- New dynamics emerge
```

---

## 🎛️ Configuration

### UI Controls

**Auto-Perturb Settings Box**:
```
☑ Enable auto-perturb
Perturb rate: [═══slider═══] 30%
```

**Default Values**:
- Enabled: Yes (checked)
- Perturb rate: 30% (moderate)

### Tunable Parameters (in code)

```python
CellTracker(
    rows, cols,
    periods_to_track=[2, 3, 4],    # Which periods to detect
    static_threshold=5,             # Steps before static is boring
    period_threshold=5              # Cycles before period is boring
)
```

**Adjustable**:
- `static_threshold`: Lower = more aggressive for still lifes
- `period_threshold`: Lower = more aggressive for oscillators
- `periods_to_track`: Add/remove periods (e.g., [2, 3, 4, 5])

---

## 💡 Design Rationale

### Why Cell-Level?

**Previous system** (grid-level):
- Only detected when entire grid repeats
- Couldn't handle partially static grids
- All-or-nothing perturbation

**New system** (cell-level):
- Detects local boring regions
- Targeted perturbation
- Handles mixed dynamics (interesting + boring areas)

### Why These Parameters?

**Static threshold = 5**:
- Catches still lifes quickly
- Not too aggressive (allows short-lived stasis)

**Period threshold = 5 cycles**:
- Reliable detection (not false positives)
- Long enough to be "boring"
- Short enough to catch early

**Periods [2, 3, 4]**:
- Most common Game of Life oscillators
- Period-1 covered by static detection
- Periods >4 are rare and often interesting

**Perturb rate default = 30%**:
- Moderate intervention
- Enough to disrupt patterns
- Not so aggressive it dominates dynamics

---

## 📈 Performance

### Memory Usage
Per cell: ~100 bytes (history + counters)
- 60×60 grid: ~360 KB
- 120×120 grid: ~1.4 MB
- 240×240 grid: ~5.7 MB

Still very manageable for browser!

### Computation
Per step: O(rows × cols × history_length)
- Typical: 60×60 × 20 = 72,000 operations
- Fast enough for real-time

### Optimization
- History limited to `max(periods) × period_threshold + 1` steps
- Counters reset immediately when patterns break
- No full grid scanning except when needed

---

## 🎮 User Experience

### Behavior at Different Rates

| Rate | Behavior | Use Case |
|------|----------|----------|
| 0% | No perturbation | Pure Game of Life |
| 10% | Gentle nudges | Subtle anti-stagnation |
| 30% | Moderate | Balanced (default) |
| 50% | Aggressive | Keep things moving |
| 100% | Maximum | Chaos mode, toggle all boring cells |

### Observable Effects

**Low rate (10-20%)**:
- Occasional cell flips in static regions
- Subtle, gradual changes
- Near-natural dynamics

**Medium rate (30-50%)**:
- Regular perturbation of boring areas
- Good balance of order and chaos
- Recommended for most uses

**High rate (70-100%)**:
- Constant disruption
- Very dynamic, rarely static
- Good for demonstrations

---

## 🔧 Implementation Details

### Data Structures

**History Tracking**:
```python
self.history[r][c] = [0, 1, 0, 1, 0, 1, ...]  # Recent states
```

**Static Counting**:
```python
self.static_count[r][c] = 5  # 5 consecutive same states
```

**Period Counting**:
```python
self.period_counts[2][r][c] = 10  # 10 steps of period-2
self.period_counts[3][r][c] = 0   # No period-3 detected
```

### Pattern Detection Logic

**Static Detection**:
```python
if history[-1] == history[-2]:
    static_count += 1
else:
    static_count = 0
```

**Period Detection** (period p):
```python
if history[-1] == history[-1-p]:
    period_counts[p] += 1
else:
    period_counts[p] = 0
```

**Boring Cell Criteria**:
```python
if static_count >= static_threshold:
    return True  # Boring!
    
for p in periods_to_track:
    if period_counts[p] >= p * period_threshold:
        return True  # Boring!
```

### Perturbation Application

```python
boring_cells = cell_tracker.get_boring_cells()
num_to_perturb = int(len(boring_cells) * perturb_rate)
cells_to_toggle = random.sample(boring_cells, num_to_perturb)

for r, c in cells_to_toggle:
    grid.toggle(r, c)
    # Reset this cell's tracking
    cell_tracker.static_count[r][c] = 0
    for period in periods:
        cell_tracker.period_counts[period][r][c] = 0
```

---

## 🧪 Testing Scenarios

### Test 1: Still Life Detection
1. Create stable pattern (block, beehive)
2. Run simulation
3. After ~5 steps, should see cells toggle
4. Increase perturb rate → more toggles

### Test 2: Oscillator Detection
1. Create blinker (period-2)
2. Run simulation
3. After ~10 steps (5 cycles), should detect and perturb
4. Pattern should eventually change

### Test 3: Complex Dynamics
1. Create mix of static and active regions
2. Run with moderate perturb rate (30%)
3. Should see:
   - Active regions continue evolving
   - Static regions get occasional nudges
   - Overall interesting dynamics

### Test 4: Rate Sensitivity
1. Start with static grid
2. Try rates: 0%, 30%, 100%
3. Observe different perturbation intensities

---

## 🚀 Future Enhancements

### Possible Additions

1. **Visual Feedback**:
   - Highlight boring cells in different color
   - Show period detection in real-time
   - Display heatmap of static counts

2. **Advanced Detection**:
   - Track periods 5-10
   - Detect "gliders" (moving patterns)
   - Identify specific pattern types

3. **Smart Perturbation**:
   - Perturb edges of boring regions (more effective)
   - Add controlled noise (Gaussian, not uniform)
   - Temperature-based perturbation (simulated annealing)

4. **User Control**:
   - Adjustable thresholds via UI
   - Period selection checkboxes
   - Manual marking of boring cells

5. **Analytics**:
   - Show percentage of boring cells
   - Graph boring vs interesting over time
   - Export pattern statistics

---

## 📝 Files Modified

1. **`docs/index.html`**:
   - Added "Auto-Perturb Settings" box
   - Added perturb rate slider + input
   - Reorganized toggle settings

2. **`docs/app.py`**:
   - Added `CellTracker` class (~80 lines)
   - Implemented `apply_cell_level_perturbation()`
   - Integrated tracking into `step_once()`
   - Added perturb rate handlers
   - Updated grid resize to reset tracker

---

## Summary

This sophisticated auto-perturb system provides:

✨ **Elegant** - Clean class-based design  
🎯 **Targeted** - Cell-level, not grid-level  
🎛️ **Configurable** - Adjustable via UI  
⚡ **Efficient** - O(n²) per step  
🎮 **Effective** - Actually prevents stagnation  

The system is production-ready and extensible! 🚀

