# Setup & Execution Guide

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.9, 3.10, or 3.11 |
| pip | latest |
| RAM | ≥ 4 GB |
| OS | Windows / macOS / Linux |
| GPU | Optional (CPU is sufficient) |

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Autonomous-Navigation-System.git
cd AI-Autonomous-Navigation-System
```

---

## Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** First run downloads YOLOv8n weights (~6MB) automatically.
> If you already have `yolov8n.pt` in the project root, it won't re-download.

---

## Step 4: (Optional) Add Test Images for YOLO

Place any road/street images into `assets/test_frames/`:
```
assets/
└── test_frames/
    ├── street1.jpg
    ├── highway.png
    └── intersection.jpg
```

If this folder is empty, YOLO is skipped and simulation runs in pure-simulation mode (which still works perfectly for demonstrating the full pipeline).

---

## Step 5: Run the Simulation

```bash
python main.py
```

### Controls

| Key | Action |
|-----|--------|
| `Space` | Pause / Resume |
| `R` | Reset car to start |
| `ESC` | Quit |

---

## Step 6: Run Jupyter Notebooks

```bash
jupyter notebook notebooks/
```

Open notebooks in order:
1. `01_system_overview.ipynb`
2. `02_perception_pipeline.ipynb`
3. `03_path_planning_demo.ipynb`

---

## Outputs

After running, check these directories:

| Directory | Contents |
|-----------|----------|
| `outputs/logs/` | Timestamped `.log` files with full simulation telemetry |
| `outputs/screenshots/` | (Add screenshot saving with `S` key — future) |
| `outputs/paths/` | Saved path data for analysis |

---

## Troubleshooting

### `pygame.error: No video mode has been set`
→ Make sure you're running in a GUI environment (not SSH without X forwarding).

### `ModuleNotFoundError: No module named 'ultralytics'`
→ Run `pip install ultralytics` or re-run `pip install -r requirements.txt`

### `Import "src.X" could not be resolved`
→ Run `python main.py` from the project root directory (where `main.py` lives).

### Car doesn't move
→ Check `src/config.py`: ensure `START_POS` and `GOAL_POS` are on road cells.
→ Run with a road cell start like `(100, 100)` and goal `(820, 540)`.

### Simulation runs but no path appears
→ Your START or GOAL may be inside an obstacle. Check `map_loader.py` road coordinates.

---

## Verifying Correct Output

✅ Pygame window opens with dark road grid  
✅ Car (green rotated rectangle) starts at top-left  
✅ HUD panel (left) shows "DRIVE" in green  
✅ Path (white/blue dots) renders from start to goal  
✅ Sensor rays (orange) radiate from car  
✅ `outputs/logs/sim_YYYYMMDD_HHMMSS.log` is created  
