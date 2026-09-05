from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from backend.models.fence_models import (
    VirtualFence,
    FenceCreateRequest,
    FenceUpdateRequest,
    IntrusionEvent,
    FenceStats
)

router = APIRouter(prefix="/api/fences", tags=["Virtual Fence & Intrusion Detection"])

# Global reference to VideoProcessor instance injected by main.py
video_processor_instance = None

def set_processor(processor):
    global video_processor_instance
    video_processor_instance = processor

def get_fence_manager():
    if not video_processor_instance or not hasattr(video_processor_instance, "virtual_fence_manager"):
        raise HTTPException(status_code=500, detail="Virtual Fence Manager not initialized")
    return video_processor_instance.virtual_fence_manager

@router.get("", response_model=List[VirtualFence])
def list_fences(camera_id: Optional[str] = Query(None, description="Filter by camera ID")):
    """Returns list of virtual fences, optionally filtered by camera."""
    fm = get_fence_manager()
    return fm.get_fences(camera_id)

@router.get("/stats", response_model=FenceStats)
def get_fence_stats():
    """Returns real-time statistics of virtual fences and intrusions."""
    fm = get_fence_manager()
    return fm.get_stats()

@router.get("/intrusions", response_model=List[IntrusionEvent])
def get_intrusion_history(
    camera_id: Optional[str] = Query(None, description="Filter by camera ID"),
    limit: int = Query(50, ge=1, le=200)
):
    """Returns recorded security intrusion event history with evidence snapshot links."""
    fm = get_fence_manager()
    return fm.get_intrusion_history(camera_id=camera_id, limit=limit)

@router.get("/{fence_id}", response_model=VirtualFence)
def get_fence(fence_id: str):
    """Fetches a specific virtual fence by ID."""
    fm = get_fence_manager()
    fence = fm.get_fence(fence_id)
    if not fence:
        raise HTTPException(status_code=404, detail=f"Fence '{fence_id}' not found")
    return fence

@router.post("", response_model=VirtualFence)
def create_fence(req: FenceCreateRequest):
    """Creates a new virtual fence (Polygon or Line Crossing) with normalized coordinates."""
    if len(req.points) < 2:
        raise HTTPException(status_code=400, detail="A fence requires at least 2 points (or 3 for polygon)")
    if req.type == "polygon" and len(req.points) < 3:
        raise HTTPException(status_code=400, detail="A polygon fence requires at least 3 points")
    
    fm = get_fence_manager()
    return fm.create_fence(req)

@router.put("/{fence_id}", response_model=VirtualFence)
def update_fence(fence_id: str, req: FenceUpdateRequest):
    """Updates an existing virtual fence."""
    fm = get_fence_manager()
    updated = fm.update_fence(fence_id, req)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Fence '{fence_id}' not found")
    return updated

@router.delete("/{fence_id}")
def delete_fence(fence_id: str):
    """Deletes a virtual fence."""
    fm = get_fence_manager()
    success = fm.delete_fence(fence_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Fence '{fence_id}' not found")
    return {"status": "success", "message": f"Fence '{fence_id}' deleted successfully"}

@router.post("/{fence_id}/toggle", response_model=VirtualFence)
def toggle_fence(fence_id: str):
    """Toggles active state of a virtual fence."""
    fm = get_fence_manager()
    fence = fm.toggle_fence(fence_id)
    if not fence:
        raise HTTPException(status_code=404, detail=f"Fence '{fence_id}' not found")
    return fence

@router.post("/{fence_id}/enable", response_model=VirtualFence)
def enable_fence(fence_id: str):
    """Enables a virtual fence."""
    fm = get_fence_manager()
    fence = fm.toggle_fence(fence_id, enabled=True)
    if not fence:
        raise HTTPException(status_code=404, detail=f"Fence '{fence_id}' not found")
    return fence

@router.post("/{fence_id}/disable", response_model=VirtualFence)
def disable_fence(fence_id: str):
    """Disables a virtual fence."""
    fm = get_fence_manager()
    fence = fm.toggle_fence(fence_id, enabled=False)
    if not fence:
        raise HTTPException(status_code=404, detail=f"Fence '{fence_id}' not found")
    return fence
