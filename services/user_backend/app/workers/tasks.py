from celery import shared_task


@shared_task(name="instances.refresh_cache")
def refresh_instance_cache(instance_id: str) -> str:
    """Placeholder task to demonstrate structure."""
    return instance_id


