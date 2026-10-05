"""
label_helper.py
================
Yeh script train.py ka replacement hai.
Training NAHI karti — sirf LabelImg ke liye setup karti hai.

Kaam:
1. Check karta hai ke saare folders exist karte hain
2. Check karta hai ke classes.txt mojood hai
3. Check karta hai ke images/ mein images hain
4. Labels/ folder ready karta hai
5. LabelImg automatically open karta hai
"""

import os
import sys
import subprocess
import platform

# ================== SETTINGS ==================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(PROJECT_ROOT, "images")
LABELS_DIR = os.path.join(PROJECT_ROOT, "labels")
CLASSES_FILE = os.path.join(PROJECT_ROOT, "classes.txt")
FRAMES_DIR = os.path.join(PROJECT_ROOT, "frames")
# ===============================================


def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def check_and_create_folders():
    """Zaroori folders check karein aur bana dein."""
    print_header("STEP 1: Folders Check")
    
    folders = {
        "Images": IMAGES_DIR,
        "Labels": LABELS_DIR,
        "Frames": FRAMES_DIR,
    }
    
    for name, path in folders.items():
        if os.path.exists(path):
            print(f"  [OK]   {name}: {path}")
        else:
            os.makedirs(path, exist_ok=True)
            print(f"  [NEW]  {name} banaya: {path}")


def check_classes_file():
    """classes.txt check karein."""
    print_header("STEP 2: Classes Check")
    
    if not os.path.exists(CLASSES_FILE):
        print(f"  [ERROR] classes.txt nahi mila: {CLASSES_FILE}")
        print(f"  [FIX]   Ek file banayein 'classes.txt' aur yeh likhein:")
        print(f"          normal")
        print(f"          straight_fall")
        print(f"          left_fall")
        print(f"          right_fall")
        print(f"          back_fall")
        return False
    
    with open(CLASSES_FILE, 'r', encoding='utf-8') as f:
        classes = [line.strip() for line in f if line.strip()]
    
    print(f"  [OK]   Classes file: {CLASSES_FILE}")
    print(f"  [INFO] {len(classes)} classes mili:")
    for i, c in enumerate(classes):
        print(f"         ID {i}: {c}")
    
    return True


def check_images():
    """images/ folder mein images hain ya nahi."""
    print_header("STEP 3: Images Check")
    
    if not os.path.exists(IMAGES_DIR):
        print(f"  [ERROR] images/ folder nahi mila!")
        return False
    
    images = [f for f in os.listdir(IMAGES_DIR) 
              if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))]
    
    if not images:
        print(f"  [WARN] images/ folder khaali hai!")
        print(f"  [FIX]  Pehle 'extract_frames.py' chalao")
        print(f"         Phir 'flatten_frames.py' chalao")
        return False
    
    print(f"  [OK]   {len(images)} images mili images/ mein")
    
    # Labels ka status check
    if os.path.exists(LABELS_DIR):
        labels = [f for f in os.listdir(LABELS_DIR) if f.endswith(".txt")]
        print(f"  [INFO] {len(labels)} label files already mojood hain")
        print(f"  [INFO] {len(images) - len(labels)} images abhi label nahi hui")
    
    return True


def check_labelimg_installed():
    """LabelImg installed hai ya nahi."""
    print_header("STEP 4: LabelImg Check")
    
    try:
        import labelImg
        print(f"  [OK]   LabelImg installed hai")
        return True
    except ImportError:
        print(f"  [ERROR] LabelImg installed NAHI hai!")
        print(f"  [FIX]   Terminal mein chalao:")
        print(f"          pip install labelImg")
        return False


def open_labelimg():
    """LabelImg GUI open karein."""
    print_header("STEP 5: LabelImg Open")
    
    print("  [INFO] LabelImg open ho raha hai...")
    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  LABELIMG MEIN YEH KAREIN:                      │")
    print("  ├─────────────────────────────────────────────────┤")
    print("  │  1. 'Open Dir' click karein                     │")
    print(f"  │     → {IMAGES_DIR}")
    print("  │                                                 │")
    print("  │  2. 'Change Save Dir' click karein              │")
    print(f"  │     → {LABELS_DIR}")
    print("  │                                                 │")
    print("  │  3. Format ko 'YOLO' set karein                 │")
    print("  │                                                 │")
    print("  │  4. 'Open classes.txt' click karein             │")
    print(f"  │     → {CLASSES_FILE}")
    print("  │                                                 │")
    print("  │  5. Labeling shuru karein:                      │")
    print("  │     - W key: naya box                           │")
    print("  │     - Ctrl+S: save                              │")
    print("  │     - D key: agli image                         │")
    print("  └─────────────────────────────────────────────────┘")
    print()
    
    # Auto-open LabelImg
    try:
        if platform.system() == "Windows":
            subprocess.Popen(["labelImg"], shell=True)
        else:
            subprocess.Popen(["labelImg"])
        print("  [OK]   LabelImg launch ho gaya!")
    except FileNotFoundError:
        print("  [WARN] 'labelImg' command kaam nahi kar raha")
        print("  [FIX]  Manually chalao:")
        print("         python -m labelImg")
    except Exception as e:
        print(f"  [WARN] Auto-launch fail: {e}")
        print("  [FIX]  Manually chalao: labelImg")


def main():
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "LABELIMG HELPER — FALL DETECTION" + " " * 16 + "║")
    print("║" + " " * 8 + "(Training NAHI — Sirf Labeling)" + " " * 17 + "║")
    print("╚" + "═" * 58 + "╝")
    
    # Step 1
    check_and_create_folders()
    
    # Step 2
    if not check_classes_file():
        print("\n[STOP] Pehle classes.txt fix karein!")
        return
    
    # Step 3
    if not check_images():
        print("\n[STOP] Pehle images/ mein images daalein!")
        print("       Commands:")
        print("       python scripts\\extract_frames.py")
        print("       python scripts\\flatten_frames.py")
        return
    
    # Step 4
    if not check_labelimg_installed():
        print("\n[STOP] Pehle LabelImg install karein!")
        return
    
    # Step 5
    open_labelimg()
    
    print("\n" + "=" * 60)
    print("  [DONE] Sab kuch ready hai!")
    print("  [INFO] LabelImg window khul gayi hogi")
    print("  [INFO] Agar nahi khuli, toh terminal mein chalao: labelImg")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()