import os
import cv2
import urllib.request
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from backend.config import (
    MODELS_DIR,
    FACE_DETECTION_MODEL,
    FACE_DETECTION_THRESHOLD
)

YUNET_DOWNLOAD_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"

class FaceDetector:
    """
    Real-Time Face Detector using OpenCV YuNet DNN.
    Designed for real-time edge CPU/CUDA inference.
    Supports Person Head-ROI detection and full-frame portrait validation.
    """
    def __init__(self, conf_threshold: float = FACE_DETECTION_THRESHOLD):
        self.conf_threshold = conf_threshold
        self.model_path = MODELS_DIR / FACE_DETECTION_MODEL
        self.detector: Optional[cv2.FaceDetectorYN] = None
        self._init_detector()

    def _ensure_model(self):
        """Auto-downloads YuNet model if missing from models directory."""
        if not self.model_path.exists():
            MODELS_DIR.mkdir(parents=True, exist_ok=True)
            print(f"[FaceDetector] Downloading YuNet model to {self.model_path}...")
            try:
                urllib.request.urlretrieve(YUNET_DOWNLOAD_URL, self.model_path)
                print(f"[FaceDetector] Download complete ({self.model_path.stat().st_size} bytes).")
            except Exception as e:
                print(f"[FaceDetector] Error downloading YuNet: {e}")

    def _init_detector(self):
        try:
            self._ensure_model()
            if self.model_path.exists():
                self.detector = cv2.FaceDetectorYN.create(
                    str(self.model_path),
                    "",
                    (320, 320),
                    score_threshold=self.conf_threshold,
                    nms_threshold=0.3,
                    top_k=5000
                )
                print(f"[FaceDetector] YuNet face detector initialized successfully from {self.model_path.name}")
            else:
                print("[FaceDetector] Warning: YuNet model not found, face detection disabled.")
        except Exception as e:
            print(f"[FaceDetector] Warning: Failed to initialize YuNet: {e}")
            self.detector = None

    def detect_face_in_person(
        self,
        frame: np.ndarray,
        person_bbox: List[float],
        head_ratio: float = 0.42
    ) -> Optional[Dict[str, Any]]:
        """
        Fast Person-Tracking Face Detection:
        Restricts face search to the head region (upper 40% of the person's bounding box).
        Returns face bbox in full-frame coordinates, confidence score, landmarks, and raw vector.
        """
        if self.detector is None or frame is None or frame.size == 0:
            return None

        h_img, w_img = frame.shape[:2]
        px1, py1, px2, py2 = map(int, person_bbox)

        # Sanitize person bbox
        px1 = max(0, min(w_img - 1, px1))
        py1 = max(0, min(h_img - 1, py1))
        px2 = max(px1 + 1, min(w_img, px2))
        py2 = max(py1 + 1, min(h_img, py2))

        pw = px2 - px1
        ph = py2 - py1
        if pw < 15 or ph < 25:
            return None  # Person too small to reliably detect face

        # Head region: top `head_ratio` of person bounding box
        head_h = int(ph * head_ratio)
        head_y1 = py1
        head_y2 = min(h_img, py1 + head_h)
        head_x1 = px1
        head_x2 = px2

        head_crop = frame[head_y1:head_y2, head_x1:head_x2]
        ch, cw = head_crop.shape[:2]
        if ch < 12 or cw < 12:
            return None

        # Update input size for YuNet
        self.detector.setInputSize((cw, ch))
        _, faces = self.detector.detect(head_crop)

        if faces is None or len(faces) == 0:
            return None

        # Choose face with highest detection score
        best_face = max(faces, key=lambda f: f[14])
        face_conf = float(best_face[14])

        if face_conf < self.conf_threshold:
            return None

        # Extract local coordinates: [x, y, w, h]
        lx, ly, lw, lh = best_face[0:4]

        # Translate to global frame coordinates
        gx1 = max(0, int(head_x1 + lx))
        gy1 = max(0, int(head_y1 + ly))
        gx2 = min(w_img, int(gx1 + lw))
        gy2 = min(h_img, int(gy1 + lh))

        # Reconstruct global 15-d vector for SFace alignment:
        # [x, y, w, h, x_re, y_re, x_le, y_le, x_nt, y_nt, x_rcm, y_rcm, x_lcm, y_lcm, score]
        global_face_vec = np.copy(best_face)
        global_face_vec[0] = gx1
        global_face_vec[1] = gy1
        for i in range(4, 14, 2):
            global_face_vec[i] += head_x1      # X coordinates of landmarks
            global_face_vec[i + 1] += head_y1  # Y coordinates of landmarks

        landmarks = [
            (float(global_face_vec[4]), float(global_face_vec[5])),   # Right eye
            (float(global_face_vec[6]), float(global_face_vec[7])),   # Left eye
            (float(global_face_vec[8]), float(global_face_vec[9])),   # Nose tip
            (float(global_face_vec[10]), float(global_face_vec[11])), # Right mouth corner
            (float(global_face_vec[12]), float(global_face_vec[13]))  # Left mouth corner
        ]

        return {
            "face_bbox": [gx1, gy1, gx2, gy2],
            "face_confidence": round(face_conf, 3),
            "landmarks": landmarks,
            "raw_face_vector": global_face_vec
        }

    def detect_face_portrait(
        self,
        image: np.ndarray,
        min_conf: float = 0.35
    ) -> Optional[Dict[str, Any]]:
        """
        Detects and validates a face in an uploaded or live webcam portrait photo.
        Used during face registration. Supports relaxed threshold and multi-scale detection.
        """
        if self.detector is None or image is None or image.size == 0:
            return None

        orig_h, orig_w = image.shape[:2]

        # Candidate scales: original, and resized if image is very large or very small
        scales = [1.0]
        max_dim = max(orig_h, orig_w)
        if max_dim > 960:
            scales.append(640.0 / max_dim)
        elif max_dim < 300:
            scales.append(480.0 / max_dim)

        self.detector.setScoreThreshold(min_conf)
        try:
            for scale in scales:
                if scale == 1.0:
                    proc_img = image
                    w, h = orig_w, orig_h
                else:
                    w = int(orig_w * scale)
                    h = int(orig_h * scale)
                    proc_img = cv2.resize(image, (w, h), interpolation=cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR)

                self.detector.setInputSize((w, h))
                _, faces = self.detector.detect(proc_img)

                if faces is not None and len(faces) > 0:
                    best_face = max(faces, key=lambda f: f[14])
                    face_conf = float(best_face[14])

                    if face_conf >= min_conf:
                        inv_scale = 1.0 / scale if scale != 1.0 else 1.0

                        x = int(best_face[0] * inv_scale)
                        y = int(best_face[1] * inv_scale)
                        fw = int(best_face[2] * inv_scale)
                        fh = int(best_face[3] * inv_scale)

                        x1 = max(0, x)
                        y1 = max(0, y)
                        x2 = min(orig_w, x + fw)
                        y2 = min(orig_h, y + fh)

                        scaled_face_vec = np.copy(best_face)
                        scaled_face_vec[0] = x1
                        scaled_face_vec[1] = y1
                        scaled_face_vec[2] = fw
                        scaled_face_vec[3] = fh
                        for i in range(4, 14, 2):
                            scaled_face_vec[i] *= inv_scale
                            scaled_face_vec[i + 1] *= inv_scale

                        landmarks = [
                            (float(scaled_face_vec[4]), float(scaled_face_vec[5])),
                            (float(scaled_face_vec[6]), float(scaled_face_vec[7])),
                            (float(scaled_face_vec[8]), float(scaled_face_vec[9])),
                            (float(scaled_face_vec[10]), float(scaled_face_vec[11])),
                            (float(scaled_face_vec[12]), float(scaled_face_vec[13]))
                        ]

                        return {
                            "face_bbox": [x1, y1, x2, y2],
                            "face_confidence": round(face_conf, 3),
                            "landmarks": landmarks,
                            "raw_face_vector": scaled_face_vec
                        }
        finally:
            self.detector.setScoreThreshold(self.conf_threshold)

        return None
