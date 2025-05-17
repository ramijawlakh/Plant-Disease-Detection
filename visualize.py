import os
from PIL import Image, ImageDraw, ImageFont

# Function to read the label file (_darknet.labels) and map class IDs to class names
def load_labels(label_file):
    with open(label_file, 'r') as f:
        labels = f.read().splitlines()
    return labels

# Function to draw bounding boxes on an image
def draw_bounding_boxes(image_path, txt_file, labels, output_dir):
    # Open the image using Pillow
    image = Image.open(image_path).convert("RGB")  # Ensure it's in RGB mode
    draw = ImageDraw.Draw(image)
    w, h = image.size  # Get image dimensions

    # Read the bounding box coordinates from the txt file
    with open(txt_file, 'r') as f:
        lines = f.readlines()

    for line in lines:
        # Each line contains the class id and the coordinates in normalized form
        class_id, x_center, y_center, width, height = map(float, line.strip().split())

        # Convert normalized coordinates to pixel values
        x_center, y_center, width, height = int(x_center * w), int(y_center * h), int(width * w), int(height * h)

        # Calculate the top-left and bottom-right coordinates of the bounding box
        x1 = int(x_center - width / 2)
        y1 = int(y_center - height / 2)
        x2 = int(x_center + width / 2)
        y2 = int(y_center + height / 2)

        # Get the class name
        class_name = labels[int(class_id)]

        # Draw the bounding box and label on the image
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)  # Green bounding box
        
        # Load font (use default if custom font not found)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()

        draw.text((x1, y1 - 4), class_name, fill="red", font=font)  # Class label

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save the image with bounding boxes to the specified output directory
    output_path = os.path.join(output_dir, f'boxed_{os.path.basename(image_path)}')
    image.save(output_path)
    print(f'Image saved to {output_path}')

    # Open with default image viewer (should be Photos if set as default)
    os.system(f'start {output_path}')  # Works on Windows

# Main function to execute the script
def main(image_path, txt_file, label_file, output_dir):
    labels = load_labels(label_file)  # Load labels from the _darknet.labels file
    draw_bounding_boxes(image_path, txt_file, labels, output_dir)

if __name__ == "__main__":
    # Example usage
    image_path = r'C:\Senior2ubuntu\Dataset\images\train\rgb_0002.jpg'  # Replace with the path to your image
    txt_file = r'C:\Senior2ubuntu\Dataset\labels\train\rgb_0002.txt'  # Replace with the path to your .txt file containing bounding box data
    label_file = r'C:\Senior2ubuntu\Dataset\_darknet.labels'  # Path to the _darknet.labels file
    output_dir = r'C:\Senior2ubuntu\visualized'  # Directory to save the images with bounding boxes

    main(image_path, txt_file, label_file, output_dir)
