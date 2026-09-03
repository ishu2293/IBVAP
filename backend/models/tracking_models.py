from typing import List, Tuple, Optional, Dict, Any
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class Detection(BaseModel):
    class_name: str  # 'person', 'car', 'truck', 'bus', 'motorcycle'
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    class_id: int

class PersonTrackData(BaseModel):
    track_id: str  # e.g., P-001
    numeric_id: int
    object_type: str = "person"
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    center: List[float]  # [center_x, center_y]
    foot_point: List[float]  # [foot_x, foot_y]
    direction: str  # e.g., NORTH, STATIONARY
    status: str  # Moving / Stationary
    history: List[List[float]] = []
    first_seen_frame: int
    last_seen_frame: int
    total_frames_tracked: int

class PlateData(BaseModel):
    plate_number: Optional[str] = None
    display_text: str = "Not Detected"
    ocr_confidence: float = 0.0
    is_confirmed: bool = False
    status: str = "Not Detected"
    plate_bbox: Optional[List[float]] = None
    plate_crop_url: Optional[str] = None
    vehicle_crop_url: Optional[str] = None

class VehicleTrackData(BaseModel):
    track_id: str  # e.g., V-001
    numeric_id: int
    object_type: str = "vehicle"
    vehicle_type: str  # CAR / TRUCK / BUS / MOTORCYCLE
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    center: List[float]  # [center_x, center_y]
    foot_point: List[float]  # [foot_x, foot_y]
    direction: str  # e.g., NORTH, SOUTH, STATIONARY
    status: str  # Moving / Stationary
    relative_speed: Optional[str] = "Normal"
    plate: PlateData
    history: List[List[float]] = []
    first_seen_frame: int
    last_seen_frame: int
    total_frames_tracked: int

class ANPRRecord(BaseModel):
    id: str
    timestamp: str
    camera_id: str
    vehicle_track_id: str
    vehicle_type: str
    plate_number: str
    ocr_confidence: float
    plate_crop_url: Optional[str] = None
    vehicle_crop_url: Optional[str] = None
    direction: str = "IN"

class VehicleHistoryItem(BaseModel):
    vehicle_id: str
    vehicle_type: str
    vehicle_confidence: float
    plate_number: str
    plate_confidence: float
    first_seen: str
    last_seen: str
    camera_id: str
    direction: str
    status: str
    plate_crop_url: Optional[str] = None
    vehicle_crop_url: Optional[str] = None

class UnifiedFrameTelemetry(BaseModel):
    frame_number: int
    timestamp_simulated: str
    current_persons: int
    current_vehicles: int
    active_tracks: int
    total_unique_persons: int
    total_unique_vehicles: int
    total_anpr_reads: int
    fps: float
    device: str
    person_tracks: List[PersonTrackData]
    vehicle_tracks: List[VehicleTrackData]
    recent_anpr_event: Optional[ANPRRecord] = None
    camera_id: Optional[str] = None
    mode: str  # demo / upload
    status: str  # RUNNING / PAUSED / STOPPED / ENDED

class SystemStatus(BaseModel):
    status: str  # ONLINE / OFFLINE
    device: str  # CPU / CUDA
    model_loaded: str
    confidence_threshold: float
    vehicle_confidence_threshold: float
    active_session: bool
    current_mode: Optional[str] = None
    current_camera: Optional[str] = None
    fps: float = 0.0

class CameraInfo(BaseModel):
    id: str
    name: str
    location: str
    video_filename: str
    status: str

class VideoMetadata(BaseModel):
    filename: str
    width: int
    height: int
    fps: float
    total_frames: int
    duration_seconds: float
