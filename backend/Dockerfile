# Use an official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose FastAPI port
EXPOSE 8002

# Default command
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
