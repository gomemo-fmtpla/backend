from celery import Celery
from redis import Redis
from app.config import settings

# Configure Celery with Redis backend
celery_app = Celery(
    'audio_tasks',
    broker='redis://redis:6380/0',
    backend='redis://redis:6380/0'
)

# Optional configurations
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

redis_client = Redis.from_url(settings.REDIS_URL)
