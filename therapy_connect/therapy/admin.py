from django.contrib import admin

from .models import Appointment, Availability, TherapyPanel

admin.site.register(Availability)
admin.site.register(TherapyPanel)
admin.site.register(Appointment)
