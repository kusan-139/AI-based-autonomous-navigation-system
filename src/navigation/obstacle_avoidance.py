"""
obstacle_avoidance.py
=====================
Navigation Module — Dynamic Obstacle Avoidance & Path Replanning

Responsibilities:
  - When DecisionMaker triggers AVOID state, expand obstacle buffer and replan
  - Maintain a list of dynamic obstacles discovered at runtime
  - Merge static (YOLO-detected) and dynamic obstacles into a unified grid
  - Return a new safe path using A* with expanded safety margins

Industry Pattern:
    Real AV systems use Dynamic Window Approach (DWA) or RRT* for replanning.
    This module implements a simpler but practically effective approach:
    inflating obstacle footprints and re-running A* — identical in concept
    to how Apollo's EM Planner handles unexpected static obstacles.
"""

import math
from src.navigation.planner import astar
from src.config import GRID_SIZE, OBSTACLE_RADIUS


class ObstacleAvoidance:
    """
    Dynamic replanning handler.

    Usage:
        oa = ObstacleAvoidance()
        oa.add_runtime_obstacles(centroids)
        new_path = oa.replan(car_pos, goal_pos, static_obstacles)
    """

    def __init__(self):
        self._dynamic_obstacles: set = set()
        self._inflation_radius: int = OBSTACLE_RADIUS    # px

    # ------------------------------------------------------------------
    def add_runtime_obstacles(self, centroids: list[tuple]) -> None:
        """
        Register newly detected obstacle centroids into the dynamic set.
        Called every time ObstacleDetector reports new threats.
        """
        for cx, cy in centroids:
            # Snap to grid
            gx = round(cx / GRID_SIZE) * GRID_SIZE
            gy = round(cy / GRID_SIZE) * GRID_SIZE
            self._dynamic_obstacles.add((gx, gy))

    # ------------------------------------------------------------------
    def clear_dynamic_obstacles(self) -> None:
        """Reset runtime obstacle registry."""
        self._dynamic_obstacles.clear()

    # ------------------------------------------------------------------
    def inflate_obstacles(self, obstacles: set, radius: int = None) -> set:
        """
        Expand each obstacle point into a disc of grid cells.
        This creates a safety buffer so the car never gets too close.

        Args:
            obstacles : set of (gx, gy) grid-snapped obstacle points
            radius    : inflation radius in pixels (default: OBSTACLE_RADIUS)

        Returns:
            Inflated obstacle set covering the safety zone.
        """
        if radius is None:
            radius = self._inflation_radius

        inflated = set()
        steps = max(1, radius // GRID_SIZE)

        for (ox, oy) in obstacles:
            for dx in range(-steps, steps + 1):
                for dy in range(-steps, steps + 1):
                    nx = ox + dx * GRID_SIZE
                    ny = oy + dy * GRID_SIZE
                    dist = math.sqrt(dx ** 2 + dy ** 2) * GRID_SIZE
                    if dist <= radius:
                        inflated.add((nx, ny))
        return inflated

    # ------------------------------------------------------------------
    def replan(
        self,
        car_pos: tuple,
        goal_pos: tuple,
        static_obstacles: set,
        extra_inflation: int = 20,
    ) -> list:
        """
        Trigger a full replan using merged + inflated obstacle set.

        Args:
            car_pos           : current car position (x, y) in pixels
            goal_pos          : goal position (x, y) in pixels
            static_obstacles  : original known obstacle set (snapped grid coords)
            extra_inflation   : additional px buffer added during avoidance replans

        Returns:
            New path as list of (x, y) waypoints, or [] if no path found.
        """
        # Snap car position to grid
        start = (
            round(car_pos[0] / GRID_SIZE) * GRID_SIZE,
            round(car_pos[1] / GRID_SIZE) * GRID_SIZE,
        )
        goal = (
            round(goal_pos[0] / GRID_SIZE) * GRID_SIZE,
            round(goal_pos[1] / GRID_SIZE) * GRID_SIZE,
        )

        # Merge static + dynamic obstacles
        all_obstacles = static_obstacles | self._dynamic_obstacles

        # Inflate with extra safety margin during avoidance
        inflated = self.inflate_obstacles(all_obstacles, radius=self._inflation_radius + extra_inflation)

        # Replan
        new_path = astar(start, goal, inflated, grid_size=GRID_SIZE)
        return new_path

    # ------------------------------------------------------------------
    def get_all_obstacles(self, static_obstacles: set) -> set:
        """
        Return the current merged & inflated obstacle set for rendering.
        """
        all_obstacles = static_obstacles | self._dynamic_obstacles
        return self.inflate_obstacles(all_obstacles)
