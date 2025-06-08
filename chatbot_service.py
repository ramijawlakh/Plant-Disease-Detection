import json
import re
from pathlib import Path
from typing import Dict, Optional, List
from transformers import pipeline, AutoTokenizer
from sqlalchemy.orm import Session
from database import ChatHistory, User

class PlantCareChatbot:
    def __init__(self):
        # Model path
        self.model_path = Path(__file__).parent / "Chatbot" / "modelv4"
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.chatbot = pipeline(
            "text-generation",
            model=self.model_path,
            tokenizer=self.tokenizer,
            do_sample=True,
            top_p=0.92,
            temperature=0.7,
            no_repeat_ngram_size=3
        )
        
        # Load disease information
        self.disease_info = self.load_disease_info()
        
        # Disease keywords for context detection
        self.disease_keywords = [
            "early blight", "late blight", "apple scab", "black rot", "cedar apple rust",
            "powdery mildew", "downy mildew", "leaf spot", "bacterial spot", "tomato mosaic virus",
            "fusarium wilt", "verticillium wilt", "septoria leaf spot", "anthracnose"
        ]
        
        # Conversation contexts (in production, this would be in Redis or similar)
        self.user_contexts = {}
    
    def load_disease_info(self) -> Dict:
        """Load disease information from JSON file"""
        try:
            disease_info_path = Path(__file__).parent / "Chatbot" / "disease_info.json"
            with open(disease_info_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def detect_disease_context(self, user_input: str) -> Optional[str]:
        """Detect disease mentioned in user input"""
        user_input_lower = user_input.lower()
        
        for disease in self.disease_keywords:
            if disease in user_input_lower:
                return disease
        
        return None
    
    def is_followup_question(self, user_input: str) -> bool:
        """Check if this is a follow-up question"""
        followup_patterns = [
            r'\b(it|this|that|the disease|the problem)\b',
            r'\b(how to|what about|can you|should I)\b',
            r'\b(more|additional|further|else)\b'
        ]
        
        user_input_lower = user_input.lower()
        for pattern in followup_patterns:
            if re.search(pattern, user_input_lower):
                return True
        
        return False
    
    def get_disease_specific_info(self, disease: str, question_type: str = "general") -> str:
        """Get specific information about a disease"""
        if disease not in self.disease_info:
            return ""
        
        disease_data = self.disease_info[disease]
        
        if question_type == "treatment" and "treatment" in disease_data:
            return f"Treatment for {disease}: {disease_data['treatment']}"
        elif question_type == "symptoms" and "symptoms" in disease_data:
            return f"Symptoms of {disease}: {disease_data['symptoms']}"
        elif question_type == "prevention" and "prevention" in disease_data:
            return f"Prevention of {disease}: {disease_data['prevention']}"
        elif "description" in disease_data:
            return f"About {disease}: {disease_data['description']}"
        
        return ""
    
    def generate_response(self, user_input: str, user_id: int, db: Session) -> Dict[str, str]:
        """Generate chatbot response with context awareness"""
        
        # Get user's conversation context
        user_context = self.user_contexts.get(user_id, {})
        current_disease = user_context.get("current_disease")
        
        # Detect disease in current input
        detected_disease = self.detect_disease_context(user_input)
        is_followup = self.is_followup_question(user_input)
        
        # Determine context
        if detected_disease:
            current_disease = detected_disease
            self.user_contexts[user_id] = {"current_disease": current_disease}
        elif is_followup and current_disease:
            # Continue with previous disease context
            pass
        else:
            # No specific disease context
            current_disease = None
        
        # Generate prompt based on context
        prompt = self.create_prompt(user_input, current_disease, is_followup)
        
        # Generate response
        response = self.generate_chatbot_response(prompt)
        
        # Add disease-specific information if relevant
        enhanced_response = self.enhance_response_with_disease_info(
            response, current_disease, user_input
        )
        
        # Save to database
        self.save_chat_to_db(db, user_id, user_input, enhanced_response, current_disease)
        
        return {
            "response": enhanced_response,
            "disease_context": current_disease
        }
    
    def create_prompt(self, user_input: str, disease_context: str = None, is_followup: bool = False) -> str:
        """Create appropriate prompt for the chatbot"""
        
        if disease_context and is_followup:
            if "treat" in user_input.lower() or "cure" in user_input.lower():
                return f"Treatment for {disease_context}: {user_input}"
            elif "symptom" in user_input.lower() or "sign" in user_input.lower():
                return f"Symptoms of {disease_context}: {user_input}"
            elif "prevent" in user_input.lower():
                return f"Prevention of {disease_context}: {user_input}"
            else:
                return f"For {disease_context}: {user_input}"
        elif disease_context:
            return f"Question about {disease_context}: {user_input}"
        else:
            return f"Question about plant disease: {user_input}"
    
    def generate_chatbot_response(self, prompt: str) -> str:
        """Generate response using the trained model"""
        max_attempts = 3
        best_answer = None
        best_answer_length = 0
        
        for attempt in range(max_attempts):
            temp = 0.7 + (attempt * 0.1)
            
            try:
                response = self.chatbot(
                    prompt,
                    max_length=len(prompt.split()) + 60,
                    truncation=True,
                    temperature=temp,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
                generated_text = response[0]["generated_text"]
                answer = generated_text[len(prompt):].strip()
                
                if len(answer.split()) > best_answer_length:
                    best_answer = answer
                    best_answer_length = len(answer.split())
                
                if best_answer_length >= 8:
                    break
                    
            except Exception as e:
                print(f"Error generating response: {e}")
                continue
        
        if best_answer_length < 5:
            return "I need more information about this plant disease. Could you rephrase your question?"
        
        return best_answer
    
    def enhance_response_with_disease_info(self, response: str, disease: str, user_input: str) -> str:
        """Enhance response with specific disease information"""
        if not disease or disease not in self.disease_info:
            return response
        
        disease_data = self.disease_info[disease]
        user_input_lower = user_input.lower()
        
        # Add specific information based on question type
        additional_info = ""
        
        if "treat" in user_input_lower and "treatment" in disease_data:
            additional_info = f"\n\nTreatment: {disease_data['treatment']}"
        elif "symptom" in user_input_lower and "symptoms" in disease_data:
            additional_info = f"\n\nSymptoms: {disease_data['symptoms']}"
        elif "prevent" in user_input_lower and "prevention" in disease_data:
            additional_info = f"\n\nPrevention: {disease_data['prevention']}"
        
        return response + additional_info
    
    def save_chat_to_db(self, db: Session, user_id: int, message: str, response: str, disease_context: str = None):
        """Save chat history to database"""
        chat_entry = ChatHistory(
            user_id=user_id,
            message=message,
            response=response,
            disease_context=disease_context
        )
        
        db.add(chat_entry)
        db.commit()
    
    def get_user_chat_history(self, db: Session, user_id: int, limit: int = 50) -> List[ChatHistory]:
        """Get user's chat history"""
        return db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id
        ).order_by(ChatHistory.created_at.desc()).limit(limit).all()

# Global chatbot instance
chatbot_service = PlantCareChatbot() 