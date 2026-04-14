# Data Directory

This folder contains sample data files used for testing, notebook demonstrations,
and offline analysis of the navigation system.

## Files

| File | Description |
|------|-------------|
| `sample_obstacles.json` | Pre-defined obstacle configurations with YOLO-style bounding boxes |
| `sample_paths.json` | Recorded A* path output from a representative simulation run |

## Format

### sample_obstacles.json
Each entry represents a detected object:
```json
{
  "id": 1,
  "label": "person",
  "cx": 300, "cy": 320,        ← centroid (used by ObstacleDetector)
  "x1": 275, "y1": 290,        ← bounding box top-left
  "x2": 325, "y2": 370,        ← bounding box bottom-right
  "confidence": 0.92,
  "source": "YOLO"
}
```

### sample_paths.json
```json
{
  "start": [60, 60],
  "goal": [820, 570],
  "algorithm": "A* (8-directional, octile heuristic)",
  "waypoints": [[x, y], ...]
}
```

## Usage in Notebooks
```python
import json
with open("data/sample_obstacles.json") as f:
    obstacles = json.load(f)
```
