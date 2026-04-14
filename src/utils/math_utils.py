"""
math_utils.py
=============
Utility Module — Common Math Helpers

Shared mathematical functions used across the navigation and simulation modules.
Keeping these here avoids circular imports and code duplication.
"""

import math


def distance(p1: tuple, p2: tuple) -> float:
    """Euclidean distance between two 2-D points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def normalize_angle(angle: float) -> float:
    """
    Normalize an angle (radians) to [-π, π].
    Prevents angle wrap-around issues in heading computations.
    """
    return math.atan2(math.sin(angle), math.cos(angle))


def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp a value to [lo, hi]."""
    return max(lo, min(hi, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b by factor t ∈ [0, 1]."""
    return a + clamp(t, 0.0, 1.0) * (b - a)


def angle_to_target(from_pos: tuple, to_pos: tuple) -> float:
    """
    Compute the heading angle (degrees, 0=East) from from_pos to to_pos.
    Returns degrees in [−180, 180].
    """
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]
    return math.degrees(math.atan2(dy, dx))


def snap_to_grid(pos: tuple, grid_size: int) -> tuple:
    """Snap a (x, y) pixel position to the nearest grid cell origin."""
    return (
        round(pos[0] / grid_size) * grid_size,
        round(pos[1] / grid_size) * grid_size,
    )


def points_within_radius(center: tuple, radius: float, points: set) -> list:
    """
    Filter a set of (x, y) points to only those within `radius` of `center`.
    Returns a sorted list by distance (nearest first).
    """
    result = []
    cx, cy = center
    for (px, py) in points:
        d = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
        if d <= radius:
            result.append(((px, py), d))
    result.sort(key=lambda x: x[1])
    return result