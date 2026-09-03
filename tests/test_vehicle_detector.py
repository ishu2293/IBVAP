import sys
from pathlib import Path
import numpy as np
import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.ai.vehicle_detector import VehicleDetector
from backend.ai.vehicle_tracker import VehicleTracker

def test_vehicles():
    detector = VehicleDetector()
    tracker = VehicleTracker()
    
    # Render test frame with car and truck
    h, w = 450, 800
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    frame[:180, :] = (25, 20, 18)
    frame[180:, :] = (45, 42, 38)
    cv2.fillPoly(frame, [np.array([[0, 240], [w, 240], [w, h], [0, h]])], (32, 30, 28))

    # Let's test detection on standard vehicle images/shapes
    from backend.utils.demo_generator import draw_vehicle_with_plate
    draw_vehicle_with_plate(frame, 200, 360, 1.2, v_type="CAR", plate_text="MH12AB1234", body_color=(40, 60, 180))
    draw_vehicle_with_plate(frame, 550, 360, 1.3, v_type="TRUCK", plate_text="DL01CD5678", body_color=(160, 60, 40))

    dets = detector.detect(frame)
    print(f"Detected {len(dets)} vehicles in test frame:")
    for d in dets:
        print(f"  Class: {d['class_name']} | Conf: {d['confidence']:.2f} | Bbox: {d['bbox']}")

if __name__ == "__main__":
    test_vehicles()
