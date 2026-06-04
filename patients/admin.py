from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'age', 'gender', 'fee_amount',
        'payment_method', 'visit_count', 'created_at',
    ]
    list_filter = ['gender', 'payment_method', 'created_at']
    search_fields = ['name', 'problem', 'diagnosis']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
