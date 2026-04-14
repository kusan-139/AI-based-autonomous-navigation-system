"""
obstacle_detector.py
====================
Perception Module — Proximity-based Obstacle Detection

Responsibilities:
  - Maintain a registry of known static obstacles (from YOLO or map)
  - Given the car's current position, find obstacles within danger range
  - Classify threat level: CLEAR / WARNING / DANGER
  - Return sorted obstacle list by proximity

Industry Pattern: AV stacks combine CNN detections with LiDAR/radar
proximity data. This module simulates the proximity fusion layer,
combining YOLO detections and virtual sensor hits into a unified
threat assessment.
"""

import math
from src.config import SENSOR_RANGE, DANGER_THRESHOLD


# ── Threat Level Constants ────────────────────────────────────────────
THREAT_CLEAR   = "CLEAR"
THREAT_WARNING = "WARNING"
THREAT_DANGER  = "DANGER"


class ObstacleDetector:
    """
    Proximity-based obstacle threat assessor.

    Usage:
        od = ObstacleDetector()
        od.update_obstacles(obstacle_centroids)
        threats = od.assess(car_x, car_y)
        # threats → list of {'pos': (x,y), 'dist': float, 'threat': str}
    """

    def __init__(self):
        self._obstacles: list[tuple] = []   # (cx, cy) list

    # ------------------------------------------------------------------
    def update_obstacles(self, centroids: list[tuple]) -> None:
        """
        Update the internal obstacle list.
        Called every frame when new YOLO detections arrive.
        """
        self._obstacles = list(centroids)

    # ------------------------------------------------------------------
    def _euclidean(self, ax: float, ay: float, bx: float, by: float) -> float:
        return math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)

    # ------------------------------------------------------------------
    def assess(self, car_x: float, car_y: float) -> list[dict]:
        """
        Assess all registered obstacles relative to the car's position.

        Returns:
            List of obstacle reports sorted by distance (nearest first):
            {
                'pos':    (cx, cy),
                'dist':   float,
                'threat': 'CLEAR' | 'WARNING' | 'DANGER'
            }
            Only obstacles within SENSOR_RANGE are returned.
        """
        reports = []
        for (cx, cy) in self._obstacles:
            dist = self._euclidean(car_x, car_y, cx, cy)
            if dist > SENSOR_RANGE:
                continue

            if dist <= DANGER_THRESHOLD:
                threat = THREAT_DANGER
            elif dist <= SENSOR_RANGE * 0.6:
                threat = THREAT_WARNING
            else:
                threat = THREAT_CLEAR

            reports.append({
                "pos":    (cx, cy),
                "dist":   round(dist, 1),
                "threat": threat,
            })

        reports.sort(key=lambda r: r["dist"])
        return reports

    # ------------------------------------------------------------------
    def nearest_threat_level(self, car_x: float, car_y: float) -> str:
        """
        Convenience method — returns the highest threat level in range.
        Used by decision_maker.py.
        """
        reports = self.assess(car_x, car_y)
        if not reports:
            return THREAT_CLEAR
        return reports[0]["threat"]

    # ------------------------------------------------------------------
    def get_static_obstacles(self) -> list[tuple]:
        """Return the current raw obstacle list."""
        return list(self._obstacles)
