import os
import cv2
import urllib.request
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

from backend.config import (
    MODELS_DIR,
    FACE_RECOGNITION_MODEL,
    FACE_RECOGNITION_THRESHOLD
)

SFACE_DOWNLOAD_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"

class FaceRecognizer:
    """
    Real-Time Face Feature Embedding & Verification Engine using OpenCV SFace DNN.
    Extracts 128-dimensional L2-normalized deep facial identity embeddings.
    Performs cosine similarity verification against registered embeddings.
    """
    def __init__(self, threshold: float = FACE_RECOGNITION_THRESHOLD):
        self.threshold = threshold
        self.model_path = MODELS_DIR / FACE_RECOGNITION_MODEL
        self.recognizer: Optional[cv2.FaceRecognizerSF] = None
        self._init_recognizer()

    def _ensure_model(self):
        """Auto-downloads SFace model if missing from models directory."""
        if not self.model_path.exists():
            MODELS_DIR.mkdir(parents=True, exist_ok=True)
            print(f"[FaceRecognizer] Downloading SFace model to {self.model_path}...")
            try:
                urllib.request.urlretrieve(SFACE_DOWNLOAD_URL, self.model_path)
                print(f"[FaceRecognizer] Download complete ({self.model_path.stat().st_size} bytes).")
            except Exception as e:
                print(f"[FaceRecognizer] Error downloading SFace: {e}")

    def _init_recognizer(self):
        try:
            self._ensure_model()
            if self.model_path.exists():
                self.recognizer = cv2.FaceRecognizerSF.create(str(self.model_path), "")
                print(f"[FaceRecognizer] SFace recognizer initialized successfully from {self.model_path.name}")
            else:
                print("[FaceRecognizer] Warning: SFace model not found, face recognition disabled.")
        except Exception as e:
            print(f"[FaceRecognizer] Warning: Failed to initialize SFace: {e}")
            self.recognizer = None

    def extract_embedding(
        self,
        frame: np.ndarray,
        raw_face_vector: np.ndarray
    ) -> Optional[np.ndarray]:
        """
        Aligns the face using landmark vectors and computes a 128-d normalized embedding.
        """
        if self.recognizer is None or frame is None or raw_face_vector is None:
            return None

        try:
            # SFace alignCrop transforms face into 112x112 canonical frontal alignment
            aligned_face = self.recognizer.alignCrop(frame, raw_face_vector)
            if aligned_face is None or aligned_face.size == 0:
                return None

            # Extract 128-d floating-point feature embedding
            feature = self.recognizer.feature(aligned_face)
            if feature is None or feature.size == 0:
                return None

            # Flatten and L2 normalize
            feature_1d = feature.flatten().astype(np.float32)
            norm = np.linalg.norm(feature_1d)
            if norm > 1e-6:
                feature_1d = feature_1d / norm

            return feature_1d
        except Exception as e:
            print(f"[FaceRecognizer] Error extracting embedding: {e}")
            return None

    def get_aligned_face(
        self,
        frame: np.ndarray,
        raw_face_vector: np.ndarray
    ) -> Optional[np.ndarray]:
        """Returns 112x112 aligned face crop for visualization / thumbnail storage."""
        if self.recognizer is None or frame is None or raw_face_vector is None:
            return None
        try:
            return self.recognizer.alignCrop(frame, raw_face_vector)
        except Exception:
            return None

    @staticmethod
    def compute_similarity(feat1: np.ndarray, feat2: np.ndarray) -> float:
        """
        Computes Cosine Similarity between two 128-d normalized embeddings.
        Returns value in range [0.0, 1.0].
        """
        if feat1 is None or feat2 is None:
            return 0.0

        f1 = feat1.flatten()
        f2 = feat2.flatten()
        norm1 = np.linalg.norm(f1)
        norm2 = np.linalg.norm(f2)
        if norm1 < 1e-6 or norm2 < 1e-6:
            return 0.0

        dot = np.dot(f1, f2) / (norm1 * norm2)
        # Cosine for unit vectors is in [-1, 1], clip to [0, 1]
        return float(max(0.0, min(1.0, dot)))
