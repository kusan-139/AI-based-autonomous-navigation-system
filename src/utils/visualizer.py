"""
visualizer.py
=============
Utility Module — HUD Overlay & Simulation Statistics Renderer

Responsibilities:
  - Draw a heads-up display (HUD) on the Pygame screen
  - Show: current state, speed, FPS, frame count, sensor status
  - Draw mini-legend for colors
  - Render path waypoints with gradient coloring
  - Render obstacle threat indicators

Industry Pattern:
    AV dashboards (e.g., Waymo Rider app, Tesla FSD UI) show real-time
    system state overlays. This module is the simulation equivalent —
    inspired by the Pygame HUD patterns used in open-source AV simulators
    like highway-env and simple-AV.
"""

import pygame
import math
from src.config import (
    WIDTH, HEIGHT,
    CYAN, WHITE, RED, ORANGE, GREEN, YELLOW, BLUE, BLACK,
    STATE_DRIVE, STATE_SLOW, STATE_STOP, STATE_AVOID, STATE_ARRIVE,
)


class HUD:
    """
    Heads-Up Display renderer for the simulation.

    Usage:
        hud = HUD()
        hud.draw(screen, state, speed, fps, frame, sensor_readings)
    """

    def __init__(self):
        pygame.font.init()
        self.font_large  = pygame.font.SysFont("Consolas", 18, bold=True)
        self.font_medium = pygame.font.SysFont("Consolas", 14)
        self.font_small  = pygame.font.SysFont("Consolas", 11)
        self._frame_times: list = []

    # ------------------------------------------------------------------
    def draw(
        self,
        screen:          pygame.Surface,
        state:           str,
        speed:           float,
        fps:             float,
        frame_id:        int,
        sensor_readings: list,
        dist_to_goal:    float,
        path_len:        int,
    ) -> None:
        """
        Render the complete HUD overlay.

        Args:
            screen          : Pygame surface to draw onto
            state           : Current decision state string
            speed           : Car's current speed (px/frame)
            fps             : Measured frames per second
            frame_id        : Current frame counter
            sensor_readings : List of sensor reading dicts from VirtualSensor
            dist_to_goal    : Remaining distance to goal in pixels
            path_len        : Remaining waypoints in path
        """
        self._draw_panel(screen)
        self._draw_state_badge(screen, state)
        self._draw_telemetry(screen, speed, fps, frame_id, dist_to_goal, path_len)
        self._draw_sensor_bar(screen, sensor_readings)
        self._draw_legend(screen)

    # ------------------------------------------------------------------
    def _draw_panel(self, screen: pygame.Surface) -> None:
        """Translucent dark panel on the left side."""
        panel = pygame.Surface((220, HEIGHT), pygame.SRCALPHA)
        panel.fill((10, 10, 18, 200))
        screen.blit(panel, (0, 0))

    # ------------------------------------------------------------------
    def _draw_state_badge(self, screen: pygame.Surface, state: str) -> None:
        """Large colored state indicator at top of panel."""
        colors = {
            STATE_DRIVE:  (50,  220, 100),
            STATE_SLOW:   (255, 200, 50),
            STATE_STOP:   (220, 50,  50),
            STATE_AVOID:  (255, 140, 0),
            STATE_ARRIVE: (100, 180, 255),
        }
        color = colors.get(state, WHITE)

        # Glow effect — draw slightly larger rect in dim color first
        badge_rect = pygame.Rect(10, 10, 200, 50)
        glow = (*[min(255, c + 40) for c in color], 60)
        glow_surf = pygame.Surface((220, 70), pygame.SRCALPHA)
        glow_surf.fill((*color, 30))
        screen.blit(glow_surf, (0, 0))

        pygame.draw.rect(screen, color, badge_rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, badge_rect, 1, border_radius=8)

        label = self.font_large.render(f"◈  {state}", True, BLACK)
        screen.blit(label, (badge_rect.x + 12, badge_rect.y + 16))

    # ------------------------------------------------------------------
    def _draw_telemetry(
        self,
        screen:       pygame.Surface,
        speed:        float,
        fps:          float,
        frame_id:     int,
        dist_to_goal: float,
        path_len:     int,
    ) -> None:
        """Numeric telemetry panel."""
        lines = [
            ("TELEMETRY", CYAN, self.font_medium),
            (f"Speed  : {speed:.2f} px/fr",   WHITE, self.font_medium),
            (f"FPS    : {fps:.1f}",            WHITE, self.font_medium),
            (f"Frame  : {frame_id:05d}",       WHITE, self.font_medium),
            (f"Goal Δ : {dist_to_goal:.0f} px",WHITE, self.font_medium),
            (f"Path   : {path_len} wpts",      WHITE, self.font_medium),
        ]

        y = 75
        for text, color, font in lines:
            surf = font.render(text, True, color)
            screen.blit(surf, (14, y))
            y += 22

    # ------------------------------------------------------------------
    def _draw_sensor_bar(
        self,
        screen: pygame.Surface,
        readings: list,
    ) -> None:
        """Visual sensor bar — 5 vertical segments, one per beam."""
        if not readings:
            return

        y_start = 230
        bar_w   = 30
        bar_h   = 60
        gap     = 8
        x_start = 14

        header = self.font_medium.render("SENSORS", True, CYAN)
        screen.blit(header, (x_start, y_start - 20))

        for i, r in enumerate(readings):
            x = x_start + i * (bar_w + gap)
            dist = r["distance"]
            max_r = r.get("range", 100)

            # Normalise: shorter distance → more red
            ratio = 1.0 - min(dist / max_r, 1.0)
            color = (
                int(50  + ratio * 200),
                int(220 - ratio * 200),
                50,
            )

            fill_h = int(bar_h * ratio)
            # Background
            pygame.draw.rect(screen, (40, 40, 55), (x, y_start, bar_w, bar_h), border_radius=4)
            # Fill
            if fill_h > 0:
                pygame.draw.rect(
                    screen, color,
                    (x, y_start + bar_h - fill_h, bar_w, fill_h),
                    border_radius=4,
                )
            pygame.draw.rect(screen, CYAN, (x, y_start, bar_w, bar_h), 1, border_radius=4)

            # Angle label
            angle_txt = self.font_small.render(f"{int(r['angle'] % 360)}°", True, (160, 160, 180))
            screen.blit(angle_txt, (x + 2, y_start + bar_h + 2))

    # ------------------------------------------------------------------
    def _draw_legend(self, screen: pygame.Surface) -> None:
        """Color legend at bottom of panel."""
        y = HEIGHT - 160
        header = self.font_medium.render("LEGEND", True, CYAN)
        screen.blit(header, (14, y))

        items = [
            ((50,  220, 100), "Car"),
            ((100, 180, 255), "Goal"),
            ((220, 50,  50),  "Obstacle"),
            ((255, 255, 255), "Path"),
            ((255, 220, 50),  "Lane Center"),
            ((255, 140, 0),   "Sensor Ray"),
        ]
        y += 20
        for color, label in items:
            pygame.draw.rect(screen, color, (14, y + 3, 12, 12), border_radius=2)
            txt = self.font_small.render(label, True, (180, 180, 200))
            screen.blit(txt, (32, y))
            y += 18

    # ------------------------------------------------------------------
    def draw_path(
        self,
        screen:   pygame.Surface,
        path:     list,
        car_idx:  int,
    ) -> None:
        """
        Draw the planned path as a gradient trail.
        Completed segments are dimmed; upcoming ones are bright white/blue.
        """
        for i, pt in enumerate(path):
            if i < car_idx:
                color = (60, 60, 80)          # dim — already traveled
            else:
                t = (i - car_idx) / max(len(path) - car_idx, 1)
                r = int(180 + 75 * (1 - t))
                g = int(180 + 75 * (1 - t))
                b = 255
                color = (r, g, b)
            pygame.draw.circle(screen, color, (int(pt[0]), int(pt[1])), 3)

    # ------------------------------------------------------------------
    def draw_goal(self, screen: pygame.Surface, goal: tuple) -> None:
        """Draw pulsing goal marker."""
        gx, gy = int(goal[0]), int(goal[1])
        pygame.draw.circle(screen, (100, 180, 255), (gx, gy), 14)
        pygame.draw.circle(screen, WHITE, (gx, gy), 14, 2)
        label = self.font_medium.render("GOAL", True, WHITE)
        screen.blit(label, (gx - 16, gy - 8))

    # ------------------------------------------------------------------
    def draw_obstacle_markers(
        self,
        screen:    pygame.Surface,
        obstacles: set,
    ) -> None:
        """Draw small red squares at obstacle grid cells."""
        for (ox, oy) in obstacles:
            pygame.draw.rect(screen, (180, 40, 40), (ox + 2, oy + 2, 16, 16), border_radius=2)
