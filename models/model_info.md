# Model Information

## YOLOv8n (Nano) — Primary Perception Model

| Property | Value |
|----------|-------|
| Framework | Ultralytics YOLOv8 |
| Variant | YOLOv8n (Nano — fastest, smallest) |
| File | `yolov8n.pt` (placed in project root) |
| Parameters | ~3.2M |
| Input Size | 640×640 (auto-resized) |
| Dataset | COCO (80 classes) |
| mAP@50 | 37.3% (COCO val) |
| Inference Speed | ~80 FPS on CPU, ~400 FPS on GPU |

## Classes Used in This Project

We filter YOLOv8 detections to the following obstacle-relevant COCO classes:

| Class ID | Label | Relevance |
|----------|-------|-----------|
| 0 | person | Pedestrian avoidance |
| 1 | bicycle | Cyclist detection |
| 2 | car | Vehicle detection |
| 5 | bus | Large vehicle |
| 7 | truck | Large vehicle |
| 9 | traffic light | Signal compliance |
| 11 | stop sign | Traffic sign recognition |

## Downloading the Model

The model is automatically downloaded on first run via Ultralytics:
```python
from ultralytics import YOLO
model = YOLO("yolov8n.pt")   # Downloads if not present
```

Or manually:
```bash
# Download pre-trained weights
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

## Model Architecture

YOLOv8 uses a CSP backbone + PANet neck + decoupled detection heads:
- **Backbone**: C2f modules (Cross-Stage Partial)
- **Neck**: PANet (Path Aggregation Network) for multi-scale fusion
- **Head**: Anchor-free, decoupled classification + regression

## Why YOLOv8n?

- ✅ Runs on CPU without GPU — accessible to all students
- ✅ Pretrained on COCO — detects all common road objects
- ✅ Lightweight enough for real-time 60 FPS simulation
- ✅ Industry-standard architecture used in production AV systems

## Future Upgrades

| Model | Use Case |
|-------|----------|
| YOLOv8s/m | Higher accuracy at cost of speed |
| YOLOv8-seg | Instance segmentation for precise obstacle shapes |
| Custom fine-tuned | Train on KITTI / nuScenes for AV-specific data |
