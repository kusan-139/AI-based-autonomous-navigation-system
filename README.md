# 🚗 AI-Based Autonomous Navigation System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![PyGame](https://img.shields.io/badge/PyGame-2.5-green?style=for-the-badge&logo=python)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-purple?style=for-the-badge)
![OpenCV](https://img.shields.io/badge/OpenCV-4.9-red?style=for-the-badge&logo=opencv)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Stars](https://img.shields.io/github/stars/YOUR_USERNAME/AI-Autonomous-Navigation-System?style=for-the-badge)

**A complete, industry-oriented autonomous navigation simulation built in Python.**  
*Perception → Decision Making → Path Planning → Control — all in one project.*

[📺 Demo](#-demo) • [🚀 Quick Start](#-quick-start) • [🏗️ Architecture](#-architecture) • [📁 Structure](#-folder-structure) • [📖 Docs](#-documentation)

</div>

---

## 📺 Demo

> The car (green) navigates from **start (top-left)** to **goal (bottom-right)**
> through a simulated urban road grid, avoiding dynamically placed obstacles
> using real-time sensor data and A* path replanning.

| Simulation Running | HUD State Machine | YOLO Detection |
|:-:|:-:|:-:|
| *Pygame window with road grid, car, path, sensors* | *Live state: DRIVE/SLOW/STOP/AVOID/ARRIVE* | *YOLOv8 bounding boxes on real image* |

```
python main.py   ←  one command, everything starts
```

---

## ✨ Features

- 🧠 **YOLOv8 Object Detection** — detects people, cars, trucks, stop signs in real images
- 🛣️ **Classical Lane Detection** — HoughLinesP-based left/right lane marking extraction
- 📡 **Virtual Ultrasonic Sensor** — 5-beam ray-cast sensor simulating proximity detection
- 🗺️ **A★ Path Planning** — 8-directional grid search with octile heuristic + path smoothing
- 🔁 **Dynamic Replanning** — automatic obstacle inflation and path recompute on STOP timeout
- 🤖 **FSM Decision Maker** — 5-state behavioral planner (DRIVE / SLOW / STOP / AVOID / ARRIVE)
- 📊 **Live HUD** — real-time state badge, telemetry, sensor bars, color legend
- 📝 **Structured Logger** — timestamped `.log` files tracking every event
- 🏙️ **Procedural City Map** — road grid with lane dashes, generated without any external files

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                   AUTONOMOUS NAVIGATION PIPELINE                    │
│                                                                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────┐     │
│  │  PERCEPTION  │────▶│   DECISION   │────▶│   NAVIGATION    │     │
│  │              │     │   MAKING     │     │                  │     │
│  │ • YOLOv8     │     │              │     │ • A* Planner     │     │
│  │ • Lane Det.  │     │ • FSM States │     │ • Path Smooth    │     │
│  │ • Obstacle   │     │   DRIVE ●    │     │ • Obst. Avoid.   │     │ 
│  │   Detector   │     │   SLOW  ●    │     │ • Controller     │     │
│  │ • Sensor     │     │   STOP  ●    │     │                  │     │
│  │   Simulation │     │   AVOID ●    │     └────────┬─────────┘     │
│  └──────┬───────┘     │   ARRIVE●    │              │               │
│         │             └─────────────┘              │                │
│         ▼                                           ▼               │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │               SIMULATION & UTILS LAYER                      │    │
│  │  Environment · Car Agent · Obstacles · Map · Logger · HUD   │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 / 3.10 / 3.11
- pip (latest)
- ~500 MB disk (YOLOv8n model + dependencies)

### Installation

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/AI-Autonomous-Navigation-System.git
cd AI-Autonomous-Navigation-System

# 2. Virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run!
python main.py
```

### Controls

| Key | Action |
|-----|--------|
| `Space` | Pause / Resume simulation |
| `R` | Reset car to start position |
| `ESC` | Quit |

### Optional: Enable YOLO Detection
Place any street/road image into `assets/test_frames/`:
```
assets/test_frames/street.jpg   ←  YOLO runs automatically
```

---

## 📁 Folder Structure

```
AI-Autonomous-Navigation-System/
│
├── 📂 assets/
│   └── test_frames/          ← Drop road images here for YOLO detection
│
├── 📂 data/
│   ├── sample_obstacles.json ← Pre-defined obstacle configs
│   ├── sample_paths.json     ← Recorded A* path data
│   └── README.md
│
├── 📂 docs/
│   ├── architecture.png      ← System architecture diagram
│   ├── system_design.md      ← Full technical design document
│   └── setup_guide.md        ← Step-by-step setup instructions
│
├── 📂 models/
│   ├── yolov8n.pt            ← YOLOv8 pretrained weights (auto-downloaded)
│   └── model_info.md         ← Model architecture & performance details
│
├── 📂 notebooks/
│   ├── 01_system_overview.ipynb      ← Project intro + architecture walkthrough
│   ├── 02_perception_pipeline.ipynb  ← YOLO + lane detection demo
│   └── 03_path_planning_demo.ipynb   ← A* visualization + FSM states
│
├── 📂 outputs/
│   ├── logs/                 ← Runtime simulation event logs
│   ├── paths/                ← Saved path outputs
│   └── screenshots/          ← Captured simulation frames
│
├── 📂 src/
│   ├── config.py             ← All simulation settings (edit to tune)
│   │
│   ├── 📂 perception/
│   │   ├── yolo_detector.py  ← YOLOv8 object detection
│   │   ├── lane_detector.py  ← HoughLines lane detection
│   │   └── obstacle_detector.py ← Proximity threat assessment
│   │
│   ├── 📂 navigation/
│   │   ├── planner.py        ← A* (8-dir, octile heuristic)
│   │   ├── controller.py     ← Path smoothing controller
│   │   ├── decision_maker.py ← FSM behavioral planner
│   │   └── obstacle_avoidance.py ← Dynamic replanning
│   │
│   ├── 📂 simulation/
│   │   ├── environment.py    ← Pygame window manager
│   │   ├── car.py            ← Vehicle kinematic agent
│   │   ├── obstacles.py      ← Dynamic obstacle manager
│   │   ├── sensor.py         ← Virtual ultrasonic sensor
│   │   └── map_loader.py     ← Procedural city map
│   │
│   └── 📂 utils/
│       ├── logger.py         ← Structured event logger
│       └── visualizer.py     ← HUD overlay renderer
│
├── main.py                   ← 🚀 Run this!
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🧩 Module Breakdown

### Perception
| Module | Algorithm | Industry Analog |
|--------|-----------|-----------------|
| `yolo_detector.py` | YOLOv8 CNN inference | Waymo/Tesla object detection |
| `lane_detector.py` | Canny + HoughLinesP | OpenPilot lane baseline |
| `obstacle_detector.py` | Euclidean proximity | LiDAR fusion layer |
| `sensor.py` | Ray-march casting | Ultrasonic / radar |

### Navigation
| Module | Algorithm | Industry Analog |
|--------|-----------|-----------------|
| `planner.py` | A* (8-dir, octile) | Apollo DP Planner |
| `controller.py` | Gradient descent smoothing | Pure Pursuit |
| `decision_maker.py` | Finite State Machine | Apollo Behavioral Planner |
| `obstacle_avoidance.py` | Obstacle inflation + replan | Apollo EM Planner |

---

## 📓 Notebooks

| Notebook | What You Learn |
|----------|----------------|
| `01_system_overview` | Project architecture, module roles, industry context |
| `02_perception_pipeline` | Run YOLO on images, visualize lane detection |
| `03_path_planning_demo` | A* animation, FSM state transitions, obstacle inflation |

```bash
jupyter notebook notebooks/
```

---

## 📊 Technical Specifications

| Component | Specification |
|-----------|---------------|
| Path Algorithm | A* with octile heuristic, 8-directional movement |
| Path Smoothing | Gradient descent (weight_smooth=0.5, tolerance=0.001) |
| Decision States | DRIVE / SLOW / STOP / AVOID / ARRIVE |
| Sensor Beams | 5 beams at -60°, -30°, 0°, +30°, +60° |
| Sensor Range | 100px (configurable in `config.py`) |
| Danger Threshold | 40px (triggers STOP state) |
| YOLO Model | YOLOv8n — 3.2M params, 80 COCO classes |
| YOLO Confidence | 0.40 threshold (configurable) |
| Simulation FPS | 60 Hz |
| Grid Size | 20px (configurable) |

---

## ⚙️ Configuration

All system parameters are in `src/config.py`:

```python
# Tune car speed
CAR_SPEED = 3.0         # pixels per frame

# Tune obstacle detection sensitivity
DANGER_THRESHOLD = 40   # pixels — triggers STOP
SENSOR_RANGE = 100      # pixels — sensor max range

# Tune path planning
GRID_SIZE = 20          # grid cell size
OBSTACLE_RADIUS = 30    # obstacle inflation buffer

# Change start & goal
START_POS = (60, 60)
GOAL_POS  = (820, 570)
```

---

## 🛣️ Roadmap

- [x] YOLOv8 object detection
- [x] Lane detection (HoughLines)
- [x] A* path planning (8-directional)
- [x] FSM decision maker
- [x] Dynamic obstacle avoidance
- [x] Virtual sensor simulation
- [x] HUD visualizer
- [x] Structured logging
- [ ] RRT* path planning (stretch goal)
- [ ] PID steering controller
- [ ] Traffic light state machine
- [ ] KITTI/nuScenes dataset integration
- [ ] ROS2 node wrapper

---

## 🤝 Contributing

Pull requests welcome! For major changes, please open an issue first.

```bash
git checkout -b feature/your-feature
git commit -m "Add: your feature description"
git push origin feature/your-feature
```

---

## 📖 References

1. [YOLOv8 — Ultralytics](https://github.com/ultralytics/ultralytics)
2. [Introduction to A* — Red Blob Games](https://www.redblobgames.com/pathfinding/a-star/introduction.html)
3. [Apollo AV Stack — Baidu](https://github.com/ApolloAuto/apollo)
4. [CARLA Simulator](https://carla.org/)
5. [OpenPilot — comma.ai](https://github.com/commaai/openpilot)
6. [highway-env — Edouard Leurent](https://github.com/Farama-Foundation/HighwayEnv)

---

## 👤 Author

**Kusan Chakraborty**  
🎓 Computer Science Engineering Student  
🔗 [LinkedIn](https://www.linkedin.com/in/kusan-chakraborty-988225359) 

> *Built as a portfolio project demonstrating autonomous systems, computer vision, path planning, and simulation.*

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">
⭐ Star this repo if it helped you!
</div>
