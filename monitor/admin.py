from django.contrib import admin
from .models import Server, Metric, Incident


admin.site.register(Server)
admin.site.register(Metric)
admin.site.register(Incident)