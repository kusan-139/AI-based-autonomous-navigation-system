"""
decision_maker.py
=================
Navigation Module — State Machine for Autonomous Decision Making

States:
    DRIVE  → Normal forward movement along planned path
    SLOW   → Obstacle detected in WARNING zone — reduce speed
    STOP   → Obstacle in DANGER zone — halt immediately
    AVOID  → Replanning triggered to bypass obstacle
    ARRIVE → Goal reached — mission complete

Industry Pattern:
    Real AV stacks (Apollo, Autoware) implement a behavioral planning
    layer as a Finite State Machine (FSM). This mirrors that architecture
    in a simplified but conceptually accurate form.
"""

import time
from src.config import (
    STATE_DRIVE, STATE_SLOW, STATE_STOP, STATE_AVOID, STATE_ARRIVE,
    DANGER_THRESHOLD, SENSOR_RANGE,
)
from src.perception.obstacle_detector import THREAT_DANGER, THREAT_WARNING, THREAT_CLEAR


class DecisionMaker:
    """
    Behavioral planner implemented as a Finite State Machine.

    Usage:
        dm = DecisionMaker()
        state = dm.update(threat_level, dist_to_goal, obstacle_detected)
        speed_factor = dm.get_speed_factor()
    """

    def __init__(self):
        self.state: str = STATE_DRIVE
        self._prev_state: str = STATE_DRIVE
        self._state_entry_time: float = time.time()
        self._stop_count: int = 0          # how many frames we've been stopped
        self._avoid_cooldown: int = 0      # frames before we can trigger AVOID again
        self._post_avoid_grace: int = 0    # grace frames after avoidance replan

    # ------------------------------------------------------------------
    def update(
        self,
        threat_level: str,
        dist_to_goal: float,
        path_empty: bool = False,
    ) -> str:
        """
        Evaluate inputs and transition to the appropriate state.

        Args:
            threat_level : THREAT_CLEAR | THREAT_WARNING | THREAT_DANGER
            dist_to_goal : Euclidean distance (px) from car to goal
            path_empty   : True when no path points remain

        Returns:
            Current state string (one of STATE_*)
        """
        self._avoid_cooldown    = max(0, self._avoid_cooldown - 1)
        self._post_avoid_grace  = max(0, self._post_avoid_grace - 1)

        # ── ARRIVE ──────────────────────────────────────────────────────
        if dist_to_goal < 20 or path_empty:
            self._transition(STATE_ARRIVE)
            return self.state

        # ── POST-AVOID GRACE: drive through even if threat persists ──────
        # After a successful replan, give the car 60 frames to move past
        # the obstacle before re-entering the STOP detection loop.
        if self._post_avoid_grace > 0:
            self._stop_count = 0
            if threat_level == THREAT_WARNING:
                self._transition(STATE_SLOW)
            else:
                self._transition(STATE_DRIVE)
            return self.state

        # ── STOP / AVOID ─────────────────────────────────────────────────
        if threat_level == THREAT_DANGER:
            self._stop_count += 1
            # After 30 frames (~0.5s at 60fps) of being stopped, try avoidance
            if self._stop_count > 30 and self._avoid_cooldown == 0:
                self._avoid_cooldown   = 90
                self._post_avoid_grace = 60   # grace window after replan
                self._stop_count       = 0
                self._transition(STATE_AVOID)
            else:
                self._transition(STATE_STOP)
            return self.state

        self._stop_count = 0   # reset stop counter if threat cleared

        # ── SLOW ──────────────────────────────────────────────────────────
        if threat_level == THREAT_WARNING:
            self._transition(STATE_SLOW)
            return self.state

        # ── DRIVE (default) ───────────────────────────────────────────────
        self._transition(STATE_DRIVE)
        return self.state

    # ------------------------------------------------------------------
    def get_speed_factor(self) -> float:
        """
        Returns a multiplier (0.0–1.0) to scale base car speed.

        DRIVE  → 1.0   (full speed)
        SLOW   → 0.5   (half speed)
        STOP   → 0.0   (stationary)
        AVOID  → 0.7   (cautious replanning)
        ARRIVE → 0.0   (stopped at goal)
        """
        return {
            STATE_DRIVE:  1.0,
            STATE_SLOW:   0.5,
            STATE_STOP:   0.0,
            STATE_AVOID:  0.7,
            STATE_ARRIVE: 0.0,
        }.get(self.state, 1.0)

    # ------------------------------------------------------------------
    def get_state(self) -> str:
        """Return current state label."""
        return self.state

    # ------------------------------------------------------------------
    def get_state_color(self) -> tuple:
        """
        HUD color coding for each state.
        Returns an (R, G, B) tuple.
        """
        return {
            STATE_DRIVE:  (50,  220, 100),   # Green
            STATE_SLOW:   (255, 200, 50),    # Yellow
            STATE_STOP:   (220, 50,  50),    # Red
            STATE_AVOID:  (255, 140, 0),     # Orange
            STATE_ARRIVE: (100, 180, 255),   # Blue
        }.get(self.state, (200, 200, 200))

    # ------------------------------------------------------------------
    def is_stopped(self) -> bool:
        return self.state in (STATE_STOP, STATE_ARRIVE)

    def should_replan(self) -> bool:
        return self.state == STATE_AVOID

    # ------------------------------------------------------------------
    def _transition(self, new_state: str) -> None:
        if new_state != self.state:
            self._prev_state = self.state
            self.state = new_state
            self._state_entry_time = time.time()

    def time_in_state(self) -> float:
        """Seconds spent in current state."""
        return time.time() - self._state_entry_time
