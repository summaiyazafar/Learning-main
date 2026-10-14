"""
pose_fall_detect.py
===================
Fall detection using YOLOv8-Pose body keypoints.

Instead of relying only on bounding-box detection, this script:
  1. Detects 17 body keypoints (COCO format) for every person in the frame
  2. Calculates body geometry:
       - Body angle (vertical = standing, horizontal = fallen)
       - Trunk tilt angle (shoulder-to-hip line)
       - Center-of-mass vertical position (normalized)
       - Body bounding-box aspect ratio (tall = standing, wide = fallen)
  3. Triggers alarm when geometry indicates a fallen posture

COCO Keypoint Index Map:
    0  = Nose         1  = Left Eye      2  = Right Eye
    3  = Left Ear     4  = Right Ear     5  = Left Shoulder
    6  = Right Shoulder   7 = Left Elbow  8 = Right Elbow
    9  = Left Wrist   10 = Right Wrist   11 = Left Hip
    12 = Right Hip    13 = Left Knee     14 = Right Knee
    15 = Left Ankle   16 = Right Ankle

Usage:
    python scripts/pose_fall_detect.py

    # To use a video file instead of webcam:
    Change SOURCE = 0  to  SOURCE = "videos/fall_0001.mp4"

Press 'q' to quit.
"""

import os
import math
import time
import threading
from collections import deque
from datetime import datetime

import cv2
from ultralytics import YOLO

try:
    import winsound
except ImportError:
    winsound = None

# =================== SETTINGS ===================
ROOT       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSE_MODEL = os.path.join(ROOT, "yolov8s-pose.pt")   # Downloaded automatically if missing
ALARM_WAV  = os.path.join(ROOT, "alarm.wav")
ALERTS_DIR = os.path.join(ROOT, "alerts")
SOURCE     = 0              # 0 = webcam | "videos/fall_0001.mp4" for video

# --- Fall detection thresholds ---
ANGLE_THRESHOLD  = 45.0   # Body angle below this (degrees from vertical) = FALLEN
ASPECT_THRESHOLD = 1.2    # Width/Height ratio above this = person is lying down
CONF_KEYPOINT    = 0.3    # Minimum keypoint confidence to use

# --- Alarm logic ---
WINDOW   = 8              # Sliding window (frames)
MIN_HITS = 5              # Min fall-frames to trigger alarm
COOLDOWN = 5              # Seconds between alarms
# ================================================

os.makedirs(ALERTS_DIR, exist_ok=True)

# COCO keypoint connections for drawing the skeleton
SKELETON = [
    (5, 6),    # Shoulders
    (5, 7),    # Left shoulder → Left elbow
    (7, 9),    # Left elbow → Left wrist
    (6, 8),    # Right shoulder → Right elbow
    (8, 10),   # Right elbow → Right wrist
    (5, 11),   # Left shoulder → Left hip
    (6, 12),   # Right shoulder → Right hip
    (11, 12),  # Hips
    (11, 13),  # Left hip → Left knee
    (13, 15),  # Left knee → Left ankle
    (12, 14),  # Right hip → Right knee
    (14, 16),  # Right knee → Right ankle
    (0, 5),    # Nose → Left shoulder
    (0, 6),    # Nose → Right shoulder
]


def angle_from_vertical(kps: list, idx_top: int, idx_bottom: int) -> float:
    """
    Calculate the angle (degrees) of the line between two keypoints
    relative to the vertical axis.
    0° = perfectly upright, 90° = horizontal (lying down).
    Returns None if either keypoint is not visible.
    """
    if kps[idx_top] is None or kps[idx_bottom] is None:
        return None
    x1, y1 = kps[idx_top]
    x2, y2 = kps[idx_bottom]
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return None
    # Angle from vertical: atan2 of (dx, dy)
    angle = math.degrees(math.atan2(abs(dx), abs(dy)))
    return angle   # 0° = vertical, 90° = horizontal


def extract_keypoints(result_kp, img_h: int, img_w: int):
    """
    Parse one person's keypoints from YOLOv8 result.
    Returns list of 17 items: each is (x, y) in pixel coords, or None if low confidence.
    """
    kps = []
    for i in range(17):
        x  = float(result_kp[i][0])
        y  = float(result_kp[i][1])
        cf = float(result_kp[i][2]) if result_kp.shape[1] >= 3 else 1.0
        if cf >= CONF_KEYPOINT and x > 0 and y > 0:
            kps.append((int(x), int(y)))
        else:
            kps.append(None)
    return kps


def analyze_pose(kps: list, box) -> dict:
    """
    Analyze keypoints and bounding box to determine if person has fallen.

    Returns a dict:
        is_fall   : bool
        angle     : float or None  (trunk angle from vertical)
        aspect    : float          (bounding box width / height)
        reason    : str            (human-readable explanation)
    """
    x1, y1, x2, y2 = box
    bw = x2 - x1
    bh = y2 - y1
    aspect = bw / bh if bh > 0 else 0

    # Trunk angle: shoulder midpoint → hip midpoint
    left_sh  = kps[5]
    right_sh = kps[6]
    left_hip = kps[11]
    right_hip = kps[12]

    angle = None
    if left_sh and right_sh and left_hip and right_hip:
        sh_mid  = ((left_sh[0]  + right_sh[0])  // 2,
                   (left_sh[1]  + right_sh[1])  // 2)
        hip_mid = ((left_hip[0] + right_hip[0]) // 2,
                   (left_hip[1] + right_hip[1]) // 2)
        kps_line = [sh_mid, hip_mid]
        angle = angle_from_vertical(kps_line, 0, 1)
    else:
        # Fallback: use ankle-to-shoulder if hips not visible
        if kps[0] and kps[15]:
            angle = angle_from_vertical(kps, 0, 15)
        elif kps[0] and kps[16]:
            angle = angle_from_vertical(kps, 0, 16)

    # Decision logic
    is_fall = False
    reason  = "Normal posture"

    if angle is not None and angle > ANGLE_THRESHOLD:
        is_fall = True
        reason  = f"Trunk angle {angle:.0f}° > {ANGLE_THRESHOLD}°"
    elif aspect > ASPECT_THRESHOLD:
        is_fall = True
        reason  = f"Aspect ratio {aspect:.2f} (lying wide)"
    elif angle is None and aspect > ASPECT_THRESHOLD:
        is_fall = True
        reason  = "No keypoints + wide bounding box"

    return {"is_fall": is_fall, "angle": angle, "aspect": aspect, "reason": reason}


def draw_skeleton(frame, kps: list, color_normal=(0, 255, 0), color_fall=(0, 0, 255), is_fall=False):
    """Draw keypoints and skeleton on the frame."""
    color = color_fall if is_fall else color_normal
    # Draw connections
    for (i, j) in SKELETON:
        if kps[i] and kps[j]:
            cv2.line(frame, kps[i], kps[j], color, 2)
    # Draw keypoints
    for kp in kps:
        if kp:
            cv2.circle(frame, kp, 4, color, -1)
            cv2.circle(frame, kp, 4, (255, 255, 255), 1)


def play_alarm():
    """Play alarm in background thread."""
    if winsound and os.path.exists(ALARM_WAV):
        winsound.PlaySound(ALARM_WAV, winsound.SND_FILENAME | winsound.SND_ASYNC)
    elif winsound:
        winsound.Beep(2000, 1500)
    else:
        print("\a", end="", flush=True)


def save_alert(frame, reason: str):
    """Save fall screenshot to alerts folder."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(ALERTS_DIR, f"pose_fall_{ts}.jpg")
    cv2.imwrite(path, frame)
    print(f"[ALERT] Screenshot saved: {path}  Reason: {reason}")


def main():
    print("=" * 58)
    print("  HOSPITAL FALL DETECTION — POSE-BASED")
    print("=" * 58)
    print(f"  Model  : {POSE_MODEL}")
    print(f"  Source : {SOURCE}")
    print(f"  Body angle threshold : {ANGLE_THRESHOLD}°")
    print(f"  Aspect ratio threshold: {ASPECT_THRESHOLD}")
    print("  Press 'q' to quit.")
    print("=" * 58)

    # Load pose model (downloads automatically if not found)
    model = YOLO(POSE_MODEL)

    cap = cv2.VideoCapture(SOURCE)
    if not cap.isOpened():
        raise SystemExit(f"[ERROR] Cannot open source: {SOURCE}")

    history    = deque(maxlen=WINDOW)
    last_alarm = 0.0
    prev_time  = time.time()

    while True:
        ok, frame = cap.read()
        if not ok:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        h, w = frame.shape[:2]

        # ---- Run pose inference ----
        results = model.predict(frame, conf=0.4, verbose=False)
        result  = results[0]

        any_fall  = False
        fall_reason = ""

        # ---- Process each detected person ----
        if result.keypoints is not None and result.boxes is not None:
            for p_idx in range(len(result.boxes)):
                box_tensor = result.boxes.xyxy[p_idx].cpu().numpy()
                x1, y1, x2, y2 = map(int, box_tensor)

                kp_data = result.keypoints.data[p_idx].cpu().numpy()
                kps = extract_keypoints(kp_data, h, w)

                info = analyze_pose(kps, (x1, y1, x2, y2))

                # Draw bounding box
                color = (0, 0, 255) if info["is_fall"] else (0, 200, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                # Draw skeleton
                draw_skeleton(frame, kps, is_fall=info["is_fall"])

                # Angle and aspect info
                label = f"Person {p_idx + 1}"
                if info["angle"] is not None:
                    label += f"  {info['angle']:.0f}deg"
                label += f"  AR:{info['aspect']:.2f}"
                cv2.putText(frame, label, (x1, max(y1 - 8, 12)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

                if info["is_fall"]:
                    any_fall    = True
                    fall_reason = info["reason"]

        # ---- Sliding window alarm ----
        history.append(any_fall)
        alarm_active = sum(history) >= MIN_HITS

        now = time.time()

        # ---- FPS ----
        fps = 1.0 / max(now - prev_time, 1e-6)
        prev_time = now

        # ---- Draw overlays ----
        if alarm_active:
            cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 255), 6)
            cv2.putText(frame, "ALARM: FALL DETECTED!",
                        (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 3)
            cv2.putText(frame, fall_reason,
                        (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 100, 255), 2)

            if now - last_alarm > COOLDOWN:
                last_alarm = now
                save_alert(frame, fall_reason)
                threading.Thread(target=play_alarm, daemon=True).start()
        else:
            cv2.putText(frame, "STATUS: NORMAL",
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 0), 2)

        cv2.putText(frame, f"FPS: {fps:.1f}  |  POSE MODE",
                    (10, h - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 1)

        cv2.imshow("Hospital Fall Detection — Pose Mode  (q = quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Pose detection stopped.")


if __name__ == "__main__":
    main()
