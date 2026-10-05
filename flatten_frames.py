"""
flatten_frames.py
frames/ folder ke saare subfolders se images ko images/ mein flat copy karta hai.
LabelImg flat folder prefer karta hai.
"""

import os
import shutil

# ================== SETTINGS ==================
SOURCE = "frames"       # Frames yahan hain (subfolders ke saath)
DEST = "images"         # Flat images yahan banengi
# ===============================================

def flatten():
    os.makedirs(DEST, exist_ok=True)
    
    count = 0
    for root, dirs, files in os.walk(SOURCE):
        for f in files:
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                src = os.path.join(root, f)
                dst = os.path.join(DEST, f)
                
                # Agar same naam ki file already hai, toh skip
                if os.path.exists(dst):
                    continue
                
                shutil.copy2(src, dst)
                count += 1
    
    print(f"[DONE] {count} images copied to {DEST}/")
    print(f"[NEXT] Ab labelImg chalao aur images/ ko label karo.")

if __name__ == "__main__":
    flatten()