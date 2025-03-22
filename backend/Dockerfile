FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY docker-requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r docker-requirements.txt

# Copy alembic configuration
COPY alembic.ini .

# Copy project files
COPY app/ /app/app/

# Additional tools for troubleshooting if needed
COPY run.py .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
