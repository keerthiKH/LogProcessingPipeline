FROM python:3.11-slim

# Disable Python output buffering
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create logs directory
RUN mkdir -p /logs

# Run the application
CMD ["python", "app.py"]
