import os
import json
import time
import datetime
import cv2
import numpy as np
from pathlib import Path
from collections import deque
from typing import List, Dict, Any, Optional, Tuple, Set

from backend.config import (
    FENCE_CONFIG_FILE,
    INTRUSIONS_DIR,
    INTRUSION_ALERT_COOLDOWN,
    DEFAULT_FENCE_SEVERITY
)
from backend.models.fence_models import (
    VirtualFence,
    FenceCreateRequest,
    FenceUpdateRequest,
    IntrusionEvent
)

def ccw(A: Tuple[float, float], B: Tuple[float, float], C: Tuple[float, float]) -> bool:
    """Checks counter-clockwise orientation of 3 points."""
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

def segments_intersect(
    A: Tuple[float, float],
    B: Tuple[float, float],
    C: Tuple[float, float],
    D: Tuple[float, float]
) -> bool:
    """Returns True if line segment AB intersects line segment CD."""
    return (ccw(A, C, D) != ccw(B, C, D)) and (ccw(A, B, C) != ccw(A, B, D))


class VirtualFenceManager:
    """
    Modular, high-performance Virtual Fence & Intrusion Detection Service.
    Supports Polygon & Line Crossing fences with normalized resolution-independent coordinates.
    Manages per-track intrusion states, cooldowns, snapshot capture, and real-time security alerts.
    """
    def __init__(self, config_path: Path = FENCE_CONFIG_FILE):
        self.config_path = Path(config_path)
        INTRUSIONS_DIR.mkdir(parents=True, exist_ok=True)
        
        # In-memory fence registry: fence_id -> VirtualFence
        self.fences: Dict[str, VirtualFence] = {}
        
        # State tracking: (person_id, fence_id) -> is_inside (bool)
        self.track_inside_states: Dict[Tuple[str, str], bool] = {}
        
        # State tracking: (person_id, fence_id) -> last_alert_timestamp (float)
        self.last_alert_times: Dict[Tuple[str, str], float] = {}
        
        # Last known foot point per person: person_id -> (foot_x, foot_y)
        self.last_foot_points: Dict[str, Tuple[float, float]] = {}
        
        # Currently active intrusions: track_id -> Set[fence_id]
        self.active_intrusions: Dict[str, Set[str]] = {}
        
        # Event History
        self.intrusion_events: deque = deque(maxlen=500)
        self.event_counter = 1
        
        # Load from disk or seed defaults
        self.load_fences()

    def load_fences(self):
        """Loads fence configurations from JSON or seeds realistic defaults."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    for item in data:
                        fence = VirtualFence(**item)
                        self.fences[fence.id] = fence
                print(f"[VirtualFence] Loaded {len(self.fences)} fence configurations from disk.")
                return
            except Exception as e:
                print(f"[VirtualFence] Error loading {self.config_path}: {e}. Seeding defaults.")

        self.seed_default_fences()

    def seed_default_fences(self):
        """Seeds standard surveillance fences for demo cameras."""
        default_fences = [
            VirtualFence(
                id="FENCE-001",
                name="Restricted Border Perimeter",
                type="polygon",
                points=[
                    [0.10, 0.40],
                    [0.90, 0.40],
                    [0.95, 0.95],
                    [0.05, 0.95]
                ],
                camera_id="CAM-01",
                enabled=True,
                severity="HIGH"
            ),
            VirtualFence(
                id="FENCE-002",
                name="Border Crossing Line",
                type="line",
                points=[
                    [0.05, 0.65],
                    [0.95, 0.65]
                ],
                camera_id="CAM-02",
                enabled=True,
                severity="CRITICAL"
            ),
            VirtualFence(
                id="FENCE-003",
                name="LAC Patrol Restricted Zone",
                type="polygon",
                points=[
                    [0.15, 0.35],
                    [0.85, 0.35],
                    [0.90, 0.90],
                    [0.10, 0.90]
                ],
                camera_id="CAM-03",
                enabled=True,
                severity="HIGH"
            )
        ]

        for fence in default_fences:
            self.fences[fence.id] = fence
        self.save_fences()

    def save_fences(self):
        """Persists fence configuration to disk."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump([f.model_dump() for f in self.fences.values()], f, indent=2)
        except Exception as e:
            print(f"[VirtualFence] Error saving fence configurations: {e}")

    def reset_session(self):
        """Clears transient per-track intrusion states when stream restarts."""
        self.track_inside_states.clear()
        self.last_alert_times.clear()
        self.last_foot_points.clear()
        self.active_intrusions.clear()

    # --- Fence CRUD ---
    def get_fences(self, camera_id: Optional[str] = None) -> List[VirtualFence]:
        if camera_id and camera_id != "ALL":
            return [f for f in self.fences.values() if f.camera_id == camera_id]
        return list(self.fences.values())

    def get_fence(self, fence_id: str) -> Optional[VirtualFence]:
        return self.fences.get(fence_id)

    def create_fence(self, req: FenceCreateRequest) -> VirtualFence:
        # Generate new fence ID
        existing_nums = []
        for fid in self.fences.keys():
            if fid.startswith("FENCE-"):
                try:
                    existing_nums.append(int(fid.split("-")[1]))
                except ValueError:
                    pass
        next_num = max(existing_nums, default=0) + 1
        fence_id = f"FENCE-{next_num:03d}"

        new_fence = VirtualFence(
            id=fence_id,
            name=req.name,
            type=req.type,
            points=req.points,
            camera_id=req.camera_id,
            enabled=req.enabled,
            severity=req.severity or "HIGH"
        )
        self.fences[fence_id] = new_fence
        self.save_fences()
        return new_fence

    def update_fence(self, fence_id: str, req: FenceUpdateRequest) -> Optional[VirtualFence]:
        fence = self.fences.get(fence_id)
        if not fence:
            return None
        
        if req.name is not None:
            fence.name = req.name
        if req.points is not None:
            fence.points = req.points
        if req.enabled is not None:
            fence.enabled = req.enabled
        if req.severity is not None:
            fence.severity = req.severity

        self.save_fences()
        return fence

    def delete_fence(self, fence_id: str) -> bool:
        if fence_id in self.fences:
            del self.fences[fence_id]
            self.save_fences()
            return True
        return False

    def toggle_fence(self, fence_id: str, enabled: Optional[bool] = None) -> Optional[VirtualFence]:
        fence = self.fences.get(fence_id)
        if not fence:
            return None
        fence.enabled = not fence.enabled if enabled is None else enabled
        self.save_fences()
        return fence

    # --- Core Intrusion Detection Engine ---
    def is_point_in_polygon(
        self,
        foot_point: Tuple[float, float],
        fence: VirtualFence,
        frame_width: int,
        frame_height: int
    ) -> bool:
        """Uses cv2.pointPolygonTest to accurately determine if point is inside polygon."""
        if len(fence.points) < 3:
            return False
        
        # Scale normalized coordinates to frame resolution
        poly_pts = np.array([
            [int(pt[0] * frame_width), int(pt[1] * frame_height)]
            for pt in fence.points
        ], dtype=np.int32)

        test_pt = (float(foot_point[0]), float(foot_point[1]))
        dist = cv2.pointPolygonTest(poly_pts, test_pt, False)
        return dist >= 0  # >= 0 means inside or on boundary

    def has_crossed_line(
        self,
        prev_foot: Tuple[float, float],
        curr_foot: Tuple[float, float],
        fence: VirtualFence,
        frame_width: int,
        frame_height: int
    ) -> bool:
        """Checks if foot trajectory segment intersects the virtual line."""
        if len(fence.points) < 2:
            return False

        # Scale line points
        p1 = (fence.points[0][0] * frame_width, fence.points[0][1] * frame_height)
        p2 = (fence.points[1][0] * frame_width, fence.points[1][1] * frame_height)

        # Skip check if person has not moved (prevent jitter)
        if abs(curr_foot[0] - prev_foot[0]) < 1.0 and abs(curr_foot[1] - prev_foot[1]) < 1.0:
            return False

        return segments_intersect(prev_foot, curr_foot, p1, p2)

    def capture_evidence_snapshot(
        self,
        frame: np.ndarray,
        person_track: Dict[str, Any],
        fence: VirtualFence,
        identity: str,
        timestamp_str: str,
        camera_id: str
    ) -> Optional[str]:
        """Captures and saves a clean evidence snapshot when an intrusion occurs."""
        try:
            h, w = frame.shape[:2]
            snapshot = frame.copy()
            bbox = person_track.get("bbox", [0, 0, 0, 0])
            x1, y1, x2, y2 = map(int, bbox)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            track_id = person_track.get("track_id", "P-UNKNOWN")

            # Draw prominent intrusion highlight box
            cv2.rectangle(snapshot, (x1, y1), (x2, y2), (0, 0, 255), 3)

            # Draw Top Evidence Banner
            banner_h = 42
            cv2.rectangle(snapshot, (0, 0), (w, banner_h), (10, 10, 30), -1)
            cv2.line(snapshot, (0, banner_h), (w, banner_h), (0, 0, 255), 2)

            banner_text = f"🚨 INTRUSION ALERT | {fence.name} ({fence.severity}) | CAM: {camera_id} | {timestamp_str}"
            cv2.putText(snapshot, banner_text, (15, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2, cv2.LINE_AA)

            # Save snapshot
            clean_cam = camera_id.replace("-", "")
            clean_track = track_id.replace("-", "")
            ts_clean = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"intrusion_{clean_cam}_{clean_track}_{ts_clean}.jpg"
            filepath = INTRUSIONS_DIR / filename
            cv2.imwrite(str(filepath), snapshot, [int(cv2.IMWRITE_JPEG_QUALITY), 85])

            return f"/media/crops/intrusions/{filename}"
        except Exception as e:
            print(f"[VirtualFence] Snapshot capture failed: {e}")
            return None

    def process_frame(
        self,
        frame: np.ndarray,
        person_tracks: List[Dict[str, Any]],
        camera_id: str,
        frame_number: int
    ) -> Tuple[List[Dict[str, Any]], Optional[IntrusionEvent]]:
        """
        Evaluates all active person tracks against active fences for the given camera.
        Returns (active_intrusions_list, optional_new_intrusion_event).
        """
        now = time.time()
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        h, w = frame.shape[:2]

        camera_fences = [f for f in self.fences.values() if f.camera_id == camera_id and f.enabled]
        
        current_active_intrusions = []
        new_alert_event: Optional[IntrusionEvent] = None

        # Clean active intrusions set for this frame
        current_frame_intrusions_map: Dict[str, Set[str]] = {}

        for p in person_tracks:
            p_id = p["track_id"]
            curr_foot = tuple(p.get("foot_point", (0.0, 0.0)))
            prev_foot = self.last_foot_points.get(p_id, curr_foot)
            
            # Extract identity from existing face recognition output
            face_info = p.get("face") or {}
            face_status = face_info.get("status", "none")
            if face_status == "recognized" and face_info.get("name"):
                identity = face_info["name"]
            elif face_status == "unknown":
                identity = "UNKNOWN"
            else:
                identity = "UNKNOWN"

            direction = p.get("direction", "STATIONARY")
            conf = p.get("confidence", 0.0)

            for fence in camera_fences:
                state_key = (p_id, fence.id)
                was_inside = self.track_inside_states.get(state_key, False)
                is_inside_now = False

                if fence.type == "polygon":
                    is_inside_now = self.is_point_in_polygon(curr_foot, fence, w, h)
                elif fence.type == "line":
                    # For a line crossing fence, crossing detection triggers an entry transition
                    crossed = self.has_crossed_line(prev_foot, curr_foot, fence, w, h)
                    if crossed:
                        is_inside_now = True
                    else:
                        is_inside_now = was_inside

                # Check State Transition: OUTSIDE -> INSIDE
                if is_inside_now:
                    if p_id not in current_frame_intrusions_map:
                        current_frame_intrusions_map[p_id] = set()
                    current_frame_intrusions_map[p_id].add(fence.id)

                    current_active_intrusions.append({
                        "person_id": p_id,
                        "fence_id": fence.id,
                        "fence_name": fence.name,
                        "severity": fence.severity,
                        "identity": identity
                    })

                    if not was_inside:
                        # Legitimate transition into restricted zone
                        last_alert = self.last_alert_times.get(state_key, 0.0)
                        if (now - last_alert) >= INTRUSION_ALERT_COOLDOWN:
                            # Trigger Alert!
                            self.last_alert_times[state_key] = now
                            event_id = f"INTR-{self.event_counter:04d}"
                            self.event_counter += 1

                            snapshot_url = self.capture_evidence_snapshot(
                                frame=frame,
                                person_track=p,
                                fence=fence,
                                identity=identity,
                                timestamp_str=now_str,
                                camera_id=camera_id
                            )

                            new_event = IntrusionEvent(
                                event_id=event_id,
                                event_type="VIRTUAL_FENCE_INTRUSION",
                                person_track_id=p_id,
                                identity=identity,
                                camera_id=camera_id,
                                fence_id=fence.id,
                                fence_name=fence.name,
                                timestamp=now_str,
                                foot_point=[curr_foot[0], curr_foot[1]],
                                direction=direction,
                                confidence=round(conf, 2),
                                severity=fence.severity,
                                snapshot_url=snapshot_url,
                                message=f"Intrusion detected in {fence.name}"
                            )
                            self.intrusion_events.appendleft(new_event)
                            new_alert_event = new_event

                    self.track_inside_states[state_key] = True

                else:
                    # Transition: INSIDE -> OUTSIDE
                    if was_inside:
                        self.track_inside_states[state_key] = False

            # Update foot point history
            self.last_foot_points[p_id] = curr_foot

        self.active_intrusions = current_frame_intrusions_map
        return current_active_intrusions, new_alert_event

    def get_intrusion_history(
        self,
        camera_id: Optional[str] = None,
        limit: int = 50
    ) -> List[IntrusionEvent]:
        """Returns recent intrusion security events."""
        events = list(self.intrusion_events)
        if camera_id and camera_id != "ALL":
            events = [e for e in events if e.camera_id == camera_id]
        return events[:limit]

    def get_stats(self) -> Dict[str, int]:
        total_fences = len(self.fences)
        active_fences = sum(1 for f in self.fences.values() if f.enabled)
        active_intr_count = sum(len(fences) for fences in self.active_intrusions.values())
        total_intrusions = len(self.intrusion_events)

        return {
            "total_fences": total_fences,
            "active_fences": active_fences,
            "active_intrusions": active_intr_count,
            "total_intrusions": total_intrusions
        }
