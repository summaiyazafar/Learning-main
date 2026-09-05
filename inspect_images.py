import os
from PIL import Image

# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
)


# ============================================================
# INSPECT DATASET
# ============================================================

def inspect_images():

    print("\n========================================")
    print("       MASK DETECTION DATASET")
    print("          IMAGE INSPECTION")
    print("========================================")

    # Check archive folder
    if not os.path.exists(ARCHIVE_DIR):
        print("\n❌ ERROR: archive folder not found!")
        print("\nExpected location:")
        print(ARCHIVE_DIR)
        return

    # Get all images
    images = [
        file
        for file in os.listdir(ARCHIVE_DIR)
        if file.lower().endswith(IMAGE_EXTENSIONS)
    ]

    print("\nArchive location:")
    print(ARCHIVE_DIR)

    print("\nTotal images found:")
    print(len(images))

    # --------------------------------------------------------
    # Check image validity and dimensions
    # --------------------------------------------------------

    valid_images = 0
    invalid_images = 0

    widths = []
    heights = []

    print("\nChecking images...")

    for index, filename in enumerate(images, start=1):

        image_path = os.path.join(ARCHIVE_DIR, filename)

        try:
            with Image.open(image_path) as img:

                width, height = img.size

                widths.append(width)
                heights.append(height)

                valid_images += 1

        except Exception as e:

            invalid_images += 1

            print(f"\n❌ Invalid image: {filename}")
            print(f"   Error: {e}")

        # Progress
        if index % 200 == 0:
            print(f"Checked {index}/{len(images)} images...")


    # ========================================================
    # RESULTS
    # ========================================================

    print("\n========================================")
    print("              RESULTS")
    print("========================================")

    print(f"\nTotal images   : {len(images)}")
    print(f"Valid images   : {valid_images}")
    print(f"Invalid images : {invalid_images}")

    # --------------------------------------------------------
    # Dimensions
    # --------------------------------------------------------

    if valid_images > 0:

        print("\n----------------------------------------")
        print("IMAGE DIMENSIONS")
        print("----------------------------------------")

        print(f"Minimum width  : {min(widths)}")
        print(f"Maximum width  : {max(widths)}")

        print(f"Minimum height : {min(heights)}")
        print(f"Maximum height : {max(heights)}")

        # Most common dimensions
        from collections import Counter

        dimensions = list(zip(widths, heights))
        dimension_counts = Counter(dimensions)

        print("\n----------------------------------------")
        print("TOP IMAGE DIMENSIONS")
        print("----------------------------------------")

        for dimension, count in dimension_counts.most_common(10):

            width, height = dimension

            print(
                f"{width} x {height}  -->  {count} images"
            )

    # ========================================================
    # SAMPLE FILENAMES
    # ========================================================

    print("\n----------------------------------------")
    print("SAMPLE FILENAMES")
    print("----------------------------------------")

    for filename in images[:20]:
        print(filename)

    # ========================================================
    # FINAL MESSAGE
    # ========================================================

    print("\n========================================")
    print("          INSPECTION COMPLETED")
    print("========================================")

    print("\nIMPORTANT:")
    print("Original images were NOT moved.")
    print("Original images were NOT deleted.")
    print("Original images were NOT renamed.")

    print("\nNext step:")
    print("We will prepare the dataset for YOLO")
    print("3-class CCTV mask detection.")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    inspect_images()