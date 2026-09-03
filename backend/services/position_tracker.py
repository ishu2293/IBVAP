from collections import deque
from typing import Dict, List, Tuple, Any
from backend.config import TRAIL_LENGTH

class PositionTracker:
    """
    Manages spatial positions (center point, foot point) and recent movement history for all tracked persons.
    Limits history buffer per Track ID so memory usage remains constant over long streams.
    """
    def __init__(self, history_length: int = TRAIL_LENGTH):
        self.history_length = history_length
        # Map: track_id -> deque of (foot_x, foot_y)
        self.history: Dict[str, deque] = {}
        # Track lifecycle metadata: track_id -> {first_seen, last_seen, total_frames}
        self.lifecycle: Dict[str, Dict[str, Any]] = {}

    def update_position(self, track_id: str, bbox: List[float], frame_number: int) -> Dict[str, Any]:
        """
        Calculates center point and foot point for a bounding box [x1, y1, x2, y2].
        Updates history buffer and track lifecycle.
        Returns dict containing center, foot_point, and position history list.
        """
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) / 2.0
        center_y = (y1 + y2) / 2.0
        foot_x = (x1 + x2) / 2.0
        foot_y = y2

        if track_id not in self.history:
            self.history[track_id] = deque(maxlen=self.history_length)
            self.lifecycle[track_id] = {
                "first_seen_frame": frame_number,
                "last_seen_frame": frame_number,
                "total_frames_tracked": 1
            }
        else:
            self.lifecycle[track_id]["last_seen_frame"] = frame_number
            self.lifecycle[track_id]["total_frames_tracked"] += 1

        self.history[track_id].append((foot_x, foot_y))

        return {
            "center": [center_x, center_y],
            "foot_point": [foot_x, foot_y],
            "history": list(self.history[track_id]),
            "first_seen_frame": self.lifecycle[track_id]["first_seen_frame"],
            "last_seen_frame": self.lifecycle[track_id]["last_seen_frame"],
            "total_frames_tracked": self.lifecycle[track_id]["total_frames_tracked"]
        }

    def get_track_lifecycle(self, track_id: str) -> Dict[str, Any]:
        return self.lifecycle.get(track_id, {
            "first_seen_frame": 0,
            "last_seen_frame": 0,
            "total_frames_tracked": 0
        })

    def reset(self):
        """
        Clear history on stream restart.
        """
        self.history.clear()
        self.lifecycle.clear()
