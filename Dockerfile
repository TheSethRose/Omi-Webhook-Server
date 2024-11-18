FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy env.example as .env if no .env exists
COPY env.example .env.example
RUN if [ ! -f .env ]; then cp .env.example .env; fi

# Copy the rest of the application
COPY . .

# Expose the port defined in .env
EXPOSE 32768

# Add healthcheck
HEALTHCHECK --interval=300s --timeout=120s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:32768/webhook?uid=health-check&key=${WEBHOOK_SECRET} -X POST -H "Content-Type: application/json" -d '{"type":"ping"}' || exit 1

# Command to run the server
CMD ["python", "server.py"]
