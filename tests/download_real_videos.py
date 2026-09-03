import urllib.request
import cv2
import numpy as np
import sys
sys.path.insert(0, '.')
from pathlib import Path
from backend.config import DEMO_CCTV_DIR

def download_realistic_videos():
    DEMO_CCTV_DIR.mkdir(parents=True, exist_ok=True)
    
    # Public domain / open-source surveillance video samples
    sample_urls = [
        # Sample 1: Traffic & Pedestrians
        ("https://github.com/intel-iot-devkit/sample-videos/raw/master/person-bicycle-car-detection.mp4", "border_demo_01.mp4"),
        # Sample 2: Vehicle traffic
        ("https://github.com/intel-iot-devkit/sample-videos/raw/master/car-detection.mp4", "border_demo_02.mp4"),
        # Sample 3: Pedestrians & Vehicles
        ("https://github.com/intel-iot-devkit/sample-videos/raw/master/pedestrian-and-vehicle-detector.mp4", "border_demo_03.mp4")
    ]

    for url, filename in sample_urls:
        target_path = DEMO_CCTV_DIR / filename
        print(f"Downloading realistic footage for {filename} from {url}...")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as resp, open(target_path, 'wb') as f:
                f.write(resp.read())
            print(f"[OK] Downloaded realistic video {filename} ({target_path.stat().st_size // 1024} KB)")
        except Exception as e:
            print(f"Failed to download {url}: {e}")

if __name__ == "__main__":
    download_realistic_videos()
