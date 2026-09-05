import cv2
import time
import datetime
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Generator, Tuple

from backend.ai.human_tracker import HumanTracker
from backend.ai.vehicle_tracker import VehicleTracker
from backend.ai.unified_tracker import UnifiedTracker
from backend.ai.anpr_engine import ANPREngine
from backend.services.position_tracker import PositionTracker
from backend.services.movement_analyzer import MovementAnalyzer
from backend.services.vehicle_manager import VehicleManager
from backend.services.face_service import FaceService
from backend.utils.draw import draw_tracking_overlays, draw_cctv_hud
from backend.config import (
    PROCESS_EVERY_N_FRAMES,
    YOLO_MODEL,
    CONFIDENCE_THRESHOLD,
    VEHICLE_CONFIDENCE_THRESHOLD,
    DEMO_CAMERAS
)

class VideoProcessor:
    """
    Unified High-Performance Video Processing Pipeline for IBVAP.
    Executes single-pass unified multi-object tracking (Person + Vehicle) + ANPR,
    computes movement trajectories, aggregates multi-frame ANPR consensus,
    renders rich overlays, and delivers real-time telemetry.
    """
    def __init__(self):
        # AI Modules
        self.unified_tracker = UnifiedTracker(model_name=YOLO_MODEL, conf_threshold=0.35)
        # Legacy module references preserved for compatibility
        self.human_tracker = HumanTracker(model_name=YOLO_MODEL, conf_threshold=CONFIDENCE_THRESHOLD)
        self.vehicle_tracker = VehicleTracker(model_name=YOLO_MODEL, conf_threshold=VEHICLE_CONFIDENCE_THRESHOLD)
        self.anpr_engine = ANPREngine()
        self.face_service = FaceService()
        
        # Spatial Telemetry Trackers
        self.person_position_tracker = PositionTracker()
        self.vehicle_position_tracker = PositionTracker()
        self.movement_analyzer = MovementAnalyzer()
        
        # Historical Data & State Managers
        self.vehicle_manager = VehicleManager()
        
        # Caches & State
        self.active_persons_cache: Dict[str, Dict[str, Any]] = {}
        self.active_vehicles_cache: Dict[str, Dict[str, Any]] = {}
        self.unique_person_ids: set = set()
        self.unique_vehicle_ids: set = set()
        
        self.selected_track_id: Optional[str] = None
        self.process_every_n_frames: int = PROCESS_EVERY_N_FRAMES
        
        self.is_running: bool = False
        self.is_paused: bool = False
        self.current_frame_number: int = 0
        self.video_metadata: Dict[str, Any] = {}
        self.current_mode: str = "demo"
        self.current_camera_id: str = "CAM-01"

    def set_selected_track(self, track_id: Optional[str]):
        self.selected_track_id = track_id

    def set_process_every_n_frames(self, n: int):
        self.process_every_n_frames = max(1, n)

    def reset_session(self):
        self.unified_tracker.reset()
        self.human_tracker.reset()
        self.vehicle_tracker.reset()
        self.anpr_engine.reset()
        self.face_service.reset_session()
        self.person_position_tracker.reset()
        self.vehicle_position_tracker.reset()
        self.active_persons_cache.clear()
        self.active_vehicles_cache.clear()
        self.unique_person_ids.clear()
        self.unique_vehicle_ids.clear()
        self.vehicle_manager.reset_session()
        self.current_frame_number = 0
        self.is_running = False
        self.is_paused = False

    def process_video_stream(
        self,
        video_path: Path,
        mode: str = "demo",
        camera_info: Optional[Dict[str, Any]] = None
    ) -> Generator[Tuple[np.ndarray, Dict[str, Any]], None, None]:
        """
        Processes video frame by frame and yields (processed_frame, unified_telemetry).
        """
        self.reset_session()
        self.current_mode = mode
        if camera_info:
            self.current_camera_id = camera_info.get("id", "CAM-01")

        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found at: {video_path}")

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Failed to open video file: {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        orig_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.video_metadata = {
            "width": width,
            "height": height,
            "fps": orig_fps,
            "total_frames": total_frames,
            "duration_seconds": total_frames / orig_fps if orig_fps > 0 else 0
        }

        self.is_running = True
        fps_start_time = time.time()
        fps_counter = 0
        current_fps = orig_fps

        last_raw_persons: List[Dict[str, Any]] = []
        last_raw_vehicles: List[Dict[str, Any]] = []

        try:
            while cap.isOpened() and self.is_running:
                if self.is_paused:
                    time.sleep(0.1)
                    continue

                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                self.current_frame_number += 1
                fps_counter += 1

                # Calculate real processing FPS
                now = time.time()
                elapsed = now - fps_start_time
                if elapsed >= 1.0:
                    current_fps = fps_counter / elapsed
                    fps_counter = 0
                    fps_start_time = now

                # 1. Execute Unified Single-Pass Tracker every N frames
                if self.current_frame_number % self.process_every_n_frames == 0:
                    last_raw_persons, last_raw_vehicles = self.unified_tracker.track_frame(frame, persist=True)

                # 2. Process Active Persons (P-001, P-002) + Facial Recognition
                current_active_persons = []
                new_face_event = None

                for p_raw in last_raw_persons:
                    p_id = p_raw["track_id"]
                    p_num = p_raw["numeric_id"]
                    p_bbox = p_raw["bbox"]
                    p_conf = p_raw["confidence"]

                    self.unique_person_ids.add(p_id)
                    pos_data = self.person_position_tracker.update_position(p_id, p_bbox, self.current_frame_number)
                    motion = self.movement_analyzer.analyze_movement(pos_data["history"])

                    # Run Facial Recognition & Watchlist Matcher
                    face_telemetry, face_evt = self.face_service.process_person_face(
                        frame=frame,
                        track_id=p_id,
                        person_bbox=p_bbox,
                        frame_number=self.current_frame_number,
                        camera_id=self.current_camera_id
                    )
                    if face_evt:
                        new_face_event = face_evt

                    person_info = {
                        "track_id": p_id,
                        "numeric_id": p_num,
                        "object_type": "person",
                        "confidence": p_conf,
                        "bbox": p_bbox,
                        "center": pos_data["center"],
                        "foot_point": pos_data["foot_point"],
                        "direction": motion["direction"],
                        "status": motion["status"],
                        "face": face_telemetry,
                        "history": pos_data["history"],
                        "first_seen_frame": pos_data["first_seen_frame"],
                        "last_seen_frame": pos_data["last_seen_frame"],
                        "total_frames_tracked": pos_data["total_frames_tracked"]
                    }
                    current_active_persons.append(person_info)
                    self.active_persons_cache[p_id] = person_info

                # 3. Process Active Vehicles (V-001, V-002) + ANPR Pipeline
                current_active_vehicles = []
                new_anpr_event = None

                for v_raw in last_raw_vehicles:
                    v_id = v_raw["track_id"]
                    v_num = v_raw["numeric_id"]
                    v_bbox = v_raw["bbox"]
                    v_conf = v_raw["confidence"]
                    v_type = v_raw.get("class_name", "CAR")

                    self.unique_vehicle_ids.add(v_id)
                    pos_data = self.vehicle_position_tracker.update_position(v_id, v_bbox, self.current_frame_number)
                    motion = self.movement_analyzer.analyze_movement(pos_data["history"])

                    # Run ANPR Engine (Plate detection + OCR + multi-frame consensus)
                    anpr_result = self.anpr_engine.process_vehicle_frame(
                        frame=frame,
                        track_id=v_id,
                        vehicle_bbox=v_bbox,
                        frame_number=self.current_frame_number,
                        camera_id=self.current_camera_id
                    )

                    # Update VehicleManager database & record newly confirmed ANPR events
                    logged_anpr = self.vehicle_manager.register_or_update_vehicle(
                        track_id=v_id,
                        vehicle_type=v_type,
                        confidence=v_conf,
                        plate_data=anpr_result,
                        camera_id=self.current_camera_id,
                        direction=motion["direction"],
                        frame_number=self.current_frame_number
                    )
                    if logged_anpr:
                        new_anpr_event = logged_anpr

                    vehicle_info = {
                        "track_id": v_id,
                        "numeric_id": v_num,
                        "object_type": "vehicle",
                        "vehicle_type": v_type,
                        "confidence": v_conf,
                        "bbox": v_bbox,
                        "center": pos_data["center"],
                        "foot_point": pos_data["foot_point"],
                        "direction": motion["direction"],
                        "status": motion["status"],
                        "relative_speed": "Normal" if motion["status"] == "Moving" else "Stationary",
                        "plate": anpr_result,
                        "history": pos_data["history"],
                        "first_seen_frame": pos_data["first_seen_frame"],
                        "last_seen_frame": pos_data["last_seen_frame"],
                        "total_frames_tracked": pos_data["total_frames_tracked"]
                    }
                    current_active_vehicles.append(vehicle_info)
                    self.active_vehicles_cache[v_id] = vehicle_info

                # 4. Render Visual Overlays (Both Persons and Vehicles with Plates)
                processed_frame = draw_tracking_overlays(
                    frame=frame,
                    person_tracks=current_active_persons,
                    vehicle_tracks=current_active_vehicles,
                    selected_track_id=self.selected_track_id
                )

                # 5. Render Command Center CCTV HUD Overlay in Demo Mode
                cam_name = camera_info.get("name", "CAM-01") if camera_info else "CAM-01"
                location = camera_info.get("location", "Border Sector") if camera_info else "Border Sector"
                sim_timestamp = datetime.datetime.now().strftime("%H:%M:%S")

                if mode == "demo":
                    processed_frame = draw_cctv_hud(
                        processed_frame,
                        camera_name=cam_name,
                        location=location,
                        timestamp=sim_timestamp,
                        current_persons=len(current_active_persons),
                        current_vehicles=len(current_active_vehicles),
                        anpr_reads=self.vehicle_manager.get_total_anpr_count(),
                        fps=current_fps
                    )

                # 6. Assemble Unified Telemetry
                telemetry = {
                    "frame_number": self.current_frame_number,
                    "timestamp_simulated": sim_timestamp,
                    "current_persons": len(current_active_persons),
                    "current_vehicles": len(current_active_vehicles),
                    "active_tracks": len(current_active_persons) + len(current_active_vehicles),
                    "total_unique_persons": len(self.unique_person_ids),
                    "total_unique_vehicles": len(self.unique_vehicle_ids),
                    "total_anpr_reads": self.vehicle_manager.get_total_anpr_count(),
                    "fps": round(current_fps, 1),
                    "device": self.unified_tracker.device.upper(),
                    "person_tracks": current_active_persons,
                    "vehicle_tracks": current_active_vehicles,
                    # Backward compatibility for existing person list
                    "tracks": current_active_persons,
                    "recent_anpr_event": new_anpr_event,
                    "recent_face_event": new_face_event,
                    "total_face_events": len(self.face_service.face_events),
                    "total_registered_personnel": len(self.face_service.database.registry),
                    "camera_id": self.current_camera_id,
                    "mode": mode,
                    "status": "RUNNING"
                }

                yield (processed_frame, telemetry)

        finally:
            cap.release()
            self.is_running = False

    def get_track_detail(self, track_id: str) -> Optional[Dict[str, Any]]:
        if track_id.startswith("V-"):
            return self.active_vehicles_cache.get(track_id)
        return self.active_persons_cache.get(track_id)

    def get_all_active_tracks(self) -> List[Dict[str, Any]]:
        return list(self.active_persons_cache.values())

    def get_all_active_vehicles(self) -> List[Dict[str, Any]]:
        return list(self.active_vehicles_cache.values())
