# Use lightweight Debian slim base
FROM python:3.11-slim

# Set some env variables
ARG APP_VERSION="unknown"
ENV APP_VERSION=${APP_VERSION}
ENV MAX_UPLOAD_SIZE_MB=10

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    poppler-utils \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app source
COPY app ./app

# Expose API port
EXPOSE 8000

# Command to start the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]