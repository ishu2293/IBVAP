from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/api/anpr", tags=["ANPR"])

video_processor_instance = None

def set_processor(processor):
    global video_processor_instance
    video_processor_instance = processor

@router.get("/history")
def get_anpr_history(
    plate: Optional[str] = Query(None, description="Search by license plate number"),
    vehicle_type: Optional[str] = Query(None, description="Filter by vehicle type (CAR, TRUCK, MOTORCYCLE, BUS)"),
    camera_id: Optional[str] = Query(None, description="Filter by camera ID (CAM-01, CAM-02, CAM-03)"),
    limit: int = Query(100, ge=1, le=500, description="Max number of records")
):
    """
    Returns searchable & filterable ANPR detection history.
    """
    if not video_processor_instance:
        return {"records": [], "total": 0}
        
    records = video_processor_instance.vehicle_manager.get_anpr_history(
        plate_search=plate,
        vehicle_type=vehicle_type,
        camera_id=camera_id,
        limit=limit
    )
    return {
        "records": records,
        "total": len(records),
        "total_anpr_reads": video_processor_instance.vehicle_manager.get_total_anpr_count()
    }

@router.get("/recent")
def get_recent_anpr(limit: int = Query(10, ge=1, le=50)):
    """
    Returns latest recognized license plate events.
    """
    if not video_processor_instance:
        return {"recent": []}
        
    recent = video_processor_instance.vehicle_manager.get_recent_anpr(limit=limit)
    return {"recent": recent}

@router.get("/stats")
def get_anpr_stats():
    """
    Returns summary statistics for ANPR module.
    """
    if not video_processor_instance:
        return {"total_reads": 0, "active_vehicles": 0}
        
    return {
        "total_reads": video_processor_instance.vehicle_manager.get_total_anpr_count(),
        "active_vehicles": len(video_processor_instance.active_vehicles_cache),
        "total_vehicles_seen": len(video_processor_instance.unique_vehicle_ids)
    }
