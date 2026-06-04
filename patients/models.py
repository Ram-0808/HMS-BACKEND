from django.db import models
from django.contrib.auth.models import User


class Patient(models.Model):
    """Patient record for Swarna Hospitals."""

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    PAYMENT_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('UPI', 'UPI'),
    ]

    name = models.CharField(max_length=200)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    problem = models.TextField(help_text="Problem description / reason for visit")
    diagnosis = models.TextField(blank=True, default='')
    visit_count = models.PositiveIntegerField(default=1)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=4, choices=PAYMENT_CHOICES, default='CASH')
    phone = models.CharField(max_length=15, blank=True, default='')
    address = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'patients'

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d')}"
