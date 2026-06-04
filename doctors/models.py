from django.db import models


class Doctor(models.Model):
    """Doctor profile for the 'Who We Are' public page."""

    name = models.CharField(max_length=200)
    specialty = models.CharField(max_length=200)
    qualification = models.CharField(max_length=300)
    photo = models.ImageField(upload_to='doctors/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        db_table = 'doctors'

    def __str__(self):
        return f"Dr. {self.name} - {self.specialty}"
