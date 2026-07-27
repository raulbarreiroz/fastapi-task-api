# Slim image to reduce size
FROM python:3.11-slim

# Prevent Python from writing .pyc files and disable output buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory inside the container
WORKDIR /app

# Copy and install dependencies first (leveraging Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY ./app ./app

# Expose the port (default 8000, can be overridden at runtime)
EXPOSE 8000

# Default command for production using Gunicorn with Uvicorn workers.
# The number of workers and port can be overridden via environment variables
# at container runtime (e.g., in docker-compose).
CMD ["sh", "-c", "gunicorn app.main:app --workers ${WORKERS:-4} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000}"]