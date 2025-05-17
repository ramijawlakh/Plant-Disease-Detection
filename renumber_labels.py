import os

# Define the directory containing train, val, and test label folders
base_dir = r"C:\Senior2\Dataset\labels"

# Define the mapping of old class IDs to new ones
class_mapping = {
    8: 7, 9: 8, 10: 9, 12: 10, 13: 11, 14: 12, 15: 13, 17: 14, 18: 15, 19: 16,
    20: 17, 21: 18, 22: 19, 23: 20, 24: 21, 25: 22, 26: 23, 28: 24, 29: 25
}

# Iterate over train, val, and test folders
for split in ["train", "val", "test"]:
    split_dir = os.path.join(base_dir, split)
    
    # Ensure the directory exists
    if not os.path.isdir(split_dir):
        print(f"Skipping missing directory: {split_dir}")
        continue

    # Process each .txt file in the directory
    for filename in os.listdir(split_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(split_dir, filename)
            
            # Read and modify the file content
            updated_lines = []
            with open(file_path, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:  # Ensure line is not empty
                        class_id = int(parts[0])
                        if class_id in class_mapping:
                            parts[0] = str(class_mapping[class_id])  # Update class ID
                        updated_lines.append(" ".join(parts))
            
            # Overwrite the file with updated content
            with open(file_path, "w") as f:
                f.write("\n".join(updated_lines) + "\n")

print("Class ID renumbering completed successfully.")
