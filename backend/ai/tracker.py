import torch
from ultralytics import YOLO
import numpy as np
from typing import List, Dict, Any, Optional
from backend.config import YOLO_MODEL, CONFIDENCE_THRESHOLD, PERSON_CLASS_ID, TRACK_BUFFER, MODELS_DIR

class PersonTracker:
    """
    Responsible for ByteTrack multi-object tracking for the 'person' class across consecutive video frames.
    Uses Ultralytics ByteTrack integration with frame persistence.
    """
    def __init__(self, model_name: str = YOLO_MODEL, conf_threshold: float = CONFIDENCE_THRESHOLD):
        self.conf_threshold = conf_threshold
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        model_path = MODELS_DIR / model_name
        if model_path.exists():
            self.model = YOLO(str(model_path))
        else:
            self.model = YOLO(model_name)
            
        print(f"[PersonTracker] Initialized ByteTrack with model '{model_name}' on device '{self.device}'")

    def track_frame(self, frame: np.ndarray, persist: bool = True) -> List[Dict[str, Any]]:
        """
        Runs YOLO + ByteTrack on a single frame.
        Returns active tracked objects:
        [{'numeric_id': 1, 'track_id': 'P-001', 'bbox': [x1, y1, x2, y2], 'confidence': 0.94, 'class_name': 'person'}]
        """
        if frame is None or frame.size == 0:
            return []

        results = self.model.track(
            source=frame,
            persist=persist,
            tracker="bytetrack.yaml",
            conf=self.conf_threshold,
            classes=[PERSON_CLASS_ID],
            device=self.device,
            verbose=False
        )

        tracks = []
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            # Check if IDs are assigned by tracker
            if boxes.id is not None:
                track_ids = boxes.id.int().cpu().tolist()
                xyxy_list = boxes.xyxy.cpu().numpy().tolist()
                conf_list = boxes.conf.cpu().numpy().tolist()
                
                for num_id, xyxy, conf in zip(track_ids, xyxy_list, conf_list):
                    formatted_id = f"P-{num_id:03d}"
                    tracks.append({
                        "numeric_id": int(num_id),
                        "track_id": formatted_id,
                        "bbox": xyxy,
                        "confidence": float(conf),
                        "class_name": "person"
                    })
            else:
                # Fallback if tracker didn't assign ID in current frame
                xyxy_list = boxes.xyxy.cpu().numpy().tolist()
                conf_list = boxes.conf.cpu().numpy().tolist()
                for i, (xyxy, conf) in enumerate(zip(xyxy_list, conf_list)):
                    formatted_id = f"P-TMP-{i+1}"
                    tracks.append({
                        "numeric_id": i + 1,
                        "track_id": formatted_id,
                        "bbox": xyxy,
                        "confidence": float(conf),
                        "class_name": "person"
                    })
                    
        return tracks

    def reset(self):
        """
        Resets tracker state for a new video stream session.
        """
        # Reset predictor so Ultralytics creates a clean tracker instance on next stream
        if hasattr(self.model, "predictor") and self.model.predictor is not None:
            self.model.predictor = None
