import numpy as np
from typing import List, Dict, Any
from backend.ai.detector import PersonDetector
from backend.ai.tracker import PersonTracker
from backend.config import YOLO_MODEL, CONFIDENCE_THRESHOLD

class HumanTracker:
    """
    Unified AI Module for Human Detection and Tracking.
    Combines PersonDetector and PersonTracker into a modular interface that can later be
    integrated with VehicleDetector, FaceRecognition, ANPR, IntrusionDetector, etc.
    """
    def __init__(self, model_name: str = YOLO_MODEL, conf_threshold: float = CONFIDENCE_THRESHOLD):
        self.detector = PersonDetector(model_name=model_name, conf_threshold=conf_threshold)
        self.tracker = PersonTracker(model_name=model_name, conf_threshold=conf_threshold)

    def process_frame(self, frame: np.ndarray, frame_number: int) -> List[Dict[str, Any]]:
        """
        Processes a raw video frame and returns persistent track outputs with bounding boxes, confidence, and IDs.
        """
        # Run ByteTrack directly (which includes YOLO detection under the hood)
        tracked_objects = self.tracker.track_frame(frame, persist=True)
        return tracked_objects

    def reset(self):
        """
        Reset tracker session state when starting a new video.
        """
        self.tracker.reset()
