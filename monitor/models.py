from django.db import models

class Server(models.Model):
    name = models.CharField(max_length=100)
    endpoint = models.URLField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Metric(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    cpu = models.FloatField()
    mem = models.FloatField()
    disk = models.FloatField()
    uptime = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.server} - {self.timestamp}"

class Incident(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    parameter = models.CharField(max_length=10, choices=[('cpu', 'CPU'), ('mem', 'Memory'), ('disk', 'Disk')])
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.server} - {self.parameter} incident"
    
