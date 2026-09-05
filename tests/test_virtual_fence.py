import pytest
import numpy as np
import time
from pathlib import Path
from backend.models.fence_models import VirtualFence, FenceCreateRequest, FenceUpdateRequest
from backend.services.virtual_fence import VirtualFenceManager, segments_intersect

@pytest.fixture
def fence_manager(tmp_path):
    config_file = tmp_path / "test_fences.json"
    manager = VirtualFenceManager(config_path=config_file)
    # Clear any seeded defaults for fresh test isolation
    manager.fences.clear()
    manager.reset_session()
    return manager

def test_point_in_polygon_and_boundary(fence_manager):
    # Polygon covering 20% to 80% in both X and Y
    fence = VirtualFence(
        id="FENCE-TEST-01",
        name="Test Zone",
        type="polygon",
        points=[[0.2, 0.2], [0.8, 0.2], [0.8, 0.8], [0.2, 0.8]],
        camera_id="CAM-01",
        enabled=True,
        severity="HIGH"
    )
    fence_manager.fences[fence.id] = fence
    width, height = 1000, 1000

    # Inside point (500, 500)
    assert fence_manager.is_point_in_polygon((500, 500), fence, width, height) is True
    # Outside point (100, 100)
    assert fence_manager.is_point_in_polygon((100, 100), fence, width, height) is False
    # Boundary point (200, 500)
    assert fence_manager.is_point_in_polygon((200, 500), fence, width, height) is True
    # Far outside point (900, 900)
    assert fence_manager.is_point_in_polygon((900, 900), fence, width, height) is False

def test_normalized_coordinates_scaling(fence_manager):
    fence = VirtualFence(
        id="FENCE-TEST-01",
        name="Test Zone",
        type="polygon",
        points=[[0.5, 0.5], [1.0, 0.5], [1.0, 1.0], [0.5, 1.0]],
        camera_id="CAM-01",
        enabled=True
    )
    # Test at 640x480 resolution
    assert fence_manager.is_point_in_polygon((400, 300), fence, 640, 480) is True
    assert fence_manager.is_point_in_polygon((200, 200), fence, 640, 480) is False

    # Test at 1920x1080 resolution
    assert fence_manager.is_point_in_polygon((1200, 800), fence, 1920, 1080) is True
    assert fence_manager.is_point_in_polygon((500, 400), fence, 1920, 1080) is False

def test_line_crossing_detection(fence_manager):
    fence = VirtualFence(
        id="FENCE-TEST-LINE",
        name="Border Line",
        type="line",
        points=[[0.2, 0.5], [0.8, 0.5]], # Line from (200, 500) to (800, 500)
        camera_id="CAM-01",
        enabled=True
    )
    fence_manager.fences[fence.id] = fence
    w, h = 1000, 1000

    # Crosses from top (500, 400) to bottom (500, 600)
    assert fence_manager.has_crossed_line((500, 400), (500, 600), fence, w, h) is True
    # Moves parallel above line from (300, 400) to (600, 400)
    assert fence_manager.has_crossed_line((300, 400), (600, 400), fence, w, h) is False
    # Stationary / no movement
    assert fence_manager.has_crossed_line((500, 500), (500, 500), fence, w, h) is False

def test_person_state_transition_and_no_alert_spam(fence_manager):
    fence = VirtualFence(
        id="FENCE-001",
        name="Restricted Zone",
        type="polygon",
        points=[[0.2, 0.2], [0.8, 0.2], [0.8, 0.8], [0.2, 0.8]],
        camera_id="CAM-01",
        enabled=True
    )
    fence_manager.fences[fence.id] = fence
    dummy_frame = np.zeros((1000, 1000, 3), dtype=np.uint8)

    # Frame 1: Person P-001 OUTSIDE (100, 100)
    p1 = {
        "track_id": "P-001",
        "bbox": [80, 50, 120, 100],
        "foot_point": [100.0, 100.0],
        "confidence": 0.90,
        "direction": "SOUTH",
        "face": {"status": "unknown"}
    }
    active_intrusions, event = fence_manager.process_frame(dummy_frame, [p1], "CAM-01", frame_number=1)
    assert len(active_intrusions) == 0
    assert event is None

    # Frame 2: Person P-001 ENTERS polygon (500, 500) => ALERT TRIGGERED!
    p1["foot_point"] = [500.0, 500.0]
    active_intrusions, event = fence_manager.process_frame(dummy_frame, [p1], "CAM-01", frame_number=2)
    assert len(active_intrusions) == 1
    assert event is not None
    assert event.person_track_id == "P-001"
    assert event.identity == "UNKNOWN"
    assert event.fence_id == "FENCE-001"

    # Frame 3: Person P-001 REMAINS INSIDE (510, 510) => NO DUPLICATE ALERT!
    p1["foot_point"] = [510.0, 510.0]
    active_intrusions, event2 = fence_manager.process_frame(dummy_frame, [p1], "CAM-01", frame_number=3)
    assert len(active_intrusions) == 1
    assert event2 is None  # No spam!

    # Frame 4: Person P-001 EXITS polygon (100, 100)
    p1["foot_point"] = [100.0, 100.0]
    active_intrusions, event3 = fence_manager.process_frame(dummy_frame, [p1], "CAM-01", frame_number=4)
    assert len(active_intrusions) == 0
    assert event3 is None

    # Frame 5: Person P-001 RE-ENTERS polygon (520, 520) after cooldown
    # Force cooldown expiry
    fence_manager.last_alert_times[("P-001", "FENCE-001")] -= 10.0
    p1["foot_point"] = [520.0, 520.0]
    active_intrusions, event4 = fence_manager.process_frame(dummy_frame, [p1], "CAM-01", frame_number=5)
    assert len(active_intrusions) == 1
    assert event4 is not None
    assert event4.person_track_id == "P-001"

def test_multiple_people_and_known_identities(fence_manager):
    fence = VirtualFence(
        id="FENCE-001",
        name="Perimeter",
        type="polygon",
        points=[[0.2, 0.2], [0.8, 0.2], [0.8, 0.8], [0.2, 0.8]],
        camera_id="CAM-01",
        enabled=True
    )
    fence_manager.fences[fence.id] = fence
    dummy_frame = np.zeros((1000, 1000, 3), dtype=np.uint8)

    p1 = {
        "track_id": "P-001",
        "bbox": [480, 400, 520, 500],
        "foot_point": [500.0, 500.0],
        "confidence": 0.95,
        "face": {"status": "recognized", "name": "Major Vikram Batra"}
    }
    p2 = {
        "track_id": "P-002",
        "bbox": [50, 50, 90, 100],
        "foot_point": [70.0, 100.0], # Outside
        "confidence": 0.88,
        "face": {"status": "unknown"}
    }
    p3 = {
        "track_id": "P-003",
        "bbox": [580, 500, 620, 600],
        "foot_point": [600.0, 600.0], # Inside
        "confidence": 0.92,
        "face": {"status": "unknown"}
    }

    active_intrusions, event = fence_manager.process_frame(dummy_frame, [p1, p2, p3], "CAM-01", frame_number=1)
    
    # Both P-001 and P-003 should be active intruders
    intruder_ids = {item["person_id"] for item in active_intrusions}
    assert "P-001" in intruder_ids
    assert "P-003" in intruder_ids
    assert "P-002" not in intruder_ids

    # Check that identity from FaceService was preserved
    p1_info = next(item for item in active_intrusions if item["person_id"] == "P-001")
    assert p1_info["identity"] == "Major Vikram Batra"

def test_camera_segregation(fence_manager):
    fence_cam1 = VirtualFence(
        id="FENCE-CAM1",
        name="Cam 1 Zone",
        type="polygon",
        points=[[0.1, 0.1], [0.9, 0.1], [0.9, 0.9], [0.1, 0.9]],
        camera_id="CAM-01",
        enabled=True
    )
    fence_cam2 = VirtualFence(
        id="FENCE-CAM2",
        name="Cam 2 Zone",
        type="polygon",
        points=[[0.1, 0.1], [0.9, 0.1], [0.9, 0.9], [0.1, 0.9]],
        camera_id="CAM-02",
        enabled=True
    )
    fence_manager.fences[fence_cam1.id] = fence_cam1
    fence_manager.fences[fence_cam2.id] = fence_cam2

    # Querying CAM-01 should not return CAM-02 fences
    assert len(fence_manager.get_fences("CAM-01")) == 1
    assert fence_manager.get_fences("CAM-01")[0].id == "FENCE-CAM1"

    assert len(fence_manager.get_fences("CAM-02")) == 1
    assert fence_manager.get_fences("CAM-02")[0].id == "FENCE-CAM2"
