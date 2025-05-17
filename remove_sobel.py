import os

def remove_sobel_prefix(directory):
    """
    Renames all files in the given directory by removing the 'sobel_' prefix if present.
    """
    for filename in os.listdir(directory):
        if filename.startswith("sobel_"):
            new_filename = filename.replace("sobel_", "", 1)  # Remove only the first occurrence
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, new_filename)
            
            os.rename(old_path, new_path)
            print(f"Renamed: {filename} → {new_filename}")

# Example usage
directory = r"C:\Senior2\Dataset\Filtered_containing_undersampled_classes\applied_sobel_before_flipping"  # Change to your actual directory
remove_sobel_prefix(directory)
