import cv2
import easyocr
import numpy as np

reader = easyocr.Reader(['en'], gpu=False)

# Create a vehicle bumper with license plate
vh, vw = 180, 280
img = np.zeros((vh, vw, 3), dtype=np.uint8)
img[:100, :] = (40, 60, 160)
img[100:, :] = (30, 45, 120)

# License plate on bumper
pw, ph = 160, 40
px1 = (vw - pw) // 2
py1 = 120
px2 = px1 + pw
py2 = py1 + ph

cv2.rectangle(img, (px1, py1), (px2, py2), (255, 255, 255), -1)
cv2.rectangle(img, (px1, py1), (px2, py2), (0, 0, 0), 2)
cv2.putText(img, "MH12AB1234", (px1 + 12, py1 + 27), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2, cv2.LINE_AA)

# Extract plate crop
plate_crop = img[py1:py2, px1:px2]
print("Plate crop shape:", plate_crop.shape)

# Run EasyOCR
res = reader.readtext(plate_crop, detail=1)
print("OCR result on bumper plate:", res)
