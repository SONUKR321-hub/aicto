FROM python:3.11-slim

# Install FFmpeg and other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agent/ ./agent/
COPY main.py .
COPY config.yaml .

# Create necessary directories
RUN mkdir -p data/videos data/edited logs

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the agent
CMD ["python", "main.py", "--daemon"]
