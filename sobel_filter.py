import cv2
import numpy as np
import os

def apply_sobel_blend(image_path: str, output_dir: str, alpha=0.45, sobel_scale=1.5):
    """
    Apply an enhanced Sobel filter and blend it with the original image to improve edge detection
    while keeping color details for plant disease detection.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the image in color
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read the image at {image_path}")
    
    # Convert to grayscale and apply Sobel filter
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    
    # Compute gradient magnitude and scale it for stronger edges
    sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
    sobel_magnitude = sobel_magnitude * sobel_scale  # Increase edge intensity
    sobel_magnitude = np.clip(sobel_magnitude, 0, 255)  # Ensure values are valid
    sobel_magnitude = np.uint8(sobel_magnitude)
    
    # Convert Sobel edges to 3-channel
    sobel_color = cv2.cvtColor(sobel_magnitude, cv2.COLOR_GRAY2BGR)
    
    # Blend with original image (adjust alpha to make edges pop more)
    blended = cv2.addWeighted(image, alpha, sobel_color, 1 - alpha, 0)
    
    # Save the result
    output_filename = "sobel_" + os.path.basename(image_path)
    output_path = os.path.join(output_dir, output_filename)
    cv2.imwrite(output_path, blended)
    print(f"Sobel filter enhanced and saved to {output_path}")


def apply_sobel_to_directory(input_dir: str, output_dir: str, alpha=0.45, sobel_scale=1.5):
    """
    Apply the enhanced Sobel filter to all images in the input directory.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        image_path = os.path.join(input_dir, filename)
        if os.path.isfile(image_path) and filename.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'tiff')):
            apply_sobel_blend(image_path, output_dir, alpha, sobel_scale)
    
    print("Processing complete.")



apply_sobel_to_directory(input_dir= 'C:\\Senior2\\Dataset\\Filtered_containing_undersampled_classes\\images', output_dir= 'C:\\Senior2\\Dataset\\Filtered_containing_undersampled_classes\\applied_sobel')