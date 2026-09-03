import urllib.request
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO

model = YOLO("models/yolo11n.pt")
sprites_dir = Path("assets/sprites")
sprites_dir.mkdir(parents=True, exist_ok=True)

def fetch_car_and_truck():
    # Download real car photo
    car_url = "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=600&q=80"
    try:
        req = urllib.request.Request(car_url, headers={'User-Agent': 'Mozilla/5.0'})
        arr = np.asarray(bytearray(urllib.request.urlopen(req, timeout=10).read()), dtype=np.uint8)
        car_img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if car_img is not None:
            # Resize and save
            car_resized = cv2.resize(car_img, (320, 200))
            cv2.imwrite(str(sprites_dir / "car_sprite.jpg"), car_resized)
            print("[OK] Car sprite saved:", car_resized.shape)
            res = model.predict(car_resized, conf=0.20, classes=[0, 2, 3, 5, 7], verbose=False)
            for b in res[0].boxes:
                print(f"  Car detection: {model.names[int(b.cls[0].item())]} conf={float(b.conf[0].item()):.2f}")
    except Exception as e:
        print("Failed to download car:", e)

if __name__ == "__main__":
    fetch_car_and_truck()
