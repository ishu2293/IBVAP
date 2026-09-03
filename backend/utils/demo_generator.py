import cv2
import numpy as np
from pathlib import Path
from backend.config import DEMO_CCTV_DIR, ASSETS_DIR

SPRITES_DIR = ASSETS_DIR / "sprites"
SPRITES_DIR.mkdir(parents=True, exist_ok=True)

def attach_license_plate(sprite: np.ndarray, plate_text: str = "MH12AB1234") -> np.ndarray:
    """
    Attaches a high-contrast legible license plate to the bumper of a vehicle sprite.
    """
    img = sprite.copy()
    vh, vw = img.shape[:2]

    # Plate dimensions on bumper (lower 30% of vehicle)
    pw = int(vw * 0.55)
    ph = int(vh * 0.22)
    px1 = (vw - pw) // 2
    py1 = int(vh * 0.68)
    px2 = px1 + pw
    py2 = py1 + ph

    # White plate backing + crisp black border
    cv2.rectangle(img, (px1, py1), (px2, py2), (255, 255, 255), -1)
    cv2.rectangle(img, (px1, py1), (px2, py2), (0, 0, 0), 2)
    # Blue IND strip on left
    cv2.rectangle(img, (px1, py1), (px1 + 10, py2), (180, 50, 20), -1)

    # Crisp bold plate text
    font_scale = 0.58 if len(plate_text) <= 10 else 0.48
    cv2.putText(img, plate_text, (px1 + 14, py1 + int(ph * 0.74)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), 2, cv2.LINE_AA)

    return img


def draw_realistic_pedestrian(frame: np.ndarray, x: int, y: int, scale: float, frame_idx: int, color=(210, 210, 210)):
    """
    Renders realistic humanoid surveillance pedestrian with natural walking gait.
    """
    h = int(115 * scale)
    torso_w = int(22 * scale)
    torso_h = int(42 * scale)
    head_r = int(11 * scale)
    limb_thick = max(2, int(4 * scale))
    
    head_cx = x
    head_cy = y - h + head_r
    torso_top_y = head_cy + head_r
    hip_y = torso_top_y + torso_h

    swing = np.sin(frame_idx * 0.18) * 18 * scale
    
    # Shadow
    cv2.ellipse(frame, (x, y + 2), (int(16 * scale), int(6 * scale)), 0, 0, 360, (20, 20, 20), -1)
    
    # Head
    cv2.circle(frame, (head_cx, head_cy), head_r, color, -1)
    # Torso (Dark security / border guard uniform)
    cv2.rectangle(frame, (x - torso_w // 2, torso_top_y), (x + torso_w // 2, hip_y), (45, 65, 45), -1)
    # Arms
    shoulder_y = torso_top_y + int(6 * scale)
    cv2.line(frame, (x - torso_w // 2, shoulder_y), (int(x - torso_w // 2 - swing), shoulder_y + int(28 * scale)), color, limb_thick)
    cv2.line(frame, (x + torso_w // 2, shoulder_y), (int(x + torso_w // 2 + swing), shoulder_y + int(28 * scale)), color, limb_thick)
    # Legs
    cv2.line(frame, (x - int(5 * scale), hip_y), (int(x - int(5 * scale) + swing), y), (30, 35, 40), limb_thick)
    cv2.line(frame, (x + int(5 * scale), hip_y), (int(x + int(5 * scale) - swing), y), (30, 35, 40), limb_thick)


def generate_cctv_simulation_video(
    filepath: Path,
    camera_name: str,
    vehicles_config: list,
    pedestrians_config: list,
    duration_sec: int = 20,
    fps: int = 25
):
    """
    Generates high-definition realistic CCTV footage with vehicles, license plates, and pedestrians.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    width, height = 800, 450
    total_frames = duration_sec * fps
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(filepath), fourcc, fps, (width, height))

    # Load base vehicle templates
    bus_raw = cv2.imread(str(SPRITES_DIR / "bus_sprite.jpg"))
    car_raw = cv2.imread(str(SPRITES_DIR / "car_sprite.jpg"))

    if bus_raw is None:
        bus_raw = np.zeros((200, 280, 3), dtype=np.uint8)
        bus_raw[:] = (120, 50, 30)
    if car_raw is None:
        car_raw = np.zeros((180, 260, 3), dtype=np.uint8)
        car_raw[:] = (40, 60, 160)

    # Pre-render vehicle sprites with crisp license plates
    rendered_vehicles = []
    for cfg in vehicles_config:
        base = bus_raw if cfg.get("type") in ["BUS", "TRUCK"] else car_raw
        base_resized = cv2.resize(base, (cfg.get("w", 280), cfg.get("h", 180)))
        sprite = attach_license_plate(base_resized, cfg.get("plate", "MH12AB1234"))
        
        rendered_vehicles.append({
            "sprite": sprite,
            "x": cfg.get("start_x", 200),
            "y": cfg.get("start_y", 320),
            "dx": cfg.get("dx", 2.0),
            "dy": cfg.get("dy", 0.0),
            "plate": cfg.get("plate", "MH12AB1234"),
            "type": cfg.get("type", "CAR")
        })

    for f in range(total_frames):
        # 1. Base Surveillance Scene (Checkpoint Road + Landscape)
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Horizon & Desert Ridge
        frame[:170, :] = (38, 34, 30)
        frame[170:220, :] = (50, 46, 42)
        
        # Checkpoint Road
        cv2.fillPoly(frame, [np.array([[0, 220], [width, 220], [width, height], [0, height]])], (32, 30, 28))
        cv2.line(frame, (0, 220), (width, 220), (90, 85, 75), 2)
        
        # Road divider & dashed lane lines
        for lx in range((f * 3) % 80, width, 80):
            cv2.line(frame, (lx, 335), (lx + 40, 335), (180, 180, 170), 2)

        # Border outpost fence & checkpoint barrier
        for fence_x in range(0, width, 30):
            cv2.line(frame, (fence_x, 150), (fence_x, 210), (75, 75, 75), 1)
        cv2.line(frame, (0, 170), (width, 170), (85, 85, 85), 1)
        cv2.line(frame, (0, 190), (width, 190), (85, 85, 85), 1)

        # 2. Draw Pedestrians
        for p in pedestrians_config:
            px = int(p["start_x"] + np.sin(f * 0.04 + p.get("phase", 0)) * p.get("range", 80))
            py = int(p["y"])
            draw_realistic_pedestrian(frame, px, py, scale=p.get("scale", 0.9), frame_idx=f)

        # 3. Draw Vehicles with Plates
        for v in rendered_vehicles:
            v["x"] += v["dx"]
            if v["dx"] > 0 and v["x"] > width + 180:
                v["x"] = -180
            elif v["dx"] < 0 and v["x"] < -180:
                v["x"] = width + 180

            vx = int(v["x"])
            vy = int(v["y"])
            sh, sw = v["sprite"].shape[:2]

            x1 = vx - sw // 2
            y1 = vy - sh // 2
            x2 = x1 + sw
            y2 = y1 + sh

            # Crop bounds
            cx1 = max(0, x1)
            cy1 = max(0, y1)
            cx2 = min(width, x2)
            cy2 = min(height, y2)

            if (cx2 - cx1) > 10 and (cy2 - cy1) > 10:
                sx1 = cx1 - x1
                sy1 = cy1 - y1
                sx2 = sx1 + (cx2 - cx1)
                sy2 = sy1 + (cy2 - cy1)

                # Ground shadow
                shadow_y = min(height - 4, cy2 + 4)
                cv2.ellipse(frame, (vx, shadow_y), (sw // 2 + 15, 16), 0, 0, 360, (15, 15, 15), -1)

                # Paste vehicle
                frame[cy1:cy2, cx1:cx2] = v["sprite"][sy1:sy2, sx1:sx2]

        out.write(frame)

    out.release()
    print(f"[DemoGenerator] Generated realistic video for {camera_name} at: {filepath}")


def ensure_demo_assets(force_regenerate: bool = False):
    """
    Ensures authentic real CCTV surveillance footage is available for all 3 demo cameras.
    """
    import urllib.request
    DEMO_CCTV_DIR.mkdir(parents=True, exist_ok=True)

    cctv_sources = [
        ("border_demo_01.mp4", "https://github.com/intel-iot-devkit/sample-videos/raw/master/person-bicycle-car-detection.mp4"),
        ("border_demo_02.mp4", "https://github.com/intel-iot-devkit/sample-videos/raw/master/car-detection.mp4"),
        ("border_demo_03.mp4", "https://github.com/intel-iot-devkit/sample-videos/raw/master/person-bicycle-car-detection.mp4")
    ]

    for filename, url in cctv_sources:
        target = DEMO_CCTV_DIR / filename
        if not target.exists() or force_regenerate:
            try:
                print(f"[DemoGenerator] Downloading real CCTV footage for {filename} from {url}...")
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                data = urllib.request.urlopen(req, timeout=30).read()
                with open(target, "wb") as f:
                    f.write(data)
                print(f"[DemoGenerator] Saved real CCTV video: {filename} ({len(data)} bytes)")
            except Exception as e:
                print(f"[DemoGenerator] Warning: Could not download {filename} ({e})")


if __name__ == "__main__":
    ensure_demo_assets(force_regenerate=True)
