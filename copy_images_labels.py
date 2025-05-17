import os
import shutil

# Paths
SOURCE_DIR = r"C:\Senior2\Dataset\416x416"  # Original dataset folder
TARGET_LABELS_DIR = r"C:\Senior2\Dataset\Filtered\labels"  # Where filtered labels will be saved
TARGET_IMAGES_DIR = r"C:\Senior2\Dataset\Filtered\images"  # Where filtered images will be saved

# Set of class IDs to keep
TARGET_CLASSES = {0, 1, 2, 3, 4, 6, 7, 9, 12, 13, 15, 17, 19, 22, 23, 24, 26, 28, 29}

# Ensure target directories exist
os.makedirs(TARGET_LABELS_DIR, exist_ok=True)
os.makedirs(TARGET_IMAGES_DIR, exist_ok=True)

def filter_and_copy_files(source_dir, labels_dir, images_dir):
    label_files = [f for f in os.listdir(source_dir) if f.startswith("rgb_") and f.endswith(".txt")]

    for label_file in label_files:
        label_path = os.path.join(source_dir, label_file)
        image_path_jpg = os.path.join(source_dir, label_file.replace(".txt", ".jpg"))
        image_path_png = os.path.join(source_dir, label_file.replace(".txt", ".png"))

        # Read label file and check if it contains any target class
        with open(label_path, "r") as file:
            lines = file.readlines()

        # Keep only lines with target classes
        filtered_lines = [line for line in lines if int(line.split()[0]) in TARGET_CLASSES]

        if filtered_lines:
            # Copy label file with filtered content
            new_label_path = os.path.join(labels_dir, label_file)
            with open(new_label_path, "w") as new_file:
                new_file.writelines(filtered_lines)

            # Copy corresponding image
            if os.path.exists(image_path_jpg):
                shutil.copy(image_path_jpg, os.path.join(images_dir, os.path.basename(image_path_jpg)))
            elif os.path.exists(image_path_png):
                shutil.copy(image_path_png, os.path.join(images_dir, os.path.basename(image_path_png)))

            print(f"Copied: {label_file} and corresponding image.")

# Run the function
filter_and_copy_files(SOURCE_DIR, TARGET_LABELS_DIR, TARGET_IMAGES_DIR)
