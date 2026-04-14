# System Design Document

## AI-Based Autonomous Navigation System

**Version:** 1.0 | **Status:** Production-ready Simulation

---

## 1. System Overview

This project implements a complete autonomous navigation pipeline in a 2D simulation environment. It mirrors the software architecture used in industry-grade autonomous vehicle (AV) stacks such as Apollo (Baidu), Autoware, and CARLA's agents — but runs entirely on a standard laptop without any hardware.

```
┌─────────────────────────────────────────────────────────────────────┐
│                   AUTONOMOUS NAVIGATION PIPELINE                     │
│                                                                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────┐    │
│  │  PERCEPTION  │────▶│   DECISION   │────▶│   NAVIGATION     │    │
│  │              │     │   MAKING     │     │                  │    │
│  │ • YOLO v8    │     │              │     │ • A* Planner     │    │
│  │ • Lane Det.  │     │ • FSM States │     │ • Path Smooth    │    │
│  │ • Obstacle   │     │   DRIVE      │     │ • Obstacle Avoid │    │
│  │   Detector   │     │   SLOW       │     │ • Controller     │    │
│  │ • Sensor     │     │   STOP       │     │                  │    │
│  │   (Virtual   │     │   AVOID      │     └────────┬─────────┘    │
│  │   Ultrasonic)│     │   ARRIVE     │              │              │
│  └──────┬───────┘     └─────────────┘              │              │
│         │                                           │              │
│         ▼                                           ▼              │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                      SIMULATION LAYER                       │  │
│  │   Environment  │  Car Agent  │  Obstacles  │  Map Loader    │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                       UTILITIES                              │  │
│  │           Logger (SimLogger)  │  HUD Visualizer             │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Module Descriptions

### 2.1 Perception Layer

#### `src/perception/yolo_detector.py`
- Loads YOLOv8n (COCO pretrained)
- Filters by confidence threshold (default: 0.40) and obstacle classes
- Outputs list of `{bbox, conf, cls_id, label}` dicts
- Provides centroid extraction for path planner integration

#### `src/perception/lane_detector.py`
- Classical computer vision pipeline: Grayscale → Gaussian Blur → Canny → ROI Mask → HoughLinesP
- Separates lines into left/right by slope sign
- Fits a single averaged line per side
- Returns annotated frame + `{left, right}` lane coordinates

#### `src/perception/obstacle_detector.py`
- Proximity-based threat assessment using Euclidean distance
- Three threat tiers: CLEAR (>60% range) / WARNING (40–60%) / DANGER (<40px)
- Provides `nearest_threat_level()` for DecisionMaker input

#### `src/simulation/sensor.py`
- Virtual 5-beam ultrasonic sensor at configurable angles
- Ray-march algorithm against a discrete obstacle set
- Returns per-beam: `{angle, distance, hit, hit_point}`

---

### 2.2 Decision Making Layer

#### `src/navigation/decision_maker.py`
**Finite State Machine:**

```
         ┌──────────────────────────────────────────┐
         │                                          │
  ┌──────▼──────┐  dist < 20px   ┌─────────────┐  │
  │    DRIVE    │───────────────▶│   ARRIVE    │  │
  │  (normal)   │◀──────────────  └─────────────┘  │
  └──────┬──────┘   CLEAR                           │
         │ WARNING                                  │
         ▼                                          │
  ┌─────────────┐  DANGER        ┌──────────────┐  │
  │    SLOW     │───────────────▶│    STOP      │  │
  │  (0.5x spd) │                │  (0.0x spd)  │─▶│ >90 frames
  └─────────────┘                └──────────────┘  │
                                                    ▼
                                         ┌──────────────┐
                                         │    AVOID     │
                                         │  (replan)    │
                                         └──────────────┘
```

Speed multipliers: DRIVE=1.0, SLOW=0.5, STOP=0.0, AVOID=0.7, ARRIVE=0.0

---

### 2.3 Navigation Layer

#### `src/navigation/planner.py`
- A* with octile distance heuristic
- 8-directional movement (cardinal + diagonal)
- Auto-snaps start/goal to grid
- Diagonal corridor check prevents wall-cutting

#### `src/navigation/controller.py`
- Gradient descent path smoothing (80/20 weight_data/weight_smooth)
- Reduces sharp zig-zag from grid-based A* output

#### `src/navigation/obstacle_avoidance.py`
- Obstacle inflation: expands each obstacle into a safety disc
- Merges static + dynamic obstacles before replanning
- Triggers A* replan with inflated obstacle buffers

---

### 2.4 Simulation Layer

#### `src/simulation/environment.py`
- Pygame window manager with FPS tracking
- Delegates map rendering to `map_loader.py`

#### `src/simulation/map_loader.py`
- Procedural urban grid: 3 horizontal + 4 vertical roads
- `build_obstacle_set()`: returns all non-road cells as obstacle grid
- `draw_map()`: road surfaces, lane dashes, building blocks

#### `src/simulation/car.py`
- Kinematic vehicle model following waypoints
- Speed factor application from DecisionMaker
- Motion trail rendering for visual clarity

#### `src/simulation/obstacles.py`
- Dynamic obstacle manager with random placement (seeded for reproducibility)
- Pulsing draw animation

---

### 2.5 Utility Layer

#### `src/utils/logger.py`
- Dual output: timestamped file `outputs/logs/` + console
- Structured log events: state changes, obstacle detections, replans, goal arrival
- DEBUG-level per-frame telemetry

#### `src/utils/visualizer.py`
- HUD panel: state badge (colored), telemetry readout, sensor bars, legend
- Path trail gradient rendering (blue-white gradient, dim for traveled)
- Pulsing goal marker

---

## 3. Data Flow (Single Frame)

```
Frame N
  │
  ├─1─▶ sensor.cast(car.x, car.y, heading, obstacles)
  │              └─▶ [5 ray readings]
  │
  ├─2─▶ obstacle_detector.assess(car.x, car.y)
  │              └─▶ threat_level: CLEAR | WARNING | DANGER
  │
  ├─3─▶ decision_maker.update(threat, dist_to_goal)
  │              └─▶ state: DRIVE | SLOW | STOP | AVOID | ARRIVE
  │
  ├─4─▶ [if AVOID] obstacle_avoidance.replan(car_pos, goal)
  │              └─▶ new path → car.set_path()
  │
  ├─5─▶ car.update(speed_factor)
  │              └─▶ car moves toward next waypoint
  │
  └─6─▶ Render: map → obstacles → sensor → path → car → HUD
```

---

## 4. Performance Characteristics

| Metric | Value |
|--------|-------|
| Simulation FPS | 60 (target) |
| A* planning time | <15ms (typical) |
| Sensor ray cast | <1ms (5 beams, grid lookup) |
| YOLO inference (CPU) | ~200ms per frame (run once at startup) |
| Memory footprint | ~300MB (YOLOv8n model loaded) |

---

## 5. Extension Points

| Feature | Module to Modify |
|---------|-----------------|
| Add GPS noise | `src/simulation/car.py` |
| Traffic light logic | `src/navigation/decision_maker.py` |
| RRT* path planning | Replace `src/navigation/planner.py` |
| Custom YOLO datasets | `src/perception/yolo_detector.py` |
| PID steering control | `src/navigation/controller.py` |
| Real camera input | `main.py` — replace frame source |
