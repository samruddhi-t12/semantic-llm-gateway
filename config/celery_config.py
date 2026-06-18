import os

# Tell Celery to use our Redis container as the message broker
broker_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
result_backend = broker_url

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True