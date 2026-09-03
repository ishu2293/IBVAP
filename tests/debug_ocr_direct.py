import cv2
import easyocr

reader = easyocr.Reader(['en'], gpu=False)
img = cv2.imread("assets/crops/debug_plate.jpg")
print("Image shape:", img.shape)
res = reader.readtext(img, detail=1)
print("Raw EasyOCR results on debug_plate.jpg:", res)
