import os
import matplotlib.pyplot as plt
from collections import Counter

# Path to the directory containing YOLO label files
LABEL_DIR = r"C:\Senior2\Dataset\labels\train"  # Change this to your actual labels folder

def count_classes(label_dir):
    class_counts = Counter()
    
    # Iterate over all label files in the directory
    for filename in os.listdir(label_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(label_dir, filename)
            with open(file_path, "r") as file:
                for line in file:
                    class_id = int(line.split()[0])  # Extract class ID (first column)
                    class_counts[class_id] += 1
                    
    return class_counts

def plot_class_distribution(class_counts):
    classes, counts = zip(*sorted(class_counts.items()))
    
    plt.figure(figsize=(12, 6))
    plt.bar(classes, counts, color="skyblue")
    plt.xlabel("Class ID")
    plt.ylabel("Frequency")
    plt.title("Class Distribution in YOLO Dataset")
    plt.xticks(range(26))  # Assuming 30 classes (0 to 29)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    
    # Annotate bars with counts
    for i, count in enumerate(counts):
        plt.text(classes[i], count + 2, str(count), ha="center", fontsize=10)

    plt.show()

# Run the analysis
class_counts = count_classes(LABEL_DIR)
plot_class_distribution(class_counts)
