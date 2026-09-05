# IBVAP – Intelligent Border Video Analytics Platform

[![System Status](https://img.shields.io/badge/System-ONLINE-10b981?style=for-the-badge)](http://localhost:8000)
[![AI Engine](https://img.shields.io/badge/YOLO-v11n-007acc?style=for-the-badge)](https://github.com/ultralytics/ultralytics)
[![Tracking](https://img.shields.io/badge/Tracker-ByteTrack-8b5cf6?style=for-the-badge)](https://github.com/ifzhang/ByteTrack)
[![ANPR](https://img.shields.io/badge/ANPR-EasyOCR-f59e0b?style=for-the-badge)](https://github.com/JaidedAI/EasyOCR)
[![Face Biometrics](https://img.shields.io/badge/Biometrics-OpenCV_SFace-ec4899?style=for-the-badge)](https://docs.opencv.org/)
[![Virtual Fence](https://img.shields.io/badge/Security-Virtual_Fence-ef4444?style=for-the-badge)](#-5-virtual-fence--intrusion-detection)

The **Intelligent Border Video Analytics Platform (IBVAP)** is a comprehensive real-time surveillance and border security AI platform. It unifies human tracking, biometric facial recognition, vehicle classification, automatic number plate recognition (ANPR), virtual fence perimeter protection, and real-time security alerts into a command-center dashboard.

---

## 🎯 Core Features & Capabilities

### 1. Human Detection & Tracking
- **YOLO Detection**: Real-time person detection powered by YOLO (`yolo11n.pt`).
- **ByteTrack Multi-Object Tracking**: Assigns persistent Track IDs (`P-001`, `P-002`) across frames, handling occlusions and crossovers.
- **Ground Foot-Point Calculation**: Computes exact ground coordinates `(fx, fy)` and movement trails.
- **Cardinal Direction Estimation**: Dynamically calculates movement direction (`NORTH`, `SOUTH-EAST`, `STATIONARY`).

### 2. Facial Biometrics & Personnel Watchlist
- **OpenCV YuNet Face Detector**: High-speed edge detector operating on person head regions.
- **OpenCV SFace Biometric Recognizer**: Generates 128-dimensional L2-normalized facial embeddings.
- **Watchlist Verification**: Verifies identities against registered border personnel (`Verified Staff` vs `UNKNOWN`).
- **Identity Consensus**: Locks biometric identities across consecutive frames to prevent flickering.

### 3. Vehicle Detection & Classification
- **Multi-Class Vehicle Tracking**: Identifies and tracks `CAR`, `TRUCK`, `BUS`, and `MOTORCYCLE` (`V-001`, `V-002`).
- **Movement Trajectories & Speed Estimation**: Computes vehicle trajectories and motion states.

### 4. Automatic Number Plate Recognition (ANPR)
- **License Plate Localization**: Detects license plate bounding boxes on vehicle bumpers.
- **OCR Engine**: Recognizes registration numbers using high-contrast plate filtering and EasyOCR.
- **Multi-Frame Consensus**: Aggregates OCR reads over time to confirm license plate readings.

### 5. Virtual Fence & Intrusion Detection
- **Dual Geometry Support**:
  - **Polygon Zones**: Configurable restricted areas using point-in-polygon tests (`cv2.pointPolygonTest`).
  - **Line-Crossing Fences**: Segment-intersection tracking of foot-point trajectories.
- **Interactive Video Drawing**: Draw fences directly on the live CCTV video with Polygon and Line modes.
- **Normalized Coordinates `[0.0 - 1.0]`**: Full resolution independence across all video sizes and screens.
- **Anti-Spam State Machine**: Triggers 1 alert when a person enters (`OUTSIDE -> INSIDE`), suppresses repeated alerts while inside, and triggers fresh alerts on exit $\to$ re-entry.
- **Configurable Cooldown**: 5-second debounce window per `(person_id, fence_id)`.
- **Evidence Snapshots**: Captures an annotated evidence snapshot with bounding boxes, person ID, biometric identity, zone name, timestamp, and camera ID.

### 6. Real-Time Security Alerts & Audio Alarm
- **Instant Telemetry Streaming**: Real-time alerts over WebSocket `/ws/video`.
- **Web Audio Alarm Synthesizer**: Browser-side dual-tone alert chime with toggleable `🔊 Alert Sound: ON / OFF`.
- **Security Breach Log**: View historical breach events with camera filters and evidence snapshot inspection.

### 7. Dual Video Modes
- **Demo CCTV Mode**: Pre-configured feeds from simulated Indian border outposts (`CAM-01 Longewala`, `CAM-02 Wagah-Attari`, `CAM-03 Galwan LAC`) with CCTV HUD overlays.
- **Video Upload Mode**: Support for user-uploaded MP4, AVI, MOV, and MKV video files.

---

## 🔄 Overall Flow of the Project

The end-to-end data pipeline processes video frames through a modular, single-pass pipeline:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            VIDEO INPUT SOURCE                               │
│                (Demo CCTV Outposts / Uploaded Video File)                   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    UNIFIED MULTI-OBJECT DETECTION & TRACKING                │
│                 YOLO (Person & Vehicle) + ByteTrack Engine                  │
└──────────────────────┬───────────────────────────────┬──────────────────────┘
                       │                               │
       [Person Tracks: P-001, P-002]       [Vehicle Tracks: V-001, V-002]
                       │                               │
                       ▼                               ▼
┌──────────────────────────────────────┐  ┌───────────────────────────────────┐
│     FACIAL BIOMETRIC RECOGNITION     │  │       ANPR & OCR ENGINE           │
│   YuNet Detector + SFace Embedder    │  │   Plate Detector + EasyOCR Engine │
│  (Verified Personnel vs UNKNOWN)     │  │   (Multi-Frame Plate Consensus)   │
└──────────────────────┬───────────────┘  └─────────────────┬─────────────────┘
                       │                                    │
                       ▼                                    │
┌──────────────────────────────────────┐                    │
│    VIRTUAL FENCE & INTRUSION ENGINE  │                    │
│   - Foot-Point vs Polygon / Line     │                    │
│   - State Transition (OUT -> IN)     │                    │
│   - Anti-Spam Debounce & Cooldown    │                    │
│   - Evidence Snapshot Capture        │                    │
└──────────────────────┬───────────────┘                    │
                       │                                    │
                       ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VISUAL OVERLAY & TELEMETRY GENERATOR                     │
│  - Bounding Boxes, Foot Points, Direction, Face Badges & Plate Tags         │
│  - Virtual Fence Overlay + ⚠ INTRUSION Highlighting                          │
│  - CCTV Command HUD Overlay                                                 │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (WebSocket Stream)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  REACT COMMAND CENTER DASHBOARD (FRONTEND)                  │
│  ├── Live CCTV Video Player & Interactive Fence Drawing Canvas              │
│  ├── Real-Time Security Intrusion Feed & Web Audio Alarm Synthesizer        │
│  ├── Active Tracking Panels (Vehicles, Persons, Virtual Fences)             │
│  ├── Live Telemetry Stats (Persons, Vehicles, ANPR Reads, Breaches, FPS)    │
│  └── Dedicated Views (ANPR Logs, Face Watchlist, Security Breaches History) │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start Guide

### Prerequisites
- **Python**: `3.10+` (Tested on Python 3.13)
- **Node.js**: `v18+` (Tested on Node v22)

---

### Running the Application

Since the frontend is pre-compiled in `frontend/dist`, you can run the entire platform with a single backend command:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server**:
   ```bash
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Open the Dashboard**:
   Navigate to [http://localhost:8000](http://localhost:8000) in your web browser.

---

### Development Mode (Optional)

To run the frontend dev server with Hot Module Replacement (HMR):

1. **Terminal 1 (Backend)**:
   ```bash
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Terminal 2 (Frontend)**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 📖 How to Use the Platform

1. **Live Surveillance**:
   - Select **Demo CCTV** (or switch to **Upload** mode for custom video).
   - Click **`START DETECTION`** to begin streaming.
2. **Virtual Fence & Perimeter Control**:
   - In the right sidebar, switch to the **`FENCES`** tab.
   - Click **`Draw on Video`**, choose **Polygon Zone** or **Line Crossing**, and click points directly on the video canvas.
   - Click **`Save Fence`**.
   - Violations trigger an immediate visual highlight, alert card, browser alarm sound, and evidence snapshot.
3. **Personnel & Vehicle Tracking**:
   - Switch between **`VEHICLES`** and **`PERSONS`** in the sidebar to inspect individual active tracks.
   - Click any track card to highlight that object on the video and open detailed telemetry.
4. **Historical Logs**:
   - **`ANPR Logs`**: Review recognized vehicle license plates.
   - **`Face Watchlist`**: Manage registered personnel and view face scan events.
   - **`Security Breaches`**: Inspect all recorded virtual fence intrusions and view saved evidence snapshots.

---

## 🔒 Privacy & Biometrics Notice

> **Security & Privacy**: Biometric facial identification and ANPR recognition are restricted to authorized surveillance monitoring. All embeddings and snapshots are stored locally and securely in the application asset directories.
