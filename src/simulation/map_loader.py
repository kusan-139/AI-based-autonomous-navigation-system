"""
map_loader.py
=============
Simulation Module — Grid Map Generation & Road Layout

Responsibilities:
  - Generate a top-down road grid procedurally (no external PNG needed)
  - Define drivable (road) and non-drivable (wall/building) cells
  - Provide obstacle set from wall cells for path planner
  - Render road, lanes, and buildings onto the Pygame surface

Industry Pattern:
    Simulators like CARLA and Gazebo load OpenDRIVE maps. This module
    implements a simplified procedural equivalent — a grid-based urban
    layout — suitable for A* path planning and sensor simulation.
"""

import pygame
from src.config import (
    WIDTH, HEIGHT, GRID_SIZE,
    BLACK, GRAY, DARK_GRAY, YELLOW, WHITE, LIGHT_GRAY,
)

# Road layout: list of (x, y, width, height) road rectangles in pixels
_ROADS = [
    # Horizontal roads
    (0,    60,  WIDTH, 80),     # Top horizontal
    (0,   280,  WIDTH, 80),     # Mid horizontal
    (0,   500,  WIDTH, 80),     # Bottom horizontal

    # Vertical roads
    (60,    0,  80, HEIGHT),    # Left vertical
    (340,   0,  80, HEIGHT),    # Mid-left vertical
    (620,   0,  80, HEIGHT),    # Mid-right vertical
    (820,   0,  80, HEIGHT),    # Right vertical
]


def _is_on_road(x: int, y: int) -> bool:
    """Check if pixel (x,y) falls inside any road rectangle."""
    for rx, ry, rw, rh in _ROADS:
        if rx <= x < rx + rw and ry <= y < ry + rh:
            return True
    return False


def build_obstacle_set() -> set:
    """
    Return the set of grid-snapped obstacle (wall) positions.
    Any grid cell NOT on a road is treated as an obstacle.

    Returns:
        set of (gx, gy) tuples — impassable cells for A* planner
    """
    obstacles = set()
    cols = WIDTH  // GRID_SIZE
    rows = HEIGHT // GRID_SIZE

    for col in range(cols):
        for row in range(rows):
            gx = col * GRID_SIZE
            gy = row * GRID_SIZE
            # Sample the center of the grid cell
            cx = gx + GRID_SIZE // 2
            cy = gy + GRID_SIZE // 2
            if not _is_on_road(cx, cy):
                obstacles.add((gx, gy))
    return obstacles


def draw_map(screen: pygame.Surface) -> None:
    """
    Render the full road network, lane markings, and city blocks
    onto the given Pygame surface.
    """
    # 1. Fill background (buildings / grass)
    screen.fill((30, 30, 38))

    # 2. Draw city blocks (slightly lighter background rectangles)
    block_color = (42, 42, 55)
    # Implicit — background already serves as block color

    # 3. Draw road surfaces
    for rx, ry, rw, rh in _ROADS:
        pygame.draw.rect(screen, GRAY, (rx, ry, rw, rh))
        pygame.draw.rect(screen, DARK_GRAY, (rx, ry, rw, rh), 2)

    # 4. Draw lane center dashes (yellow dashed lines)
    _draw_lane_markings(screen)

    # 5. Draw grid overlay (very subtle, for debugging)
    # _draw_grid(screen)  # Uncomment to see grid cells


def _draw_lane_markings(screen: pygame.Surface) -> None:
    """Draw yellow dashed center lines on all roads."""
    dash_len  = 20
    gap_len   = 15
    thickness = 2

    for rx, ry, rw, rh in _ROADS:
        if rw > rh:
            # Horizontal road → horizontal dashes along center
            cy = ry + rh // 2
            x = rx
            while x < rx + rw:
                pygame.draw.line(screen, YELLOW, (x, cy), (min(x + dash_len, rx + rw), cy), thickness)
                x += dash_len + gap_len
        else:
            # Vertical road → vertical dashes along center
            cx = rx + rw // 2
            y = ry
            while y < ry + rh:
                pygame.draw.line(screen, YELLOW, (cx, y), (cx, min(y + dash_len, ry + rh)), thickness)
                y += dash_len + gap_len


def _draw_grid(screen: pygame.Surface) -> None:
    """Render the planning grid (debug helper)."""
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, LIGHT_GRAY, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, LIGHT_GRAY, (0, y), (WIDTH, y), 1)
