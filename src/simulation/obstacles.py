"""
obstacles.py
============
Simulation Module — Dynamic Obstacle Manager

Responsibilities:
  - Maintain a list of runtime dynamic obstacles (not from YOLO)
  - Optionally add randomly generated obstacles for simulation diversity
  - Draw obstacles on the Pygame screen as animated red polygons
  - Export obstacle centroids for the sensor and avoidance modules
"""

import pygame
import math
import random
from src.config import RED, GRID_SIZE, WIDTH, HEIGHT


class ObstacleManager:
    """
    Manages dynamic obstacles in the simulation environment.

    Usage:
        obs_mgr = ObstacleManager()
        obs_mgr.add_random(count=6)
        obs_mgr.draw(screen, frame_id)
        centroids = obs_mgr.get_centroids()
    """

    def __init__(self):
        self._obstacles: list[dict] = []   # each: {x, y, w, h, color}

    # ------------------------------------------------------------------
    def add(self, x: int, y: int, w: int = 20, h: int = 20) -> None:
        """Add a single static obstacle at (x, y)."""
        self._obstacles.append({
            "x": x, "y": y, "w": w, "h": h,
            "color": (200 + random.randint(0, 55), random.randint(30, 60), random.randint(30, 60))
        })

    # ------------------------------------------------------------------
    def add_random(self, count: int = 5, seed: int = 42) -> None:
        """
        Place `count` random obstacles on road segments.
        Uses a fixed seed for reproducibility across runs.
        """
        rng = random.Random(seed)
        # Road center coordinates to scatter obstacles near roads
        road_ys  = [100, 320, 540]
        road_xs  = [100, 380, 660]

        placed = 0
        attempts = 0
        while placed < count and attempts < 200:
            attempts += 1
            # Pick a road axis randomly
            if rng.random() < 0.5:
                x = rng.randint(80, WIDTH - 80)
                y = rng.choice(road_ys) + rng.randint(-20, 20)
            else:
                x = rng.choice(road_xs) + rng.randint(-20, 20)
                y = rng.randint(80, HEIGHT - 80)

            # Don't place at start or goal area
            if math.sqrt((x - 60) ** 2 + (y - 60) ** 2) < 80:
                continue
            if math.sqrt((x - 820) ** 2 + (y - 570) ** 2) < 80:
                continue

            self.add(x, y)
            placed += 1

    # ------------------------------------------------------------------
    def get_centroids(self) -> list[tuple]:
        """Return centroid (x, y) of each obstacle."""
        return [(o["x"] + o["w"] // 2, o["y"] + o["h"] // 2) for o in self._obstacles]

    # ------------------------------------------------------------------
    def get_grid_cells(self) -> set:
        """
        Return grid-snapped obstacle positions for the path planner.
        Expands each obstacle into its covered grid cells.
        """
        cells = set()
        for o in self._obstacles:
            gx = round(o["x"] / GRID_SIZE) * GRID_SIZE
            gy = round(o["y"] / GRID_SIZE) * GRID_SIZE
            cells.add((gx, gy))
        return cells

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface, frame_id: int = 0) -> None:
        """
        Draw obstacles with a subtle pulsing glow effect.
        """
        for o in self._obstacles:
            pulse = abs(math.sin(frame_id * 0.05)) * 20
            color = (
                min(255, o["color"][0] + int(pulse)),
                o["color"][1],
                o["color"][2],
            )
            rect = pygame.Rect(o["x"] - o["w"] // 2, o["y"] - o["h"] // 2, o["w"], o["h"])
            pygame.draw.rect(screen, color, rect, border_radius=4)
            pygame.draw.rect(screen, (255, 120, 120), rect, 1, border_radius=4)