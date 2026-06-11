from celery import Celery
from backend.app.core.config import settings

# Initialize Celery app
celery_app = Celery(
    "vishakan_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Celery configurations
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
)

# Optional: auto-discover tasks in services
# celery_app.autodiscover_tasks(['backend.app.services'])
