import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitoring.settings')
app = Celery('monitoring')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'poll-servers': {
        'task': 'monitor.tasks.poll_servers',
        'schedule': 900.0,  # 15 минут
    },
    'check-incidents': {
        'task': 'monitor.tasks.check_incidents',
        'schedule': 300.0,  # 5 минут
    },
}