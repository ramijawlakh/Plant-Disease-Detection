import os
import shutil
import random

# Paths
CURRENT_DATASET_DIR = r"C:\Senior2\Dataset\Current Dataset"
IMAGES_DIR = r"C:\Senior2\Dataset\images"
LABELS_DIR = r"C:\Senior2\Dataset\labels"

# Ensure the output directories exist
for split in ["train", "val", "test"]:
    os.makedirs(os.path.join(IMAGES_DIR, split), exist_ok=True)
    os.makedirs(os.path.join(LABELS_DIR, split), exist_ok=True)

# Get all images in 'Current Dataset'
images = [f for f in os.listdir(CURRENT_DATASET_DIR) if f.startswith("rgb_") and f.endswith((".jpg", ".png"))]

# Shuffle images randomly
random.shuffle(images)

# Compute split sizes
total_images = len(images)
train_count = int(total_images * 0.8)
val_count = int(total_images * 0.1)
test_count = total_images - (train_count + val_count)  # Ensure all images are used

# Split datasets
train_images = images[:train_count]
val_images = images[train_count:train_count + val_count]
test_images = images[train_count + val_count:]

def move_files(image_list, dest_image_dir, dest_label_dir):
    for image_file in image_list:
        # Define source paths
        image_path = os.path.join(CURRENT_DATASET_DIR, image_file)
        label_path = os.path.join(CURRENT_DATASET_DIR, image_file.replace(".jpg", ".txt").replace(".png", ".txt"))
        
        # Define destination paths
        dest_image_path = os.path.join(dest_image_dir, image_file)
        dest_label_path = os.path.join(dest_label_dir, os.path.basename(label_path))

        # Move files
        shutil.move(image_path, dest_image_path)
        if os.path.exists(label_path):
            shutil.move(label_path, dest_label_path)

        print(f"Moved: {image_file} → {dest_image_dir}")

# Move files into respective splits
move_files(train_images, os.path.join(IMAGES_DIR, "train"), os.path.join(LABELS_DIR, "train"))
move_files(val_images, os.path.join(IMAGES_DIR, "val"), os.path.join(LABELS_DIR, "val"))
move_files(test_images, os.path.join(IMAGES_DIR, "test"), os.path.join(LABELS_DIR, "test"))

print("Dataset split completed successfully.")
