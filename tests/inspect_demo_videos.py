import sys
sys.path.insert(0, '.')
import cv2
import numpy as np
from ultralytics import YOLO
from backend.config import DEMO_CCTV_DIR

model = YOLO("models/yolo11n.pt")

def inspect_video(video_filename):
    video_path = DEMO_CCTV_DIR / video_filename
    print(f"\n--- Inspecting {video_filename} ---")
    cap = cv2.VideoCapture(str(video_path))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Total frames: {frame_count}, Res: {int(cap.get(3))}x{int(cap.get(4))}")
    
    vehicles_detected = 0
    persons_detected = 0
    
    for i in range(min(50, frame_count)):
        ret, frame = cap.read()
        if not ret:
            break
        
        # Test detection with conf=0.25
        res = model.predict(frame, conf=0.25, classes=[0, 2, 3, 5, 7], verbose=False)
        boxes = res[0].boxes
        if boxes is not None and len(boxes) > 0:
            for b in boxes:
                cls_id = int(b.cls[0].item())
                conf = float(b.conf[0].item())
                name = model.names[cls_id]
                if cls_id == 0:
                    persons_detected += 1
                elif cls_id in [2, 3, 5, 7]:
                    vehicles_detected += 1
                    if i % 10 == 0:
                        print(f"  Frame {i:02d}: {name} ({conf:.2f}) bbox={[int(x) for x in b.xyxy[0].tolist()]}")
                        
    cap.release()
    print(f"Summary for {video_filename} (50 frames): Persons={persons_detected}, Vehicles={vehicles_detected}")

if __name__ == "__main__":
    inspect_video("border_demo_01.mp4")
    inspect_video("border_demo_02.mp4")
