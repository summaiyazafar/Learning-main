import cv2
from ultralytics import YOLO
import time

MODEL_PATH = "best.pt"
SOURCE = 0  # 0 = webcam. CCTV ke liye: "rtsp://user:pass@camera_ip:554/stream"
CONF_THRESHOLD = 0.15

CLASS_COLORS = {
    "Improper Mask": (0, 255, 255),
    "Mask": (0, 255, 0),
    "No Mask": (0, 0, 255),
}

def main():
    model = YOLO(MODEL_PATH)
    cap = cv2.VideoCapture(SOURCE)
    if not cap.isOpened():
        print(f"ERROR: Cannot open source: {SOURCE}")
        return

    prev_time = 0
    print("Starting detection... Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Reconnecting...")
            cap.release()
            cap = cv2.VideoCapture(SOURCE)
            continue

        results = model.predict(frame, conf=CONF_THRESHOLD, verbose=False)
        result = results[0]
        counts = {"Improper Mask": 0, "Mask": 0, "No Mask": 0}

        for box in result.boxes:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            counts[cls_name] = counts.get(cls_name, 0) + 1
            color = CLASS_COLORS.get(cls_name, (255, 255, 255))
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{cls_name} {conf:.2f}", (x1, max(y1 - 10, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time else 0
        prev_time = curr_time

        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        for i, (cls_name, count) in enumerate(counts.items()):
            color = CLASS_COLORS.get(cls_name, (255, 255, 255))
            cv2.putText(frame, f"{cls_name}: {count}", (10, 60 + 30 * i),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow("Face Mask CCTV Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
