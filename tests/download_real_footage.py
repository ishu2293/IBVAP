import urllib.request
import cv2
from pathlib import Path
from ultralytics import YOLO

model = YOLO("models/yolo11n.pt")

urls = [
    ("https://github.com/computervisioneng/automatic-number-plate-recognition-python-yolov8/raw/main/sample.mp4", "anpr_sample.mp4"),
    ("https://github.com/intel-iot-devkit/sample-videos/raw/master/person-bicycle-car-detection.mp4", "intel_pbc.mp4"),
    ("https://github.com/intel-iot-devkit/sample-videos/raw/master/car-detection.mp4", "intel_cars.mp4"),
    ("https://github.com/wavelolz/Video-License-Plate-Recognition/raw/master/003.mp4", "wave_003.mp4")
]

for url, fname in urls:
    dest = Path("assets/test_videos") / fname
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {fname} from {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as resp, open(dest, 'wb') as f:
            f.write(resp.read())
        print(f"  [OK] Saved {fname} ({dest.stat().st_size} bytes)")
        
        # Test 10 frames
        cap = cv2.VideoCapture(str(dest))
        v_count = 0
        p_count = 0
        for _ in range(30):
            ret, fr = cap.read()
            if not ret:
                break
            res = model.predict(fr, conf=0.22, classes=[0, 2, 3, 5, 7], verbose=False)
            for b in res[0].boxes:
                c = int(b.cls[0].item())
                if c == 0:
                    p_count += 1
                else:
                    v_count += 1
        cap.release()
        print(f"  Detections in first 30 frames: Persons={p_count}, Vehicles={v_count}")
    except Exception as e:
        print(f"  [ERR] Failed: {e}")
