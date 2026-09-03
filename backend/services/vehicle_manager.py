import datetime
from typing import List, Dict, Any, Optional
from collections import deque

class VehicleManager:
    """
    Manages historical records and active states for all vehicles and ANPR detections.
    Provides query, search, filtering, and aggregation methods for the API & frontend.
    """
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        
        # vehicle_track_id -> vehicle_dict
        self.vehicles: Dict[str, Dict[str, Any]] = {}
        
        # List of historical ANPR detection events
        self.anpr_history: deque = deque(maxlen=max_history_size)
        
        # Logged plate unique set to prevent duplicate log events per session
        self.logged_plates: set = set()
        
        # Recent ANPR feed (last 10 confirmed events)
        self.recent_anpr_feed: deque = deque(maxlen=20)

    def register_or_update_vehicle(
        self,
        track_id: str,
        vehicle_type: str,
        confidence: float,
        plate_data: Dict[str, Any],
        camera_id: str,
        direction: str,
        frame_number: int
    ) -> Optional[Dict[str, Any]]:
        """
        Updates vehicle state and creates an ANPR record when a plate is confirmed.
        Returns newly logged ANPR record dict if newly confirmed, else None.
        """
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        
        if track_id not in self.vehicles:
            self.vehicles[track_id] = {
                "vehicle_id": track_id,
                "vehicle_type": vehicle_type,
                "vehicle_confidence": round(float(confidence), 2),
                "plate_number": plate_data.get("plate_number") or "Not Detected",
                "plate_confidence": plate_data.get("ocr_confidence", 0.0),
                "first_seen": now_str,
                "last_seen": now_str,
                "camera_id": camera_id,
                "direction": direction,
                "status": "Active",
                "plate_crop_url": plate_data.get("plate_crop_url"),
                "vehicle_crop_url": plate_data.get("vehicle_crop_url"),
                "total_frames": 1
            }
        else:
            veh = self.vehicles[track_id]
            veh["last_seen"] = now_str
            veh["direction"] = direction
            veh["vehicle_type"] = vehicle_type
            veh["vehicle_confidence"] = max(veh["vehicle_confidence"], round(float(confidence), 2))
            veh["total_frames"] += 1
            
            if plate_data.get("plate_number"):
                veh["plate_number"] = plate_data["plate_number"]
                veh["plate_confidence"] = max(veh["plate_confidence"], plate_data.get("ocr_confidence", 0.0))
            if plate_data.get("plate_crop_url"):
                veh["plate_crop_url"] = plate_data["plate_crop_url"]
            if plate_data.get("vehicle_crop_url"):
                veh["vehicle_crop_url"] = plate_data["vehicle_crop_url"]

        # Check if plate is confirmed and should be logged as an ANPR event
        plate_num = plate_data.get("plate_number")
        is_confirmed = plate_data.get("is_confirmed", False)
        
        if plate_num and is_confirmed:
            event_key = f"{track_id}_{plate_num}"
            if event_key not in self.logged_plates:
                self.logged_plates.add(event_key)
                
                anpr_record = {
                    "id": f"ANPR-{len(self.anpr_history) + 1:04d}",
                    "timestamp": now_str,
                    "camera_id": camera_id,
                    "vehicle_track_id": track_id,
                    "vehicle_type": vehicle_type,
                    "plate_number": plate_num,
                    "ocr_confidence": plate_data.get("ocr_confidence", 0.0),
                    "plate_crop_url": plate_data.get("plate_crop_url"),
                    "vehicle_crop_url": plate_data.get("vehicle_crop_url"),
                    "direction": direction
                }
                
                self.anpr_history.appendleft(anpr_record)
                self.recent_anpr_feed.appendleft(anpr_record)
                return anpr_record

        return None

    def get_vehicle(self, track_id: str) -> Optional[Dict[str, Any]]:
        return self.vehicles.get(track_id)

    def get_all_vehicles(self) -> List[Dict[str, Any]]:
        return list(self.vehicles.values())

    def get_anpr_history(
        self,
        plate_search: Optional[str] = None,
        vehicle_type: Optional[str] = None,
        camera_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Returns filtered ANPR history.
        """
        results = list(self.anpr_history)

        if plate_search:
            q = plate_search.upper().strip()
            results = [r for r in results if q in r["plate_number"].upper()]

        if vehicle_type and vehicle_type.upper() != "ALL":
            vt = vehicle_type.upper().strip()
            results = [r for r in results if r["vehicle_type"].upper() == vt]

        if camera_id and camera_id.upper() != "ALL":
            cam = camera_id.upper().strip()
            results = [r for r in results if r["camera_id"].upper() == cam]

        return results[:limit]

    def get_recent_anpr(self, limit: int = 10) -> List[Dict[str, Any]]:
        return list(self.recent_anpr_feed)[:limit]

    def get_total_anpr_count(self) -> int:
        return len(self.logged_plates)

    def reset_session(self):
        self.vehicles.clear()
        self.anpr_history.clear()
        self.logged_plates.clear()
        self.recent_anpr_feed.clear()
