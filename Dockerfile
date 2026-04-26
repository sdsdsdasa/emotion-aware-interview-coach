# syntax=docker/dockerfile:1

# Base Python image
FROM python:3.11-slim

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create app directory inside container
WORKDIR /app

# Install system packages if needed (extend later)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN pip install fastapi[standard]

# Copy the entire project
COPY . .

# RUN FASTAPI SERVER instead of Python script
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
