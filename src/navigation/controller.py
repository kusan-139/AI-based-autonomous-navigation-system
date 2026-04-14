"""
controller.py
=============
Navigation Module — Path Tracking Controller

Responsibilities:
  - Provide a clean interface to assign a path to the car
  - Smoothly interpolate path waypoints to reduce zig-zag movement
  - (Future) Implement PID-based steering correction

Industry Pattern:
    Real AV stacks use Stanley Controller or Pure Pursuit for path tracking.
    This module implements a simplified pure-pursuit equivalent: selecting
    the nearest lookahead point and steering toward it.
"""

import math
from src.config import GRID_SIZE


def assign_path(car, path: list) -> None:
    """
    Assign a computed path to the car.
    Smooths the path to reduce angular jitter.

    Args:
        car  : Car instance from simulation/car.py
        path : List of (x, y) waypoints from A* planner
    """
    smoothed = smooth_path(path)
    car.set_path(smoothed)


def smooth_path(path: list, weight_smooth: float = 0.5, weight_data: float = 0.5, tolerance: float = 0.001) -> list:
    """
    Gradient descent path smoothing.
    Reduces sharp corners while keeping the path close to the original.

    Args:
        path           : Raw A* path as list of (x, y) tuples
        weight_smooth  : How much to pull toward neighboring points
        weight_data    : How much to stay close to original path
        tolerance      : Convergence threshold

    Returns:
        Smoothed path as list of (x, y) float tuples.
    """
    if len(path) < 3:
        return path

    # Copy as floats
    smooth = [[float(p[0]), float(p[1])] for p in path]
    orig   = [[float(p[0]), float(p[1])] for p in path]

    change = tolerance + 1.0
    while change > tolerance:
        change = 0.0
        for i in range(1, len(smooth) - 1):
            for dim in range(2):
                old = smooth[i][dim]
                smooth[i][dim] += (
                    weight_data   * (orig[i][dim]      - smooth[i][dim]) +
                    weight_smooth * (smooth[i-1][dim] + smooth[i+1][dim] - 2 * smooth[i][dim])
                )
                change += abs(smooth[i][dim] - old)

    return [(int(p[0]), int(p[1])) for p in smooth]