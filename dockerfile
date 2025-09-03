FROM python:3.11-slim

LABEL maintainer="Your Name"
LABEL description="Helsinki Tech Analyst Pipeline"
LABEL version="1.0"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ ./src

# Create __init__.py files to make directories proper Python packages
RUN touch src/__init__.py && \
    touch src/data_pipeline/__init__.py && \
    touch src/ml_logic/__init__.py

RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Document DB port
EXPOSE 5432 8080 5000

CMD ["python", "-m", "src.data_pipeline.main"]