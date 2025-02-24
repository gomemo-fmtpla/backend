#!/bin/bash
redis-server --port 6380 --daemonize yes
celery -A app.tasks.audio_queue:celery_app worker --loglevel=info --concurrency=10 &
uvicorn app.main:app --host 0.0.0.0 --port 3657
