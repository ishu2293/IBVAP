import sys
sys.path.insert(0, '.')
import urllib.request
import shutil
from pathlib import Path
from backend.config import DEMO_CCTV_DIR

DEMO_CCTV_DIR.mkdir(parents=True, exist_ok=True)

# 1. Real surveillance footage sources
pbc_url = "https://github.com/intel-iot-devkit/sample-videos/raw/master/person-bicycle-car-detection.mp4"
cars_url = "https://github.com/intel-iot-devkit/sample-videos/raw/master/car-detection.mp4"

print("Fetching authentic real CCTV surveillance footage...")
req1 = urllib.request.Request(pbc_url, headers={'User-Agent': 'Mozilla/5.0'})
pbc_data = urllib.request.urlopen(req1, timeout=30).read()

req2 = urllib.request.Request(cars_url, headers={'User-Agent': 'Mozilla/5.0'})
cars_data = urllib.request.urlopen(req2, timeout=30).read()

# Save real footage to all 3 camera slots
with open(DEMO_CCTV_DIR / "border_demo_01.mp4", "wb") as f:
    f.write(pbc_data)
print(f"[OK] border_demo_01.mp4 saved (size: {len(pbc_data)} bytes)")

with open(DEMO_CCTV_DIR / "border_demo_02.mp4", "wb") as f:
    f.write(cars_data)
print(f"[OK] border_demo_02.mp4 saved (size: {len(cars_data)} bytes)")

with open(DEMO_CCTV_DIR / "border_demo_03.mp4", "wb") as f:
    f.write(pbc_data)
print(f"[OK] border_demo_03.mp4 saved (size: {len(pbc_data)} bytes)")

print("All demo camera slots restored to 100% real CCTV surveillance footage!")
