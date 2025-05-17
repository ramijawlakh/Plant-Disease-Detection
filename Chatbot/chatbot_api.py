from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer
import torch
import re

# Initialize FastAPI app
app = FastAPI()

# Load the fine-tuned chatbot model
model_path = "modelv4"  # Ensure your model is inside the "model" folder
tokenizer = AutoTokenizer.from_pretrained(model_path)

chatbot = pipeline(
    "text-generation",
    model=model_path,
    tokenizer=tokenizer,
    do_sample=True,
    top_p=0.92,
    temperature=0.7,
    no_repeat_ngram_size=3
)

# Conversation context tracking
conversation_history = {}
current_disease = None
previous_question = None
previous_response = None

# Define request format
class ChatRequest(BaseModel):
    user_input: str

@app.post("/chat")
def chat(request: ChatRequest):
    global current_disease, previous_question, previous_response

    user_input = request.user_input.lower()

    # Check if it's a follow-up question
    is_followup = bool(re.search(r'\b(it|this|that|the disease|the problem)\b', user_input))

    # List of plant diseases
    disease_keywords = [
        "early blight", "late blight", "apple scab", "black rot", "cedar apple rust",
        "powdery mildew", "downy mildew", "leaf spot", "bacterial spot", "tomato mosaic virus",
        "fusarium wilt", "verticillium wilt", "septoria leaf spot", "anthracnose"
    ]

    # Identify disease in input
    detected_disease = None
    for disease in disease_keywords:
        if disease in user_input:
            detected_disease = disease
            current_disease = disease
            break

    # Generate prompt based on context
    if is_followup and current_disease:
        prompt = f"For {current_disease}: {user_input}"

        if "treat" in user_input and previous_question and "identify" in previous_question:
            prompt = f"Treatment for {current_disease}: {user_input}"
    else:
        prompt = f"Question about plant disease: {user_input}"
        if detected_disease:
            prompt = f"Question about {detected_disease}: {user_input}"

    # Try multiple times to get a meaningful response
    max_attempts = 3
    best_answer = None
    best_answer_length = 0

    for attempt in range(max_attempts):
        temp = 0.7 + (attempt * 0.1)

        response = chatbot(
            prompt,
            max_length=len(prompt.split()) + 50,
            truncation=True,
            temperature=temp
        )

        # Extract the generated text
        generated_text = response[0]["generated_text"]
        answer = generated_text[len(prompt):].strip()

        if len(answer.split()) > best_answer_length and answer != previous_response:
            best_answer = answer
            best_answer_length = len(answer.split())

        if best_answer_length >= 8:
            break

    # Final response
    if best_answer_length < 5:
        answer = "I need more information about this plant disease. Could you rephrase your question?"
    else:
        answer = best_answer

    # Update conversation tracking
    previous_question = user_input
    previous_response = answer

    if current_disease:
        if current_disease not in conversation_history:
            conversation_history[current_disease] = {"questions": [], "responses": []}
        conversation_history[current_disease]["questions"].append(user_input)
        conversation_history[current_disease]["responses"].append(answer)

    return {"response": answer}
