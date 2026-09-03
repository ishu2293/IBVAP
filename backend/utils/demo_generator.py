import cv2
import numpy as np
import urllib.request
from pathlib import Path
from backend.config import DEMO_CCTV_DIR, ASSETS_DIR

SPRITES_DIR = ASSETS_DIR / "sprites"
SPRITES_DIR.mkdir(parents=True, exist_ok=True)

# Pre-defined vehicle sprite URLs (Car, Truck/Bus, Patrol Vehicle)
SAMPLE_VEHICLE_URLS = {
    "car": "https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/assets/bus.jpg",
}

def ensure_vehicle_assets():
    """
    Downloads or creates realistic photographic vehicle templates for synthetic CCTV simulation.
    """
    car_sprite_path = SPRITES_DIR / "car_sprite.png"
    truck_sprite_path = SPRITES_DIR / "truck_sprite.png"

    if not car_sprite_path.exists() or not truck_sprite_path.exists():
        try:
            # Download sample bus/car image
            url = "https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/assets/bus.jpg"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            resp = urllib.request.urlopen(req, timeout=8)
            arr = np.asarray(bytearray(resp.read()), dtype=np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

            if img is not None:
                # Extract bus region from sample: approx [230:750, 0:800]
                bus_crop = img[220:740, 10:800]
                bus_resized = cv2.resize(bus_crop, (280, 160))
                cv2.imwrite(str(truck_sprite_path), bus_resized)

                # Create a car sprite crop
                car_crop = cv2.resize(img[250:650, 100:600], (220, 120))
                cv2.imwrite(str(car_sprite_path), car_crop)
                print("[DemoGenerator] Vehicle sprites downloaded successfully.")
        except Exception as e:
            print(f"[DemoGenerator] Warning: Online sprite download skipped ({e}). Creating local high-detail textures.")
            create_high_detail_vehicle_sprite(car_sprite_path, "CAR")
            create_high_detail_vehicle_sprite(truck_sprite_path, "BUS")


def create_high_detail_vehicle_sprite(filepath: Path, v_type: str = "CAR"):
    """
    Fallback: creates a high-detail textured vehicle image.
    """
    if v_type == "CAR":
        w, h = 240, 130
        img = np.zeros((h, w, 3), dtype=np.uint8)
        # Metallic gradient
        for y in range(h):
            shade = int(140 + 70 * np.sin(y / h * np.pi))
            img[y, :] = (shade - 30, shade, shade + 30)
        cv2.rectangle(img, (20, 50), (w - 20, h - 20), (30, 45, 140), -1) # Body
        cv2.rectangle(img, (60, 15), (w - 60, 50), (30, 40, 50), -1) # Glass
        cv2.circle(img, (60, h - 20), 22, (20, 20, 20), -1)
        cv2.circle(img, (w - 60, h - 20), 22, (20, 20, 20), -1)
        cv2.imwrite(str(filepath), img)
    else:
        w, h = 280, 160
        img = np.zeros((h, w, 3), dtype=np.uint8)
        cv2.rectangle(img, (10, 20), (w - 10, h - 20), (160, 70, 40), -1)
        cv2.rectangle(img, (30, 30), (w - 30, 80), (30, 40, 50), -1)
        cv2.circle(img, (70, h - 20), 26, (20, 20, 20), -1)
        cv2.circle(img, (w - 70, h - 20), 26, (20, 20, 20), -1)
        cv2.imwrite(str(filepath), img)


def draw_walking_human(frame: np.ndarray, x: int, y: int, scale: float, frame_idx: int, color=(220, 220, 220)):
    """
    Draws a realistic humanoid figure with moving limbs.
    """
    h = int(120 * scale)
    torso_w = int(24 * scale)
    torso_h = int(45 * scale)
    head_r = int(12 * scale)
    limb_thick = max(2, int(4 * scale))
    
    head_cx = x
    head_cy = y - h + head_r
    torso_top_y = head_cy + head_r
    hip_y = torso_top_y + torso_h

    swing = np.sin(frame_idx * 0.15) * 20 * scale
    
    # Head
    cv2.circle(frame, (head_cx, head_cy), head_r, color, -1)
    # Torso
    cv2.rectangle(frame, (x - torso_w // 2, torso_top_y), (x + torso_w // 2, hip_y), color, -1)
    # Arms
    shoulder_y = torso_top_y + int(8 * scale)
    cv2.line(frame, (x - torso_w // 2, shoulder_y), (int(x - torso_w // 2 - swing), shoulder_y + int(30 * scale)), color, limb_thick)
    cv2.line(frame, (x + torso_w // 2, shoulder_y), (int(x + torso_w // 2 + swing), shoulder_y + int(30 * scale)), color, limb_thick)
    # Legs
    cv2.line(frame, (x - int(6 * scale), hip_y), (int(x - int(6 * scale) + swing), y), color, limb_thick)
    cv2.line(frame, (x + int(6 * scale), hip_y), (int(x + int(6 * scale) - swing), y), color, limb_thick)


def overlay_vehicle_sprite(
    frame: np.ndarray,
    sprite: np.ndarray,
    x: int,
    y: int,
    plate_text: str = "MH12AB1234"
):
    """
    Overlays a photographic vehicle sprite onto the CCTV frame with a crisp license plate.
    """
    fh, fw = frame.shape[:2]
    sh, sw = sprite.shape[:2]

    x1 = max(0, x - sw // 2)
    y1 = max(0, y - sh // 2)
    x2 = min(fw, x1 + sw)
    y2 = min(fh, y1 + sh)

    crop_sw = x2 - x1
    crop_sh = y2 - y1

    if crop_sw <= 10 or crop_sh <= 10:
        return

    # Blend sprite onto frame with soft shadow
    shadow_y = min(fh - 5, y2 + 5)
    cv2.ellipse(frame, (x, shadow_y), (sw // 2 + 10, 15), 0, 0, 360, (15, 15, 15), -1)

    # Insert vehicle texture
    frame[y1:y2, x1:x2] = sprite[:crop_sh, :crop_sw]

    # Draw crisp license plate on bumper
    pl_w = 74
    pl_h = 20
    pl_x1 = max(0, x - pl_w // 2)
    pl_y1 = min(fh - pl_h - 2, y2 - int(sh * 0.28))
    pl_x2 = min(fw, pl_x1 + pl_w)
    pl_y2 = pl_y1 + pl_h

    cv2.rectangle(frame, (pl_x1, pl_y1), (pl_x2, pl_y2), (255, 255, 255), -1)
    cv2.rectangle(frame, (pl_x1, pl_y1), (pl_x2, pl_y2), (0, 0, 0), 1)
    cv2.putText(frame, plate_text, (pl_x1 + 3, pl_y1 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 0), 1, cv2.LINE_AA)


def generate_demo_cctv_video(
    filepath: Path,
    num_persons: int = 2,
    num_vehicles: int = 2,
    duration_sec: int = 15,
    fps: int = 25
):
    """
    Generates a realistic CCTV border surveillance video with moving persons and vehicles.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    ensure_vehicle_assets()

    width, height = 800, 450
    total_frames = duration_sec * fps
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(filepath), fourcc, fps, (width, height))

    car_sprite = cv2.imread(str(SPRITES_DIR / "car_sprite.png"))
    truck_sprite = cv2.imread(str(SPRITES_DIR / "truck_sprite.png"))

    if car_sprite is None:
        create_high_detail_vehicle_sprite(SPRITES_DIR / "car_sprite.png", "CAR")
        car_sprite = cv2.imread(str(SPRITES_DIR / "car_sprite.png"))
    if truck_sprite is None:
        create_high_detail_vehicle_sprite(SPRITES_DIR / "truck_sprite.png", "BUS")
        truck_sprite = cv2.imread(str(SPRITES_DIR / "truck_sprite.png"))

    # Initialize persons
    persons = []
    for i in range(num_persons):
        start_x = int(80 + (i * 220) % (width - 160))
        start_y = int(240 + (i * 30) % 70)
        dx = (1.5 if i % 2 == 0 else -1.2) * (1 + 0.15 * i)
        dy = (0.3 if i % 3 == 0 else -0.3) * (0.8 + 0.1 * i)
        scale = 0.85 + 0.1 * (i % 2)
        persons.append({
            "x": start_x,
            "y": start_y,
            "dx": dx,
            "dy": dy,
            "scale": scale
        })

    demo_plates = ["MH12AB1234", "DL01CD5678", "RJ14EF9012", "KA05GH3456", "PB02IJ7890"]
    vehicles = []
    for i in range(num_vehicles):
        sprite = truck_sprite if i % 2 == 1 else car_sprite
        plate = demo_plates[i % len(demo_plates)]
        start_x = int(140 + i * 280)
        start_y = int(340 + (i % 2) * 40)
        dx = (2.2 if i % 2 == 0 else -2.0)
        vehicles.append({
            "x": start_x,
            "y": start_y,
            "dx": dx,
            "sprite": sprite,
            "plate": plate
        })

    for f in range(total_frames):
        # Create surveillance outpost background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Sky & Mountain ridge
        frame[:180, :] = (35, 30, 28)
        # Ground / Desert patrol road
        frame[180:, :] = (55, 52, 48)
        
        # Patrol road
        cv2.fillPoly(frame, [np.array([[0, 240], [width, 240], [width, height], [0, height]])], (38, 36, 34))
        cv2.line(frame, (0, 240), (width, 240), (95, 90, 80), 2)
        
        # Lane markers
        for lx in range((f * 4) % 70, width, 70):
            cv2.line(frame, (lx, 325), (lx + 35, 325), (170, 170, 160), 2)

        # Border security fence
        for fence_x in range(0, width, 35):
            cv2.line(frame, (fence_x, 145), (fence_x, 195), (85, 85, 85), 1)
        cv2.line(frame, (0, 165), (width, 165), (95, 95, 95), 1)
        cv2.line(frame, (0, 180), (width, 180), (95, 95, 95), 1)

        # Draw persons
        for p in persons:
            p["x"] += p["dx"]
            p["y"] += p["dy"]
            if p["x"] < 40 or p["x"] > width - 40:
                p["dx"] *= -1
            if p["y"] < 210 or p["y"] > 270:
                p["dy"] *= -1
            draw_walking_human(frame, int(p["x"]), int(p["y"]), p["scale"], f)

        # Draw vehicles
        for v in vehicles:
            v["x"] += v["dx"]
            if v["dx"] > 0 and v["x"] > width + 140:
                v["x"] = -140
            elif v["dx"] < 0 and v["x"] < -140:
                v["x"] = width + 140

            overlay_vehicle_sprite(
                frame,
                v["sprite"],
                int(v["x"]),
                int(v["y"]),
                plate_text=v["plate"]
            )

        out.write(frame)

    out.release()
    print(f"[DemoGenerator] Generated video with persons + vehicles at: {filepath}")


def ensure_demo_assets(force_regenerate: bool = False):
    """
    Checks if demo videos exist in assets/demo_cctv/, generates them if missing or forced.
    """
    DEMO_CCTV_DIR.mkdir(parents=True, exist_ok=True)
    cctv_configs = [
        ("border_demo_01.mp4", 3, 2),
        ("border_demo_02.mp4", 2, 2),
        ("border_demo_03.mp4", 2, 1)
    ]
    for filename, p_count, v_count in cctv_configs:
        target_path = DEMO_CCTV_DIR / filename
        if not target_path.exists() or force_regenerate:
            print(f"[DemoGenerator] Generating synthetic video for '{filename}'...")
            generate_demo_cctv_video(target_path, num_persons=p_count, num_vehicles=v_count, duration_sec=20, fps=25)


if __name__ == "__main__":
    ensure_demo_assets(force_regenerate=True)
