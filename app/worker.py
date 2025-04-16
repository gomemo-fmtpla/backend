import os
import time
from celery import Celery
from app.config import settings

# Inisialisasi Celery
celery_app = Celery('gomemo_app',
                    broker=settings.CELERY_BROKER_URL,
                    backend=settings.CELERY_RESULT_BACKEND)

# Konfigurasi Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_concurrency=50,  # 50 worker yang diminta
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_time_limit=3600,  # 1 jam time limit
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=20,
    broker_connection_timeout=30,
)

# Mencoba memastikan koneksi dengan Redis berhasil
print(f"Celery using broker URL: {settings.CELERY_BROKER_URL}")
print(f"Celery using result backend: {settings.CELERY_RESULT_BACKEND}")

# Import tugas-tugas
from app.tasks import youtube_tasks, audio_tasks 