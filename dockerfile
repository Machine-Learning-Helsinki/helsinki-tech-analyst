FROM python:3.12-slim

# Add metadata
LABEL maintainer="Your Name"
LABEL description="Helsinki Tech Analyst Pipeline"
LABEL version="1.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./

# Security: Create and switch to non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

CMD ["python", "-m", "data_pipeline.main"]