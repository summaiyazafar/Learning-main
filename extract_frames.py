"""
extract_frames.py
Videos se frames extract karta hai.
Har video ka alag folder banata hai frames/ mein.
"""

import cv2
import os

# ================== SETTINGS ==================
VIDEOS_FOLDER = "videos"       # Saari videos yahan hain
OUTPUT_BASE = "frames"         # Frames yahan save honge
FRAMES_PER_SECOND = 5          # 1 second mein kitne frames (5 = good balance)
# ===============================================

def extract_all_videos():
    if not os.path.exists(VIDEOS_FOLDER):
        print(f"[ERROR] Videos folder nahi mila: {VIDEOS_FOLDER}")
        return
    
    # Saari video files dhoondo
    video_files = []
    for f in os.listdir(VIDEOS_FOLDER):
        if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
            video_files.append(f)
    
    if not video_files:
        print(f"[ERROR] {VIDEOS_FOLDER}/ mein koi video nahi mili!")
        return
    
    print(f"[INFO] {len(video_files)} videos mili. Extraction shuru...")
    
    for video_file in video_files:
        video_path = os.path.join(VIDEOS_FOLDER, video_file)
        name = os.path.splitext(video_file)[0]
        out_folder = os.path.join(OUTPUT_BASE, name)
        os.makedirs(out_folder, exist_ok=True)
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"[SKIP] Video nahi khuli: {video_file}")
            continue
        
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step = max(1, round(fps / FRAMES_PER_SECOND))
        
        i = 0
        saved = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if i % step == 0:
                saved += 1
                out_path = os.path.join(out_folder, f"{name}_{saved:05d}.jpg")
                cv2.imwrite(out_path, frame)
            i += 1
        
        cap.release()
        print(f"[OK] {video_file} -> {saved} frames saved in {out_folder}/")
    
    print(f"\n[DONE] Saare frames extract ho gaye!")
    print(f"[NEXT] Ab 'flatten_frames.py' chalao ya manually images/ mein copy karo.")

if __name__ == "__main__":
    extract_all_videos()