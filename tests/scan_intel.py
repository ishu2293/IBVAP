import cv2
from ultralytics import YOLO

model = YOLO("models/yolo11n.pt")

for vname in ["assets/test_videos/intel_cars.mp4", "assets/test_videos/intel_pbc.mp4"]:
    cap = cv2.VideoCapture(vname)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"\n--- Scanning {vname} ({total} frames) ---")
    f = 0
    p_tot, v_tot = 0, 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        f += 1
        res = model.predict(frame, conf=0.15, classes=[0, 2, 3, 5, 7], verbose=False)
        for b in res[0].boxes:
            c = int(b.cls[0].item())
            if c == 0:
                p_tot += 1
            else:
                v_tot += 1
                if v_tot <= 5:
                    print(f"  Frame {f}: {model.names[c]} conf={float(b.conf[0].item()):.2f} bbox={[int(x) for x in b.xyxy[0].tolist()]}")
    cap.release()
    print(f"Total: Persons={p_tot}, Vehicles={v_tot}")
