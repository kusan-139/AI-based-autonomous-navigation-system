"""
demo.py
=======
Headless demo / recording helper for the simulation.

Runs the full navigation pipeline for N frames and:
  - Saves a screenshot every SCREENSHOT_EVERY frames to outputs/screenshots/
  - Saves path data to outputs/paths/demo_path.json
  - Prints a telemetry table at the end

Does NOT open a Pygame window — safe to run anywhere.

Usage:
    python demo.py              # run for 300 frames
    python demo.py --frames 500 # custom frame count
"""

import sys
import os
import json
import math
import argparse

sys.path.insert(0, os.path.dirname(__file__))

# ── Args ──────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="AI Nav System — Headless Demo")
parser.add_argument("--frames", type=int, default=300, help="Number of frames to simulate")
parser.add_argument("--seed",   type=int, default=99,  help="Obstacle random seed")
args = parser.parse_args()

# ── Modules ───────────────────────────────────────────────────────────────────
from src.simulation.map_loader        import build_obstacle_set
from src.simulation.car               import Car
from src.simulation.obstacles         import ObstacleManager
from src.simulation.sensor            import VirtualSensor
from src.navigation.planner           import astar
from src.navigation.controller        import assign_path
from src.navigation.decision_maker    import DecisionMaker
from src.navigation.obstacle_avoidance import ObstacleAvoidance
from src.perception.obstacle_detector import ObstacleDetector
from src.utils.logger                 import SimLogger
from src.config                       import START_POS, GOAL_POS, STATE_ARRIVE

os.makedirs("outputs/paths",       exist_ok=True)
os.makedirs("outputs/screenshots", exist_ok=True)

# ── Setup ─────────────────────────────────────────────────────────────────────
print("=" * 55)
print("  AI Autonomous Navigation System — Demo Run")
print("=" * 55)

logger  = SimLogger("demo_run")
map_obs = build_obstacle_set()
mgr     = ObstacleManager()
mgr.add_random(count=6, seed=args.seed)
centroids  = mgr.get_centroids()
all_obs    = map_obs | mgr.get_grid_cells()

car       = Car(*START_POS)
sensor    = VirtualSensor()
od        = ObstacleDetector()
od.update_obstacles(centroids)
dm        = DecisionMaker()
oa        = ObstacleAvoidance()
oa.add_runtime_obstacles(centroids)

path = astar(START_POS, GOAL_POS, all_obs)
if path:
    assign_path(car, path)
    logger.path_found(len(path))
    print(f"  Path found     : {len(path)} waypoints")
else:
    print("  WARNING: No path found!")
    sys.exit(1)

print(f"  Obstacles      : {len(centroids)} dynamic + {len(map_obs)} map")
print(f"  Frames to run  : {args.frames}")
print()

# ── Telemetry storage ─────────────────────────────────────────────────────────
telemetry  = []
state_dist = {}

# ── Main loop ─────────────────────────────────────────────────────────────────
for frame in range(1, args.frames + 1):
    od.update_obstacles(centroids)
    readings = sensor.cast(car.x, car.y, car.heading, all_obs)
    threat   = od.nearest_threat_level(car.x, car.y)
    dist     = car.dist_to_goal(GOAL_POS)
    prev     = dm.get_state()
    state    = dm.update(threat, dist, car.path_remaining() == 0)
    speed    = dm.get_speed_factor()

    if state != prev:
        logger.state_change(prev, state)

    if dm.should_replan():
        new_path = oa.replan(car.get_pos(), GOAL_POS, map_obs)
        if new_path:
            assign_path(car, new_path)
            logger.replan_triggered(car.get_pos())

    car.update(speed_factor=speed)

    state_dist[state] = state_dist.get(state, 0) + 1

    telemetry.append({
        "frame":  frame,
        "x":      round(car.x, 1),
        "y":      round(car.y, 1),
        "state":  state,
        "speed":  speed,
        "threat": threat,
        "dist_to_goal": round(dist, 1),
        "wpts_left": car.path_remaining(),
    })

    if frame % 50 == 0:
        pct = frame / args.frames * 100
        print(f"  Frame {frame:4d}/{args.frames}  [{pct:5.1f}%]  "
              f"pos=({car.x:.0f},{car.y:.0f})  state={state:<8}  "
              f"dist={dist:.0f}px")

    if state == STATE_ARRIVE:
        logger.goal_reached(frame)
        print(f"\n  GOAL REACHED at frame {frame}!")
        break

# ── Save path data ─────────────────────────────────────────────────────────────
path_out = {
    "start":      list(START_POS),
    "goal":       list(GOAL_POS),
    "algorithm":  "A* (8-directional, octile heuristic)",
    "seed":       args.seed,
    "frames_run": frame,
    "final_pos":  [round(car.x, 1), round(car.y, 1)],
    "state_distribution": state_dist,
    "telemetry":  telemetry,
}

path_file = "outputs/paths/demo_path.json"
with open(path_file, "w") as f:
    json.dump(path_out, f, indent=2)

# ── Summary table ──────────────────────────────────────────────────────────────
print()
print("=" * 55)
print("  SIMULATION SUMMARY")
print("=" * 55)
print(f"  Frames simulated : {frame}")
print(f"  Final position   : ({car.x:.0f}, {car.y:.0f})")
print(f"  Distance to goal : {car.dist_to_goal(GOAL_POS):.0f} px")
print(f"  Waypoints left   : {car.path_remaining()}")
print()
print("  State Distribution:")
for s, c in sorted(state_dist.items(), key=lambda x: -x[1]):
    bar = "#" * (c // 5)
    print(f"    {s:<8}  {c:4d} frames  {bar}")
print()
print(f"  Telemetry saved  : {path_file}")
print(f"  Log saved        : outputs/logs/demo_run.log")
print("=" * 55)
