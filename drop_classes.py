import os

# Directory containing images and labels
DATASET_DIR = r"C:\Senior2\Dataset\Current Dataset"
UNWANTED_CLASSES = {7}

def remove_unwanted_files(dataset_dir):
    label_files = [f for f in os.listdir(dataset_dir) if f.startswith("rgb_") and f.endswith(".txt")]

    for label_file in label_files:
        label_path = os.path.join(dataset_dir, label_file)
        image_path = os.path.join(dataset_dir, label_file.replace(".txt", ".jpg"))  # Assuming images are .jpg
        image_path_png = os.path.join(dataset_dir, label_file.replace(".txt", ".png"))  # Alternative check for .png
        
        # Read label file and check for unwanted classes
        with open(label_path, "r") as file:
            lines = file.readlines()

        if any(int(line.split()[0]) in UNWANTED_CLASSES for line in lines):
            os.remove(label_path)  # Delete label file
            if os.path.exists(image_path):
                os.remove(image_path)  # Delete image if it exists
            elif os.path.exists(image_path_png):
                os.remove(image_path_png)  # Delete .png image if it exists
            
            print(f"Deleted: {label_file} and corresponding image.")

# Run the script
remove_unwanted_files(DATASET_DIR)
