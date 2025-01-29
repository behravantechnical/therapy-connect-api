from django.contrib import admin

from .models import PatientProfile, PsychologicalIssue, TherapistProfile

admin.site.register(PsychologicalIssue)
admin.site.register(PatientProfile)
admin.site.register(TherapistProfile)
