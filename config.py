import os
from pathlib import Path

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://plantcare_user:plantcare_pass@localhost:5432/plantcare_db"
)

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Model Paths
BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "Chatbot" / "modelv4"
YOLO_MODEL_PATH = BASE_DIR / "runs" / "medium_model" / "train" / "medium_plant_disease_exp2" / "weights" / "best.pt"

# File Storage
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

if ENVIRONMENT == "production":
    ALLOWED_ORIGINS.extend([
        "https://your-domain.com",
        "https://www.your-domain.com"
    ])