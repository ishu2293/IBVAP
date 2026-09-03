from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/api/vehicles", tags=["Vehicles"])

video_processor_instance = None

def set_processor(processor):
    global video_processor_instance
    video_processor_instance = processor

@router.get("/active")
def get_active_vehicles():
    """
    Returns list of all active vehicles in current camera view.
    """
    if not video_processor_instance:
        return {"vehicles": []}
    return {"vehicles": video_processor_instance.get_all_active_vehicles()}

@router.get("/history")
def get_vehicle_history():
    """
    Returns complete history of all tracked vehicles in the system.
    """
    if not video_processor_instance:
        return {"vehicles": []}
    return {"vehicles": video_processor_instance.vehicle_manager.get_all_vehicles()}

@router.get("/{vehicle_id}")
def get_vehicle_detail(vehicle_id: str):
    """
    Returns full details, lifecycle, and plate info for a specific vehicle track ID (e.g. V-001).
    """
    if not video_processor_instance:
        raise HTTPException(status_code=404, detail="No active video session.")
        
    detail = video_processor_instance.get_track_detail(vehicle_id)
    if not detail:
        # Check historical registry if not in active cache
        detail = video_processor_instance.vehicle_manager.get_vehicle(vehicle_id)
        
    if not detail:
        raise HTTPException(status_code=404, detail=f"Vehicle ID '{vehicle_id}' not found.")
    return detail
