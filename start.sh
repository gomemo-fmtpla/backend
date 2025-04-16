#!/bin/bash

# Start Redis server in the background
redis-server --port 6380 &

# Wait for Redis to start
sleep 2

# Start Celery workers (50 worker concurrency)
celery -A app.worker.celery_app worker --loglevel=info --concurrency=50 &

# Run FastAPI application 
uvicorn app.main:app --host 0.0.0.0 --port 3657 --reload
