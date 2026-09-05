# IBVAP – Intelligent Border Video Analytics Platform
## Module 01: Real-Time Human Detection & Tracking System

[![System Status](https://img.shields.io/badge/System-ONLINE-10b981?style=for-the-badge)](http://localhost:3000)
[![YOLO Engine](https://img.shields.io/badge/YOLO-v11n-007acc?style=for-the-badge)](https://github.com/ultralytics/ultralytics)
[![Tracking](https://img.shields.io/badge/Tracker-ByteTrack-8b5cf6?style=for-the-badge)](https://github.com/ifzhang/ByteTrack)

The **Human Detection and Tracking System** is the core foundational module of the **Intelligent Border Video Analytics Platform (IBVAP)**. It processes live CCTV feeds and pre-recorded surveillance videos in real time to detect humans, continuously track each person across frames using persistent Track IDs (`P-001`, `P-002`), calculate ground foot-point coordinates, estimate movement directions (`NORTH`, `SOUTH-EAST`, `STATIONARY`), and draw visual movement trails.

---

## 🎯 Key Capabilities

- **Real-Time YOLO Person Detection**: Uses Ultralytics YOLO (`yolo11n.pt` nano model) strictly filtered for COCO `person` class with configurable confidence threshold (default: `0.5`).
- **Persistent ByteTrack Object Tracking**: Assigns unique Track IDs (`P-001`, `P-002`) that persist across frames, handle path crossovers, short occlusions, and brief detection losses.
- **Position & Spatial History**: Computes center point `(cx, cy)` and ground foot point `(fx, fy)`. Maintains a memory-capped history deque for motion trails.
- **Direction Estimation**: Calculates real-time cardinal movement direction (`NORTH`, `SOUTH`, `EAST`, `WEST`, `NORTH-EAST`, `NORTH-WEST`, `SOUTH-EAST`, `SOUTH-WEST`, `STATIONARY`) using noise-filtering displacement thresholds.
- **Demo CCTV & Upload Modes**:
  - **Mode 1 – Upload Video**: Process custom MP4, AVI, MOV, or MKV video files.
  - **Mode 2 – Demo CCTV**: Multi-camera border command center simulation (`CAM-01 Border Sector A`, `CAM-02 Border Road B`, `CAM-03 BOP North`) with live CCTV HUD overlays (🔴 LIVE indicator, camera name, location, timestamp, frame counter, active track count).
- **Border Security Command Center UI**: Modern, dark-themed React + TypeScript dashboard with live telemetry counters (Persons Detected, Active Tracks, Total Unique Tracks, Processing FPS, Hardware Device: CPU/CUDA), active person list, and interactive track detail inspector.

---

## 🏗️ Architecture & Modular Design

The system is designed with a future-ready modular architecture allowing seamless integration of downstream analytics (Vehicle Detection, ANPR, Face Recognition, Intrusion Rules, Risk & Alert Engines).

```text
               +----------------------------------+
               |        Input Source              |
               | (Upload MP4 / Demo CCTV Cameras) |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |      FastAPI Video Processor     |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |   YOLO Person Detection (Class 0)|
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |      ByteTrack Object Tracker    |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               | Spatial Position & History Buffer|
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               | Movement Analyzer (Direction/Vel)|
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |  OpenCV Overlay & Telemetry JSON |
               +----------------------------------+
                                |
                     (WebSocket /ws/video)
                                |
                                v
               +----------------------------------+
               |  React Command Center Dashboard  |
               +----------------------------------+
```

---

## 📁 Project Structure

```text
person detection and tracking/
│
├── backend/
│   ├── main.py                   # FastAPI server, WebSocket endpoint & CORS config
│   ├── config.py                 # System parameters (YOLO model, confidence, frame skip, cameras)
│   │
│   ├── ai/
│   │   ├── detector.py           # PersonDetector class (Ultralytics YOLO)
│   │   ├── tracker.py            # PersonTracker class (ByteTrack integration)
│   │   └── human_tracker.py      # Unified HumanTracker module
│   │
│   ├── services/
│   │   ├── video_processor.py    # Main stream loop, overlay rendering & FPS calculator
│   │   ├── position_tracker.py   # Center & foot point calculation + history deque
│   │   └── movement_analyzer.py  # Cardinal movement direction & motion status
│   │
│   ├── models/
│   │   └── tracking_models.py    # Pydantic schemas (Detection, TrackData, FrameTelemetry)
│   │
│   ├── api/
│   │   ├── video.py              # Upload & camera list endpoints
│   │   └── tracking.py           # Track details & system status endpoints
│   │
│   └── utils/
│       ├── draw.py               # Overlay drawing (boxes, labels, trails, CCTV HUD)
│       └── demo_generator.py     # Synthetic demo CCTV video generator
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx        # Command center top bar & mode switcher
│   │   │   ├── VideoPlayer.jsx   # Live stream canvas, player controls & frame skip slider
│   │   │   ├── CameraSelector.jsx# CCTV camera switcher buttons
│   │   │   ├── StatsPanel.jsx    # Telemetry stat cards
│   │   │   ├── TrackListPanel.jsx# Active person list
│   │   │   └── TrackDetailPanel.jsx # Single track inspection drawer
│   │   ├── services/
│   │   │   └── api.js            # Axios REST client & WebSocket manager
│   │   ├── App.jsx               # Root dashboard container
│   │   ├── index.css             # Tailwind directives & command center theme
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── index.html
│
├── assets/
│   └── demo_cctv/                # Sample video assets (auto-generated if missing)
│
├── models/                       # Downloaded YOLO models (e.g. yolo11n.pt)
├── requirements.txt
└── README.md
```

---

## ⚡ Setup & Installation

### Prerequisites

- **Python**: `3.10` or higher (Tested on Python 3.13)
- **Node.js**: `v18` or higher (Tested on Node v22)
- **Git**

---

### 1. Backend Setup

1. Open terminal in the project root:
   ```bash
   python -m venv venv
   ```
2. Activate virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     source venv/bin/activate
     ```
3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI backend server:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   The backend API will be available at `http://localhost:8000`.

---

### 2. Frontend Setup

1. Open a new terminal in the `frontend/` directory:
   ```bash
   cd frontend
   npm install
   ```
2. Launch the Vite development server:
   ```bash
   npm run dev
   ```
3. Open your browser and navigate to:
   ```text
   http://localhost:3000
   ```

---

## 📖 How to Use

### Mode 1: Demo CCTV Mode

1. Select **"Demo CCTV"** in the top header bar.
2. Choose one of the pre-configured border surveillance cameras:
   - **CAM-01**: Border Sector A (North Fence Gate 4)
   - **CAM-02**: Border Road B (Patrol Route Bravo)
   - **CAM-03**: BOP North Outpost (Observation Tower 2)
3. Click **START DETECTION**.
4. The live video stream will render bounding boxes, persistent Track IDs (`P-001`), confidence scores, center/foot points, movement trails, and the simulated CCTV HUD.
5. Click any active track card on the right panel to open its **Track Details** and highlight that person on the video canvas.

### Mode 2: Upload Video Mode

1. Select **"Upload Video"** in the top header bar.
2. Drag & drop an MP4, AVI, MOV, or MKV video file into the dropzone (or click "Select Video").
3. Click **START DETECTION**.
4. Adjust the **"Process Every: 1x / 2x / 3x"** frame skipping control if needed for CPU performance optimization.

---

## 🧠 AI AI Algorithms Explained

### 1. YOLO Person Detection

Ultralytics YOLO performs single-pass real-time object detection. The model evaluates candidate regions and outputs bounding box coordinates `[x1, y1, x2, y2]`, confidence scores, and class labels. The system strictly filters for COCO class ID `0` (`person`), ignoring non-human objects.

### 2. ByteTrack Tracking

Unlike traditional trackers that discard low-confidence detections, **ByteTrack** retains low-confidence bounding boxes to maintain track continuity during temporary occlusions or motion blur. It uses Kalman filtering for state estimation and Hungarian algorithm matching based on Intersection over Union (IoU) to map detections to track IDs (`P-001`, `P-002`).

### 3. Face Detection & Recognition (Module 04)

- **YuNet Face Detector (`face_detection_yunet_2023mar.onnx`)**: High-speed edge DNN model built into OpenCV (`cv2.FaceDetectorYN`). Restricts detection to the upper head-region of each detected person (`P-001`, `P-002`) to optimize CPU processing by 10x and associate faces directly with track IDs.
- **SFace Face Embedder (`face_recognition_sface_2021dec.onnx`)**: Deep feature extractor built into OpenCV (`cv2.FaceRecognizerSF`). Aligns faces using 5 facial landmarks (eyes, nose, mouth corners) and produces 128-dimensional L2-normalized biometric embeddings.
- **Cosine Similarity Verification**: Compares real-time embeddings against authorized personnel in the local watchlist database (`assets/registered_faces/face_registry.json`).
- **Identity Consensus & Event De-duplication**: Locks recognized identities to track IDs across consecutive frames, logging `FACE_RECOGNIZED` and `UNKNOWN_FACE` events with an intelligent cooldown window to eliminate event spam.

---

## 🔒 Biometric Data & Privacy Notice

> **Privacy Notice**: Facial recognition is intended for authorized security monitoring. Facial images and biometric information are processed only for the intended surveillance purpose and should be handled according to applicable organizational policies, privacy requirements, and data-retention rules. Stored biometric embeddings are restricted to local secure storage.

---

## 🔮 Future Extensions

This module exposes clean interfaces for planned downstream IBVAP capabilities:
- **Module 05**: Virtual Perimeter Intrusion & Loitering Analytics
- **Module 06**: Unified Border Risk & Threat Assessment Engine

---

## 📄 License

Internal IBVAP Proprietary Platform. All rights reserved.
