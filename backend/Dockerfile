# ShifaScribe Backend Dockerfile (FastAPI, PyTorch, Whisper AI & DRAP NLP)
FROM python:3.11-slim

# Prevent Python from writing .pyc and enable unbuffered stdout logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PORT=8000

WORKDIR /app

# Install essential OS dependencies for audio processing, libsndfile, ffmpeg, and C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libsndfile1 \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Ensure storage directory exists
RUN mkdir -p /app/storage/audio

# Expose FastAPI port
EXPOSE 8000

# Health check probe
HEALTHCHECK --interval=30s --timeout=10s --start-period=180s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch FastAPI server with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
