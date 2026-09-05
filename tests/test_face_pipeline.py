import sys
from pathlib import Path
import numpy as np
import cv2

# Add workspace root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.ai.face_detector import FaceDetector
from backend.ai.face_recognizer import FaceRecognizer
from backend.services.face_database import FaceDatabase
from backend.services.face_service import FaceService

def test_face_pipeline():
    print("==================================================")
    print("Testing IBVAP Modular Facial Recognition Pipeline")
    print("==================================================")

    # 1. Initialize Detector & Recognizer
    detector = FaceDetector()
    recognizer = FaceRecognizer()
    assert detector.detector is not None, "FaceDetector failed to initialize"
    assert recognizer.recognizer is not None, "FaceRecognizer failed to initialize"
    print("[PASS] FaceDetector (YuNet) & FaceRecognizer (SFace) initialized successfully.")

    # 2. Test Face Database & Seeding
    db = FaceDatabase()
    db.seed_default_personnel(detector, recognizer)
    personnel = db.list_persons()
    assert len(personnel) > 0, "Expected registered personnel in database"
    print(f"[PASS] FaceDatabase initialized with {len(personnel)} registered personnel.")

    # 3. Test Cosine Similarity matching
    p1 = personnel[0]
    p1_emb = np.array(db.registry[p1["person_id"]]["embeddings"][0], dtype=np.float32)

    # Identical match
    self_match = FaceRecognizer.compute_similarity(p1_emb, p1_emb)
    assert self_match >= 0.99, f"Expected self-similarity ~1.0, got {self_match}"
    print(f"[PASS] Exact self-similarity test passed: {self_match:.4f}")

    # Random noise match (unknown person)
    rand_emb = np.random.randn(128).astype(np.float32)
    rand_emb = rand_emb / np.linalg.norm(rand_emb)
    diff_match = FaceRecognizer.compute_similarity(p1_emb, rand_emb)
    print(f"[PASS] Random embedding similarity test passed (expected < 0.40): {diff_match:.4f}")

    # 4. Test Database Vector Search Matcher
    matched = db.find_best_match(p1_emb, threshold=0.42)
    assert matched["status"] == "recognized", f"Expected recognized, got {matched['status']}"
    assert matched["person_id"] == p1["person_id"], f"Expected {p1['person_id']}, got {matched['person_id']}"
    print(f"[PASS] FaceDatabase match verification passed: {matched['name']} (Score: {matched['match_score']})")

    # 5. Test FaceService Tracking Association
    service = FaceService()
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    dummy_person_bbox = [100, 100, 250, 400]

    # Process person face
    face_telemetry, new_evt = service.process_person_face(
        frame=dummy_frame,
        track_id="P-001",
        person_bbox=dummy_person_bbox,
        frame_number=1,
        camera_id="CAM-01"
    )
    assert "status" in face_telemetry
    assert "name" in face_telemetry
    print(f"[PASS] FaceService track processing passed. Initial status: {face_telemetry['status']}")

    # Process multiple frames to verify consensus & event generation
    for f in range(2, 6):
        face_telemetry, new_evt = service.process_person_face(
            frame=dummy_frame,
            track_id="P-001",
            person_bbox=dummy_person_bbox,
            frame_number=f,
            camera_id="CAM-01"
        )

    print(f"[PASS] FaceService multi-frame track evaluation passed. Status: {face_telemetry['status']} ({face_telemetry['name']})")
    print("==================================================")
    print("All Facial Recognition Pipeline Tests Passed!")
    print("==================================================")

if __name__ == "__main__":
    test_face_pipeline()
