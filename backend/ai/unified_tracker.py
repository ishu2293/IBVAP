import torch
from ultralytics import YOLO
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from backend.config import (
    YOLO_MODEL,
    CONFIDENCE_THRESHOLD,
    VEHICLE_CONFIDENCE_THRESHOLD,
    ALL_TARGET_CLASS_IDS,
    PERSON_CLASS_ID,
    VEHICLE_CLASS_IDS,
    CLASS_NAME_MAPPING,
    MODELS_DIR
)

class UnifiedTracker:
    """
    High-Performance Unified Multi-Object Tracker for IBVAP.
    Executes YOLO + ByteTrack in a SINGLE PASS for all target classes (Person, Car, Truck, Bus, Motorcycle).
    Provides smooth Kalman/EMA bounding box stabilization and consistent persistent IDs (P-001, V-001).
    """
    def __init__(self, model_name: str = YOLO_MODEL, conf_threshold: float = 0.35):
        self.conf_threshold = conf_threshold
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        model_path = MODELS_DIR / model_name
        if model_path.exists():
            self.model = YOLO(str(model_path))
        else:
            self.model = YOLO(model_name)
            
        # Smooth bounding box cache: track_id -> [smoothed_x1, smoothed_y1, smoothed_x2, smoothed_y2]
        self.smoothed_bboxes: Dict[str, List[float]] = {}
        # Tracking ID counters
        self.person_id_map: Dict[int, str] = {}
        self.vehicle_id_map: Dict[int, str] = {}
        self.next_person_num: int = 1
        self.next_vehicle_num: int = 1
        
        print(f"[UnifiedTracker] Initialized Single-Pass YOLO + ByteTrack on device '{self.device}'")

    def track_frame(self, frame: np.ndarray, persist: bool = True) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Runs YOLO + ByteTrack on a single frame in ONE unified pass.
        Returns:
            (person_tracks, vehicle_tracks)
        """
        if frame is None or frame.size == 0:
            return [], []

        results = self.model.track(
            source=frame,
            persist=persist,
            tracker="bytetrack.yaml",
            conf=self.conf_threshold,
            classes=ALL_TARGET_CLASS_IDS,
            device=self.device,
            verbose=False
        )

        person_tracks = []
        vehicle_tracks = []

        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            if boxes.id is not None:
                track_ids = boxes.id.int().cpu().tolist()
                xyxy_list = boxes.xyxy.cpu().numpy().tolist()
                conf_list = boxes.conf.cpu().numpy().tolist()
                cls_list = boxes.cls.int().cpu().tolist()

                for raw_id, xyxy, conf, cls_id in zip(track_ids, xyxy_list, conf_list, cls_list):
                    # Apply Exponential Moving Average (EMA) smoothing to bounding box
                    smoothed_bbox = self._smooth_bbox(raw_id, xyxy)
                    
                    if cls_id == PERSON_CLASS_ID:
                        # Human track
                        if raw_id not in self.person_id_map:
                            self.person_id_map[raw_id] = f"P-{self.next_person_num:03d}"
                            self.next_person_num += 1
                        
                        p_id = self.person_id_map[raw_id]
                        person_tracks.append({
                            "numeric_id": int(raw_id),
                            "track_id": p_id,
                            "bbox": smoothed_bbox,
                            "confidence": float(conf),
                            "class_id": 0,
                            "class_name": "PERSON"
                        })

                    elif cls_id in VEHICLE_CLASS_IDS:
                        # Vehicle track
                        if raw_id not in self.vehicle_id_map:
                            self.vehicle_id_map[raw_id] = f"V-{self.next_vehicle_num:03d}"
                            self.next_vehicle_num += 1
                        
                        v_id = self.vehicle_id_map[raw_id]
                        v_type = CLASS_NAME_MAPPING.get(cls_id, "CAR")
                        vehicle_tracks.append({
                            "numeric_id": int(raw_id),
                            "track_id": v_id,
                            "bbox": smoothed_bbox,
                            "confidence": float(conf),
                            "class_id": int(cls_id),
                            "class_name": v_type
                        })

        return person_tracks, vehicle_tracks

    def _smooth_bbox(self, raw_id: int, current_bbox: List[float], alpha: float = 0.70) -> List[float]:
        """
        Smooths bounding box coordinates across frames to eliminate jitter.
        """
        key = str(raw_id)
        if key not in self.smoothed_bboxes:
            self.smoothed_bboxes[key] = current_bbox
            return current_bbox

        prev = self.smoothed_bboxes[key]
        smoothed = [
            alpha * c + (1.0 - alpha) * p
            for c, p in zip(current_bbox, prev)
        ]
        self.smoothed_bboxes[key] = smoothed
        return smoothed

    def reset(self):
        """
        Resets tracking states for a new session.
        """
        self.smoothed_bboxes.clear()
        self.person_id_map.clear()
        self.vehicle_id_map.clear()
        self.next_person_num = 1
        self.next_vehicle_num = 1
        if hasattr(self.model, "predictor") and self.model.predictor is not None:
            self.model.predictor = None
