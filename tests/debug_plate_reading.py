import sys
sys.path.insert(0, '.')
import cv2
from backend.config import DEMO_CCTV_DIR
from backend.ai.plate_detector import PlateDetector
from backend.ai.ocr_engine import OCREngine
from ultralytics import YOLO

detector = PlateDetector()
ocr = OCREngine()
model = YOLO("models/yolo11n.pt")

cap = cv2.VideoCapture(str(DEMO_CCTV_DIR / "border_demo_01.mp4"))
ret, frame = cap.read()
cap.release()

res = model.predict(frame, conf=0.20, classes=[2, 3, 5, 7], verbose=False)
for b in res[0].boxes:
    bbox = b.xyxy[0].tolist()
    print("Vehicle bbox:", bbox)
    p_res = detector.detect_plate(frame, bbox)
    print("PlateDetector result:", p_res is not None)
    if p_res:
        plate_crop = p_res["plate_crop"]
        print("Plate crop shape:", plate_crop.shape)
        cv2.imwrite("assets/crops/debug_plate.jpg", plate_crop)
        read_res = ocr.read_plate(plate_crop)
        print("OCR result:", read_res)
