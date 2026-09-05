import cv2
import numpy as np
import hashlib
from typing import List, Dict, Any, Tuple, Optional, Set

def get_track_color(track_id: str) -> Tuple[int, int, int]:
    """
    Generates a consistent, visually distinct BGR color for a given track ID string.
    """
    hash_object = hashlib.md5(track_id.encode())
    hash_bytes = hash_object.digest()
    
    # Use distinct palettes for persons (P-) vs vehicles (V-)
    if track_id.startswith("V-"):
        # Distinct cyan/amber/blue/orange tones for vehicles
        b = int(hash_bytes[0] % 180 + 75)
        g = int(hash_bytes[1] % 180 + 75)
        r = int(hash_bytes[2] % 120 + 135)
    else:
        # Emerald/green tones for persons
        r = int(hash_bytes[0] % 150 + 50)
        g = int(hash_bytes[1] % 200 + 55)
        b = int(hash_bytes[2] % 150 + 50)
        
    return (b, g, r)  # BGR order for OpenCV


def draw_virtual_fences(
    frame: np.ndarray,
    fences: List[Any],
    active_fence_ids: Optional[Set[str]] = None
) -> np.ndarray:
    """
    Renders polygon and line-crossing virtual fences on the video frame.
    Highlights fences experiencing active intrusion in warning red/amber.
    """
    if not fences:
        return frame

    overlay_frame = frame.copy()
    h_img, w_img = overlay_frame.shape[:2]
    active_ids = active_fence_ids or set()
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Overlay layer for translucent polygon fills
    poly_mask = np.zeros_like(frame, dtype=np.uint8)
    has_poly_fill = False

    for fence in fences:
        # Support both Pydantic models and dicts
        fid = getattr(fence, "id", None) or fence.get("id", "FENCE")
        fname = getattr(fence, "name", None) or fence.get("name", "Zone")
        ftype = getattr(fence, "type", None) or fence.get("type", "polygon")
        fpoints = getattr(fence, "points", None) or fence.get("points", [])
        fseverity = getattr(fence, "severity", None) or fence.get("severity", "HIGH")
        fenabled = getattr(fence, "enabled", True) if hasattr(fence, "enabled") else fence.get("enabled", True)

        if not fenabled or len(fpoints) < 2:
            continue

        is_intruded = fid in active_ids

        # Colors
        if is_intruded:
            color = (0, 0, 255)       # Bright Red for Intrusion
            fill_color = (0, 0, 180)
            tag_text = f"🚨 INTRUSION | {fname}"
        elif fseverity == "CRITICAL":
            color = (0, 140, 255)     # Amber for Critical Zone
            fill_color = (0, 100, 200)
            tag_text = f"ZONE | {fname}"
        else:
            color = (255, 190, 0)     # Bright Cyan for Restricted Border Zone
            fill_color = (180, 120, 0)
            tag_text = f"ZONE | {fname}"

        # Scale normalized points
        pts = np.array([
            [int(pt[0] * w_img), int(pt[1] * h_img)]
            for pt in fpoints
        ], dtype=np.int32)

        if ftype == "polygon" and len(pts) >= 3:
            # Fill polygon on mask
            cv2.fillPoly(poly_mask, [pts], fill_color)
            has_poly_fill = True

            # Draw polygon outline
            cv2.polylines(overlay_frame, [pts], isClosed=True, color=color, thickness=2, lineType=cv2.LINE_AA)

            # Draw corner vertex markers
            for pt in pts:
                cv2.circle(overlay_frame, (pt[0], pt[1]), 4, color, -1)
                cv2.circle(overlay_frame, (pt[0], pt[1]), 6, (255, 255, 255), 1)

            # Draw label badge at the top-left-most vertex
            top_pt = min(pts, key=lambda p: (p[1], p[0]))
            tx, ty = top_pt[0], top_pt[1]

            sz, _ = cv2.getTextSize(tag_text, font, 0.40, 1)
            bx1 = max(4, tx - 2)
            by1 = max(4, ty - sz[1] - 8)
            bx2 = min(w_img - 4, bx1 + sz[0] + 12)
            by2 = by1 + sz[1] + 6

            cv2.rectangle(overlay_frame, (bx1, by1), (bx2, by2), (15, 18, 25), -1)
            cv2.rectangle(overlay_frame, (bx1, by1), (bx2, by2), color, 1)
            cv2.putText(overlay_frame, tag_text, (bx1 + 5, by2 - 4), font, 0.40, color, 1, cv2.LINE_AA)

        elif ftype == "line" and len(pts) >= 2:
            p1 = tuple(pts[0])
            p2 = tuple(pts[1])

            # Draw virtual fence line
            cv2.line(overlay_frame, p1, p2, color, 3 if is_intruded else 2, cv2.LINE_AA)
            cv2.circle(overlay_frame, p1, 5, color, -1)
            cv2.circle(overlay_frame, p2, 5, color, -1)

            # Midpoint label
            mx = (p1[0] + p2[0]) // 2
            my = (p1[1] + p2[1]) // 2
            line_tag = f"LINE | {fname}" if not is_intruded else f"🚨 LINE CROSSED | {fname}"
            sz, _ = cv2.getTextSize(line_tag, font, 0.38, 1)
            bx1 = max(4, mx - sz[0] // 2 - 6)
            by1 = max(4, my - sz[1] - 6)
            bx2 = min(w_img - 4, bx1 + sz[0] + 12)
            by2 = by1 + sz[1] + 6

            cv2.rectangle(overlay_frame, (bx1, by1), (bx2, by2), (15, 18, 25), -1)
            cv2.rectangle(overlay_frame, (bx1, by1), (bx2, by2), color, 1)
            cv2.putText(overlay_frame, line_tag, (bx1 + 5, by2 - 4), font, 0.38, color, 1, cv2.LINE_AA)

    # Blend translucent fills
    if has_poly_fill:
        cv2.addWeighted(poly_mask, 0.22, overlay_frame, 1.0, 0, overlay_frame)

    return overlay_frame


def draw_tracking_overlays(
    frame: np.ndarray,
    person_tracks: List[Dict[str, Any]],
    vehicle_tracks: List[Dict[str, Any]],
    selected_track_id: Optional[str] = None,
    active_intrusions_map: Optional[Dict[str, Set[str]]] = None
) -> np.ndarray:
    """
    Draws bounding boxes, track IDs, confidence, vehicle classification,
    license plates, movement trails, center points, and foot points on the video frame.
    Seamlessly adds intrusion tags when a person violates a virtual fence.
    """
    overlay_frame = frame.copy()
    h_img, w_img = overlay_frame.shape[:2]
    intrusions_map = active_intrusions_map or {}

    # 1. Draw Person Tracks
    for track in person_tracks:
        track_id = track["track_id"]
        bbox = track["bbox"]
        conf = track["confidence"]
        direction = track.get("direction", "STATIONARY")
        history = track.get("history", [])
        foot_point = track.get("foot_point", None)
        center = track.get("center", None)

        x1, y1, x2, y2 = map(int, bbox)
        is_intruder = track_id in intrusions_map and len(intrusions_map[track_id]) > 0
        
        # Color: If intruder, emphasize with red accent while keeping base color distinguishable
        color = (0, 0, 255) if is_intruder else get_track_color(track_id)
        
        is_selected = (selected_track_id == track_id)
        thickness = 3 if (is_selected or is_intruder) else 2

        # Bounding box
        cv2.rectangle(overlay_frame, (x1, y1), (x2, y2), color, thickness)
        if is_selected:
            cv2.rectangle(overlay_frame, (x1 - 2, y1 - 2), (x2 + 2, y2 + 2), (0, 255, 255), 2)

        # Facial Recognition Info
        face_info = track.get("face")
        face_status = face_info.get("status") if face_info else "none"
        face_bbox = face_info.get("face_bbox") if face_info else None

        # Draw Face Box if detected
        if face_bbox:
            fx1, fy1, fx2, fy2 = map(int, face_bbox)
            if face_status == "recognized":
                f_color = (60, 220, 90)    # Emerald Green
            elif face_status == "unknown":
                f_color = (0, 140, 255)    # Amber / Warning
            else:
                f_color = (255, 200, 50)   # Cyan searching

            cv2.rectangle(overlay_frame, (fx1, fy1), (fx2, fy2), f_color, 1)
            # Corner accents
            c_len = max(3, min(8, (fx2 - fx1) // 4))
            cv2.line(overlay_frame, (fx1, fy1), (fx1 + c_len, fy1), f_color, 2)
            cv2.line(overlay_frame, (fx1, fy1), (fx1, fy1 + c_len), f_color, 2)
            cv2.line(overlay_frame, (fx2, fy1), (fx2 - c_len, fy1), f_color, 2)
            cv2.line(overlay_frame, (fx2, fy1), (fx2, fy1 + c_len), f_color, 2)
            cv2.line(overlay_frame, (fx1, fy2), (fx1 + c_len, fy2), f_color, 2)
            cv2.line(overlay_frame, (fx1, fy2), (fx1, fy2 - c_len), f_color, 2)
            cv2.line(overlay_frame, (fx2, fy2), (fx2 - c_len, fy2), f_color, 2)
            cv2.line(overlay_frame, (fx2, fy2), (fx2, fy2 - c_len), f_color, 2)

        # Label Header
        font = cv2.FONT_HERSHEY_SIMPLEX
        label_id = f"{track_id}"
        
        if face_info and face_status == "recognized":
            label_id = f"{track_id} | {face_info['name']}"
            label_conf = f"VERIFIED {int(face_info.get('match_score', 0) * 100)}%"
            header_bg = (30, 100, 40)  # Dark Emerald
        elif face_info and face_status == "unknown":
            label_id = f"{track_id} | UNKNOWN"
            label_conf = f"UNREGISTERED ({int(conf * 100)}%)"
            header_bg = (20, 60, 140)  # Dark Amber/Alert
        else:
            label_conf = f"PERSON {int(conf * 100)}%"
            header_bg = color

        # Intrusion Sub-badge if active
        intrusion_tag = "⚠ INTRUSION | HIGH" if is_intruder else None

        text_size_id, _ = cv2.getTextSize(label_id, font, 0.42, 1)
        text_size_conf, _ = cv2.getTextSize(label_conf, font, 0.38, 1)
        text_size_intr = cv2.getTextSize(intrusion_tag, font, 0.38, 1)[0] if intrusion_tag else (0, 0)
        
        header_h = text_size_id[1] + text_size_conf[1] + 10 + (text_size_intr[1] + 6 if intrusion_tag else 0)
        header_w = max(text_size_id[0], text_size_conf[0], text_size_intr[0]) + 12

        header_y1 = max(0, y1 - header_h - 2)
        header_y2 = max(header_h + 2, y1)
        cv2.rectangle(overlay_frame, (x1, header_y1), (x1 + header_w, header_y2), header_bg if not is_intruder else (15, 15, 140), -1)
        if is_intruder:
            cv2.rectangle(overlay_frame, (x1, header_y1), (x1 + header_w, header_y2), (0, 0, 255), 1)

        curr_y = header_y1 + text_size_id[1] + 2
        cv2.putText(overlay_frame, label_id, (x1 + 4, curr_y), font, 0.42, (255, 255, 255), 2, cv2.LINE_AA)
        
        curr_y += text_size_conf[1] + 4
        cv2.putText(overlay_frame, label_conf, (x1 + 4, curr_y), font, 0.38, (220, 220, 220), 1, cv2.LINE_AA)

        if intrusion_tag:
            curr_y += text_size_intr[1] + 4
            cv2.putText(overlay_frame, intrusion_tag, (x1 + 4, curr_y), font, 0.38, (0, 255, 255), 1, cv2.LINE_AA)

        # Direction text
        dir_text = f"PERSON | {direction}"
        cv2.putText(overlay_frame, dir_text, (x1 + 4, min(y2 - 6, h_img - 6)), font, 0.40, color, 1, cv2.LINE_AA)

        # Center & Foot points
        if center:
            cv2.circle(overlay_frame, (int(center[0]), int(center[1])), 3, (0, 255, 255), -1)
        if foot_point:
            cv2.circle(overlay_frame, (int(foot_point[0]), int(foot_point[1])), 4, (0, 0, 255) if is_intruder else color, -1)

        # Movement Trail
        if history and len(history) > 1:
            points = [tuple(map(int, pt)) for pt in history]
            for i in range(1, len(points)):
                pt1, pt2 = points[i - 1], points[i]
                alpha = (i / len(points))
                trail_color = tuple(int(c * alpha) for c in color)
                cv2.line(overlay_frame, pt1, pt2, trail_color, max(1, int(3 * alpha)), cv2.LINE_AA)

    # 2. Draw Vehicle Tracks & ANPR Overlays
    for track in vehicle_tracks:
        track_id = track["track_id"]
        v_type = track.get("vehicle_type", "CAR")
        bbox = track["bbox"]
        conf = track["confidence"]
        direction = track.get("direction", "STATIONARY")
        history = track.get("history", [])
        plate_info = track.get("plate", {})
        plate_num = plate_info.get("plate_number")
        plate_conf = plate_info.get("ocr_confidence", 0.0)
        plate_status = plate_info.get("status", "Not Detected")
        plate_bbox = plate_info.get("plate_bbox")

        x1, y1, x2, y2 = map(int, bbox)
        color = get_track_color(track_id)
        
        is_selected = (selected_track_id == track_id)
        thickness = 3 if is_selected else 2

        # 1. Draw Vehicle Bounding Box
        cv2.rectangle(overlay_frame, (x1, y1), (x2, y2), color, thickness)
        if is_selected:
            cv2.rectangle(overlay_frame, (x1 - 2, y1 - 2), (x2 + 2, y2 + 2), (0, 255, 255), 2)

        # 2. Draw Vehicle Header Box (V-001 | CAR | 94% + Plate Info)
        font = cv2.FONT_HERSHEY_SIMPLEX
        label_line1 = f"{track_id} | {v_type} | {int(conf * 100)}%"
        
        if plate_num:
            label_line2 = f"Plate: {plate_num} | {int(plate_conf * 100)}%"
        elif plate_status == "Recognizing":
            label_line2 = "Plate: Recognizing..."
        elif plate_status == "Uncertain":
            label_line2 = "Plate: Uncertain"
        else:
            label_line2 = "Plate: Not Detected"

        sz1, _ = cv2.getTextSize(label_line1, font, 0.48, 1)
        sz2, _ = cv2.getTextSize(label_line2, font, 0.42, 1)
        header_h = sz1[1] + sz2[1] + 12
        header_w = max(sz1[0], sz2[0]) + 14

        header_y1 = max(0, y1 - header_h - 3)
        header_y2 = max(header_h + 3, y1)
        cv2.rectangle(overlay_frame, (x1, header_y1), (x1 + header_w, header_y2), (20, 24, 33), -1)
        cv2.rectangle(overlay_frame, (x1, header_y1), (x1 + header_w, header_y2), color, 1)

        # Line 1: Track ID & Class
        cv2.putText(overlay_frame, label_line1, (x1 + 4, header_y1 + sz1[1] + 3), font, 0.48, color, 2, cv2.LINE_AA)
        
        # Line 2: Plate Info
        plate_text_color = (0, 255, 255) if plate_num else (180, 180, 180)
        cv2.putText(overlay_frame, label_line2, (x1 + 4, header_y1 + sz1[1] + sz2[1] + 7), font, 0.42, plate_text_color, 1, cv2.LINE_AA)

        # Direction text on bottom edge of vehicle box
        dir_text = f"DIR: {direction}"
        cv2.putText(overlay_frame, dir_text, (x1 + 4, min(y2 - 6, h_img - 6)), font, 0.40, color, 1, cv2.LINE_AA)

        # 3. Draw Dedicated License Plate Bounding Box (if detected)
        if plate_bbox:
            px1, py1, px2, py2 = map(int, plate_bbox)
            px1, py1 = max(0, px1), max(0, py1)
            px2, py2 = min(w_img, px2), min(h_img, py2)
            
            # Plate rectangle in bright yellow/cyan
            plate_box_color = (0, 255, 255) if plate_num else (0, 200, 255)
            cv2.rectangle(overlay_frame, (px1, py1), (px2, py2), plate_box_color, 2)
            
            # Plate mini-badge above plate
            if plate_num:
                tag = f"{plate_num} {int(plate_conf * 100)}%"
                tag_sz, _ = cv2.getTextSize(tag, font, 0.38, 1)
                tag_y1 = max(0, py1 - tag_sz[1] - 4)
                cv2.rectangle(overlay_frame, (px1, tag_y1), (px1 + tag_sz[0] + 6, py1), (0, 0, 0), -1)
                cv2.putText(overlay_frame, tag, (px1 + 3, py1 - 3), font, 0.38, (0, 255, 255), 1, cv2.LINE_AA)

        # 4. Movement Trail
        if history and len(history) > 1:
            points = [tuple(map(int, pt)) for pt in history]
            for i in range(1, len(points)):
                pt1, pt2 = points[i - 1], points[i]
                alpha = (i / len(points))
                trail_color = tuple(int(c * alpha) for c in color)
                cv2.line(overlay_frame, pt1, pt2, trail_color, max(1, int(3 * alpha)), cv2.LINE_AA)

    return overlay_frame


def draw_cctv_hud(
    frame: np.ndarray,
    camera_name: str,
    location: str,
    timestamp: str,
    current_persons: int,
    current_vehicles: int,
    anpr_reads: int,
    fps: float,
    active_intrusions_count: int = 0
) -> np.ndarray:
    """
    Draws a command center CCTV HUD overlay on the frame.
    """
    hud_frame = frame.copy()
    h, w, _ = hud_frame.shape
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Top left: CCTV status badge & details
    cv2.circle(hud_frame, (25, 25), 6, (0, 0, 255), -1)
    cv2.putText(hud_frame, "LIVE", (38, 30), font, 0.55, (0, 0, 255), 2, cv2.LINE_AA)

    cam_info = f"CAM: {camera_name}  |  LOC: {location}  |  TIME: {timestamp}"
    cv2.putText(hud_frame, cam_info, (100, 30), font, 0.45, (220, 220, 220), 1, cv2.LINE_AA)

    # Top right: AI ANALYTICS ACTIVE badge
    ai_badge = "AI ANALYTICS ACTIVE (HUMAN + VEHICLE + FENCE)"
    sz_badge, _ = cv2.getTextSize(ai_badge, font, 0.38, 1)
    cv2.rectangle(hud_frame, (w - sz_badge[0] - 25, 14), (w - 15, 38), (15, 35, 25), -1)
    cv2.rectangle(hud_frame, (w - sz_badge[0] - 25, 14), (w - 15, 38), (0, 255, 128), 1)
    cv2.putText(hud_frame, ai_badge, (w - sz_badge[0] - 20, 30), font, 0.38, (0, 255, 128), 1, cv2.LINE_AA)

    # Corner brackets overlay (Security camera vibe)
    bracket_len = min(w, h) // 15
    b_color = (0, 0, 255) if active_intrusions_count > 0 else (0, 255, 0)
    # Top-Left
    cv2.line(hud_frame, (10, 10), (10 + bracket_len, 10), b_color, 2)
    cv2.line(hud_frame, (10, 10), (10, 10 + bracket_len), b_color, 2)
    # Top-Right
    cv2.line(hud_frame, (w - 10, 10), (w - 10 - bracket_len, 10), b_color, 2)
    cv2.line(hud_frame, (w - 10, 10), (w - 10, 10 + bracket_len), b_color, 2)
    # Bottom-Left
    cv2.line(hud_frame, (10, h - 10), (10 + bracket_len, h - 10), b_color, 2)
    cv2.line(hud_frame, (10, h - 10), (10, h - 10 - bracket_len), b_color, 2)
    # Bottom-Right
    cv2.line(hud_frame, (w - 10, h - 10), (w - 10 - bracket_len, h - 10), b_color, 2)
    cv2.line(hud_frame, (w - 10, h - 10), (w - 10, 10 + bracket_len), b_color, 2)

    # Bottom bar overlay
    bottom_bar_h = 32
    cv2.rectangle(hud_frame, (0, h - bottom_bar_h), (w, h), (10, 15, 25), -1)
    cv2.line(hud_frame, (0, h - bottom_bar_h), (w, h - bottom_bar_h), (30, 45, 65), 1)
    
    intr_str = f"   INTRUSIONS: {active_intrusions_count:02d}" if active_intrusions_count > 0 else ""
    stats_str = f"PERSONS: {current_persons:02d}   VEHICLES: {current_vehicles:02d}   ANPR: {anpr_reads:02d}{intr_str}   FPS: {fps:.1f}   SYSTEM: IBVAP-V2.1"
    text_color = (0, 100, 255) if active_intrusions_count > 0 else (0, 255, 160)
    cv2.putText(hud_frame, stats_str, (15, h - 10), font, 0.45, text_color, 1, cv2.LINE_AA)

    return hud_frame
