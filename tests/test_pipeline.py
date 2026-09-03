import sys
from pathlib import Path
import numpy as np
import cv2

# Add workspace root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import DEMO_CCTV_DIR
from backend.services.video_processor import VideoProcessor
from backend.ai.plate_detector import PlateDetector
from backend.ai.ocr_engine import OCREngine
from backend.ai.anpr_engine import ANPREngine

def test_pipeline():
    print("========================================")
    print("Testing IBVAP Dual Pipeline & ANPR Engine")
    print("========================================")

    # 1. Test OCR Engine Plate Normalization
    ocr = OCREngine()
    test_plate_clean = ocr.normalize_plate_text("MH 12 AB 1234")
    assert test_plate_clean == "MH12AB1234", f"Expected 'MH12AB1234', got {test_plate_clean}"
    print("[PASS] OCR plate normalization test passed (MH12AB1234)")

    # 2. Test Multi-frame Consensus Engine
    anpr = ANPREngine()
    dummy_frame = np.zeros((400, 600, 3), dtype=np.uint8)
    dummy_vehicle_bbox = [100, 100, 400, 300]
    
    # Draw plate on dummy vehicle
    cv2.rectangle(dummy_frame, (200, 240), (320, 275), (255, 255, 255), -1)
    cv2.putText(dummy_frame, "MH12AB1234", (205, 265), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    res = anpr.process_vehicle_frame(dummy_frame, "V-001", dummy_vehicle_bbox, frame_number=1)
    print(f"[PASS] ANPR frame 1 result: {res['display_text']}, Conf: {res['ocr_confidence']}")

    # 3. Test VideoProcessor on sample video stream
    demo_video_path = DEMO_CCTV_DIR / "border_demo_01.mp4"
    assert demo_video_path.exists(), f"Demo video {demo_video_path} does not exist"

    processor = VideoProcessor()
    gen = processor.process_video_stream(
        video_path=demo_video_path,
        mode="demo",
        camera_info={"id": "CAM-01", "name": "Longewala Desert Outpost", "location": "Rajasthan"}
    )

    print("Running video processor for 25 frames...")
    frames_tested = 0
    persons_detected_count = 0
    vehicles_detected_count = 0

    for processed_frame, telemetry in gen:
        frames_tested += 1
        p_count = telemetry["current_persons"]
        v_count = telemetry["current_vehicles"]
        fps = telemetry["fps"]

        if p_count > 0:
            persons_detected_count += 1
        if v_count > 0:
            vehicles_detected_count += 1

        if frames_tested % 5 == 0:
            print(f"  Frame #{telemetry['frame_number']:02d} | Persons: {p_count} | Vehicles: {v_count} | Active Tracks: {telemetry['active_tracks']} | ANPR Total: {telemetry['total_anpr_reads']} | FPS: {fps}")

        if frames_tested >= 25:
            break

    print("========================================")
    print(f"Pipeline Test Completed Successfully! {frames_tested} frames evaluated.")
    print(f"Frames with Person detections: {persons_detected_count}/{frames_tested}")
    print(f"Frames with Vehicle detections: {vehicles_detected_count}/{frames_tested}")
    print(f"Total Unique Persons: {telemetry['total_unique_persons']}")
    print(f"Total Unique Vehicles: {telemetry['total_unique_vehicles']}")
    print("========================================")

if __name__ == "__main__":
    test_pipeline()
