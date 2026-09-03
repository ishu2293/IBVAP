import torch
from ultralytics import YOLO
import numpy as np
from typing import List, Dict, Any
from backend.config import YOLO_MODEL, CONFIDENCE_THRESHOLD, PERSON_CLASS_ID, MODELS_DIR

class PersonDetector:
    """
    Responsible solely for taking a video frame and returning YOLO detections filtered for the 'person' class.
    """
    def __init__(self, model_name: str = YOLO_MODEL, conf_threshold: float = CONFIDENCE_THRESHOLD):
        self.conf_threshold = conf_threshold
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Look for model in local models directory or load by name
        model_path = MODELS_DIR / model_name
        if model_path.exists():
            self.model = YOLO(str(model_path))
        else:
            # Ultralytics will auto-download yolo11n.pt if not present and save to current dir / weights
            self.model = YOLO(model_name)
            
        print(f"[PersonDetector] Initialized YOLO model '{model_name}' on device '{self.device}'")

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Runs YOLO inference on a frame (BGR image) and extracts person detections.
        Returns list of dicts: [{'bbox': [x1, y1, x2, y2], 'confidence': float, 'class_id': 0, 'class_name': 'person'}]
        """
        if frame is None or frame.size == 0:
            return []

        results = self.model.predict(
            source=frame,
            conf=self.conf_threshold,
            classes=[PERSON_CLASS_ID],
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
                
                detections.append({
                    "bbox": xyxy,
                    "confidence": conf,
                    "class_id": cls_id,
                    "class_name": "person"
                })
                
        return detections
