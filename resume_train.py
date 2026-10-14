"""
resume_train.py
===============
Resumes YOLOv8 training from where it was interrupted or stopped early.

Use this when:
  - Training stopped due to early stopping (patience triggered)
  - Training was interrupted (power cut, Ctrl+C, crash)
  - You want to add more epochs to an existing run

Usage:
    python scripts/resume_train.py

What it does:
  - Loads the last saved checkpoint (last.pt)
  - Continues training with the SAME settings BUT:
      * patience = 0  (early stopping DISABLED)
      * Extends training for more epochs

Note:
  When resuming, YOLOv8 reads the original args from the checkpoint.
  The only thing it changes is resuming from the last epoch.
"""

import os
import sys
from ultralytics import YOLO

# =================== SETTINGS ===================
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAST = os.path.join(ROOT, "runs", "detect", "fall_detector", "weights", "last.pt")
BEST = os.path.join(ROOT, "runs", "detect", "fall_detector", "weights", "best.pt")
# ================================================


def main():
    print("=" * 60)
    print("  FALL DETECTION — RESUME TRAINING")
    print("=" * 60)

    # ---- Check checkpoint exists ----
    if not os.path.exists(LAST):
        print(f"[ERROR] No checkpoint found at: {LAST}")
        print("[INFO]  This means either:")
        print("        1. Training was never started (run train.py first)")
        print("        2. The checkpoint was deleted")
        print()
        print("[FIX]  Run fresh training:")
        print("       python scripts/train.py")
        sys.exit(1)

    last_size = os.path.getsize(LAST) / (1024 * 1024)
    print(f"[OK]  Checkpoint found: {LAST}")
    print(f"[OK]  Checkpoint size:  {last_size:.1f} MB")

    if os.path.exists(BEST):
        best_size = os.path.getsize(BEST) / (1024 * 1024)
        print(f"[OK]  Best weights:    {BEST} ({best_size:.1f} MB)")

    print()
    print("[INFO] Starting RESUME training...")
    print("[INFO] Early stopping is DISABLED — will train all remaining epochs.")
    print("[INFO] Press Ctrl+C to pause training (checkpoint is saved automatically).")
    print()

    # ---- Load model from checkpoint and resume ----
    model = YOLO(LAST)
    model.train(resume=True)

    print()
    print("[DONE] Training complete!")
    print(f"[DONE] Best model: {BEST}")
    print("[NEXT] Run the dashboard: python scripts/dashboard.py")
    print("[NEXT] Or run detection:  python scripts/detect_alert.py")


if __name__ == "__main__":
    main()
