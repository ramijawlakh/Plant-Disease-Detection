import os
import random

# Dataset directory
DATASET_DIR = r"C:\Senior2\Dataset\Current Dataset"

# Classes to reduce
TARGET_CLASSES = {5, 25}
INSTANCES_TO_REMOVE = 20  # Number of instances to delete

def find_files_to_remove(dataset_dir, target_classes, remove_count):
    """
    Finds label files that contain the target classes and selects 'remove_count' random instances for deletion.
    """
    removable_files = []

    # List all label files
    label_files = [f for f in os.listdir(dataset_dir) if f.startswith("rgb_") and f.endswith(".txt")]

    for label_file in label_files:
        label_path = os.path.join(dataset_dir, label_file)
        image_path_jpg = os.path.join(dataset_dir, label_file.replace(".txt", ".jpg"))
        image_path_png = os.path.join(dataset_dir, label_file.replace(".txt", ".png"))

        # Read label file and check for target class instances
        with open(label_path, "r") as file:
            lines = file.readlines()

        if any(int(line.split()[0]) in target_classes for line in lines):
            removable_files.append((label_path, image_path_jpg, image_path_png))

    # Randomly select 'remove_count' instances to delete
    return random.sample(removable_files, min(remove_count, len(removable_files)))

def delete_selected_files(files_to_delete):
    """
    Deletes the selected label and image files.
    """
    for label_path, image_jpg, image_png in files_to_delete:
        os.remove(label_path)  # Delete label file
        if os.path.exists(image_jpg):
            os.remove(image_jpg)  # Delete image (JPG)
        elif os.path.exists(image_png):
            os.remove(image_png)  # Delete image (PNG)

        print(f"Deleted: {os.path.basename(label_path)} and corresponding image.")

# Find files containing the target classes
files_to_delete = find_files_to_remove(DATASET_DIR, TARGET_CLASSES, INSTANCES_TO_REMOVE)

# Delete selected files
delete_selected_files(files_to_delete)
