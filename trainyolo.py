from ultralytics import YOLO

# Load a COCO-pretrained YOLO11n model
model = YOLO("yolo11m.pt")

# Train the model on the COCO8 example dataset for 100 epochs
results = model.train(data="C:\Senior3\Dataset\plant_dataset.yaml", epochs=300, imgsz=640)

