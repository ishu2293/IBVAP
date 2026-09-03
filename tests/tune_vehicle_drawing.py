import sys
from pathlib import Path
import numpy as np
import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ultralytics import YOLO

def test_tune():
    model = YOLO("yolo11n.pt")
    
    # Try different realistic car renderings
    h, w = 450, 800
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    frame[:200, :] = (40, 30, 25) # Sky
    frame[200:, :] = (50, 48, 45) # Ground

    # Draw realistic road
    cv2.fillPoly(frame, [np.array([[0, 240], [w, 240], [w, h], [0, h]])], (30, 28, 25))

    # Test drawing a car with realistic styling
    cx, cy = 350, 350
    scale = 1.3
    
    # Shadow under car
    cv2.ellipse(frame, (cx, cy + 10), (int(120 * scale), int(15 * scale)), 0, 0, 360, (15, 15, 15), -1)

    # Car body: lower metallic rectangle + curved hood/trunk
    body_col = (180, 50, 40) # Metallic Red/Blue
    cv2.rectangle(frame, (cx - int(100*scale), cy - int(35*scale)), (cx + int(100*scale), cy), body_col, -1)
    
    # Cabin roof (trapezoid)
    pts = np.array([
        [cx - int(55*scale), cy - int(35*scale)],
        [cx - int(35*scale), cy - int(65*scale)],
        [cx + int(40*scale), cy - int(65*scale)],
        [cx + int(65*scale), cy - int(35*scale)]
    ], np.int32)
    cv2.fillPoly(frame, [pts], (210, 210, 210))

    # Glass windows
    win_pts = np.array([
        [cx - int(50*scale), cy - int(36*scale)],
        [cx - int(32*scale), cy - int(62*scale)],
        [cx + int(37*scale), cy - int(62*scale)],
        [cx + int(60*scale), cy - int(36*scale)]
    ], np.int32)
    cv2.fillPoly(frame, [win_pts], (40, 50, 60))
    # Pillar
    cv2.line(frame, (cx, cy - int(62*scale)), (cx, cy - int(36*scale)), (200, 200, 200), int(3*scale))

    # Wheels (outer rubber + inner chrome rim + lug nuts)
    for wx in [cx - int(65*scale), cx + int(65*scale)]:
        cv2.circle(frame, (wx, cy), int(18*scale), (20, 20, 20), -1)
        cv2.circle(frame, (wx, cy), int(10*scale), (180, 180, 180), -1)
        cv2.circle(frame, (wx, cy), int(4*scale), (50, 50, 50), -1)

    # Headlights & Taillights
    cv2.rectangle(frame, (cx + int(96*scale), cy - int(28*scale)), (cx + int(101*scale), cy - int(18*scale)), (255, 255, 200), -1) # Headlight
    cv2.rectangle(frame, (cx - int(101*scale), cy - int(28*scale)), (cx - int(96*scale), cy - int(18*scale)), (0, 0, 240), -1) # Taillight

    # License Plate
    pl_w, pl_h = int(65*scale), int(18*scale)
    cv2.rectangle(frame, (cx - pl_w//2, cy - int(18*scale)), (cx + pl_w//2, cy - int(18*scale) + pl_h), (255, 255, 255), -1)
    cv2.rectangle(frame, (cx - pl_w//2, cy - int(18*scale)), (cx + pl_w//2, cy - int(18*scale) + pl_h), (0, 0, 0), 1)
    cv2.putText(frame, "MH12AB1234", (cx - pl_w//2 + 3, cy - int(18*scale) + int(13*scale)), cv2.FONT_HERSHEY_SIMPLEX, 0.35*scale, (0, 0, 0), 1)

    # Run inference with all classes to see what YOLO sees
    results = model.predict(frame, conf=0.15, verbose=False)
    for r in results:
        boxes = r.boxes
        for b in boxes:
            cls_id = int(b.cls[0].item())
            conf = float(b.conf[0].item())
            cls_name = model.names[cls_id]
            print(f"YOLO detected: {cls_name} (class {cls_id}) with confidence {conf:.2f}")

if __name__ == "__main__":
    test_tune()
