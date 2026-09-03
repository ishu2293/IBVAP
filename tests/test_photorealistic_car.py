import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("models/yolo11n.pt")

def create_photorealistic_car():
    # Let's generate a realistic photographic-looking vehicle texture
    # Dimensions: 240 x 110
    car_w, car_h = 240, 110
    car_img = np.zeros((car_h, car_w, 4), dtype=np.uint8) # RGBA with transparency

    # Metallic car gradient
    for y in range(car_h):
        shade = int(120 + 60 * np.sin((y / car_h) * np.pi))
        for x in range(car_w):
            car_img[y, x] = (shade - 30, shade, shade + 30, 255)

    # Cut car silhouette
    mask = np.zeros((car_h, car_w), dtype=np.uint8)
    
    # Body points: hood, windshield, roof, rear window, trunk, bumper
    poly = np.array([
        [5, 80],
        [15, 55],
        [55, 50],
        [85, 20],
        [165, 20],
        [195, 50],
        [230, 55],
        [235, 80],
        [230, 95],
        [195, 95], # Rear wheel cutout
        [175, 75],
        [145, 75],
        [125, 95],
        [75, 95],  # Front wheel cutout
        [55, 75],
        [25, 75],
        [5, 95]
    ], np.int32)
    cv2.fillPoly(mask, [poly], 255)

    # Windows
    win_mask = np.zeros((car_h, car_w), dtype=np.uint8)
    win_poly = np.array([
        [88, 24],
        [162, 24],
        [188, 48],
        [65, 48]
    ], np.int32)
    cv2.fillPoly(win_mask, [win_poly], 255)

    # Apply masks
    car_img[mask == 0] = (0, 0, 0, 0)
    car_img[win_mask == 255] = (40, 50, 60, 255) # Tinted glass
    # B-pillar
    cv2.line(car_img, (125, 24), (125, 48), (60, 80, 100, 255), 4)

    # Headlights & Taillights
    cv2.rectangle(car_img, (228, 55), (235, 68), (240, 255, 255, 255), -1)
    cv2.rectangle(car_img, (5, 55), (12, 68), (0, 0, 230, 255), -1)

    # Wheels (Rubber + Rim)
    for wx, wy in [(40, 85), (160, 85)]:
        cv2.circle(car_img, (wx, wy), 20, (20, 20, 20, 255), -1)
        cv2.circle(car_img, (wx, wy), 11, (180, 180, 180, 255), -1)
        cv2.circle(car_img, (wx, wy), 4, (40, 40, 40, 255), -1)

    # License Plate
    pl_w, pl_h = 60, 16
    pl_x = 100
    pl_y = 70
    cv2.rectangle(car_img, (pl_x, pl_y), (pl_x + pl_w, pl_y + pl_h), (255, 255, 255, 255), -1)
    cv2.rectangle(car_img, (pl_x, pl_y), (pl_x + pl_w, pl_y + pl_h), (0, 0, 0, 255), 1)
    cv2.putText(car_img, "MH12AB1234", (pl_x + 3, pl_y + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.30, (0, 0, 0, 255), 1)

    return car_img

def test_on_background():
    car = create_photorealistic_car()
    
    # Background frame
    h, w = 450, 800
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    frame[:180, :] = (30, 25, 22)
    frame[180:, :] = (55, 52, 48)
    cv2.fillPoly(frame, [np.array([[0, 220], [w, 220], [w, h], [0, h]])], (35, 33, 30))

    # Overlay car
    cx, cy = 300, 280
    ch, cw = car.shape[:2]
    
    # Alpha blend
    alpha = car[:, :, 3] / 255.0
    for c in range(3):
        frame[cy:cy+ch, cx:cx+cw, c] = (
            alpha * car[:, :, c] + (1.0 - alpha) * frame[cy:cy+ch, cx:cx+cw, c]
        )

    # Detect with YOLO
    res = model.predict(frame, conf=0.20, verbose=False)
    print("Detections on photorealistic vehicle frame:")
    for b in res[0].boxes:
        cls_id = int(b.cls[0].item())
        conf = float(b.conf[0].item())
        name = model.names[cls_id]
        print(f"  -> {name} ({cls_id}): conf = {conf:.2f}, bbox = {b.xyxy[0].tolist()}")

if __name__ == "__main__":
    test_on_background()
