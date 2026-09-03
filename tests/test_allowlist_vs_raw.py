import cv2
import easyocr

reader = easyocr.Reader(['en'], gpu=False)
img = cv2.imread("assets/crops/debug_plate.jpg")

print("1. With allowlist:", reader.readtext(img, allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
print("2. Without allowlist:", reader.readtext(img))
