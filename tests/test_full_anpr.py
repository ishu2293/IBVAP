import sys
sys.path.insert(0, '.')
from backend.config import DEMO_CCTV_DIR
from backend.services.video_processor import VideoProcessor

def test_full_anpr():
    print("Testing 50 frames of CAM-01 with ANPR and Vehicle Tracking...")
    processor = VideoProcessor()
    demo_video_path = DEMO_CCTV_DIR / "border_demo_01.mp4"
    gen = processor.process_video_stream(
        video_path=demo_video_path,
        mode="demo",
        camera_info={"id": "CAM-01", "name": "Longewala Desert Outpost", "location": "Rajasthan"}
    )
    
    for processed_frame, telemetry in gen:
        fn = telemetry["frame_number"]
        v_count = telemetry["current_vehicles"]
        p_count = telemetry["current_persons"]
        anpr_total = telemetry["total_anpr_reads"]
        v_tracks = telemetry["vehicle_tracks"]
        
        plates = [f"{v['track_id']}:{v['plate']['plate_number'] or v['plate']['status']}" for v in v_tracks]
        
        if fn % 10 == 0 or fn <= 5:
            print(f"Frame #{fn:02d} | Persons: {p_count} | Vehicles: {v_count} | ANPR Reads: {anpr_total} | Plates: {plates}")
            
        if fn >= 50:
            break

if __name__ == "__main__":
    test_full_anpr()
