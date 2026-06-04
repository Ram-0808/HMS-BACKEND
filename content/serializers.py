from rest_framework import serializers
from .models import SiteSetting, GalleryImage, StoredImage
from .image_utils import store_uploaded_image
from .validators import validate_image_size


class SiteSettingSerializer(serializers.ModelSerializer):
    """Serializer for site-wide configurable settings."""
    hospital_image = serializers.SerializerMethodField()

    class Meta:
        model = SiteSetting
        fields = [
            'id',
            'hospital_image',
            'hero_tagline', 'about_story',
            'vision_statement',
            'phone', 'emergency_phone', 'email',
            'address', 'working_hours',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']

    def get_hospital_image(self, obj):
        if obj.hospital_image:
            request = self.context.get('request')
            url = f"/api/images/{obj.hospital_image.id}/"
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def update(self, instance, validated_data):
        request = self.context.get('request')
        uploaded_file = request.data.get('hospital_image') if request else None

        if uploaded_file == '':
            # Remove the image
            if instance.hospital_image:
                old = instance.hospital_image
                instance.hospital_image = None
                instance.save()
                old.delete()
            return instance

        if uploaded_file:
            validate_image_size(uploaded_file)
            stored = store_uploaded_image(uploaded_file)
            old = instance.hospital_image
            instance.hospital_image = stored
            instance.save(update_fields=['hospital_image'])
            if old:
                old.delete()
            return instance

        return super().update(instance, validated_data)


class GalleryImageSerializer(serializers.ModelSerializer):
    """Serializer for gallery images (carousel)."""
    image = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        fields = ['id', 'image', 'caption', 'order', 'is_active', 'created_at']

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            url = f"/api/images/{obj.image.id}/"
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        uploaded_file = request.data.get('image') if request else None

        if uploaded_file:
            validate_image_size(uploaded_file)
            stored = store_uploaded_image(uploaded_file)
            validated_data['image'] = stored

        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        uploaded_file = request.data.get('image') if request else None

        if uploaded_file:
            validate_image_size(uploaded_file)
            stored = store_uploaded_image(uploaded_file)
            old = instance.image
            instance.image = stored
            instance.save(update_fields=['image'])
            old.delete()
            return instance

        return super().update(instance, validated_data)
