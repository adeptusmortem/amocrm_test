from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Server, Metric, Incident
import random

@shared_task
def poll_servers():
    servers = Server.objects.filter(is_active=True)
    for server in servers:
        # Заглушка для эндпоинта
        data = {
            "cpu": random.uniform(0, 100),
            "mem": f"{random.uniform(0, 100)}%",
            "disk": f"{random.uniform(0, 100)}%",
            "uptime": "1d 2h 37m 6s"
        }
        Metric.objects.create(
            server=server,
            cpu=data['cpu'],
            mem=float(data['mem'].strip('%')),
            disk=float(data['disk'].strip('%')),
            uptime=data['uptime']
        )

@shared_task
def check_incidents():
    servers = Server.objects.filter(is_active=True)
    for server in servers:
        check_parameter(server, 'cpu', 85, timedelta(minutes=30))
        check_parameter(server, 'mem', 90, timedelta(minutes=30))
        check_parameter(server, 'disk', 95, timedelta(hours=2))

def check_parameter(server, param, threshold, duration):
    now = timezone.now()
    start_check = now - duration
    metrics = Metric.objects.filter(
        server=server,
        timestamp__gte=start_check,
        timestamp__lte=now
    )
    if not metrics:
        return

    min_value = min(getattr(m, param) for m in metrics)
    incident = Incident.objects.filter(
        server=server,
        parameter=param,
        is_resolved=False
    ).first()

    if min_value > threshold:
        if not incident:
            Incident.objects.create(
                server=server,
                parameter=param,
                start_time=start_check,
                is_resolved=False
            )
    else:
        if incident:
            incident.end_time = now
            incident.is_resolved = True
            incident.save()