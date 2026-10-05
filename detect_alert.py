import cv2
import time
import winsound
import os
from collections import deque
from ultralytics import YOLO

# ================== SETTINGS ==================
# SOURCE = 0                  # 0 = Webcam
SOURCE = "videos/fall_0001.mp4"   # Video file ka path
WEIGHTS = "runs/detect/fall_detector/weights/best.pt"  # Apna best.pt ka sahi path dein
CONF = 0.5                  # Confidence threshold
WINDOW = 10                 # Kitne frames ka history rakhein
MIN_HITS = 6                # Kitne frames mein fall ho to alarm bajaye
COOLDOWN = 5                # Alarm ke beech seconds (spam na ho)
# ===============================================

# Check karein ke weights file exist karti hai
if not os.path.exists(WEIGHTS):
    print(f"[ERROR] Weights file nahi mili: {WEIGHTS}")
    print("Apna best.pt ka sahi path dein.")
    exit()

# Model load karein
model = YOLO(WEIGHTS)
print(f"[INFO] Model load ho gaya: {WEIGHTS}")
print(f"[INFO] Classes: {model.names}")

# Video source open karein
cap = cv2.VideoCapture(SOURCE)
if not cap.isOpened():
    print(f"[ERROR] Video source nahi khula: {SOURCE}")
    exit()

# History aur alarm ke liye variables
hist = deque(maxlen=WINDOW)
last_alert = 0
os.makedirs("alerts", exist_ok=True)

# FPS calculate karne ke liye
prev_time = time.time()

print("[INFO] Detection shuru... 'q' dabayein band karne ke liye.")

while True:
    ok, frame = cap.read()
    if not ok:
        print("[INFO] Video khatam ya frame nahi mila.")
        break

    # YOLO prediction
    r = model.predict(frame, conf=CONF, verbose=False)[0]

    # Fall classes detect karein
    names = [model.names[int(c)] for c in r.boxes.cls]
    fall_names = [n for n in names if "fall" in n.lower()]

    # History update karein
    hist.append(len(fall_names) > 0)

    # Annotated frame (bounding boxes ke sath)
    out = r.plot()

    # FPS calculate karein
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
    prev_time = curr_time
    cv2.putText(out, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Agar window mein MIN_HITS se zyada fall detect ho
    if sum(hist) >= MIN_HITS:
        kind = fall_names[0] if fall_names else "fall"

        # ALARM text screen par
        cv2.putText(out, f"ALARM: {kind.upper()} DETECTED!", (30, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

        # Cooldown ke baad alarm bajayein
        if time.time() - last_alert > COOLDOWN:
            last_alert = time.time()

            # Alert image save karein
            alert_path = f"alerts/fall_{int(time.time())}.jpg"
            cv2.imwrite(alert_path, out)
            print(f"[ALARM] {kind} detected! Image saved: {alert_path}")

            # Beep bajayein (Windows only)
            try:
                winsound.Beep(2000, 1500)
            except Exception as e:
                print(f"[WARN] Beep nahi baj saka: {e}")

    # Screen par dikhayein (resize karke)
    cv2.imshow("Fall Detection", cv2.resize(out, None, fx=0.7, fy=0.7))

    # 'q' dabane par band karein
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("[INFO] Detection band ho gayi.")