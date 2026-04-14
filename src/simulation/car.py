"""
car.py
======
Simulation Module — Autonomous Vehicle Agent

Responsibilities:
  - Store car position, heading, speed
  - Follow a planned path waypoint by waypoint
  - Apply speed factor from DecisionMaker
  - Draw car as a rotated rectangle with heading indicator

Industry Pattern:
    Simulates the kinematic bicycle model used in Apollo, CARLA, and highway-env.
    Heading is computed from movement vector = smooth, realistic turning.
"""

import pygame
import math
from src.config import (
    CAR_SPEED, CAR_WIDTH, CAR_HEIGHT, WAYPOINT_RADIUS,
    GREEN, WHITE, START_POS,
)


class Car:
    """
    Autonomous vehicle agent that follows a waypoint path.

    Usage:
        car = Car(x, y)
        car.set_path(path)
        car.update(speed_factor=1.0)
        car.draw(screen)
    """

    def __init__(self, x: float = None, y: float = None):
        self.x: float = float(x if x is not None else START_POS[0])
        self.y: float = float(y if y is not None else START_POS[1])
        self._base_speed: float = CAR_SPEED

        self.path: list          = []
        self.target_index: int   = 0
        self.heading: float      = 0.0     # degrees, 0 = East
        self.speed: float        = 0.0     # current speed this frame

        self._trail: list        = []      # (x, y) history for trail rendering
        self._max_trail: int     = 80

    # ------------------------------------------------------------------
    def set_path(self, path: list) -> None:
        """Assign a new planned path. Resets target index."""
        self.path = list(path)
        self.target_index = 0

    # ------------------------------------------------------------------
    def update(self, speed_factor: float = 1.0) -> None:
        """
        Advance the car toward the next waypoint.

        Args:
            speed_factor : 0.0 (stop) → 1.0 (full speed) from DecisionMaker
        """
        self.speed = self._base_speed * speed_factor

        if not self.path or self.target_index >= len(self.path):
            self.speed = 0.0
            return

        target = self.path[self.target_index]
        dx = target[0] - self.x
        dy = target[1] - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < WAYPOINT_RADIUS:
            self.target_index += 1
            return

        if dist > 0 and self.speed > 0:
            norm_dx = dx / dist
            norm_dy = dy / dist
            self.heading = math.degrees(math.atan2(norm_dy, norm_dx))
            self.x += norm_dx * self.speed
            self.y += norm_dy * self.speed

        # Record trail
        self._trail.append((int(self.x), int(self.y)))
        if len(self._trail) > self._max_trail:
            self._trail.pop(0)

    # ------------------------------------------------------------------
    def get_pos(self) -> tuple:
        return (self.x, self.y)

    def dist_to_goal(self, goal: tuple) -> float:
        return math.sqrt((self.x - goal[0]) ** 2 + (self.y - goal[1]) ** 2)

    def path_remaining(self) -> int:
        return max(0, len(self.path) - self.target_index)

    def reached_goal(self) -> bool:
        return self.target_index >= len(self.path) and len(self.path) > 0

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the car as a rotated rectangle with heading arrow."""
        self._draw_trail(screen)
        self._draw_body(screen)

    # ------------------------------------------------------------------
    def _draw_trail(self, screen: pygame.Surface) -> None:
        """Fading motion trail behind the car."""
        n = len(self._trail)
        for i, (tx, ty) in enumerate(self._trail):
            alpha = int(255 * (i / max(n, 1)))
            r = max(2, int(6 * (i / max(n, 1))))
            color = (0, max(60, int(180 * i / max(n, 1))), max(60, int(80 * i / max(n, 1))))
            pygame.draw.circle(screen, color, (tx, ty), r)

    # ------------------------------------------------------------------
    def _draw_body(self, screen: pygame.Surface) -> None:
        """Draw rotated car rectangle + heading indicator arrow."""
        cx, cy = int(self.x), int(self.y)
        angle_rad = math.radians(self.heading)

        # Corner offsets
        hw = CAR_WIDTH  // 2
        hh = CAR_HEIGHT // 2

        corners_local = [
            (-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh),
        ]
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        corners_world = [
            (cx + lx * cos_a - ly * sin_a,
             cy + lx * sin_a + ly * cos_a)
            for lx, ly in corners_local
        ]

        pygame.draw.polygon(screen, GREEN, corners_world)
        pygame.draw.polygon(screen, WHITE, corners_world, 1)

        # Heading arrow (front indicator dot)
        front_x = cx + (hw + 4) * cos_a
        front_y = cy + (hw + 4) * sin_a
        pygame.draw.circle(screen, WHITE, (int(front_x), int(front_y)), 3)