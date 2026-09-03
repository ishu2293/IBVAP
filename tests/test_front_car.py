import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("models/yolo11n.pt")

def test_front_car():
    h, w = 450, 800
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    frame[:180, :] = (40, 35, 30)
    frame[180:, :] = (55, 52, 48)
    cv2.fillPoly(frame, [np.array([[0, 220], [w, 220], [w, h], [0, h]])], (35, 33, 30))

    # Front-facing car approaching camera (Typical CCTV perspective)
    cx, cy = 400, 300
    scale = 1.2
    
    # Dimensions
    cw = int(180 * scale)
    ch = int(140 * scale)
    x1, y1 = cx - cw//2, cy - ch//2
    x2, y2 = cx + cw//2, cy + ch//2

    # 1. Shadow
    cv2.ellipse(frame, (cx, y2), (cw//2 + 10, 15), 0, 0, 360, (15, 15, 15), -1)

    # 2. Lower Body & Bumper
    body_col = (180, 60, 40) # Metallic Red
    cv2.rectangle(frame, (x1, y1 + int(50*scale)), (x2, y2 - int(10*scale)), body_col, -1)
    
    # 3. Cabin & Windshield (Trapezoid roof)
    cab_pts = np.array([
        [x1 + int(20*scale), y1 + int(50*scale)],
        [x1 + int(35*scale), y1],
        [x2 - int(35*scale), y1],
        [x2 - int(20*scale), y1 + int(50*scale)]
    ], np.int32)
    cv2.fillPoly(frame, [cab_pts], body_col)

    # Glass windshield
    glass_pts = np.array([
        [x1 + int(25*scale), y1 + int(48*scale)],
        [x1 + int(38*scale), y1 + int(6*scale)],
        [x2 - int(38*scale), y1 + int(6*scale)],
        [x2 - int(25*scale), y1 + int(48*scale)]
    ], np.int32)
    cv2.fillPoly(frame, [glass_pts], (30, 40, 50)) # Tinted dark glass

    # Rearview mirrors
    cv2.rectangle(frame, (x1 - int(10*scale), y1 + int(35*scale)), (x1, y1 + int(48*scale)), body_col, -1)
    cv2.rectangle(frame, (x2, y1 + int(35*scale)), (x2 + int(10*scale), y1 + int(48*scale)), body_col, -1)

    # 4. Front Grille
    grille_w = int(80 * scale)
    grille_h = int(35 * scale)
    gx1 = cx - grille_w//2
    gy1 = y1 + int(65 * scale)
    cv2.rectangle(frame, (gx1, gy1), (gx1 + grille_w, gy1 + grille_h), (20, 20, 20), -1)
    # Grille slats
    for slat_y in range(gy1 + 5, gy1 + grille_h, 6):
        cv2.line(frame, (gx1 + 4, slat_y), (gx1 + grille_w - 4, slat_y), (120, 120, 120), 1)

    # 5. Headlights
    hl_w = int(30 * scale)
    hl_h = int(22 * scale)
    # Left Headlight
    cv2.rectangle(frame, (x1 + int(10*scale), gy1), (x1 + int(10*scale) + hl_w, gy1 + hl_h), (240, 255, 255), -1)
    cv2.rectangle(frame, (x1 + int(10*scale), gy1), (x1 + int(10*scale) + hl_w, gy1 + hl_h), (180, 180, 180), 1)
    # Right Headlight
    cv2.rectangle(frame, (x2 - int(10*scale) - hl_w, gy1), (x2 - int(10*scale), gy1 + hl_h), (240, 255, 255), -1)
    cv2.rectangle(frame, (x2 - int(10*scale) - hl_w, gy1), (x2 - int(10*scale), gy1 + hl_h), (180, 180, 180), 1)

    # 6. Front Tires (peeking at bottom)
    cv2.rectangle(frame, (x1 + int(6*scale), y2 - int(25*scale)), (x1 + int(24*scale), y2), (20, 20, 20), -1)
    cv2.rectangle(frame, (x2 - int(24*scale), y2 - int(25*scale)), (x2 - int(6*scale), y2), (20, 20, 20), -1)

    # 7. License Plate on front bumper
    pl_w = int(68 * scale)
    pl_h = int(18 * scale)
    pl_x = cx - pl_w//2
    pl_y = gy1 + grille_h + int(5 * scale)
    cv2.rectangle(frame, (pl_x, pl_y), (pl_x + pl_w, pl_y + pl_h), (255, 255, 255), -1)
    cv2.rectangle(frame, (pl_x, pl_y), (pl_x + pl_w, pl_y + pl_h), (0, 0, 0), 1)
    cv2.putText(frame, "MH12AB1234", (pl_x + 3, pl_y + int(13*scale)), cv2.FONT_HERSHEY_SIMPLEX, 0.35*scale, (0, 0, 0), 1, cv2.LINE_AA)

    res = model.predict(frame, conf=0.15, verbose=False)
    print("Detections on front-facing vehicle frame:")
    for b in res[0].boxes:
        cls_id = int(b.cls[0].item())
        conf = float(b.conf[0].item())
        name = model.names[cls_id]
        print(f"  -> {name} ({cls_id}): conf = {conf:.2f}, bbox = {b.xyxy[0].tolist()}")

if __name__ == "__main__":
    test_front_car()
