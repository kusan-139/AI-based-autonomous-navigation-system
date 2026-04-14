"""
sensor.py
=========
Simulation Module — Virtual Ultrasonic / Proximity Sensor

Responsibilities:
  - Cast multiple sensor rays from the car's position at various angles
  - Detect the nearest obstacle along each ray within SENSOR_RANGE
  - Return per-ray readings: (angle, hit_point, distance)
  - Render sensor rays on the Pygame screen (orange = active, dim = inactive)

Industry Pattern:
    Simulates the ultrasonic sensor array found on most autonomous platforms
    (e.g., Waymo's radar rings, TurtleBot's RPLidar).
    Ray-casting against a discrete obstacle grid is the standard simulation
    approach used in ROS Gazebo and CARLA.
"""

import math
import pygame
from src.config import (
    SENSOR_RANGE, SENSOR_ANGLES, DANGER_THRESHOLD,
    ORANGE, RED, GRAY,
)


class VirtualSensor:
    """
    Multi-ray proximity sensor attached to the car.

    Usage:
        sensor = VirtualSensor()
        readings = sensor.cast(car_x, car_y, heading_deg, obstacles)
        sensor.draw(screen, car_x, car_y, readings)
    """

    def __init__(self):
        self.range: int   = SENSOR_RANGE
        self.angles: list = SENSOR_ANGLES      # relative beam angles in degrees
        self.step: int    = 4                  # ray march step size in pixels

    # ------------------------------------------------------------------
    def cast(
        self,
        car_x: float,
        car_y: float,
        heading_deg: float,
        obstacles: set,
    ) -> list[dict]:
        """
        Cast sensor rays from the car position.

        Args:
            car_x, car_y  : car's pixel position
            heading_deg   : car's current heading in degrees (0 = east)
            obstacles     : set of (x, y) obstacle pixel positions

        Returns:
            List of dicts per beam:
            {
                'angle':    float  — absolute beam angle in degrees
                'distance': float  — distance to hit (SENSOR_RANGE if no hit)
                'hit':      bool   — True if obstacle detected
                'hit_point': (x,y) — pixel coords of first hit (or beam tip)
            }
        """
        readings = []
        for rel_angle in self.angles:
            abs_angle_rad = math.radians(heading_deg + rel_angle)
            hit, dist, hit_pt = self._march(car_x, car_y, abs_angle_rad, obstacles)
            readings.append({
                "angle":     heading_deg + rel_angle,
                "distance":  dist,
                "hit":       hit,
                "hit_point": hit_pt,
            })
        return readings

    # ------------------------------------------------------------------
    def _march(
        self,
        ox: float, oy: float,
        angle_rad: float,
        obstacles: set,
    ) -> tuple:
        """
        March a single ray until it hits an obstacle or exceeds range.

        Returns:
            (hit: bool, distance: float, hit_point: (x,y))
        """
        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)

        for d in range(0, self.range, self.step):
            px = int(ox + dx * d)
            py = int(oy + dy * d)

            # Check against obstacle set
            if (px, py) in obstacles:
                return True, float(d), (px, py)

            # Also check a small radius neighbourhood (grid-snapped)
            for nx, ny in [(px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)]:
                if (nx, ny) in obstacles:
                    return True, float(d), (nx, ny)

        # No hit
        tip = (int(ox + dx * self.range), int(oy + dy * self.range))
        return False, float(self.range), tip

    # ------------------------------------------------------------------
    def nearest_distance(self, readings: list[dict]) -> float:
        """Return the minimum distance across all sensor rays."""
        if not readings:
            return float(self.range)
        return min(r["distance"] for r in readings)

    # ------------------------------------------------------------------
    def any_danger(self, readings: list[dict]) -> bool:
        """True if any beam reads below DANGER_THRESHOLD."""
        return any(r["hit"] and r["distance"] <= DANGER_THRESHOLD for r in readings)

    # ------------------------------------------------------------------
    def draw(
        self,
        screen: pygame.Surface,
        car_x: float,
        car_y: float,
        readings: list[dict],
    ) -> None:
        """
        Render sensor beams on the Pygame screen.
          - Orange thin line = no hit
          - Red pulsing dot  = obstacle hit
        """
        cx, cy = int(car_x), int(car_y)

        for r in readings:
            hx, hy = r["hit_point"]
            if r["hit"]:
                color = (220, 60, 60)    # red beam
                pygame.draw.line(screen, color, (cx, cy), (hx, hy), 1)
                pygame.draw.circle(screen, (255, 80, 80), (hx, hy), 5)
            else:
                color = (*ORANGE, 80)    # dim orange — no alpha in pygame lines
                pygame.draw.line(screen, ORANGE, (cx, cy), (hx, hy), 1)
