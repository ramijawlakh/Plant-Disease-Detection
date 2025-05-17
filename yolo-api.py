from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import shutil
import os
from pathlib import Path
from predictyolo import run_inference

app = FastAPI()

# Temporary directory for uploaded files
TEMP_DIR = Path("/tmp/uploads")
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/predict/")
async def predict(
    file: UploadFile = File(...), 
    confidence_threshold: float = Form(0.5), 
    output_dir: str = Form("/tmp/output")
):
    """
    Endpoint to upload an image, run YOLOv11 object detection, and return the processed image.
    
    Parameters:
    - file: The image file to be uploaded.
    - confidence_threshold: The minimum confidence required for a detection.
    - output_dir: Directory where the output images will be stored.
    
    Returns:
    - Processed image with bounding boxes drawn.
    """
    output_path = Path(output_dir)
    os.makedirs(output_path, exist_ok=True)

    # Save uploaded file to temporary directory
    img_path = TEMP_DIR / file.filename
    with open(img_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run inference
    run_inference(str(TEMP_DIR), str(output_path), confidence_threshold)

    # Return the processed image
    predicted_image_path = output_path / f'predicted_{file.filename}'
    return FileResponse(predicted_image_path)

