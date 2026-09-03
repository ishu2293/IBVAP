import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from backend.config import UPLOADS_DIR, DEMO_CAMERAS, DEMO_CCTV_DIR
from backend.utils.demo_generator import ensure_demo_assets

router = APIRouter(prefix="/api/video", tags=["Video"])

class SessionControlRequest(BaseModel):
    mode: str = "demo"  # 'demo' or 'upload'
    camera_id: Optional[str] = "CAM-01"
    filename: Optional[str] = None
    process_every_n_frames: Optional[int] = 1

@router.get("/cameras")
def get_cameras():
    """
    Returns available demo CCTV cameras and their status.
    """
    ensure_demo_assets()
    return {"cameras": DEMO_CAMERAS}

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Uploads an MP4, AVI, MOV, or MKV video file for processing.
    """
    valid_exts = {".mp4", ".avi", ".mov", ".mkv"}
    ext = Path(file.filename).suffix.lower()
    if ext not in valid_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Supported formats: MP4, AVI, MOV, MKV"
        )

    target_path = UPLOADS_DIR / file.filename
    try:
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {
            "status": "success",
            "message": f"File '{file.filename}' uploaded successfully.",
            "filename": file.filename,
            "filepath": str(target_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save video: {str(e)}")
