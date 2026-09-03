import urllib.request
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO

model = YOLO("models/yolo11n.pt")
sprites_dir = Path("assets/sprites")
sprites_dir.mkdir(parents=True, exist_ok=True)

def download_sprites():
    # 1. Ultralytics official Bus
    bus_url = "https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/assets/bus.jpg"
    req = urllib.request.Request(bus_url, headers={'User-Agent': 'Mozilla/5.0'})
    arr = np.asarray(bytearray(urllib.request.urlopen(req).read()), dtype=np.uint8)
    bus_full = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    # Bus crop
    bus_crop = bus_full[220:740, 5:600]
    cv2.imwrite(str(sprites_dir / "bus_sprite.jpg"), bus_crop)
    print("Bus sprite saved:", bus_crop.shape)

    # 2. Car photo from unsplash / github
    car_url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/data/auto-oriented.jpg"
    # Or create a high quality photorealistic car from real car crop
    # Let's test bus crop with YOLO
    res = model.predict(bus_crop, conf=0.25, classes=[0, 2, 3, 5, 7], verbose=False)
    for b in res[0].boxes:
        print(f"  Bus detection: {model.names[int(b.cls[0].item())]} conf={float(b.conf[0].item()):.2f}")

if __name__ == "__main__":
    download_sprites()
