import cv2
import numpy as np

img = cv2.imread("assets/crops/debug_plate.jpg")
print("Min, Max, Mean color:", np.min(img), np.max(img), np.mean(img))

# In test_pipeline.py earlier, how did EasyOCR read MH12AB1234?
# In test_pipeline.py:
# dummy_frame = np.zeros((400, 600, 3), dtype=np.uint8)
# cv2.rectangle(dummy_frame, (200, 240), (320, 275), (255, 255, 255), -1)
# cv2.putText(dummy_frame, "MH12AB1234", (205, 265), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
# And PlateDetector found it and EasyOCR read: MH1ZAB1234 (conf: 0.98)!
