import math
from typing import List, Tuple, Dict
from backend.config import DIRECTION_THRESHOLD

class MovementAnalyzer:
    """
    Analyzes recent position history of tracked persons to calculate movement direction and motion status.
    Prevents camera jitter/model noise from flip-flopping direction using configurable thresholds.
    """
    def __init__(self, threshold: float = DIRECTION_THRESHOLD):
        self.threshold = threshold

    def analyze_movement(self, history: List[Tuple[float, float]]) -> Dict[str, str]:
        """
        Analyzes position history [(x0, y0), ..., (xn, yn)].
        Returns dict with keys: 'direction', 'status'.
        """
        if not history or len(history) < 2:
            return {"direction": "STATIONARY", "status": "Stationary"}

        # Compare current position (last entry) against an earlier point in history for stable direction
        lookback = min(len(history) - 1, 5)
        prev_x, prev_y = history[-1 - lookback]
        curr_x, curr_y = history[-1]

        dx = curr_x - prev_x
        dy = curr_y - prev_y  # Note: Image Y decreases upwards, increases downwards

        dist = math.hypot(dx, dy)
        if dist < self.threshold:
            return {"direction": "STATIONARY", "status": "Stationary"}

        # Determine horizontal component
        h_dir = ""
        if dx > self.threshold * 0.5:
            h_dir = "EAST"
        elif dx < -self.threshold * 0.5:
            h_dir = "WEST"

        # Determine vertical component (dy < 0 is UP/NORTH in image coordinates)
        v_dir = ""
        if dy < -self.threshold * 0.5:
            v_dir = "NORTH"
        elif dy > self.threshold * 0.5:
            v_dir = "SOUTH"

        # Combine components
        if v_dir and h_dir:
            direction = f"{v_dir}-{h_dir}"
        elif v_dir:
            direction = v_dir
        elif h_dir:
            direction = h_dir
        else:
            direction = "STATIONARY"

        status = "Moving" if direction != "STATIONARY" else "Stationary"
        return {"direction": direction, "status": status}
