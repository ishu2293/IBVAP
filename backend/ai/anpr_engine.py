import cv2
import time
import numpy as np
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from backend.ai.plate_detector import PlateDetector
from backend.ai.ocr_engine import OCREngine
from backend.config import (
    PLATE_CONFIDENCE_THRESHOLD,
    OCR_CONFIDENCE_THRESHOLD,
    ANPR_CONSENSUS_FRAMES,
    ANPR_PROCESS_INTERVAL,
    PLATE_CROPS_DIR,
    VEHICLE_CROPS_DIR
)

class ANPREngine:
    """
    Automatic Number Plate Recognition (ANPR) Orchestrator with Multi-Frame Consensus.
    Integrates PlateDetector and OCREngine to reliably extract, verify, and associate
    license plates with persistent Vehicle Track IDs (e.g., V-001 -> MH12AB1234).
    """
    def __init__(self):
        self.plate_detector = PlateDetector(conf_threshold=PLATE_CONFIDENCE_THRESHOLD)
        self.ocr_engine = OCREngine(conf_threshold=OCR_CONFIDENCE_THRESHOLD)
        
        # Per-vehicle track ID memory:
        # track_id -> {
        #    'candidates': [{'text': str, 'ocr_conf': float, 'plate_conf': float, 'frame': int}],
        #    'final_plate': Optional[str],
        #    'final_conf': Optional[float],
        #    'is_confirmed': bool,
        #    'last_processed_frame': int,
        #    'plate_crop_path': Optional[str],
        #    'vehicle_crop_path': Optional[str],
        #    'last_plate_bbox': Optional[List[float]]
        # }
        self.vehicle_anpr_records: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "candidates": [],
            "final_plate": None,
            "final_conf": 0.0,
            "is_confirmed": False,
            "last_processed_frame": 0,
            "plate_crop_path": None,
            "vehicle_crop_path": None,
            "last_plate_bbox": None,
            "status": "Not Detected"
        })

    def process_vehicle_frame(
        self,
        frame: np.ndarray,
        track_id: str,
        vehicle_bbox: List[float],
        frame_number: int,
        camera_id: str = "CAM-01"
    ) -> Dict[str, Any]:
        """
        Executes ANPR pipeline for a specific tracked vehicle in current frame:
        Vehicle Crop -> Plate Detection -> OCR -> Multi-frame Consensus -> Association.
        """
        record = self.vehicle_anpr_records[track_id]
        
        # If plate is already confirmed, return cached result immediately with 0 OCR overhead
        if record["is_confirmed"]:
            return self._build_return_dict(record)

        # For unconfirmed vehicles, run OCR at most once every 3 frames
        frames_since_last = frame_number - record["last_processed_frame"]
        if frames_since_last < 3:
            return self._build_return_dict(record)

        record["last_processed_frame"] = frame_number

        # 1. License Plate Detection within vehicle bbox
        detection_res = self.plate_detector.detect_plate(frame, vehicle_bbox)
        
        if detection_res is None:
            if not record["is_confirmed"]:
                record["status"] = "Not Detected"
            return self._build_return_dict(record)

        plate_bbox_frame = detection_res["plate_bbox_frame"]
        plate_crop = detection_res["plate_crop"]
        plate_conf = detection_res["confidence"]
        vehicle_crop = detection_res["vehicle_crop"]
        record["last_plate_bbox"] = plate_bbox_frame

        # 2. OCR Reading & Normalization
        ocr_res = self.ocr_engine.read_plate(plate_crop)

        if ocr_res and ocr_res.get("plate_number"):
            plate_text = ocr_res["plate_number"]
            ocr_conf = ocr_res["ocr_confidence"]
            is_uncertain = ocr_res.get("uncertain", False)

            # Store OCR candidate for multi-frame consensus
            record["candidates"].append({
                "text": plate_text,
                "ocr_conf": ocr_conf,
                "plate_conf": plate_conf,
                "frame": frame_number,
                "is_uncertain": is_uncertain
            })

            # Save crop images
            self._save_crop_images(track_id, plate_crop, vehicle_crop, record)

            # 3. Multi-frame Consensus Aggregation
            self._aggregate_multi_frame_consensus(track_id, record)

        else:
            if not record["is_confirmed"]:
                if record["candidates"]:
                    record["status"] = "Uncertain"
                else:
                    record["status"] = "Not Detected"

        return self._build_return_dict(record)

    def _aggregate_multi_frame_consensus(self, track_id: str, record: Dict[str, Any]):
        """
        Aggregates OCR results over multiple frames using frequency voting and confidence weighting.
        """
        candidates = record["candidates"]
        if not candidates:
            return

        # Group by plate text
        plate_stats = defaultdict(lambda: {"count": 0, "conf_sum": 0.0, "max_conf": 0.0})
        for c in candidates:
            text = c["text"]
            conf = c["ocr_conf"]
            plate_stats[text]["count"] += 1
            plate_stats[text]["conf_sum"] += conf
            if conf > plate_stats[text]["max_conf"]:
                plate_stats[text]["max_conf"] = conf

        # Score candidate = average_conf * (1 + 0.15 * count)
        best_plate = None
        best_score = 0.0
        best_avg_conf = 0.0
        best_count = 0

        for text, stats in plate_stats.items():
            count = stats["count"]
            avg_conf = stats["conf_sum"] / count
            score = avg_conf * (1.0 + 0.15 * min(count, 5))

            if score > best_score:
                best_score = score
                best_plate = text
                best_avg_conf = avg_conf
                best_count = count

        if best_plate:
            record["final_plate"] = best_plate
            record["final_conf"] = round(float(best_avg_conf), 2)
            
            # Confirm plate if count reaches consensus threshold or high confidence
            if best_count >= ANPR_CONSENSUS_FRAMES or best_avg_conf >= 0.88:
                record["is_confirmed"] = True
                record["status"] = "Confirmed"
            else:
                record["status"] = "Recognizing"

    def _save_crop_images(
        self,
        track_id: str,
        plate_crop: np.ndarray,
        vehicle_crop: np.ndarray,
        record: Dict[str, Any]
    ):
        """
        Persists crop thumbnails to assets/crops/ for UI inspection and ANPR logs.
        """
        try:
            plate_filename = f"{track_id}_plate.jpg"
            vehicle_filename = f"{track_id}_vehicle.jpg"

            plate_path = PLATE_CROPS_DIR / plate_filename
            vehicle_path = VEHICLE_CROPS_DIR / vehicle_filename

            if plate_crop is not None and plate_crop.size > 0:
                cv2.imwrite(str(plate_path), plate_crop)
                record["plate_crop_path"] = f"/media/crops/plates/{plate_filename}"

            if vehicle_crop is not None and vehicle_crop.size > 0:
                cv2.imwrite(str(vehicle_path), vehicle_crop)
                record["vehicle_crop_path"] = f"/media/crops/vehicles/{vehicle_filename}"

        except Exception as e:
            print(f"[ANPREngine] Warning: Failed to save crops for {track_id}: {e}")

    def _build_return_dict(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds standardized ANPR telemetry payload for a vehicle.
        """
        plate = record.get("final_plate")
        conf = record.get("final_conf", 0.0)
        status = record.get("status", "Not Detected")
        
        display_text = plate if (plate and status != "Not Detected") else status
        
        return {
            "plate_number": plate if status == "Confirmed" or status == "Recognizing" else None,
            "display_text": display_text,
            "ocr_confidence": conf,
            "is_confirmed": record.get("is_confirmed", False),
            "status": status,
            "plate_bbox": record.get("last_plate_bbox"),
            "plate_crop_url": record.get("plate_crop_path"),
            "vehicle_crop_url": record.get("vehicle_crop_path")
        }

    def reset(self):
        """
        Clears ANPR memory on video stream restart.
        """
        self.vehicle_anpr_records.clear()
