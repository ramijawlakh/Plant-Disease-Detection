from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    profile_picture: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Prediction schemas
class PredictionBase(BaseModel):
    confidence_threshold: float

class PredictionCreate(PredictionBase):
    pass

class PredictionResponse(BaseModel):
    id: int
    image_filename: str
    confidence_threshold: float
    prediction_results: Optional[str] = None
    detected_diseases: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Chat schemas
class ChatRequest(BaseModel):
    user_input: str

class ChatResponse(BaseModel):
    response: str
    disease_context: Optional[str] = None

class ChatHistoryItem(BaseModel):
    id: int
    message: str
    response: str
    disease_context: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# History schemas
class UserHistory(BaseModel):
    predictions: List[PredictionResponse]
    chat_history: List[ChatHistoryItem]

# Analytics schemas
class DiseaseStats(BaseModel):
    disease_name: str
    count: int
    percentage: float

class Analytics(BaseModel):
    total_predictions: int
    total_users: int
    total_chats: int
    most_common_diseases: List[DiseaseStats]
    recent_activity: dict

# Profile schemas
class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None 