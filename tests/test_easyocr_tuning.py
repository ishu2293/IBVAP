import cv2
import easyocr
import numpy as np

reader = easyocr.Reader(['en'], gpu=False)
img = cv2.imread("assets/crops/debug_plate.jpg")

# 1. Resize to height = 100 with border padding
h, w = img.shape[:2]
scale = 100.0 / h
resized = cv2.resize(img, (int(w * scale), 100), interpolation=cv2.INTER_CUBIC)
# Add white border padding
padded = cv2.copyMakeBorder(resized, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=[255, 255, 255])

print("Padded shape:", padded.shape)
res = reader.readtext(padded, detail=1, min_size=5, text_threshold=0.2, low_text=0.2)
print("EasyOCR results with padding & scaling:", res)
