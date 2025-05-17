# Use official Python image
# FROM python:3.10

# # Set working directory
# WORKDIR /app


# # Install system dependencies for OpenCV
# RUN apt-get update && apt-get install -y \
#     libgl1-mesa-glx \
#     libglib2.0-0 \
#     && rm -rf /var/lib/apt/lists/*



# Instead of python:3.10, pick NVIDIA's CUDA + cuDNN image
FROM nvidia/cuda:12.0.1-cudnn8-runtime-ubuntu22.04


# Set working directory
WORKDIR /app

# Install Python & pip (Ubuntu variant)
RUN apt-get update && apt-get install -y \
    python3.10 python3.10-venv python3-pip \
    libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*



# Install dependencies
#RUN pip install --no-cache-dir -r requirements.txt

COPY requirements.txt .

RUN pip install -r requirements.txt

# Copy files
COPY . /app



# Expose port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
