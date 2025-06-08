import torch
import cv2
import os
import numpy as np
import json
from ultralytics import YOLO
from pathlib import Path
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from database import Prediction, User

# Load disease information
def load_disease_info():
    """Load disease information from JSON file"""
    try:
        with open("Chatbot/disease_info.json", "r") as f:
            disease_list = json.load(f)
            
        # Convert list to dictionary keyed by disease name
        disease_dict = {}
        for disease_entry in disease_list:
            if isinstance(disease_entry, dict) and "disease" in disease_entry:
                disease_name = disease_entry["disease"]
                disease_dict[disease_name] = {
                    "causes": disease_entry.get("causes", ""),
                    "symptoms": disease_entry.get("symptoms", ""),
                    "treatments": disease_entry.get("treatments", ""),
                    "affected": disease_entry.get("affected", "")
                }
        
        return disease_dict
    except FileNotFoundError:
        print("Warning: disease_info.json not found. Disease information will not be available.")
        return {}
    except Exception as e:
        print(f"Error loading disease info: {e}")
        return {}

class PlantDiseasePredictor:
    def __init__(self):
        # Model path
        self.weights_path = (
            Path(__file__).parent / "runs" / "medium_model" / "train"
            / "medium_plant_disease_exp2" / "weights" / "best.pt"
        )
        
        # Load model
        self.model = YOLO(self.weights_path)
        
        # Set device
        if torch.cuda.is_available():
            self.model.to('cuda')
        else:
            self.model.to('cpu')
        
        # Load disease information
        self.disease_info = load_disease_info()
    
    def predict_image(self, image_path: str, confidence_threshold: float = 0.5) -> Dict:
        """
        Run prediction on an image and return structured results
        """
        # Load and preprocess image
        img = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Run inference
        results = self.model(img_rgb)
        result = results[0]
        
        # Extract predictions
        boxes = result.boxes.xyxy.cpu().numpy() if result.boxes is not None else np.array([])
        confidences = result.boxes.conf.cpu().numpy() if result.boxes is not None else np.array([])
        classes = result.boxes.cls.cpu().numpy() if result.boxes is not None else np.array([])
        labels = result.names
        
        # Filter by confidence threshold
        valid_indices = confidences >= confidence_threshold
        boxes = boxes[valid_indices]
        confidences = confidences[valid_indices]
        classes = classes[valid_indices]
        
        # Structure results
        predictions = []
        detected_diseases = set()
        
        for i, (box, conf, cls) in enumerate(zip(boxes, confidences, classes)):
            disease_name = labels[int(cls)]
            detected_diseases.add(disease_name)
            
            prediction = {
                "id": i,
                "disease": disease_name,
                "confidence": float(conf),
                "bbox": {
                    "x1": float(box[0]),
                    "y1": float(box[1]),
                    "x2": float(box[2]),
                    "y2": float(box[3])
                },
                "info": self.disease_info.get(disease_name, {})
            }
            predictions.append(prediction)
        
        return {
            "predictions": predictions,
            "detected_diseases": list(detected_diseases),
            "total_detections": len(predictions),
            "avg_confidence": float(np.mean(confidences)) if len(confidences) > 0 else 0.0
        }
    
    def create_annotated_image(self, image_path: str, output_path: str, prediction_results: Dict) -> str:
        """
        Create annotated image with bounding boxes and labels
        """
        # Load image
        img = cv2.imread(image_path)
        
        # Font settings
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.75
        color = (255, 255, 220)
        thickness = 2
        
        # Draw predictions
        for pred in prediction_results["predictions"]:
            bbox = pred["bbox"]
            x1, y1, x2, y2 = int(bbox["x1"]), int(bbox["y1"]), int(bbox["x2"]), int(bbox["y2"])
            
            # Draw bounding box
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Create label
            label = f"{pred['disease']} {pred['confidence']:.2f}"
            
            # Calculate text position
            text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
            text_y = max(y1 - 10, text_size[1])
            
            # Add text background
            cv2.rectangle(img, (x1, text_y - text_size[1] - 5), 
                         (x1 + text_size[0], text_y + 5), (0, 255, 0), -1)
            
            # Add text
            cv2.putText(img, label, (x1, text_y), font, font_scale, color, thickness)
        
        # Save annotated image
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, img)
        
        return output_path

# Global predictor instance
predictor = PlantDiseasePredictor()

def save_prediction_to_db(
    db: Session, 
    user: User, 
    image_filename: str, 
    image_path: str, 
    predicted_image_path: str,
    confidence_threshold: float,
    prediction_results: Dict
) -> Prediction:
    """Save prediction results to database"""
    
    db_prediction = Prediction(
        user_id=user.id,
        image_filename=image_filename,
        image_path=image_path,
        predicted_image_path=predicted_image_path,
        confidence_threshold=confidence_threshold,
        prediction_results=json.dumps(prediction_results["predictions"]),
        detected_diseases=json.dumps(prediction_results["detected_diseases"])
    )
    
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    
    return db_prediction 