import os
from collections import Counter

# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")

# Supported image formats
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


# ============================================================
# CHECK DATASET
# ============================================================

def check_dataset():

    if not os.path.exists(ARCHIVE_DIR):
        print("\n❌ ERROR: archive folder not found!")
        print(f"Expected location:\n{ARCHIVE_DIR}")
        return

    images = [
        file for file in os.listdir(ARCHIVE_DIR)
        if file.lower().endswith(IMAGE_EXTENSIONS)
    ]

    print("\n========================================")
    print("     MASK DETECTION DATASET CHECK")
    print("========================================")

    print(f"\nArchive location:")
    print(ARCHIVE_DIR)

    print(f"\nTotal images found: {len(images)}")

    print("\n----------------------------------------")
    print("First 20 image filenames:")
    print("----------------------------------------")

    for image in images[:20]:
        print(image)

    print("\n========================================")
    print("IMPORTANT")
    print("========================================")
    print(
        "\nYour images are currently mixed together."
        "\nWe will NOT move or delete the original images."
        "\nFirst we will inspect the dataset and then perform labeling."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    check_dataset()