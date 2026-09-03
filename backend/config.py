import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
ASSETS_DIR = BASE_DIR / "assets"
DEMO_CCTV_DIR = ASSETS_DIR / "demo_cctv"
UPLOADS_DIR = BASE_DIR / "uploads"
CROPS_DIR = ASSETS_DIR / "crops"
PLATE_CROPS_DIR = CROPS_DIR / "plates"
VEHICLE_CROPS_DIR = CROPS_DIR / "vehicles"

# Ensure required directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DEMO_CCTV_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
CROPS_DIR.mkdir(parents=True, exist_ok=True)
PLATE_CROPS_DIR.mkdir(parents=True, exist_ok=True)
VEHICLE_CROPS_DIR.mkdir(parents=True, exist_ok=True)

# Model Settings
YOLO_MODEL = os.getenv("YOLO_MODEL", "yolo11n.pt")  # Lightweight nano model
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.25"))
VEHICLE_CONFIDENCE_THRESHOLD = float(os.getenv("VEHICLE_CONFIDENCE_THRESHOLD", "0.22"))
IOU_THRESHOLD = float(os.getenv("IOU_THRESHOLD", "0.45"))

# COCO Class IDs
PERSON_CLASS_ID = 0  # COCO 0 = person
CAR_CLASS_ID = 2     # COCO 2 = car
MOTORCYCLE_CLASS_ID = 3  # COCO 3 = motorcycle
BUS_CLASS_ID = 5     # COCO 5 = bus
TRUCK_CLASS_ID = 7   # COCO 7 = truck

VEHICLE_CLASS_IDS = [CAR_CLASS_ID, MOTORCYCLE_CLASS_ID, BUS_CLASS_ID, TRUCK_CLASS_ID]
ALL_TARGET_CLASS_IDS = [PERSON_CLASS_ID] + VEHICLE_CLASS_IDS

CLASS_NAME_MAPPING = {
    PERSON_CLASS_ID: "PERSON",
    CAR_CLASS_ID: "CAR",
    MOTORCYCLE_CLASS_ID: "MOTORCYCLE",
    BUS_CLASS_ID: "BUS",
    TRUCK_CLASS_ID: "TRUCK"
}

# ANPR Settings
PLATE_CONFIDENCE_THRESHOLD = float(os.getenv("PLATE_CONFIDENCE_THRESHOLD", "0.40"))
OCR_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.35"))
ANPR_CONSENSUS_FRAMES = int(os.getenv("ANPR_CONSENSUS_FRAMES", "2"))  # Frames needed for consensus
ANPR_PROCESS_INTERVAL = int(os.getenv("ANPR_PROCESS_INTERVAL", "2"))  # Process ANPR every N frames per vehicle

# Video Processing Settings
PROCESS_EVERY_N_FRAMES = int(os.getenv("PROCESS_EVERY_N_FRAMES", "1"))
TARGET_FPS = int(os.getenv("TARGET_FPS", "30"))

# Tracker & Analytics Settings
TRACK_BUFFER = int(os.getenv("TRACK_BUFFER", "30"))
TRAIL_LENGTH = int(os.getenv("TRAIL_LENGTH", "20"))
DIRECTION_THRESHOLD = float(os.getenv("DIRECTION_THRESHOLD", "5.0"))  # Pixels min displacement for direction calculation

# Demo Cameras Definition (Indian Border Outposts)
DEMO_CAMERAS = [
    {
        "id": "CAM-01",
        "name": "Longewala Desert Outpost",
        "location": "Jaisalmer Sector, Rajasthan (Thar Desert)",
        "video_filename": "border_demo_01.mp4",
        "status": "ONLINE"
    },
    {
        "id": "CAM-02",
        "name": "Wagah-Attari Gate Checkpoint",
        "location": "Amritsar Crossing, Punjab",
        "video_filename": "border_demo_02.mp4",
        "status": "ONLINE"
    },
    {
        "id": "CAM-03",
        "name": "Galwan Valley LAC Outpost",
        "location": "Eastern Ladakh Ridge Patrol",
        "video_filename": "border_demo_03.mp4",
        "status": "ONLINE"
    }
]
