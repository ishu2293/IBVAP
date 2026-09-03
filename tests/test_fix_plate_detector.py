import sys
sys.path.insert(0, '.')
import cv2
import numpy as np
from backend.ai.plate_detector import PlateDetector
from backend.ai.ocr_engine import OCREngine

detector = PlateDetector()
ocr = OCREngine()

# Load demo frame
cap = cv2.VideoCapture("assets/demo_cctv/border_demo_01.mp4")
ret, frame = cap.read()
cap.release()

# Vehicle on frame (Bus/Truck)
v_bbox = [370, 253, 667, 432]
res = detector.detect_plate(frame, v_bbox)
print("Plate detection on vehicle:", res)
if res:
    print("Detected plate bbox:", res["plate_bbox_frame"])
    ocr_res = ocr.read_plate(res["plate_crop"])
    print("OCR Result on detected plate:", ocr_res)
