from rest_framework import serializers
from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    """Doctor profile serializer for public + admin use."""

    class Meta:
        model = Doctor
        fields = [
            'id', 'name', 'specialty', 'qualification',
            'photo', 'bio', 'is_active', 'created_at',
        ]
