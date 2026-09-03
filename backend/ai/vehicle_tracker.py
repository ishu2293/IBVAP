import torch
from ultralytics import YOLO
import numpy as np
from typing import List, Dict, Any, Optional
from backend.config import (
    YOLO_MODEL,
    VEHICLE_CONFIDENCE_THRESHOLD,
    VEHICLE_CLASS_IDS,
    CLASS_NAME_MAPPING,
    TRACK_BUFFER,
    MODELS_DIR
)

class VehicleTracker:
    """
    Responsible for ByteTrack multi-object tracking for vehicle classes across video frames.
    Uses Ultralytics ByteTrack with persistent track IDs (V-001, V-002, etc.).
    """
    def __init__(self, model_name: str = YOLO_MODEL, conf_threshold: float = VEHICLE_CONFIDENCE_THRESHOLD):
        self.conf_threshold = conf_threshold
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        model_path = MODELS_DIR / model_name
        if model_path.exists():
            self.model = YOLO(str(model_path))
        else:
            self.model = YOLO(model_name)
            
        print(f"[VehicleTracker] Initialized ByteTrack for Vehicles with model '{model_name}' on device '{self.device}'")

    def track_frame(self, frame: np.ndarray, persist: bool = True) -> List[Dict[str, Any]]:
        """
        Runs YOLO + ByteTrack for vehicle classes on a single frame.
        Returns active tracked vehicle objects:
        [{
            'numeric_id': 1,
            'track_id': 'V-001',
            'bbox': [x1, y1, x2, y2],
            'confidence': 0.93,
            'class_id': 2,
            'class_name': 'CAR'
        }]
        """
        if frame is None or frame.size == 0:
            return []

        results = self.model.track(
            source=frame,
            persist=persist,
            tracker="bytetrack.yaml",
            conf=self.conf_threshold,
            classes=VEHICLE_CLASS_IDS,
            device=self.device,
            verbose=False
        )

        tracks = []
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            if boxes.id is not None:
                track_ids = boxes.id.int().cpu().tolist()
                xyxy_list = boxes.xyxy.cpu().numpy().tolist()
                conf_list = boxes.conf.cpu().numpy().tolist()
                cls_list = boxes.cls.int().cpu().tolist()
                
                for num_id, xyxy, conf, cls_id in zip(track_ids, xyxy_list, conf_list, cls_list):
                    formatted_id = f"V-{num_id:03d}"
                    class_name = CLASS_NAME_MAPPING.get(cls_id, "VEHICLE")
                    tracks.append({
                        "numeric_id": int(num_id),
                        "track_id": formatted_id,
                        "bbox": xyxy,
                        "confidence": float(conf),
                        "class_id": int(cls_id),
                        "class_name": class_name
                    })
            else:
                # Fallback if tracker didn't assign ID in current frame
                xyxy_list = boxes.xyxy.cpu().numpy().tolist()
                conf_list = boxes.conf.cpu().numpy().tolist()
                cls_list = boxes.cls.int().cpu().tolist()
                for i, (xyxy, conf, cls_id) in enumerate(zip(xyxy_list, conf_list, cls_list)):
                    formatted_id = f"V-TMP-{i+1}"
                    class_name = CLASS_NAME_MAPPING.get(cls_id, "VEHICLE")
                    tracks.append({
                        "numeric_id": i + 1,
                        "track_id": formatted_id,
                        "bbox": xyxy,
                        "confidence": float(conf),
                        "class_id": int(cls_id),
                        "class_name": class_name
                    })
                    
        return tracks

    def reset(self):
        """
        Resets tracker state for a new video stream session.
        """
        if hasattr(self.model, "predictor") and self.model.predictor is not None:
            self.model.predictor = None
