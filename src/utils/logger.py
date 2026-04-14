"""
logger.py
=========
Utility Module — Runtime Event Logger

Responsibilities:
  - Log simulation events (state transitions, obstacle hits, path replans)
  - Write to timestamped log files in outputs/logs/
  - Support both console and file output simultaneously
  - Provide structured log format for later analysis

Industry Pattern:
    Real AV systems (Apollo, Waymo) use ROS2 rosbag + structured logging.
    This module provides a lightweight Python equivalent using stdlib logging.
"""

import os
import logging
import datetime
from src.config import LOG_DIR


class SimLogger:
    """
    Structured event logger for the simulation.

    Usage:
        logger = SimLogger()
        logger.state_change("DRIVE", "STOP")
        logger.obstacle_detected((400, 300), dist=35.2)
        logger.replan_triggered((100, 150))
    """

    def __init__(self, session_name: str = None):
        os.makedirs(LOG_DIR, exist_ok=True)

        if session_name is None:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            session_name = f"sim_{ts}"

        self.session_name = session_name
        log_path = os.path.join(LOG_DIR, f"{session_name}.log")

        # ── Configure logging ─────────────────────────────────────────
        self._logger = logging.getLogger(session_name)
        self._logger.setLevel(logging.DEBUG)

        # File handler
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setLevel(logging.DEBUG)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-7s | %(message)s",
            datefmt="%H:%M:%S",
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self._logger.addHandler(fh)
        self._logger.addHandler(ch)
        self._logger.propagate = False

        self._logger.info(f"=== Session started: {session_name} ===")
        self._logger.info(f"Log file: {log_path}")

    # ------------------------------------------------------------------
    def state_change(self, prev_state: str, new_state: str) -> None:
        """Log a state machine transition."""
        self._logger.info(f"STATE  {prev_state:6s} → {new_state}")

    # ------------------------------------------------------------------
    def obstacle_detected(self, pos: tuple, dist: float, threat: str) -> None:
        """Log an obstacle detection event."""
        self._logger.warning(
            f"OBSTACLE pos=({pos[0]:4d},{pos[1]:4d})  dist={dist:6.1f}px  threat={threat}"
        )

    # ------------------------------------------------------------------
    def replan_triggered(self, car_pos: tuple) -> None:
        """Log a path replanning event."""
        self._logger.warning(
            f"REPLAN  triggered from pos=({car_pos[0]:.0f},{car_pos[1]:.0f})"
        )

    # ------------------------------------------------------------------
    def path_found(self, length: int) -> None:
        """Log successful path computation."""
        self._logger.info(f"PATH    computed  waypoints={length}")

    # ------------------------------------------------------------------
    def goal_reached(self, total_frames: int) -> None:
        """Log goal arrival."""
        self._logger.info(f"ARRIVE  goal reached after {total_frames} frames")

    # ------------------------------------------------------------------
    def frame(self, frame_id: int, state: str, speed: float, fps: float) -> None:
        """Log per-frame telemetry (DEBUG level — file only)."""
        self._logger.debug(
            f"FRAME {frame_id:05d}  state={state:6s}  speed={speed:.2f}  fps={fps:.1f}"
        )

    # ------------------------------------------------------------------
    def info(self, msg: str) -> None:
        self._logger.info(msg)

    def warning(self, msg: str) -> None:
        self._logger.warning(msg)

    def error(self, msg: str) -> None:
        self._logger.error(msg)
