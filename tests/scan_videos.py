import sys
sys.path.insert(0, '.')
import cv2
from ultralytics import YOLO
from backend.config import DEMO_CCTV_DIR

model = YOLO("models/yolo11n.pt")

for vname in ["border_demo_01.mp4", "border_demo_02.mp4", "border_demo_03.mp4"]:
    vpath = DEMO_CCTV_DIR / vname
    cap = cv2.VideoCapture(str(vpath))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"\nScanning {vname} ({total} frames)...")
    v_found = 0
    p_found = 0
    f_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        f_idx += 1
        res = model.predict(frame, conf=0.20, classes=[0, 2, 3, 5, 7], verbose=False)
        for b in res[0].boxes:
            c = int(b.cls[0].item())
            if c == 0:
                p_found += 1
            else:
                v_found += 1
                if v_found <= 5:
                    print(f"  Frame {f_idx}: {model.names[c]} conf={float(b.conf[0].item()):.2f} bbox={[int(x) for x in b.xyxy[0].tolist()]}")
    cap.release()
    print(f"Total for {vname}: Persons={p_found}, Vehicles={v_found}")
