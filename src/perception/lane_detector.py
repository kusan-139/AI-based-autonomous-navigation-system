"""
lane_detector.py
================
Perception Module — Lane / Road Marking Detection using OpenCV

Responsibilities:
  - Convert frame to grayscale and apply Gaussian blur
  - Apply Canny edge detection
  - Mask the region of interest (lower half = road ahead)
  - Apply Probabilistic Hough Transform to find lane lines
  - Separate lines into LEFT lane and RIGHT lane by slope
  - Return averaged lane lines and draw them on frame

Industry Pattern: This is a classical computer-vision lane detector,
identical in approach to NVIDIA's early DAVE-2 and OpenPilot's laneline
perception baseline before moving to neural networks.
"""

import cv2
import numpy as np
from typing import Optional

from src.config import (
    LANE_CANNY_LOW, LANE_CANNY_HIGH,
    LANE_RHO, LANE_THETA_DEG,
    LANE_THRESHOLD, LANE_MIN_LEN, LANE_MAX_GAP,
)


class LaneDetector:
    """
    Detects left and right lane markings in a frame using HoughLinesP.

    Usage:
        ld = LaneDetector()
        lane_frame, lanes = ld.detect(frame)
        # lanes = {'left': (x1,y1,x2,y2) or None, 'right': ... or None}
    """

    def __init__(self):
        self.rho       = LANE_RHO
        self.theta     = np.deg2rad(LANE_THETA_DEG)
        self.threshold = LANE_THRESHOLD
        self.min_len   = LANE_MIN_LEN
        self.max_gap   = LANE_MAX_GAP

    # ------------------------------------------------------------------
    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        """Grayscale → blur → Canny edges."""
        gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges   = cv2.Canny(blurred, LANE_CANNY_LOW, LANE_CANNY_HIGH)
        return edges

    # ------------------------------------------------------------------
    def _region_of_interest(self, edges: np.ndarray) -> np.ndarray:
        """
        Mask only the lower trapezoidal region (road ahead).
        Mirrors what real AV stacks do to ignore the sky/buildings.
        """
        h, w  = edges.shape
        mask  = np.zeros_like(edges)
        poly  = np.array([[
            (int(w * 0.05), h),
            (int(w * 0.45), int(h * 0.55)),
            (int(w * 0.55), int(h * 0.55)),
            (int(w * 0.95), h),
        ]], dtype=np.int32)
        cv2.fillPoly(mask, poly, 255)
        return cv2.bitwise_and(edges, mask)

    # ------------------------------------------------------------------
    def _fit_line(self, lines, height: int, side: str) -> Optional[tuple]:
        """
        Average all line segments on one side into a single line
        specified by (x1, y1, x2, y2).
        """
        if not lines:
            return None

        points = []
        for x1, y1, x2, y2 in lines:
            points += [(x1, y1), (x2, y2)]

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        if len(set(xs)) < 2:
            return None

        try:
            m, b = np.polyfit(xs, ys, 1)
        except np.linalg.LinAlgError:
            return None

        y_bottom = height
        y_top    = int(height * 0.6)

        if m == 0:
            return None

        x_bottom = int((y_bottom - b) / m)
        x_top    = int((y_top    - b) / m)
        return (x_bottom, y_bottom, x_top, y_top)

    # ------------------------------------------------------------------
    def detect(self, frame: np.ndarray) -> tuple[np.ndarray, dict]:
        """
        Full lane detection pipeline.

        Returns:
            annotated_frame : BGR frame with lane overlays drawn
            lanes           : {'left': tuple|None, 'right': tuple|None}
        """
        h, w  = frame.shape[:2]
        edges = self._preprocess(frame)
        roi   = self._region_of_interest(edges)

        raw_lines = cv2.HoughLinesP(
            roi,
            self.rho, self.theta, self.threshold,
            minLineLength=self.min_len,
            maxLineGap=self.max_gap
        )

        left_lines, right_lines = [], []

        if raw_lines is not None:
            for line in raw_lines:
                x1, y1, x2, y2 = line[0]
                if x2 == x1:
                    continue
                slope = (y2 - y1) / (x2 - x1)

                if slope < -0.3:          # Negative slope → left lane
                    left_lines.append((x1, y1, x2, y2))
                elif slope > 0.3:         # Positive slope → right lane
                    right_lines.append((x1, y1, x2, y2))

        left_lane  = self._fit_line(left_lines,  h, "left")
        right_lane = self._fit_line(right_lines, h, "right")

        annotated = frame.copy()
        overlay   = np.zeros_like(frame)

        lane_color = (0, 220, 255)   # Cyan-yellow
        line_thick = 4

        if left_lane:
            x1, y1, x2, y2 = left_lane
            cv2.line(annotated, (x1, y1), (x2, y2), lane_color, line_thick)

        if right_lane:
            x1, y1, x2, y2 = right_lane
            cv2.line(annotated, (x1, y1), (x2, y2), lane_color, line_thick)

        # Draw filled lane polygon between lanes
        if left_lane and right_lane:
            lx1, ly1, lx2, ly2 = left_lane
            rx1, ry1, rx2, ry2 = right_lane
            poly_pts = np.array([[lx1, ly1], [lx2, ly2], [rx2, ry2], [rx1, ry1]])
            cv2.fillPoly(overlay, [poly_pts], (0, 255, 100, 60))
            annotated = cv2.addWeighted(annotated, 1.0, overlay, 0.35, 0)

        # Label
        lane_status = []
        if left_lane:  lane_status.append("Left ✓")
        if right_lane: lane_status.append("Right ✓")
        status_text = "Lanes: " + ("  ".join(lane_status) if lane_status else "Not Detected")
        cv2.putText(annotated, status_text, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 220, 255), 2, cv2.LINE_AA)

        lanes = {"left": left_lane, "right": right_lane}
        return annotated, lanes
