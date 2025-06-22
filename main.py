from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import shutil
import json
from pathlib import Path
from typing import List

# Local imports
from database import get_db, create_tables, User, Prediction, ChatHistory
from auth import (
    authenticate_user, create_access_token, get_current_active_user, 
    get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
)
from schemas import (
    UserCreate, UserLogin, Token, User as UserSchema, 
    ChatRequest, ChatResponse, PredictionResponse, UserHistory,
    Analytics, DiseaseStats
)
from prediction_service import predictor, save_prediction_to_db
from chatbot_service import chatbot_service

# Create FastAPI app
app = FastAPI(
    title="Plant Disease Detection & Care Assistant",
    description="AI-powered plant disease detection with care chatbot",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
create_tables()

# Create necessary directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ================= AUTHENTICATION ENDPOINTS ================= #

@app.post("/api/auth/register", response_model=UserSchema)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/api/auth/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

# ================= PREDICTION ENDPOINTS ================= #

@app.post("/api/predict", response_model=dict)
async def predict_disease(
    file: UploadFile = File(...),
    confidence_threshold: float = Form(0.5),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload image and predict plant diseases"""
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save uploaded file
    file_extension = Path(file.filename).suffix
    unique_filename = f"user_{current_user.id}_{file.filename}"
    image_path = UPLOAD_DIR / unique_filename
    
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Run prediction
        prediction_results = predictor.predict_image(str(image_path), confidence_threshold)
        
        # Create annotated image
        output_filename = f"predicted_{unique_filename}"
        output_path = OUTPUT_DIR / output_filename
        predictor.create_annotated_image(str(image_path), str(output_path), prediction_results)
        
        # Save to database
        db_prediction = save_prediction_to_db(
            db, current_user, file.filename, str(image_path), 
            str(output_path), confidence_threshold, prediction_results
        )
        
        return {
            "id": db_prediction.id,
            "predictions": prediction_results["predictions"],
            "detected_diseases": prediction_results["detected_diseases"],
            "total_detections": prediction_results["total_detections"],
            "avg_confidence": prediction_results["avg_confidence"],
            "image_url": f"/api/images/predicted/{output_filename}"
        }
        
    except Exception as e:
        # Clean up files on error
        if image_path.exists():
            image_path.unlink()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/api/images/predicted/{filename}")
async def get_predicted_image(filename: str):
    """Get predicted image file"""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)

@app.get("/api/predictions", response_model=List[PredictionResponse])
async def get_user_predictions(
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's prediction history"""
    predictions = db.query(Prediction).filter(
        Prediction.user_id == current_user.id
    ).order_by(Prediction.created_at.desc()).limit(limit).all()
    
    return predictions

# ================= CHAT ENDPOINTS ================= #

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_bot(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send message to chatbot and get response"""
    
    try:
        response = chatbot_service.generate_response(
            request.user_input, current_user.id, db
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/api/chat/history")
async def get_chat_history(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's chat history"""
    
    chat_history = chatbot_service.get_user_chat_history(db, current_user.id, limit)
    return chat_history

# ================= HISTORY ENDPOINTS ================= #

@app.get("/api/history", response_model=UserHistory)
async def get_user_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get complete user history (predictions + chat)"""
    
    predictions = db.query(Prediction).filter(
        Prediction.user_id == current_user.id
    ).order_by(Prediction.created_at.desc()).limit(20).all()
    
    chat_history = db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id
    ).order_by(ChatHistory.created_at.desc()).limit(50).all()
    
    return {
        "predictions": predictions,
        "chat_history": chat_history
    }

# ================= ANALYTICS ENDPOINTS ================= #

@app.get("/api/analytics", response_model=Analytics)
async def get_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user-specific analytics data"""
    
    # User-specific stats instead of global totals
    user_predictions = db.query(Prediction).filter(Prediction.user_id == current_user.id).count()
    user_chats = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).count()
    
    # Most common diseases for this user only
    user_predictions_with_diseases = db.query(Prediction).filter(
        Prediction.user_id == current_user.id,
        Prediction.detected_diseases.isnot(None)
    ).all()
    
    disease_counts = {}
    for pred in user_predictions_with_diseases:
        try:
            diseases = json.loads(pred.detected_diseases)
            for disease in diseases:
                disease_counts[disease] = disease_counts.get(disease, 0) + 1
        except:
            continue
    
    # Convert to stats format
    total_user_disease_detections = sum(disease_counts.values())
    most_common_diseases = []
    
    for disease, count in sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        percentage = (count / total_user_disease_detections * 100) if total_user_disease_detections > 0 else 0
        most_common_diseases.append({
            "disease_name": disease,
            "count": count,
            "percentage": round(percentage, 2)
        })
    
    return {
        "total_predictions": user_predictions,
        "total_users": 1,  # Always 1 for user-specific view
        "total_chats": user_chats,
        "most_common_diseases": most_common_diseases,
        "recent_activity": {
            "message": f"Personal analytics for {current_user.username}"
        }
    }

# ================= STATIC FILES ================= #

# Serve the React frontend (will be created next)
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Plant Care API is running"}

# Mount static files (React build will go here)
frontend_path = Path(__file__).parent / "frontend" / "build"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
else:
    # Fallback to development frontend
    dev_frontend_path = Path(__file__).parent / "frontend"
    if dev_frontend_path.exists():
        app.mount("/", StaticFiles(directory=str(dev_frontend_path), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)