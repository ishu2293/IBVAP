import torch
from fastapi import APIRouter, HTTPException
from typing import Optional
from backend.config import YOLO_MODEL, CONFIDENCE_THRESHOLD

router = APIRouter(prefix="/api", tags=["Tracking & System"])

# Global reference to VideoProcessor instance injected by main.py
video_processor_instance = None

def set_processor(processor):
    global video_processor_instance
    video_processor_instance = processor

@router.get("/system/status")
def get_system_status():
    """
    Returns system status, device (CPU vs CUDA), YOLO model name, and active session state.
    """
    device = "CUDA" if torch.cuda.is_available() else "CPU"
    is_running = video_processor_instance.is_running if video_processor_instance else False
    current_mode = video_processor_instance.current_mode if video_processor_instance else None
    current_camera = video_processor_instance.current_camera_id if video_processor_instance else None

    return {
        "status": "ONLINE",
        "device": device,
        "model_loaded": YOLO_MODEL,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "active_session": is_running,
        "current_mode": current_mode,
        "current_camera": current_camera
    }

@router.get("/tracks")
def get_active_tracks():
    """
    Returns list of all active tracks in the current stream session.
    """
    if not video_processor_instance:
        return {"tracks": []}
    return {"tracks": video_processor_instance.get_all_active_tracks()}

@router.get("/tracks/{track_id}")
def get_track_detail(track_id: str):
    """
    Returns detailed tracking telemetry for a specific Track ID (e.g. P-001).
    """
    if not video_processor_instance:
        raise HTTPException(status_code=404, detail="No active video session.")
    
    detail = video_processor_instance.get_track_detail(track_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Track ID '{track_id}' not found.")
    return detail

@router.post("/tracks/{track_id}/select")
def select_track(track_id: str):
    """
    Highlights a specific Track ID on the processed video stream overlay.
    """
    if video_processor_instance:
        video_processor_instance.set_selected_track(track_id)
    return {"status": "success", "selected_track_id": track_id}
