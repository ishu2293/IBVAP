import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("models/yolo11n.pt")

def test_render():
    # Create test image
    w, h = 800, 450
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:180, :] = (40, 35, 30)
    img[180:, :] = (60, 55, 50)
    
    # Let's test a realistic car rendering
    # A realistic SUV / Sedan side profile
    cx, cy = 400, 320
    
    # 1. Shadow
    cv2.ellipse(img, (cx, cy + 30), (140, 20), 0, 0, 360, (20, 20, 20), -1)
    
    # 2. Main lower body
    body_pts = np.array([
        [cx - 130, cy + 20],
        [cx - 130, cy - 15],
        [cx - 90, cy - 25],
        [cx - 60, cy - 25],
        [cx - 30, cy - 60],
        [cx + 50, cy - 60],
        [cx + 85, cy - 25],
        [cx + 125, cy - 20],
        [cx + 130, cy + 20]
    ], np.int32)
    cv2.fillPoly(img, [body_pts], (40, 60, 180)) # Blue metallic
    
    # 3. Cabin Windows (Dark glossy glass with pillar)
    win_pts = np.array([
        [cx - 55, cy - 25],
        [cx - 28, cy - 56],
        [cx + 46, cy - 56],
        [cx + 78, cy - 25]
    ], np.int32)
    cv2.fillPoly(img, [win_pts], (30, 40, 50))
    cv2.line(img, (cx + 8, cy - 56), (cx + 8, cy - 25), (40, 60, 180), 6) # B-pillar
    
    # 4. Wheel arches & Wheels
    for wx in [cx - 75, cx + 75]:
        cv2.circle(img, (wx, cy + 20), 28, (20, 20, 20), -1) # Outer tire
        cv2.circle(img, (wx, cy + 20), 16, (190, 190, 190), -1) # Alloy rim
        cv2.circle(img, (wx, cy + 20), 6, (60, 60, 60), -1) # Hub
    
    # 5. Headlights & Taillights
    cv2.rectangle(img, (cx + 124, cy - 15), (cx + 130, cy - 5), (220, 255, 255), -1)
    cv2.rectangle(img, (cx - 130, cy - 15), (cx - 124, cy - 5), (0, 0, 240), -1)
    
    # 6. License Plate
    cv2.rectangle(img, (cx - 35, cy + 2), (cx + 35, cy + 22), (255, 255, 255), -1)
    cv2.rectangle(img, (cx - 35, cy + 2), (cx + 35, cy + 22), (0, 0, 0), 1)
    cv2.putText(img, "MH12AB1234", (cx - 32, cy + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 0), 1, cv2.LINE_AA)

    res = model.predict(img, conf=0.10, verbose=False)
    print("Predictions on rendered car:")
    for b in res[0].boxes:
        cls_id = int(b.cls[0].item())
        conf = float(b.conf[0].item())
        name = model.names[cls_id]
        print(f"  -> {name} ({cls_id}): conf = {conf:.2f}, bbox = {b.xyxy[0].tolist()}")

if __name__ == "__main__":
    test_render()
