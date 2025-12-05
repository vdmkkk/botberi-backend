from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    settings.app_name,
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
)
celery_app.conf.task_default_queue = settings.celery_default_queue
celery_app.conf.task_routes = {"app.workers.tasks.*": {"queue": settings.celery_default_queue}}


@celery_app.task(name="health.ping")
def ping() -> str:
    """Simple heartbeat task to validate Celery wiring."""
    return "pong"


__all__ = ["celery_app"]


