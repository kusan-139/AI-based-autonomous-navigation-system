"""
environment.py
==============
Simulation Module — Pygame Environment Manager

Responsibilities:
  - Initialize and manage the Pygame display window
  - Delegate map/road rendering to map_loader
  - Expose the screen surface for all other modules to draw onto
"""

import pygame
from src.config import WIDTH, HEIGHT, FPS, WINDOW_TITLE
from src.simulation.map_loader import draw_map


class Environment:
    """
    Manages the Pygame window and render surface.

    Usage:
        env = Environment()
        env.render()           # call once per frame to clear + redraw map
        env.tick(fps)          # cap framerate, returns delta time
        env.quit()             # clean shutdown
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock  = pygame.time.Clock()
        self._frame = 0

    # ------------------------------------------------------------------
    def render(self) -> None:
        """Clear screen and redraw the road map. Call at start of each frame."""
        draw_map(self.screen)
        self._frame += 1

    # ------------------------------------------------------------------
    def tick(self, fps: int = FPS) -> float:
        """
        Cap framerate and return actual FPS this frame.
        """
        ms = self.clock.tick(fps)
        actual_fps = self.clock.get_fps()
        return actual_fps

    # ------------------------------------------------------------------
    def flip(self) -> None:
        """Flip display buffer to screen."""
        pygame.display.flip()

    # ------------------------------------------------------------------
    def quit(self) -> None:
        pygame.quit()

    # ------------------------------------------------------------------
    @property
    def frame_count(self) -> int:
        return self._frame