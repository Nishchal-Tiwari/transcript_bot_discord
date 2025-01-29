# Use an official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive
ENV OPUS_PATH="/usr/lib/x86_64-linux-gnu/libopus.so.0"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    redis-server \
    libopus-dev \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the project files
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
# Install dependencies in editable mode
RUN pip install --no-cache-dir -e .

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose Redis port (optional, for debugging)
EXPOSE 6379

# Start Redis and Supervisor to manage processes
CMD redis-server --daemonize yes && supervisord -c /etc/supervisor/conf.d/supervisord.conf
