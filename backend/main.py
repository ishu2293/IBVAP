import asyncio
import base64
import json
import cv2
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import ASSETS_DIR, UPLOADS_DIR, CROPS_DIR, DEMO_CAMERAS, DEMO_CCTV_DIR, BASE_DIR
from backend.services.video_processor import VideoProcessor
from backend.api import video, tracking, vehicles, anpr_api
from backend.utils.demo_generator import ensure_demo_assets

app = FastAPI(
    title="IBVAP - Intelligent Border Video Analytics Platform",
    description="Unified Human & Vehicle Detection, Tracking & Multi-Frame ANPR powered by YOLO, ByteTrack & EasyOCR",
    version="2.0.0"
)

# Enable CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure demo assets exist on startup
ensure_demo_assets()

# Mount Media Directories (Demo CCTV & Crops)
app.mount("/media", StaticFiles(directory=str(ASSETS_DIR)), name="media")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Initialize global VideoProcessor
processor = VideoProcessor()
tracking.set_processor(processor)
vehicles.set_processor(processor)
anpr_api.set_processor(processor)

# Register API Routers
app.include_router(video.router)
app.include_router(tracking.router)
app.include_router(vehicles.router)
app.include_router(anpr_api.router)

FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
FRONTEND_ASSETS = FRONTEND_DIST / "assets"

# Mount Frontend Assets (JS/CSS/Fonts)
if FRONTEND_ASSETS.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_ASSETS)), name="frontend_assets")

@app.on_event("startup")
def startup_event():
    print("[IBVAP Backend] System initialized. Ready for Human Detection, Vehicle Tracking & ANPR.")

@app.websocket("/ws/video")
async def video_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[WebSocket] Client connected.")

    active_task: asyncio.Task = None

    async def stream_worker(video_file_path: Path, mode: str, camera_info: dict, frame_skip: int):
        processor.set_process_every_n_frames(frame_skip)
        try:
            generator = processor.process_video_stream(
                video_path=video_file_path,
                mode=mode,
                camera_info=camera_info
            )

            for processed_frame, telemetry in generator:
                # Encode frame to JPEG
                ret, buffer = cv2.imencode(".jpg", processed_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if not ret:
                    continue

                jpg_as_text = base64.b64encode(buffer).decode("utf-8")
                frame_data_uri = f"data:image/jpeg;base64,{jpg_as_text}"

                payload = {
                    "type": "frame",
                    "image": frame_data_uri,
                    "telemetry": telemetry
                }

                await websocket.send_text(json.dumps(payload))
                await asyncio.sleep(0.001)

            # Video finished cleanly
            await websocket.send_text(json.dumps({
                "type": "video_ended",
                "message": "Video stream processing completed."
            }))

        except asyncio.CancelledError:
            print("[WebSocket Stream] Task cancelled.")
            processor.is_running = False
        except Exception as e:
            print(f"[WebSocket Error] {str(e)}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Processing error: {str(e)}"
            }))

    try:
        while True:
            data_str = await websocket.receive_text()
            msg = json.loads(data_str)
            action = msg.get("action")

            if action == "start":
                if active_task and not active_task.done():
                    active_task.cancel()
                    processor.is_running = False
                    await asyncio.sleep(0.1)

                mode = msg.get("mode", "demo")
                frame_skip = int(msg.get("process_every_n_frames", 1))

                if mode == "demo":
                    cam_id = msg.get("camera_id", "CAM-01")
                    cam_info = next((c for c in DEMO_CAMERAS if c["id"] == cam_id), DEMO_CAMERAS[0])
                    video_path = DEMO_CCTV_DIR / cam_info["video_filename"]

                    if not video_path.exists():
                        ensure_demo_assets()

                else:  # Upload mode
                    filename = msg.get("filename")
                    if not filename:
                        await websocket.send_text(json.dumps({"type": "error", "message": "No upload filename provided."}))
                        continue
                    video_path = UPLOADS_DIR / filename
                    cam_info = {"id": "UPLOAD", "name": filename, "location": "Uploaded File"}

                active_task = asyncio.create_task(stream_worker(video_path, mode, cam_info, frame_skip))

            elif action == "pause":
                processor.is_paused = True
                await websocket.send_text(json.dumps({"type": "status", "status": "PAUSED"}))

            elif action == "resume":
                processor.is_paused = False
                await websocket.send_text(json.dumps({"type": "status", "status": "RUNNING"}))

            elif action == "stop":
                if active_task and not active_task.done():
                    active_task.cancel()
                processor.reset_session()
                await websocket.send_text(json.dumps({"type": "status", "status": "STOPPED"}))

            elif action == "select_track":
                track_id = msg.get("track_id")
                processor.set_selected_track(track_id)

    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected.")
        if active_task and not active_task.done():
            active_task.cancel()
        processor.reset_session()

# Mount Frontend SPA at root
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
