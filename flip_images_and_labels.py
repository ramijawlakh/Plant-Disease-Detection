import os
import cv2


def flip_images_and_labels(image_dir, label_dir, output_image_dir, output_label_dir):
    """
    Applies horizontal flipping to images and updates corresponding YOLO labels.
    """
    os.makedirs(output_image_dir, exist_ok=True)
    os.makedirs(output_label_dir, exist_ok=True)

    # Process each image file
    for image_file in os.listdir(image_dir):
        if image_file.endswith((".jpg", ".png")):  # Supports JPG and PNG images
            image_path = os.path.join(image_dir, image_file)
            
            # Label file must match the image file (except extension)
            label_filename = os.path.splitext(image_file)[0] + ".txt"
            label_path = os.path.join(label_dir, label_filename)

            # Read and flip the image
            image = cv2.imread(image_path)
            if image is None:
                print(f"Skipping {image_path}: Unable to read")
                continue

            flipped_image = cv2.flip(image, 1)  # Flip horizontally
            flipped_image_path = os.path.join(output_image_dir, image_file)
            cv2.imwrite(flipped_image_path, flipped_image)

            # Process corresponding label file
            if os.path.exists(label_path):
                with open(label_path, "r") as file:
                    lines = file.readlines()

                flipped_labels = []
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) != 5:
                        print(f"Skipping invalid label line: {line} in {label_path}")
                        continue
                    
                    class_id, x_center, y_center, width, height = int(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])

                    # Flip x_center -> new_x_center = 1 - x_center
                    new_x_center = 1.0 - x_center
                    flipped_labels.append(f"{class_id} {new_x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

                # Save flipped label
                flipped_label_path = os.path.join(output_label_dir, label_filename)
                with open(flipped_label_path, "w") as file:
                    file.writelines(flipped_labels)

                print(f"Processed: {image_file} and {label_filename}")
            else:
                print(f"No label found for: {image_file}")


# Example usage
image_dir = r"C:\Senior2\Dataset\Filtered_containing_undersampled_classes\applied_sobel_before_flipping"
label_dir = r"C:\Senior2\Dataset\Filtered_containing_undersampled_classes\labels_before_flipping"
output_image_dir = r"C:\Senior2\Dataset\Filtered_containing_undersampled_classes\sobel_flipped_images"
output_label_dir = r"C:\Senior2\Dataset\Filtered_containing_undersampled_classes\sobel_flipped_labels"

flip_images_and_labels(image_dir, label_dir, output_image_dir, output_label_dir)
