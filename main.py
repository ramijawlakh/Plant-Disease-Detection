from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer
import shutil
import os
import re
from pathlib import Path
from predictyolo import run_inference

app = FastAPI()

# ------------------- Object Detection (YOLOv11) ------------------- #
TEMP_DIR = Path("/tmp/uploads")
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/predict/")
async def predict(
    file: UploadFile = File(...), 
    confidence_threshold: float = Form(0.5), 
    output_dir: str = Form("/tmp/output")
):
    """
    Upload an image, run YOLOv11 object detection, and return the processed image.
    """
    output_path = Path(output_dir)
    os.makedirs(output_path, exist_ok=True)

    # Save uploaded file to temporary directory
    img_path = TEMP_DIR / file.filename
    with open(img_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run YOLO inference
    run_inference(str(TEMP_DIR), str(output_path), confidence_threshold)

    # Return the processed image
    predicted_image_path = output_path / f'predicted_{file.filename}'
    return FileResponse(predicted_image_path)


# ------------------- Plant Disease Chatbot ------------------- #
#model_path = r"C:\Senior3\Chatbot\modelv4"  # Ensure your model is inside the "model" folder
model_path = "/app/modelv4"
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

# Conversation tracking
conversation_history = {}
current_disease = None
previous_question = None
previous_response = None

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

    # Generate response
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

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# This serves the frontend folder
#app.mount("/", StaticFiles(directory=r"C:\Senior3\frontend", html=True), name="frontend")
from pathlib import Path

FRONTEND_DIR = Path(__file__).parent / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")