"""
split_dataset.py
images/ aur labels/ ko train/val/test mein split karta hai.
YOLO training ke liye dataset/ folder banata hai.
"""

import os
import shutil
import random

# ================== SETTINGS ==================
SOURCE_IMAGES = "images"       # Labeled images
SOURCE_LABELS = "labels"       # LabelImg ke .txt files (IMPORTANT: sahi path)
OUTPUT_DIR = "dataset"         # YOLO dataset yahan banega
CLASSES = ["normal", "straight_fall", "left_fall", "right_fall", "back_fall"]

TRAIN_RATIO = 0.7              # 70% training
VAL_RATIO = 0.2                # 20% validation
TEST_RATIO = 0.1               # 10% test
RANDOM_SEED = 42               # Same split har baar
# ===============================================

random.seed(RANDOM_SEED)

def main():
    # Check karein ke source folders exist karte hain
    if not os.path.exists(SOURCE_IMAGES):
        print(f"[ERROR] {SOURCE_IMAGES}/ nahi mila!")
        return
    if not os.path.exists(SOURCE_LABELS):
        print(f"[ERROR] {SOURCE_LABELS}/ nahi mila!")
        return
    
    # Output folders banao
    for split in ["train", "val", "test"]:
        os.makedirs(f"{OUTPUT_DIR}/images/{split}", exist_ok=True)
        os.makedirs(f"{OUTPUT_DIR}/labels/{split}", exist_ok=True)
    
    # Saari images dhoondo
    image_files = []
    for f in os.listdir(SOURCE_IMAGES):
        if f.lower().endswith((".jpg", ".jpeg", ".png")):
            image_files.append(f)
    
    if not image_files:
        print(f"[ERROR] {SOURCE_IMAGES}/ mein koi image nahi mili!")
        return
    
    print(f"[INFO] Total {len(image_files)} images mili")
    
    random.shuffle(image_files)
    n = len(image_files)
    n_train = int(n * TRAIN_RATIO)
    n_val = int(n * VAL_RATIO)
    
    train_files = image_files[:n_train]
    val_files = image_files[n_train:n_train + n_val]
    test_files = image_files[n_train + n_val:]
    
    print(f"[INFO] Train: {len(train_files)}, Val: {len(val_files)}, Test: {len(test_files)}")
    
    def copy_files(files, split):
        copied = 0
        missing = 0
        for img_name in files:
            # Image copy
            src_img = os.path.join(SOURCE_IMAGES, img_name)
            dst_img = f"{OUTPUT_DIR}/images/{split}/{img_name}"
            shutil.copy2(src_img, dst_img)
            
            # Label copy
            label_name = os.path.splitext(img_name)[0] + ".txt"
            src_label = os.path.join(SOURCE_LABELS, label_name)
            dst_label = f"{OUTPUT_DIR}/labels/{split}/{label_name}"
            
            if os.path.exists(src_label):
                shutil.copy2(src_label, dst_label)
            else:
                # Empty label file (background image)
                open(dst_label, "w").close()
                missing += 1
            copied += 1
        
        print(f"[{split.upper()}] {copied} images, {missing} missing labels")
    
    copy_files(train_files, "train")
    copy_files(val_files, "val")
    copy_files(test_files, "test")
    
    # data.yaml banao
    data_yaml_path = f"{OUTPUT_DIR}/data.yaml"
    abs_path = os.path.abspath(OUTPUT_DIR).replace("\\", "/")
    
    with open(data_yaml_path, "w") as f:
        f.write(f"path: {abs_path}\n")
        f.write("train: images/train\n")
        f.write("val: images/val\n")
        f.write("test: images/test\n")
        f.write(f"nc: {len(CLASSES)}\n")
        f.write(f"names: {CLASSES}\n")
    
    print(f"\n[DONE] Dataset ready!")
    print(f"[INFO] data.yaml: {data_yaml_path}")
    print(f"[NEXT] Ab training chalao: python scripts/train.py")

if __name__ == "__main__":
    main()