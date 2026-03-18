"""Celery application configuration."""

from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "ai_pulse",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_default_queue="default",
    beat_schedule={
        "ingest-all-sources-every-30m": {
            "task": "app.tasks.ingest.ingest_all_sources",
            "schedule": crontab(minute="*/30"),
        },
    },
)

# Auto-discover tasks in app.tasks
celery_app.autodiscover_tasks(["app.tasks"])
