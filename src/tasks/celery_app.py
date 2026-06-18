from celery import Celery

celery = Celery(
    "gateway_tasks",
    broker="redis://127.0.0.1:6379/0",
    include=["src.tasks.workers"]
)

celery.config_from_object("config.celery_config")