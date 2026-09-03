import torch
from ultralytics import YOLO
import numpy as np
from typing import List, Dict, Any
from backend.config import (
    YOLO_MODEL,
    VEHICLE_CONFIDENCE_THRESHOLD,
    VEHICLE_CLASS_IDS,
    CLASS_NAME_MAPPING,
    MODELS_DIR
)

class VehicleDetector:
    """
    Dedicated AI Module for Vehicle Detection & Classification.
    Extracts vehicle classes: CAR (2), MOTORCYCLE (3), BUS (5), TRUCK (7).
    """
    def __init__(self, model_name: str = YOLO_MODEL, conf_threshold: float = VEHICLE_CONFIDENCE_THRESHOLD):
        self.conf_threshold = conf_threshold
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        model_path = MODELS_DIR / model_name
        if model_path.exists():
            self.model = YOLO(str(model_path))
        else:
            self.model = YOLO(model_name)
            
        print(f"[VehicleDetector] Initialized YOLO model '{model_name}' on device '{self.device}'")

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Runs YOLO inference on a frame (BGR image) and extracts vehicle detections.
        Returns list of dicts:
        [{'bbox': [x1, y1, x2, y2], 'confidence': float, 'class_id': int, 'class_name': str}]
        """
        if frame is None or frame.size == 0:
            return []

        results = self.model.predict(
            source=frame,
            conf=self.conf_threshold,
            classes=VEHICLE_CLASS_IDS,
            device=self.device,
            verbose=False
        )

        detections = []
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            for box in boxes:
                xyxy = box.xyxy[0].cpu().numpy().tolist()  # [x1, y1, x2, y2]
                conf = float(box.conf[0].cpu().item())
                cls_id = int(box.cls[0].cpu().item())
                class_name = CLASS_NAME_MAPPING.get(cls_id, "VEHICLE")
                
                detections.append({
                    "bbox": xyxy,
                    "confidence": conf,
                    "class_id": cls_id,
                    "class_name": class_name
                })
                
        return detections
