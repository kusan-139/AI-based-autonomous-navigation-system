"""
yolo_detector.py
================
Perception Module — Object Detection using YOLOv8

Responsibilities:
  - Load a pretrained YOLOv8 model (yolov8n.pt, lightweight)
  - Run inference on a single BGR frame (OpenCV format)
  - Filter detections by confidence AND obstacle class list
  - Return bounding boxes with class labels and confidence scores
  - Draw annotated bounding boxes onto the frame for visualization

Industry Pattern: This mirrors how real AV stacks (e.g., Waymo/Tesla)
integrate a CNN-based object detector as the primary perception module.
"""

import cv2
import numpy as np
from ultralytics import YOLO

from src.config import (
    YOLO_MODEL_PATH,
    YOLO_CONFIDENCE,
    OBSTACLE_CLASSES,
)

# COCO dataset class names (80 classes)
COCO_NAMES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train",
    "truck", "boat", "traffic light", "fire hydrant", "stop sign",
    "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow",
    "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag",
    "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite",
    "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana",
    "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza",
    "donut", "cake", "chair", "couch", "potted plant", "bed", "dining table",
    "toilet", "tv", "laptop", "mouse", "remote", "keyboard", "cell phone",
    "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock",
    "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
]


class YOLODetector:
    """
    YOLOv8-based object detector for the autonomous navigation pipeline.

    Usage:
        detector = YOLODetector()
        detections = detector.detect(frame)         # list of Detection dicts
        annotated  = detector.draw_detections(frame, detections)
    """

    def __init__(self, model_path: str = YOLO_MODEL_PATH):
        print(f"[YOLODetector] Loading model: {model_path}")
        self.model = YOLO(model_path)
        self.confidence_threshold = YOLO_CONFIDENCE
        self.obstacle_classes = set(OBSTACLE_CLASSES)
        print("[YOLODetector] ✅ Model ready.")

    # ------------------------------------------------------------------
    def detect(self, frame: np.ndarray) -> list[dict]:
        """
        Run inference on a BGR frame.

        Returns:
            List of dicts:
            {
                'bbox':   (x1, y1, x2, y2),
                'conf':   float,
                'cls_id': int,
                'label':  str
            }
            Only detections above confidence threshold AND in obstacle
            class list are returned.
        """
        results = self.model(frame, verbose=False)
        detections = []

        for result in results:
            for box in result.boxes:
                conf   = float(box.conf[0])
                cls_id = int(box.cls[0])

                if conf < self.confidence_threshold:
                    continue
                if cls_id not in self.obstacle_classes:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                label = COCO_NAMES[cls_id] if cls_id < len(COCO_NAMES) else f"cls{cls_id}"

                detections.append({
                    "bbox":   (x1, y1, x2, y2),
                    "conf":   conf,
                    "cls_id": cls_id,
                    "label":  label,
                })

        return detections

    # ------------------------------------------------------------------
    def get_obstacle_centroids(self, detections: list[dict]) -> list[tuple]:
        """
        Convert bounding boxes → centroid (cx, cy) points.
        Used by the path planner to inject obstacles into the grid.
        """
        centroids = []
        for d in detections:
            x1, y1, x2, y2 = d["bbox"]
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            centroids.append((cx, cy))
        return centroids

    # ------------------------------------------------------------------
    def draw_detections(self, frame: np.ndarray, detections: list[dict]) -> np.ndarray:
        """
        Draw annotated bounding boxes with label + confidence on frame.
        Returns the annotated frame (BGR).
        """
        for d in detections:
            x1, y1, x2, y2 = d["bbox"]
            label = f"{d['label']} {d['conf']:.2f}"

            # Box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 80), 2)

            # Label background
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
            cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 4, y1), (0, 255, 80), -1)

            # Label text
            cv2.putText(
                frame, label, (x1 + 2, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA
            )

        # Counter
        cv2.putText(
            frame,
            f"Objects Detected: {len(detections)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 80), 2, cv2.LINE_AA
        )
        return frame