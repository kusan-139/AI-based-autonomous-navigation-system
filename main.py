"""
main.py
=======
AI-Based Autonomous Navigation System — Main Simulation Entry Point

Pipeline (executed every frame):
  ┌─────────────────────────────────────────────────┐
  │  1. Sensor Casting   → VirtualSensor.cast()     │
  │  2. Threat Assess    → ObstacleDetector.assess()│
  │  3. Decision Making  → DecisionMaker.update()   │
  │  4. Avoidance/Replan → ObstacleAvoidance.replan()│
  │  5. Control          → Car.update(speed_factor) │
  │  6. Render           → Environment + HUD.draw() │
  └─────────────────────────────────────────────────┘

Controls:
  R     → Reset car to start position
  Space → Pause / Resume
  ESC   → Quit
"""

import pygame
import sys
import os
import math

# ── Core modules ────────────────────────────────────────────────────────────
from src.simulation.environment   import Environment
from src.simulation.car           import Car
from src.simulation.obstacles     import ObstacleManager
from src.simulation.sensor        import VirtualSensor
from src.simulation.map_loader    import build_obstacle_set

from src.navigation.planner       import astar
from src.navigation.controller    import assign_path
from src.navigation.decision_maker import DecisionMaker
from src.navigation.obstacle_avoidance import ObstacleAvoidance

from src.perception.obstacle_detector import ObstacleDetector

from src.utils.logger     import SimLogger
from src.utils.visualizer import HUD

from src.config import (
    START_POS, GOAL_POS, GRID_SIZE,
    WHITE, BLUE, RED, GREEN, CYAN,
    STATE_ARRIVE,
)

# ── Optional: YOLO (only if test_frames exist) ──────────────────────────────
import cv2
_YOLO_ENABLED = False
_yolo_detector = None
_yolo_frame    = None

_yolo_frame_dir = "assets/test_frames"
if os.path.exists(_yolo_frame_dir) and len(os.listdir(_yolo_frame_dir)) > 0:
    try:
        from src.perception.yolo_detector import YOLODetector
        _yolo_detector = YOLODetector()
        for fname in os.listdir(_yolo_frame_dir):
            fpath = os.path.join(_yolo_frame_dir, fname)
            img = cv2.imread(fpath)
            if img is not None:
                _yolo_frame = img
                _YOLO_ENABLED = True
                print(f"✅ YOLO enabled — loaded: {fpath}")
                break
    except Exception as e:
        print(f"⚠️  YOLO skipped: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════
print("🚗  AI Autonomous Navigation System — Starting...")

env    = Environment()
logger = SimLogger()
hud    = HUD()

# ── Vehicle ──────────────────────────────────────────────────────────────────
car = Car(*START_POS)

# ── Obstacle infrastructure ───────────────────────────────────────────────────
map_obstacles   = build_obstacle_set()           # wall cells from road map
obs_manager     = ObstacleManager()
obs_manager.add_random(count=6, seed=99)         # 6 random dynamic obstacles
obstacle_det    = ObstacleDetector()
obstacle_avoid  = ObstacleAvoidance()
sensor          = VirtualSensor()
decision_maker  = DecisionMaker()

# ── Merge obstacles for path planning ────────────────────────────────────────
sim_centroids  = obs_manager.get_centroids()
obstacle_det.update_obstacles(sim_centroids)
obstacle_avoid.add_runtime_obstacles(sim_centroids)
all_obstacles  = map_obstacles | obs_manager.get_grid_cells()

# ── YOLO obstacle injection ───────────────────────────────────────────────────
yolo_detections = []
if _YOLO_ENABLED and _yolo_detector and _yolo_frame is not None:
    yolo_detections = _yolo_detector.detect(_yolo_frame)
    yolo_centroids  = _yolo_detector.get_obstacle_centroids(yolo_detections)
    obstacle_avoid.add_runtime_obstacles(yolo_centroids)
    obstacle_det.update_obstacles(sim_centroids + yolo_centroids)
    logger.info(f"YOLO detected {len(yolo_detections)} objects")

# ── Initial A* path planning ──────────────────────────────────────────────────
print("🗺️  Computing A* path...")
path = astar(START_POS, GOAL_POS, all_obstacles)
if path:
    assign_path(car, path)
    logger.path_found(len(path))
    print(f"✅ Path found: {len(path)} waypoints")
else:
    logger.warning("No initial path found — using empty path")
    print("⚠️  No path found. Check START_POS / GOAL_POS vs obstacles.")

# ═══════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════════
paused   = False
running  = True
fps_val  = 60.0
frame_id = 0

print("🟢  Simulation running. [R]=Reset  [Space]=Pause  [ESC]=Quit")

while running:
    frame_id += 1

    # ── Event handling ────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_SPACE:
                paused = not paused
                logger.info("PAUSED" if paused else "RESUMED")

            elif event.key == pygame.K_r:
                # Reset car to start
                car = Car(*START_POS)
                path = astar(START_POS, GOAL_POS, all_obstacles)
                if path:
                    assign_path(car, path)
                decision_maker = DecisionMaker()
                logger.info("RESET — car returned to start")

    if paused:
        fps_val = env.tick()
        env.flip()
        continue

    # ── RENDER: Map + obstacles ───────────────────────────────────────────
    env.render()
    obs_manager.draw(env.screen, frame_id)

    # ── PERCEPTION: Sensor cast ───────────────────────────────────────────
    sensor_readings = sensor.cast(
        car.x, car.y,
        car.heading,
        all_obstacles | obs_manager.get_grid_cells(),
    )
    sensor.draw(env.screen, car.x, car.y, sensor_readings)

    # ── PERCEPTION: Threat assessment ─────────────────────────────────────
    obstacle_det.update_obstacles(
        obs_manager.get_centroids()
    )
    threat_level = obstacle_det.nearest_threat_level(car.x, car.y)
    threats      = obstacle_det.assess(car.x, car.y)

    # Log notable threat events
    if threats and threats[0]["threat"] != "CLEAR":
        t = threats[0]
        logger.obstacle_detected(t["pos"], t["dist"], t["threat"])

    # ── DECISION MAKING ───────────────────────────────────────────────────
    dist_goal = car.dist_to_goal(GOAL_POS)
    prev_state = decision_maker.get_state()
    state = decision_maker.update(
        threat_level=threat_level,
        dist_to_goal=dist_goal,
        path_empty=car.path_remaining() == 0,
    )

    if state != prev_state:
        logger.state_change(prev_state, state)

    # ── AVOIDANCE: Replan if needed ───────────────────────────────────────
    if decision_maker.should_replan():
        logger.replan_triggered(car.get_pos())
        new_path = obstacle_avoid.replan(
            car_pos=car.get_pos(),
            goal_pos=GOAL_POS,
            static_obstacles=all_obstacles,
        )
        if new_path:
            assign_path(car, new_path)
            logger.path_found(len(new_path))

    # ── CONTROL: Move car ─────────────────────────────────────────────────
    speed_factor = decision_maker.get_speed_factor()
    car.update(speed_factor=speed_factor)

    # ── RENDER: Path ──────────────────────────────────────────────────────
    hud.draw_path(env.screen, car.path, car.target_index)

    # ── RENDER: Goal marker ───────────────────────────────────────────────
    hud.draw_goal(env.screen, GOAL_POS)

    # ── RENDER: Car ───────────────────────────────────────────────────────
    car.draw(env.screen)

    # ── RENDER: HUD overlay ───────────────────────────────────────────────
    hud.draw(
        screen          = env.screen,
        state           = state,
        speed           = car.speed,
        fps             = fps_val,
        frame_id        = frame_id,
        sensor_readings = sensor_readings,
        dist_to_goal    = dist_goal,
        path_len        = car.path_remaining(),
    )

    # ── RENDER: YOLO detection window (if enabled) ────────────────────────
    if _YOLO_ENABLED and _yolo_frame is not None and yolo_detections:
        annotated = _yolo_detector.draw_detections(_yolo_frame.copy(), yolo_detections)
        cv2.imshow("YOLO — Object Detection", annotated)
        cv2.waitKey(1)

    # ── Frame logging (debug) ─────────────────────────────────────────────
    logger.frame(frame_id, state, car.speed, fps_val)

    # ── Flip display ──────────────────────────────────────────────────────
    env.flip()
    fps_val = env.tick()

    # ── Check ARRIVE ──────────────────────────────────────────────────────
    if state == STATE_ARRIVE:
        logger.goal_reached(frame_id)
        print(f"🎯  Goal reached in {frame_id} frames!")
        # Wait 3 seconds then exit (or press ESC)
        pygame.time.wait(3000)
        running = False

# ═══════════════════════════════════════════════════════════════════════════
# CLEAN EXIT
# ═══════════════════════════════════════════════════════════════════════════
logger.info("=== Simulation ended ===")
if _YOLO_ENABLED:
    cv2.destroyAllWindows()
env.quit()
sys.exit()