"""
flatten_frames.py
=================
Copies all images from nested sub-folders inside frames/ into the flat images/ folder.
This is required because the custom label_tool.py expects all images in a single folder.

Usage:
    python scripts/flatten_frames.py

Flow:
    frames/<video>/<video>_00001.jpg  -->  images/<video>_00001.jpg
"""

import os
import shutil

# =================== SETTINGS ===================
ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "frames")   # Source: nested frame folders
DEST   = os.path.join(ROOT, "images")  # Destination: flat images folder
# ================================================


def flatten():
    """Walk the frames/ directory and copy all images into images/ (flat)."""
    if not os.path.exists(SOURCE):
        print(f"[ERROR] Frames folder not found: {SOURCE}")
        print("[FIX]  Run 'python scripts/extract_frames.py' first.")
        return

    os.makedirs(DEST, exist_ok=True)

    count    = 0
    skipped  = 0

    for root, dirs, files in os.walk(SOURCE):
        for f in sorted(files):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                src = os.path.join(root, f)
                dst = os.path.join(DEST, f)

                if os.path.exists(dst):
                    skipped += 1
                    continue

                shutil.copy2(src, dst)
                count += 1

    print(f"[DONE] {count} image(s) copied to: {DEST}/")
    if skipped:
        print(f"[INFO] {skipped} image(s) already existed and were skipped.")
    print("[NEXT] Run 'python scripts/label_tool.py' to label the images.")


if __name__ == "__main__":
    flatten()