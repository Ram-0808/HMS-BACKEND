from rest_framework import serializers
from .models import SiteSetting, GalleryImage


class SiteSettingSerializer(serializers.ModelSerializer):
    """Serializer for site-wide configurable settings."""

    class Meta:
        model = SiteSetting
        fields = [
            'id',
            # Images
            'hospital_image',
            # About Us
            'hero_tagline', 'about_story',
            # Vision
            'vision_statement',
            # Contact
            'phone', 'emergency_phone', 'email',
            'address', 'working_hours',
            # Metadata
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']


class GalleryImageSerializer(serializers.ModelSerializer):
    """Serializer for gallery images (carousel)."""

    class Meta:
        model = GalleryImage
        fields = ['id', 'image', 'caption', 'order', 'is_active', 'created_at']
