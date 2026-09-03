import cv2
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from backend.config import PLATE_CONFIDENCE_THRESHOLD

class PlateDetector:
    """
    Dedicated License Plate Detection Module.
    Locates license plate bounding boxes and extracts plate crops within a detected vehicle bounding box.
    """
    def __init__(self, conf_threshold: float = PLATE_CONFIDENCE_THRESHOLD):
        self.conf_threshold = conf_threshold

    def detect_plate(
        self,
        frame: np.ndarray,
        vehicle_bbox: List[float]
    ) -> Optional[Dict[str, Any]]:
        """
        Extracts the vehicle crop, detects license plate candidates,
        and returns the best detected plate region with bounding box and confidence.

        Returns:
        {
            'plate_bbox_frame': [px1, py1, px2, py2],  # In global frame coordinates
            'plate_bbox_vehicle': [vx1, vy1, vx2, vy2], # Relative to vehicle crop
            'plate_crop': np.ndarray,
            'confidence': float,
            'vehicle_crop': np.ndarray
        } or None
        """
        if frame is None or frame.size == 0:
            return None

        h_frame, w_frame = frame.shape[:2]
        vx1, vy1, vx2, vy2 = map(int, vehicle_bbox)
        vx1 = max(0, min(w_frame - 1, vx1))
        vy1 = max(0, min(h_frame - 1, vy1))
        vx2 = max(0, min(w_frame, vx2))
        vy2 = max(0, min(h_frame, vy2))

        if (vx2 - vx1) < 20 or (vy2 - vy1) < 20:
            return None

        vehicle_crop = frame[vy1:vy2, vx1:vx2]
        vh, vw = vehicle_crop.shape[:2]

        candidates = self._find_plate_candidates(vehicle_crop)

        if not candidates:
            # Fallback: analyze lower-third region of the vehicle (standard plate mounting zone)
            lower_y1 = int(vh * 0.60)
            lower_y2 = int(vh * 0.98)
            lower_x1 = int(vw * 0.15)
            lower_x2 = int(vw * 0.85)

            if (lower_y2 - lower_y1) > 10 and (lower_x2 - lower_x1) > 20:
                plate_crop = vehicle_crop[lower_y1:lower_y2, lower_x1:lower_x2]
                ch, cw = plate_crop.shape[:2]
                if ch < 40 or cw < 120:
                    scale_factor = max(40.0 / max(ch, 1), 140.0 / max(cw, 1))
                    plate_crop = cv2.resize(plate_crop, (int(cw * scale_factor), int(ch * scale_factor)), interpolation=cv2.INTER_CUBIC)
                
                px1 = vx1 + lower_x1
                py1 = vy1 + lower_y1
                px2 = vx1 + lower_x2
                py2 = vy1 + lower_y2
                return {
                    "plate_bbox_frame": [px1, py1, px2, py2],
                    "plate_bbox_vehicle": [lower_x1, lower_y1, lower_x2, lower_y2],
                    "plate_crop": plate_crop,
                    "confidence": 0.65,
                    "vehicle_crop": vehicle_crop
                }
            return None

        best_candidate = candidates[0]
        bx1, by1, bx2, by2, score = best_candidate

        # Add small margin
        margin_x = int((bx2 - bx1) * 0.05)
        margin_y = int((by2 - by1) * 0.05)
        crop_x1 = max(0, bx1 - margin_x)
        crop_y1 = max(0, by1 - margin_y)
        crop_x2 = min(vw, bx2 + margin_x)
        crop_y2 = min(vh, by2 + margin_y)

        plate_crop = vehicle_crop[crop_y1:crop_y2, crop_x1:crop_x2]
        if plate_crop is not None and plate_crop.size > 0:
            ch, cw = plate_crop.shape[:2]
            if ch < 40 or cw < 100:
                scale_factor = max(40.0 / max(ch, 1), 120.0 / max(cw, 1))
                plate_crop = cv2.resize(plate_crop, (int(cw * scale_factor), int(ch * scale_factor)), interpolation=cv2.INTER_CUBIC)

        px1 = vx1 + crop_x1
        py1 = vy1 + crop_y1
        px2 = vx1 + crop_x2
        py2 = vy1 + crop_y2

        return {
            "plate_bbox_frame": [px1, py1, px2, py2],
            "plate_bbox_vehicle": [crop_x1, crop_y1, crop_x2, crop_y2],
            "plate_crop": plate_crop,
            "confidence": round(float(score), 2),
            "vehicle_crop": vehicle_crop
        }

    def _find_plate_candidates(self, vehicle_crop: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """
        Uses morphological filtering, edge gradients, and contour analysis to locate license plates.
        """
        vh, vw = vehicle_crop.shape[:2]
        gray = cv2.cvtColor(vehicle_crop, cv2.COLOR_BGR2GRAY)

        # 1. Morphological Top-hat and Black-hat transforms to highlight plate region
        kernel_rect = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
        tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel_rect)
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel_rect)
        enhanced = cv2.add(gray, tophat)
        enhanced = cv2.subtract(enhanced, blackhat)

        # 2. Sobel horizontal edge gradient
        grad_x = cv2.Sobel(enhanced, cv2.CV_32F, 1, 0, ksize=3)
        grad_x = np.absolute(grad_x)
        (min_val, max_val) = (np.min(grad_x), np.max(grad_x))
        if max_val - min_val > 0:
            grad_x = 255 * ((grad_x - min_val) / (max_val - min_val))
        grad_x = grad_x.astype("uint8")

        # 3. Blur & Otsu threshold
        grad_x = cv2.GaussianBlur(grad_x, (5, 5), 0)
        _, thresh = cv2.threshold(grad_x, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # 4. Morphological closing to connect plate text characters into a single rectangle
        kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 5))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel_close)

        # 5. Find contours
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candidates = []

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if h == 0 or w == 0:
                continue

            aspect_ratio = float(w) / float(h)
            area = w * h
            vehicle_area = vh * vw

            # License plates are strictly located on the lower half/bumper of the vehicle
            y_center = y + h / 2.0
            rel_y = y_center / vh
            if rel_y < 0.52:
                continue

            # License plates typically have aspect ratio between 1.8 and 6.5
            # and occupy between 1% and 35% of the vehicle area
            if 1.8 <= aspect_ratio <= 6.5 and (0.01 * vehicle_area) <= area <= (0.35 * vehicle_area):
                # Score based on aspect ratio, vertical location, and contrast
                ar_score = 1.0 - min(abs(aspect_ratio - 3.8) / 3.8, 1.0)
                pos_score = 0.95 if rel_y >= 0.65 else 0.70
                conf = 0.5 * ar_score + 0.4 * pos_score + 0.1
                candidates.append((x, y, x + w, y + h, min(conf, 0.98)))

        # Sort candidate boxes by score descending
        candidates.sort(key=lambda c: c[4], reverse=True)
        return candidates
