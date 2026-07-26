# Slim image to reduce size
FROM python:3.11-slim

# Avoid python generate .pyc files and buffer in console
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Work directory inside the container
WORKDIR /app

# Copy and install dependencies fisrt (using cache of Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY ./app ./app

# Expose the port 6666
EXPOSE 6666

# Command to run the application (with hot reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]