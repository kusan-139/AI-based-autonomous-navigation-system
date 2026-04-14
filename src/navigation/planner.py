"""
planner.py
==========
Navigation Module — A* Path Planning

Responsibilities:
  - Compute the shortest collision-free path on a discrete grid
  - Support diagonal movement (8-directional) for smoother paths
  - Snap start/goal to nearest grid cell automatically
  - Accept an obstacle set (grid-snapped pixel coordinates)

Industry Pattern:
    A* is the foundational global planner in most AV systems.
    Apollo's DP Planner is a cost-function variant of A*.
    This implementation mirrors the core algorithm used in introductory
    AV courses (Udacity, MIT 6.832) with 8-directional movement.
"""

import heapq
import math
from src.config import GRID_SIZE, WIDTH, HEIGHT


def heuristic(a: tuple, b: tuple) -> float:
    """
    Octile distance heuristic — admissible for 8-directional grids.
    More accurate than Manhattan for diagonal movement.
    """
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy)


def snap_to_grid(pos: tuple, grid_size: int = GRID_SIZE) -> tuple:
    """Snap a pixel position to the nearest grid cell origin."""
    return (
        round(pos[0] / grid_size) * grid_size,
        round(pos[1] / grid_size) * grid_size,
    )


def astar(
    start:     tuple,
    goal:      tuple,
    obstacles: set,
    grid_size: int = GRID_SIZE,
) -> list:
    """
    A* shortest path on a grid.

    Args:
        start     : (x, y) pixel start position (auto-snapped to grid)
        goal      : (x, y) pixel goal position  (auto-snapped to grid)
        obstacles : Set of (gx, gy) impassable grid cells
        grid_size : Grid cell size in pixels

    Returns:
        Ordered list of (x, y) waypoints from start → goal,
        or empty list [] if no path exists.
    """
    start = snap_to_grid(start, grid_size)
    goal  = snap_to_grid(goal,  grid_size)

    # 8-directional movement (cardinal + diagonal)
    gs   = grid_size
    diag = int(gs * math.sqrt(2))
    NEIGHBORS = [
        (gs,  0,  gs), (-gs,  0,  gs),  # E, W
        (0,  gs,  gs), (0,  -gs,  gs),  # S, N
        (gs,  gs, diag), (-gs, gs,  diag),  # SE, SW
        (gs, -gs, diag), (-gs, -gs, diag),  # NE, NW
    ]

    open_set = []
    heapq.heappush(open_set, (0.0, start))

    came_from: dict = {}
    g_score:   dict = {start: 0.0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            return _reconstruct(came_from, current)

        cx, cy = current
        for dx, dy, cost in NEIGHBORS:
            nx, ny = cx + dx, cy + dy
            neighbor = (nx, ny)

            # Bounds check
            if not (0 <= nx < WIDTH and 0 <= ny < HEIGHT):
                continue

            if neighbor in obstacles:
                continue

            # For diagonal moves, also check that corridor is clear
            if dx != 0 and dy != 0:
                if (cx + dx, cy) in obstacles or (cx, cy + dy) in obstacles:
                    continue

            tentative_g = g_score[current] + cost

            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor]   = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))

    return []    # No path found


def _reconstruct(came_from: dict, current: tuple) -> list:
    """Trace back from goal to start and return ordered path."""
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.append(current)
    return path[::-1]