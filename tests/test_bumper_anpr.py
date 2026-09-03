import sys
sys.path.insert(0, '.')
import cv2
import numpy as np
import re
from backend.ai.plate_detector import PlateDetector
from backend.ai.ocr_engine import OCREngine

ocr = OCREngine()
detector = PlateDetector()

def test_bumper_anpr():
    # Create a realistic vehicle crop with license plate on bumper
    vw, vh = 300, 180
    v_crop = np.zeros((vh, vw, 3), dtype=np.uint8)
    # Car body
    v_crop[:int(vh*0.5), :] = (40, 60, 160)
    v_crop[int(vh*0.5):, :] = (30, 45, 120)
    # Grille & Bumper
    cv2.rectangle(v_crop, (50, 90), (250, 130), (20, 20, 20), -1)
    # Headlights
    cv2.rectangle(v_crop, (10, 90), (45, 120), (240, 255, 255), -1)
    cv2.rectangle(v_crop, (255, 90), (290, 120), (240, 255, 255), -1)
    # License plate
    pl_x1, pl_y1, pl_x2, pl_y2 = 100, 135, 200, 165
    cv2.rectangle(v_crop, (pl_x1, pl_y1), (pl_x2, pl_y2), (255, 255, 255), -1)
    cv2.rectangle(v_crop, (pl_x1, pl_y1), (pl_x2, pl_y2), (0, 0, 0), 1)
    cv2.putText(v_crop, "MH12AB1234", (pl_x1 + 6, pl_y1 + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2, cv2.LINE_AA)

    # Test PlateDetector
    frame = np.zeros((450, 800, 3), dtype=np.uint8)
    frame[100:100+vh, 200:200+vw] = v_crop
    v_bbox = [200, 100, 200+vw, 100+vh]

    res = detector.detect_plate(frame, v_bbox)
    print("PlateDetector result:", res is not None)
    if res:
        print("Detected plate bbox in frame:", res["plate_bbox_frame"])
        ocr_res = ocr.read_plate(res["plate_crop"])
        print("OCR result on extracted crop:", ocr_res)

if __name__ == "__main__":
    test_bumper_anpr()
