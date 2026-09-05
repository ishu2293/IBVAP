import cv2
import numpy as np
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/api/faces", tags=["Facial Recognition"])

video_processor_instance = None

def set_processor(processor):
    global video_processor_instance
    video_processor_instance = processor

PRIVACY_NOTICE_TEXT = (
    "Privacy Notice: Facial recognition is intended for authorized security monitoring. "
    "Facial images and biometric information are processed only for the intended surveillance purpose "
    "and should be handled according to applicable organizational policies, privacy requirements, "
    "and data-retention rules."
)

@router.get("/notice")
def get_privacy_notice():
    """Returns official project biometric data and privacy notice."""
    return {"notice": PRIVACY_NOTICE_TEXT}

@router.get("/registry")
def list_registered_faces():
    """
    Returns list of all authorized / registered personnel in the watchlist database.
    Does not expose raw biometric embedding vectors.
    """
    if not video_processor_instance or not hasattr(video_processor_instance, "face_service"):
        return {"personnel": [], "total": 0}

    records = video_processor_instance.face_service.database.list_persons()
    return {
        "personnel": records,
        "total": len(records),
        "privacy_notice": PRIVACY_NOTICE_TEXT
    }

@router.get("/next-id")
def get_next_person_id():
    """Returns the next sequential personnel ID for pre-filling."""
    if not video_processor_instance or not hasattr(video_processor_instance, "face_service"):
        return {"next_id": "P_001"}
    next_id = video_processor_instance.face_service.database.generate_next_person_id()
    return {"next_id": next_id}

@router.post("/register")
async def register_face(
    name: str = Form(..., description="Full Name of personnel"),
    person_id: Optional[str] = Form(None, description="Unique personnel identifier (auto-generated if omitted)"),
    role: str = Form("Security Personnel", description="Assigned role or rank"),
    department: str = Form("Border Security Command", description="Department / Battalion"),
    file: UploadFile = File(..., description="Frontal face portrait photo (JPG/PNG)")
):
    """
    Registers an authorized person into the Facial Recognition Watchlist.
    Validates face presence, extracts 128-d deep embedding, and saves avatar thumbnail.
    """
    if not video_processor_instance or not hasattr(video_processor_instance, "face_service"):
        raise HTTPException(status_code=503, detail="Facial recognition service not initialized.")

    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        raise HTTPException(status_code=400, detail="Only JPG, PNG, and WebP image formats are supported.")

    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None or img.size == 0:
            raise HTTPException(status_code=400, detail="Failed to decode image file.")

        fs = video_processor_instance.face_service
        pid = person_id.strip() if person_id and person_id.strip() else None
        success, message, profile = fs.database.register_person(
            person_id=pid,
            name=name.strip(),
            role=role.strip(),
            department=department.strip(),
            image=img,
            detector=fs.detector,
            recognizer=fs.recognizer
        )

        if not success:
            raise HTTPException(status_code=422, detail=message)

        return {
            "status": "success",
            "message": message,
            "personnel": profile
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.delete("/{person_id}")
def delete_registered_face(person_id: str):
    """
    Removes an authorized person from the watchlist database and deletes their avatar image.
    """
    if not video_processor_instance or not hasattr(video_processor_instance, "face_service"):
        raise HTTPException(status_code=503, detail="Facial recognition service not initialized.")

    success = video_processor_instance.face_service.database.delete_person(person_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Person ID '{person_id}' not found in registry.")

    return {
        "status": "success",
        "message": f"Personnel record '{person_id}' deleted successfully."
    }

@router.get("/events")
def get_face_events(
    event_type: Optional[str] = Query(None, description="Filter by event type: FACE_RECOGNIZED, UNKNOWN_FACE, or ALL"),
    camera_id: Optional[str] = Query(None, description="Filter by camera ID"),
    limit: int = Query(50, ge=1, le=200, description="Max number of records")
):
    """
    Returns queryable face detection and recognition event log with de-duplication.
    """
    if not video_processor_instance or not hasattr(video_processor_instance, "face_service"):
        return {"events": [], "total": 0}

    events = video_processor_instance.face_service.get_all_events(
        event_type=event_type,
        camera_id=camera_id,
        limit=limit
    )
    return {
        "events": events,
        "total": len(events)
    }

@router.get("/recent")
def get_recent_face_feed(limit: int = Query(10, ge=1, le=30)):
    """Returns real-time recent face recognition feed."""
    if not video_processor_instance or not hasattr(video_processor_instance, "face_service"):
        return {"recent": []}

    return {"recent": video_processor_instance.face_service.get_recent_events(limit=limit)}

@router.get("/stats")
def get_face_stats():
    """Returns summary analytics for the facial recognition module."""
    if not video_processor_instance or not hasattr(video_processor_instance, "face_service"):
        return {"total_registered_personnel": 0, "total_face_events": 0, "recognized_events": 0, "unknown_alerts": 0}

    return video_processor_instance.face_service.get_stats()
