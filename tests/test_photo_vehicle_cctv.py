import urllib.request
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO

model = YOLO("models/yolo11n.pt")

def fetch_and_test():
    # 1. Fetch official Ultralytics bus image
    bus_url = "https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/assets/bus.jpg"
    req = urllib.request.Request(bus_url, headers={'User-Agent': 'Mozilla/5.0'})
    arr = np.asarray(bytearray(urllib.request.urlopen(req).read()), dtype=np.uint8)
    bus_img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    # Crop the bus (approx [220:750, 0:600])
    bus_crop = bus_img[220:750, 0:600]
    
    # 2. Add high-contrast Indian License Plate to bus bumper
    bh, bw = bus_crop.shape[:2]
    pw, ph = int(bw * 0.40), int(bh * 0.12)
    px1 = (bw - pw) // 2
    py1 = int(bh * 0.65)
    cv2.rectangle(bus_crop, (px1, py1), (px1 + pw, py1 + ph), (255, 255, 255), -1)
    cv2.rectangle(bus_crop, (px1, py1), (px1 + pw, py1 + ph), (0, 0, 0), 2)
    cv2.putText(bus_crop, "MH12AB1234", (px1 + 10, py1 + int(ph * 0.7)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2, cv2.LINE_AA)

    # 3. Create CCTV frame and paste bus
    frame = np.zeros((450, 800, 3), dtype=np.uint8)
    frame[:180, :] = (40, 35, 30)
    frame[180:, :] = (55, 52, 48)
    
    bus_resized = cv2.resize(bus_crop, (280, 200))
    frame[200:400, 150:430] = bus_resized

    # Run YOLO detection
    res = model.predict(frame, conf=0.20, classes=[0, 2, 3, 5, 7], verbose=False)
    print("Detections on photographic vehicle CCTV frame:")
    for b in res[0].boxes:
        cls_id = int(b.cls[0].item())
        conf = float(b.conf[0].item())
        name = model.names[cls_id]
        print(f"  -> {name} ({cls_id}): conf = {conf:.2f}, bbox = {[int(x) for x in b.xyxy[0].tolist()]}")

if __name__ == "__main__":
    fetch_and_test()
