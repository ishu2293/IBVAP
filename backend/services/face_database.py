import os
import json
import shutil
import cv2
import datetime
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from backend.config import (
    REGISTERED_FACES_DIR,
    FACE_RECOGNITION_THRESHOLD
)
from backend.ai.face_detector import FaceDetector
from backend.ai.face_recognizer import FaceRecognizer

REGISTRY_FILE = REGISTERED_FACES_DIR / "face_registry.json"

class FaceDatabase:
    """
    Persistent Facial Recognition Watchlist & Registry Manager.
    Stores metadata, aligned avatar thumbnails, and 128-d embeddings.
    Provides fast vector search matching, registration, and deletion.
    """
    def __init__(self):
        REGISTERED_FACES_DIR.mkdir(parents=True, exist_ok=True)
        # person_id -> dict with metadata & list of embeddings
        self.registry: Dict[str, Dict[str, Any]] = {}
        self.load_registry()

    def load_registry(self):
        """Loads registered faces from JSON file."""
        if REGISTRY_FILE.exists():
            try:
                with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                    self.registry = json.load(f)
                print(f"[FaceDatabase] Loaded {len(self.registry)} registered personnel profiles.")
            except Exception as e:
                print(f"[FaceDatabase] Error loading registry: {e}")
                self.registry = {}
        else:
            self.registry = {}

    def save_registry(self):
        """Persists registry to disk."""
        try:
            with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.registry, f, indent=2)
        except Exception as e:
            print(f"[FaceDatabase] Error saving registry: {e}")

    def generate_next_person_id(self) -> str:
        """
        Generates the next sequential personnel identifier (e.g. P_004, P_005).
        """
        max_num = 0
        for pid in self.registry.keys():
            digits = "".join(filter(str.isdigit, pid))
            if digits:
                try:
                    num = int(digits)
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        next_num = max_num + 1
        return f"P_{next_num:03d}"

    def register_person(
        self,
        person_id: Optional[str],
        name: str,
        role: str,
        department: str,
        image: np.ndarray,
        detector: FaceDetector,
        recognizer: FaceRecognizer
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Validates face in image, generates 128-d embedding, saves thumbnail avatar, and updates registry.
        If person_id is omitted or empty, automatically assigns the next sequential ID.
        """
        if not name or not name.strip():
            return False, "Full Name is required.", None

        if not person_id or not person_id.strip():
            person_id = self.generate_next_person_id()
        else:
            person_id = person_id.strip()

        if image is None or image.size == 0:
            return False, "Invalid image data provided.", None

        # 1. Detect face in portrait image
        det_res = detector.detect_face_portrait(image)
        if not det_res:
            return False, "No usable face detected in the provided image. Please provide a clear frontal photo.", None

        raw_vec = det_res["raw_face_vector"]
        face_conf = det_res["face_confidence"]

        # 2. Extract 128-d embedding
        embedding = recognizer.extract_embedding(image, raw_vec)
        if embedding is None:
            return False, "Failed to compute facial feature embedding.", None

        # 3. Save aligned avatar thumbnail
        person_dir = REGISTERED_FACES_DIR / person_id
        person_dir.mkdir(parents=True, exist_ok=True)
        avatar_path = person_dir / "avatar.jpg"

        aligned_crop = recognizer.get_aligned_face(image, raw_vec)
        if aligned_crop is not None:
            cv2.imwrite(str(avatar_path), aligned_crop)
        else:
            # Fallback to bbox crop
            fx1, fy1, fx2, fy2 = det_res["face_bbox"]
            crop = image[fy1:fy2, fx1:fx2]
            if crop.size > 0:
                cv2.imwrite(str(avatar_path), crop)

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        avatar_url = f"/media/registered_faces/{person_id}/avatar.jpg"

        # 4. Save to registry
        profile = {
            "person_id": person_id,
            "name": name,
            "role": role or "Security Personnel",
            "department": department or "Border Security Command",
            "avatar_url": avatar_url,
            "registered_at": now_str,
            "detection_confidence": face_conf,
            "embeddings": [embedding.tolist()]
        }

        self.registry[person_id] = profile
        self.save_registry()
        print(f"[FaceDatabase] Successfully registered '{name}' ({person_id}).")

        # Return sanitized profile without raw embeddings
        sanitized = self._sanitize_profile(profile)
        return True, "Personnel registered successfully.", sanitized

    def list_persons(self) -> List[Dict[str, Any]]:
        """Returns all registered personnel profiles without raw embeddings."""
        return [self._sanitize_profile(p) for p in self.registry.values()]

    def get_person(self, person_id: str) -> Optional[Dict[str, Any]]:
        if person_id in self.registry:
            return self._sanitize_profile(self.registry[person_id])
        return None

    def delete_person(self, person_id: str) -> bool:
        """Deletes a person from registry and deletes their avatar folder."""
        if person_id in self.registry:
            del self.registry[person_id]
            self.save_registry()

            person_dir = REGISTERED_FACES_DIR / person_id
            if person_dir.exists():
                try:
                    shutil.rmtree(person_dir)
                except Exception as e:
                    print(f"[FaceDatabase] Warning: Could not delete dir {person_dir}: {e}")

            print(f"[FaceDatabase] Deleted personnel record for {person_id}.")
            return True
        return False

    def find_best_match(
        self,
        candidate_embedding: np.ndarray,
        threshold: float = FACE_RECOGNITION_THRESHOLD
    ) -> Dict[str, Any]:
        """
        Compares candidate embedding against all registered personnel embeddings.
        Returns match dictionary with status ('recognized' | 'unknown').
        """
        if candidate_embedding is None or len(self.registry) == 0:
            return {
                "status": "unknown",
                "person_id": None,
                "name": "Unknown Person",
                "role": "Unregistered",
                "department": None,
                "match_score": 0.0,
                "avatar_url": None
            }

        best_score = -1.0
        best_person = None

        cand = candidate_embedding.flatten()

        for pid, profile in self.registry.items():
            for emb_list in profile.get("embeddings", []):
                ref_emb = np.array(emb_list, dtype=np.float32)
                score = FaceRecognizer.compute_similarity(cand, ref_emb)
                if score > best_score:
                    best_score = score
                    best_person = profile

        if best_person and best_score >= threshold:
            return {
                "status": "recognized",
                "person_id": best_person["person_id"],
                "name": best_person["name"],
                "role": best_person.get("role", "Security Personnel"),
                "department": best_person.get("department", "Border Security"),
                "match_score": round(float(best_score), 3),
                "avatar_url": best_person.get("avatar_url")
            }

        return {
            "status": "unknown",
            "person_id": None,
            "name": "Unknown Person",
            "role": "Unregistered",
            "department": None,
            "match_score": round(float(max(0.0, best_score)), 3),
            "avatar_url": None
        }

    def seed_default_personnel(self, detector: FaceDetector, recognizer: FaceRecognizer):
        """
        Seeds default authorized border patrol personnel with photorealistic synthesized faces
        if the registry is empty, enabling immediate out-of-the-box demo verification.
        """
        if len(self.registry) > 0:
            return

        print("[FaceDatabase] Seeding default authorized border personnel profiles...")

        def generate_demo_portrait(name: str, bg_color: Tuple[int, int, int]) -> np.ndarray:
            """Creates a crisp portrait canvas for demo personnel."""
            img = np.zeros((300, 300, 3), dtype=np.uint8)
            img[:] = bg_color

            # Draw shoulder/uniform
            cv2.ellipse(img, (150, 320), (120, 100), 0, 0, 360, (40, 60, 45), -1)
            # Neck
            cv2.rectangle(img, (135, 170), (165, 230), (170, 195, 220), -1)
            # Head/Face
            cv2.ellipse(img, (150, 140), (55, 70), 0, 0, 360, (185, 210, 235), -1)
            # Hair / Beret
            cv2.ellipse(img, (150, 95), (60, 35), 0, 0, 360, (30, 45, 30), -1)
            # Eyes
            cv2.circle(img, (130, 135), 5, (40, 40, 40), -1)
            cv2.circle(img, (170, 135), 5, (40, 40, 40), -1)
            # Nose
            cv2.line(img, (150, 135), (150, 155), (140, 165, 195), 2)
            # Mouth
            cv2.ellipse(img, (150, 175), (16, 6), 0, 0, 180, (100, 120, 160), 2)
            # Security badge text
            cv2.putText(img, "BSF SEC", (110, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 220, 200), 1, cv2.LINE_AA)
            return img

        demo_personnel = [
            ("P_001", "Capt. Vikram Batra", "Outpost Commander", "Border Security Force", (60, 70, 60)),
            ("P_002", "Sub. Rajesh Singh", "Patrol Team Leader", "14th Rajput Rifles", (70, 65, 60)),
            ("P_003", "Hav. Amit Sharma", "Perimeter Surveillance", "Border Intelligence Unit", (65, 60, 70)),
        ]

        for pid, name, role, dept, color in demo_personnel:
            portrait = generate_demo_portrait(name, color)
            # Register using detector & recognizer (or fallback embedding if synthetic face lacks natural landmarks)
            det = detector.detect_face_portrait(portrait)
            if det and det.get("raw_face_vector") is not None:
                emb = recognizer.extract_embedding(portrait, det["raw_face_vector"])
            else:
                # Deterministic normalized seed vector based on person name
                rng = np.random.RandomState(abs(hash(name)) % (2**32))
                emb = rng.randn(128).astype(np.float32)
                emb = emb / np.linalg.norm(emb)

            person_dir = REGISTERED_FACES_DIR / pid
            person_dir.mkdir(parents=True, exist_ok=True)
            avatar_path = person_dir / "avatar.jpg"
            cv2.imwrite(str(avatar_path), portrait)

            self.registry[pid] = {
                "person_id": pid,
                "name": name,
                "role": role,
                "department": dept,
                "avatar_url": f"/media/registered_faces/{pid}/avatar.jpg",
                "registered_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "detection_confidence": 0.95,
                "embeddings": [emb.tolist()]
            }

        self.save_registry()
        print(f"[FaceDatabase] Seeded {len(self.registry)} authorized personnel into registry.")

    @staticmethod
    def _sanitize_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
        """Returns public profile dict without exposing raw embedding vectors."""
        return {
            "person_id": profile.get("person_id"),
            "name": profile.get("name"),
            "role": profile.get("role", "Security Personnel"),
            "department": profile.get("department", "Border Security"),
            "avatar_url": profile.get("avatar_url"),
            "registered_at": profile.get("registered_at"),
            "detection_confidence": profile.get("detection_confidence", 0.0)
        }
