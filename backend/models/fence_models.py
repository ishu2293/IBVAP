from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
import datetime

class VirtualFence(BaseModel):
    id: str
    name: str
    type: Literal["polygon", "line"]
    points: List[List[float]]  # Normalized [0.0 - 1.0] coordinates [[x1, y1], [x2, y2], ...]
    camera_id: str = "CAM-01"
    enabled: bool = True
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "HIGH"
    created_at: Optional[str] = Field(default_factory=lambda: datetime.datetime.now().isoformat())

class FenceCreateRequest(BaseModel):
    name: str
    type: Literal["polygon", "line"]
    points: List[List[float]]
    camera_id: str = "CAM-01"
    enabled: bool = True
    severity: Optional[Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]] = "HIGH"

class FenceUpdateRequest(BaseModel):
    name: Optional[str] = None
    points: Optional[List[List[float]]] = None
    enabled: Optional[bool] = None
    severity: Optional[Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]] = None

class IntrusionEvent(BaseModel):
    event_id: str
    event_type: str = "VIRTUAL_FENCE_INTRUSION"
    person_track_id: str
    identity: str = "UNKNOWN"
    camera_id: str
    fence_id: str
    fence_name: str
    timestamp: str
    foot_point: List[float]
    direction: str = "STATIONARY"
    confidence: float = 0.0
    severity: str = "HIGH"
    snapshot_url: Optional[str] = None
    message: Optional[str] = None

class FenceStats(BaseModel):
    total_fences: int
    active_fences: int
    active_intrusions: int
    total_intrusions: int
