import urllib.request
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO

model = YOLO("models/yolo11n.pt")

def test_online_or_texture():
    # Let's see if we can fetch a sample border/traffic CCTV frame or test YOLO detection on it
    test_urls = [
        "https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/assets/bus.jpg",
        "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=800&q=80", # Car
    ]
    
    for i, url in enumerate(test_urls):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            resp = urllib.request.urlopen(req, timeout=5)
            arr = np.asarray(bytearray(resp.read()), dtype=np.uint8)
            img = cv2.imdecode(arr, -1)
            if img is not None:
                print(f"Sample {i+1} downloaded: shape={img.shape}")
                res = model.predict(img, conf=0.3, verbose=False)
                for b in res[0].boxes:
                    cls_id = int(b.cls[0].item())
                    conf = float(b.conf[0].item())
                    name = model.names[cls_id]
                    print(f"  Detected: {name} ({cls_id}) conf={conf:.2f}")
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")

if __name__ == "__main__":
    test_online_or_texture()
