#!/bin/bash

# Start Redis server in the background
redis-server --port 6380 &

# Wait for Redis to start
sleep 5

# Export environment variables for Redis connection
export REDIS_URL=redis://localhost:6380/0
export CELERY_BROKER_URL=redis://localhost:6380/0
export CELERY_RESULT_BACKEND=redis://localhost:6380/0

# Start Celery workers (50 worker concurrency)
celery -A app.worker.celery_app worker --loglevel=info --concurrency=50 &

# Wait for Celery to initialize
sleep 2

# Run FastAPI application 
uvicorn app.main:app --host 0.0.0.0 --port 3657
