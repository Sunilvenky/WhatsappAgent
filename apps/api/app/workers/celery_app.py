"""
Celery app configuration for async task processing.
"""
from celery import Celery
from celery.schedules import crontab
from ..core.config import settings

# Create Celery app
celery_app = Celery(
    "whatsapp_agent",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.campaign_worker",
        "app.workers.message_worker",
        "app.workers.analytics_worker",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,  # One task at a time for throttling
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    task_acks_late=True,  # Acknowledge task after completion
    task_reject_on_worker_lost=True,
    result_expires=3600,  # Results expire after 1 hour
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    "process-scheduled-campaigns": {
        "task": "app.workers.campaign_worker.process_scheduled_campaigns",
        "schedule": 60.0,  # Every minute
    },
    "process-drip-campaigns": {
        "task": "app.workers.campaign_worker.process_drip_sequences",
        "schedule": 300.0,  # Every 5 minutes
    },
    "cleanup-old-messages": {
        "task": "app.workers.message_worker.cleanup_old_messages",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    "update-analytics": {
        "task": "app.workers.analytics_worker.update_campaign_analytics",
        "schedule": 600.0,  # Every 10 minutes
    },
    "check-ban-risks": {
        "task": "app.workers.campaign_worker.monitor_ban_risks",
        "schedule": 1800.0,  # Every 30 minutes
    },
}

# Task routes
celery_app.conf.task_routes = {
    "app.workers.campaign_worker.*": {"queue": "campaigns"},
    "app.workers.message_worker.*": {"queue": "messages"},
    "app.workers.analytics_worker.*": {"queue": "analytics"},
}
