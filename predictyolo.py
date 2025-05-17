"""
import torch
import cv2
import os
import numpy as np
from ultralytics import YOLO

# Load the YOLO model weights (Ultralytics YOLO)
model = YOLO(r'C:\Senior3\runs\medium_model\train\medium_plant_disease_exp2\weights\best.pt')  # Load the custom trained model
model.to('cpu')  # Force CPU usage (change to 'cuda' if you want to use GPU)

# Directory for input images
image_dir = r'C:\Senior3\images from google'
output_dir = r'C:\Senior3\images from google\predictions'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Confidence threshold (predictions below this threshold will be discarded)
confidence_threshold = 0.5  # You can adjust this value (e.g., 0.5, 0.7)

# Run predictions on each image in the input directory
for img_name in os.listdir(image_dir):
    img_path = os.path.join(image_dir, img_name)
    
    if not img_name.lower().endswith(('.png', '.jpg', '.jpeg')):  # Skip non-image files
        continue
    
    # Load the image using OpenCV (BGR format by default)
    img = cv2.imread(img_path)

    # Convert to RGB (Ultralytics expects RGB images)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Run inference using the YOLO model
    results = model(img_rgb)  # Model inference (Ultralytics handles it internally)

    # Access the results for the first image in the batch
    result = results[0]  # Get the first result (if batch size > 1, iterate)

    # Print details using verbose method
    print(result.verbose())  # Print detailed information about the detections

    # Extract the bounding boxes, labels, and confidences
    boxes = result.boxes.xyxy.cpu().numpy()  # Bounding boxes (x1, y1, x2, y2)
    labels = result.names  # Class names
    confidences = result.boxes.conf.cpu().numpy()  # Confidence scores

    # Customize font size, thickness, and color
    font = cv2.FONT_HERSHEY_SIMPLEX  # Font style
    font_scale = 1.0  # Font size (adjust this value)
    color = (255, 0, 0)  # Text color (green in BGR)
    thickness = 2  # Font thickness
    text_offset = -15  # Vertical space between boxes and text

    # Draw the bounding boxes on the original BGR image for predictions above the confidence threshold
    for i, (x1, y1, x2, y2) in enumerate(boxes):
        if confidences[i] >= confidence_threshold:  # Only draw boxes with confidence >= threshold
            # Draw the bounding box (BGR format)
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            
            # Label and confidence score (You can adjust label and confidence formatting)
            label = f"{labels[int(result.boxes.cls[i].item())]} {confidences[i]:.2f}"

            # Adjust text position (this is just one way to modify the text position)
            text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
            text_x = int(x1)
            text_y = int(y1) - text_offset

            # Ensure text doesn't go out of the image boundaries
            if text_y < 0:
                text_y = int(y1) + text_offset

            # Put the text on the image
            cv2.putText(img, label, (text_x, text_y), font, font_scale, color, thickness)

    # Save the image with bounding boxes drawn, in BGR format (original colors)
    output_path = os.path.join(output_dir, f'predicted_{img_name}')
    cv2.imwrite(output_path, img)  # Save the image in BGR format

print(f"Inference completed. Predicted images are saved in '{output_dir}'.")
"""

import torch
import cv2
import os
import numpy as np
from ultralytics import YOLO
from pathlib import Path

WEIGHTS_PATH = (
    Path(__file__).parent        # predictyolo.py’s folder
    / "runs"                     # your runs folder under /app/runs
    / "medium_model" / "train"
    / "medium_plant_disease_exp2"
    / "weights" / "best.pt"
)

def run_inference(input_dir, output_dir, confidence_threshold):
    # Load the YOLO model weights (Ultralytics YOLO)
    #model = YOLO(r'C:\Senior3\runs\medium_model\train\medium_plant_disease_exp2\weights\best.pt')  # Load the custom trained model
    model = YOLO(WEIGHTS_PATH)
    
    if torch.cuda.is_available():
        model.to('cuda')
    else:
        model.to('cpu')  # Force CPU usage (change to 'cuda' if you want to use GPU)

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Run predictions on each image in the input directory
    for img_name in os.listdir(input_dir):
        img_path = os.path.join(input_dir, img_name)
        
        if not img_name.lower().endswith(('.png', '.jpg', '.jpeg')):  # Skip non-image files
            continue
        
        # Load the image using OpenCV (BGR format by default)
        img = cv2.imread(img_path)

        # Convert to RGB (Ultralytics expects RGB images)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Run inference using the YOLO model
        results = model(img_rgb)  # Model inference (Ultralytics handles it internally)

        # Access the results for the first image in the batch
        result = results[0]  # Get the first result (if batch size > 1, iterate)

        # Print details using verbose method
        print(result.verbose())  # Print detailed information about the detections

        # Extract the bounding boxes, labels, and confidences
        boxes = result.boxes.xyxy.cpu().numpy()  # Bounding boxes (x1, y1, x2, y2)
        labels = result.names  # Class names
        confidences = result.boxes.conf.cpu().numpy()  # Confidence scores

        # Customize font size, thickness, and color
        font = cv2.FONT_HERSHEY_SIMPLEX  # Font style
        font_scale = 0.75  # Font size (adjust this value)
        color = (255, 255, 220)  # Text color (green in BGR)
        thickness = 2  # Font thickness
        text_offset = -15  # Vertical space between boxes and text

        # Draw the bounding boxes on the original BGR image for predictions above the confidence threshold
        for i, (x1, y1, x2, y2) in enumerate(boxes):
            if confidences[i] >= confidence_threshold:  # Only draw boxes with confidence >= threshold
                # Draw the bounding box (BGR format)
                cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                
                # Label and confidence score (You can adjust label and confidence formatting)
                label = f"{labels[int(result.boxes.cls[i].item())]} {confidences[i]:.2f}"

                # Adjust text position (this is just one way to modify the text position)
                text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
                text_x = int(x1)
                text_y = int(y1) - text_offset

                # Ensure text doesn't go out of the image boundaries
                if text_y < 0:
                    text_y = int(y1) + text_offset

                # Put the text on the image
                cv2.putText(img, label, (text_x, text_y), font, font_scale, color, thickness)

        # Save the image with bounding boxes drawn, in BGR format (original colors)
        output_path = os.path.join(output_dir, f'predicted_{img_name}')
        cv2.imwrite(output_path, img)  # Save the image in BGR format

    print(f"Inference completed. Predicted images are saved in '{output_dir}'.")

# Example usage
#input_directory = r'C:\Senior3\images from google'
#output_directory = r'C:\Senior3\images from google\predictions'
#confidence_threshold_value = 0.5  # Adjust as needed
#run_inference(input_directory, output_directory, confidence_threshold_value)
