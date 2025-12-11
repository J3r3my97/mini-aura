FROM python:3.11-slim

# Install system dependencies for image processing
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download rembg model during build (so it's cached in image)
RUN python -c "from rembg import new_session; new_session('u2net')"

# Copy application code
COPY . .

# Run the worker service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
