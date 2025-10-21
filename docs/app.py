from js import document, window
from pyodide.ffi import create_proxy
import random
from life.engine import LifeGrid, PatternMonitor
from life.utils import seed_random, inject_noise, perturb_oscillation

# --- Canvas / UI wiring ---
canvas = document.getElementById("board")
ctx = canvas.getContext("2d")

playpause_btn = document.getElementById("playPause")
step_btn      = document.getElementById("step")
clear_btn     = document.getElementById("clear")
seed_btn      = document.getElementById("seed")
noise_btn     = document.getElementById("noise")
status_display = document.getElementById("statusDisplay")

speed_rng  = document.getElementById("speed")
speed_input = document.getElementById("speedInput")

density_rng = document.getElementById("density")
density_input = document.getElementById("densityInput")

toroidal_chk = document.getElementById("toroidal")
auto_perturb_chk = document.getElementById("autoPerturb")

perturbrate_rng = document.getElementById("perturbRate")
perturbrate_input = document.getElementById("perturbRateInput")

gridsize_rng = document.getElementById("gridSize")
gridsize_input = document.getElementById("gridSizeInput")
gridsize_val = document.getElementById("gridSizeVal")

# Global state
grid_size = int(gridsize_rng.value)
speed_ms = int(speed_rng.value)
density = int(density_rng.value) / 100.0
perturb_rate = int(perturbrate_rng.value) / 100.0
running = False
timer_id = None
status_timer_id = None

# Activity tracking for "grid died" detection
last_grid_hash = None
no_activity_steps = 0

# Calculate cell size and adjust canvas to fit grid perfectly
cell_size = canvas.width // grid_size

# Resize canvas to match grid dimensions exactly
canvas.width = grid_size * cell_size
canvas.height = grid_size * cell_size

# Initialize grid
grid = LifeGrid(grid_size, grid_size, toroidal=True)
monitor = PatternMonitor(window=64, min_repeats=3)
seed_random(grid, density=density)

# =============================================================================
# STATUS MESSAGE SYSTEM
# =============================================================================
# Configure status messages: [text, color, background, display_time_seconds]
# Colors use CSS color values
STATUS_MESSAGES = {
    "running": ["Running!", "#10b981", "#064e3b", 2],      # Green
    "paused": ["Paused", "#ef4444", "#7f1d1d", 2],         # Red
    "stopped": ["Stopped", "#ef4444", "#7f1d1d", 2],       # Red
    "cleared": ["Grid Cleared", "#6b7280", "#1f2937", 2],  # Gray
    "randomized": ["Randomized!", "#3b82f6", "#1e3a8a", 2], # Blue
    "noise": ["Noise Injected!", "#f59e0b", "#78350f", 2], # Orange
    "grid_died": ["Grid died: no activity detected. Press Play to restart!", "#ef4444", "#7f1d1d", 5],  # Red, longer display
    "stepped": ["Stepped", "#8b5cf6", "#4c1d95", 1.5],     # Purple
}

def show_status(status_key):
    """
    Display a status message with color and auto-fade.
    status_key: key from STATUS_MESSAGES dict
    """
    global status_timer_id
    
    if status_key not in STATUS_MESSAGES:
        return
    
    text, text_color, bg_color, display_time = STATUS_MESSAGES[status_key]
    
    # Clear any existing timer
    if status_timer_id is not None:
        window.clearTimeout(status_timer_id)
        status_timer_id = None
    
    # Set message content and styling
    status_display.innerText = text
    status_display.style.color = text_color
    status_display.style.backgroundColor = bg_color
    status_display.className = "status-display"
    
    # Schedule fade-out
    def fade_status():
        global status_timer_id
        status_display.className = "status-display hidden"
        status_timer_id = None
    
    status_timer_id = window.setTimeout(
        create_proxy(fade_status), 
        int(display_time * 1000)
    )

# =============================================================================

# Speed label removed - now showing actual ms value

def is_grid_dead():
    """Check if grid has no alive cells - OPTIMIZED: early exit"""
    # OPTIMIZATION: Exit as soon as we find any alive cell (don't scan entire grid)
    for r in range(grid.cfg.rows):
        for c in range(grid.cfg.cols):
            if grid.grid[r][c] == 1:
                return False  # Found alive cell, grid is not dead!
    return True  # Scanned everything, no alive cells found

def update_button_state():
    """Update play/pause button appearance based on state"""
    if is_grid_dead():
        playpause_btn.className = "play-btn dead"
        playpause_btn.innerText = "▶ Play"
    elif running:
        playpause_btn.className = "play-btn playing"
        playpause_btn.innerText = "⏸ Pause"
    else:
        playpause_btn.className = "play-btn paused"
        playpause_btn.innerText = "▶ Play"

def resize_canvas():
    """Resize canvas to exactly fit the grid with no empty space"""
    canvas.width = grid.cfg.cols * cell_size
    canvas.height = grid.cfg.rows * cell_size

def draw():
    """Render the grid to canvas - OPTIMIZED: no resize, no gridlines"""
    # OPTIMIZATION: Don't resize canvas every frame (only when grid size changes)
    # OPTIMIZATION: Skip gridlines for performance (122 stroke operations saved!)
    
    # Clear canvas
    ctx.fillStyle = "#0a0d12"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    # Draw alive cells only
    ctx.fillStyle = "#4fd1ff"
    for r in range(grid.cfg.rows):
        for c in range(grid.cfg.cols):
            if grid.grid[r][c] == 1:
                ctx.fillRect(c * cell_size + 1, r * cell_size + 1, cell_size - 1, cell_size - 1)

def step_once(perturb_if_repeating=True):
    """Execute one generation step - OPTIMIZED: single hash computation"""
    global running, last_grid_hash, no_activity_steps
    
    # OPTIMIZATION: Compute hash ONCE and reuse for both pattern detection AND activity check
    h = grid.state_hash()
    
    # Pattern detection for auto-perturb
    period = monitor.observe(h)
    if perturb_if_repeating and auto_perturb_chk.checked and period is not None:
        # Use perturb_rate to control how aggressive the perturbation is
        from life.utils import perturb_oscillation
        # Apply perturbation based on rate (higher rate = more cells perturbed)
        num_perturbs = max(1, int(perturb_rate * 5))  # 0-5 perturbations
        for _ in range(num_perturbs):
            perturb_oscillation(grid, radius=2)
    
    # Activity detection (reuse the same hash!)
    if last_grid_hash is not None and h == last_grid_hash:
        no_activity_steps += 1
    else:
        no_activity_steps = 0
    last_grid_hash = h
    
    grid.step()
    draw()
    
    # Check for death or no activity
    if is_grid_dead():
        if running:
            running = False
            if timer_id is not None:
                window.clearTimeout(timer_id)
            update_button_state()
            show_status("grid_died")
    elif no_activity_steps >= 2:
        # No activity detected (still life or period-1 oscillator)
        if running:
            running = False
            if timer_id is not None:
                window.clearTimeout(timer_id)
            update_button_state()
            show_status("grid_died")

def run_loop(*args):
    """Main animation loop"""
    global timer_id
    if not running:
        return
    
    step_once(perturb_if_repeating=True)
    
    # Schedule next iteration
    if running:  # Check again in case grid died
        timer_id = window.setTimeout(create_proxy(run_loop), speed_ms)

def toggle_play_pause(*args):
    """Toggle between play and pause states"""
    global running, timer_id, last_grid_hash, no_activity_steps
    
    # If grid is dead and not running, auto-seed
    if is_grid_dead() and not running:
        seed_random(grid, density=density)
        draw()
        # Reset activity tracking
        last_grid_hash = None
        no_activity_steps = 0
    
    if running:
        # Pause
        running = False
        if timer_id is not None:
            window.clearTimeout(timer_id)
            timer_id = None
        show_status("paused")
    else:
        # Play
        # Reset activity tracking when starting
        last_grid_hash = None
        no_activity_steps = 0
        running = True
        show_status("running")
        timer_id = window.setTimeout(create_proxy(run_loop), speed_ms)
    
    update_button_state()

def board_click(evt):
    """Handle cell click to toggle state"""
    global last_grid_hash, no_activity_steps
    rect = canvas.getBoundingClientRect()
    x = evt.clientX - rect.left
    y = evt.clientY - rect.top
    c = int(x // cell_size)
    r = int(y // cell_size)
    if 0 <= r < grid.cfg.rows and 0 <= c < grid.cfg.cols:
        grid.toggle(r, c)
        draw()
        update_button_state()
        # Reset activity tracking when user modifies grid
        last_grid_hash = None
        no_activity_steps = 0

def do_step(*args):
    """Single step without auto-perturb - also pauses simulation"""
    global running, timer_id
    
    # Pause if running
    if running:
        running = False
        if timer_id is not None:
            window.clearTimeout(timer_id)
            timer_id = None
    
    step_once(perturb_if_repeating=False)
    update_button_state()
    show_status("stepped")

def do_clear(*args):
    """Clear the grid"""
    global running, timer_id, last_grid_hash, no_activity_steps
    # Stop if running
    if running:
        running = False
        if timer_id is not None:
            window.clearTimeout(timer_id)
            timer_id = None
    
    grid.clear()
    draw()
    update_button_state()
    show_status("cleared")
    # Reset activity tracking
    last_grid_hash = None
    no_activity_steps = 0

def do_seed(*args):
    """Randomize grid with current density"""
    global last_grid_hash, no_activity_steps
    seed_random(grid, density=density)
    draw()
    update_button_state()
    show_status("randomized")
    # Reset activity tracking
    last_grid_hash = None
    no_activity_steps = 0

def do_noise(*args):
    """Inject random noise (2% of cells)"""
    global last_grid_hash, no_activity_steps
    inject_noise(grid, fraction=0.02)
    draw()
    update_button_state()
    show_status("noise")
    # Reset activity tracking when noise is added
    last_grid_hash = None
    no_activity_steps = 0

def on_speed_change(evt):
    """Handle speed slider change (inverted: right = faster = lower ms)"""
    global speed_ms
    # Invert the slider: max value = min ms
    slider_val = int(speed_rng.value)
    max_val = int(speed_rng.max)
    min_val = int(speed_rng.min)
    # Invert: when slider is at max, use min ms and vice versa
    speed_ms = max_val + min_val - slider_val
    
    # Update input box
    speed_input.value = speed_ms
    
    # If running, restart with new speed
    if running:
        global timer_id
        if timer_id is not None:
            window.clearTimeout(timer_id)
        timer_id = window.setTimeout(create_proxy(run_loop), speed_ms)

def on_speed_input_change(evt):
    """Handle speed input box change"""
    global speed_ms
    try:
        val = int(speed_input.value)
        val = max(5, min(600, val))  # Clamp to 5-600
        speed_ms = val
        speed_input.value = val
        
        # Update slider (inverted)
        max_val = int(speed_rng.max)
        min_val = int(speed_rng.min)
        speed_rng.value = max_val + min_val - val
        
        # If running, restart with new speed
        if running:
            global timer_id
            if timer_id is not None:
                window.clearTimeout(timer_id)
            timer_id = window.setTimeout(create_proxy(run_loop), speed_ms)
    except:
        pass

def on_density_change(evt):
    """Handle density slider change"""
    global density
    val = int(density_rng.value)
    density = val / 100.0
    density_input.value = val

def on_density_input_change(evt):
    """Handle density input box change"""
    global density
    try:
        val = int(density_input.value)
        val = max(0, min(99, val))  # Clamp to 0-99
        density = val / 100.0
        density_input.value = val
        density_rng.value = val
    except:
        pass

def on_toroidal_change(evt):
    """Handle toroidal checkbox change"""
    grid.cfg.toroidal = bool(toroidal_chk.checked)

def on_perturbrate_change(evt):
    """Handle perturb rate slider change"""
    global perturb_rate
    val = int(perturbrate_rng.value)
    perturb_rate = val / 100.0
    perturbrate_input.value = val

def on_perturbrate_input_change(evt):
    """Handle perturb rate input box change"""
    global perturb_rate
    try:
        val = int(perturbrate_input.value)
        val = max(0, min(100, val))  # Clamp to 0-100
        perturb_rate = val / 100.0
        perturbrate_input.value = val
        perturbrate_rng.value = val
    except:
        pass

def resize_grid(new_size):
    """Resize grid to new size (shared logic)"""
    global grid_size, cell_size, grid, monitor, running, timer_id, last_grid_hash, no_activity_steps
    
    # Stop animation if running
    was_running = running
    if running:
        running = False
        if timer_id is not None:
            window.clearTimeout(timer_id)
            timer_id = None
    
    # Update display
    gridsize_val.innerText = f"{new_size}"
    gridsize_input.value = new_size
    gridsize_rng.value = new_size
    
    # Calculate new cell size to fit canvas (use original canvas max dimension)
    max_canvas_size = 720
    new_cell_size = max_canvas_size // new_size
    
    # Create new grid
    tor = bool(toroidal_chk.checked)
    new_grid = LifeGrid(new_size, new_size, toroidal=tor)
    
    # Copy center region from old grid if possible
    old_size = grid.cfg.rows
    copy_size = min(old_size, new_size)
    old_offset = (old_size - copy_size) // 2
    new_offset = (new_size - copy_size) // 2
    
    for r in range(copy_size):
        for c in range(copy_size):
            if 0 <= old_offset + r < old_size and 0 <= old_offset + c < old_size:
                val = grid.grid[old_offset + r][old_offset + c]
                new_grid.grid[new_offset + r][new_offset + c] = val
    
    # Update globals
    grid_size = new_size
    cell_size = new_cell_size
    grid = new_grid
    monitor = PatternMonitor(window=64, min_repeats=3)
    
    
    # Reset activity tracking
    last_grid_hash = None
    no_activity_steps = 0
    
    # OPTIMIZATION: Resize canvas only when grid size actually changes
    resize_canvas()
    
    draw()
    update_button_state()
    
    # Resume if was running
    if was_running and not is_grid_dead():
        running = True
        show_status("running")
        timer_id = window.setTimeout(create_proxy(run_loop), speed_ms)
        update_button_state()

def on_gridsize_change(evt):
    """Handle grid size slider change"""
    new_size = int(gridsize_rng.value)
    resize_grid(new_size)

def on_gridsize_input_change(evt):
    """Handle grid size input box change"""
    try:
        val = int(gridsize_input.value)
        val = max(2, min(240, val))  # Clamp to 2-240
        resize_grid(val)
    except:
        pass

# Wire events
playpause_btn.addEventListener("click", create_proxy(toggle_play_pause))
step_btn.addEventListener("click", create_proxy(do_step))
clear_btn.addEventListener("click", create_proxy(do_clear))
seed_btn.addEventListener("click", create_proxy(do_seed))
noise_btn.addEventListener("click", create_proxy(do_noise))

speed_rng.addEventListener("input", create_proxy(on_speed_change))
speed_input.addEventListener("change", create_proxy(on_speed_input_change))
density_rng.addEventListener("input", create_proxy(on_density_change))
density_input.addEventListener("change", create_proxy(on_density_input_change))
toroidal_chk.addEventListener("change", create_proxy(on_toroidal_change))
perturbrate_rng.addEventListener("input", create_proxy(on_perturbrate_change))
perturbrate_input.addEventListener("change", create_proxy(on_perturbrate_input_change))
gridsize_rng.addEventListener("input", create_proxy(on_gridsize_change))
gridsize_input.addEventListener("change", create_proxy(on_gridsize_input_change))

canvas.addEventListener("click", create_proxy(board_click))

# Initialize display
resize_canvas()  # Set initial canvas size
draw()
update_button_state()

# Set initial values
on_speed_change(None)
on_density_change(None)
on_perturbrate_change(None)
gridsize_val.innerText = f"{grid_size}"
