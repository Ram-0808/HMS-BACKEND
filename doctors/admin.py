from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialty', 'qualification', 'is_active', 'created_at']
    list_filter = ['is_active', 'specialty']
    search_fields = ['name', 'specialty']
