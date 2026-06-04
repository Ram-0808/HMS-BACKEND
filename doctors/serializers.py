from rest_framework import serializers
from .models import Doctor
from content.image_utils import store_uploaded_image
from content.validators import validate_image_size


class DoctorSerializer(serializers.ModelSerializer):
    """Doctor profile serializer for public + admin use."""
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = [
            'id', 'name', 'specialty', 'qualification',
            'photo', 'bio', 'is_active', 'created_at',
        ]

    def get_photo(self, obj):
        """Return the URL to serve the image, or null."""
        if obj.photo:
            request = self.context.get('request')
            url = f"/api/images/{obj.photo.id}/"
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        uploaded_file = request.data.get('photo') if request else None

        if uploaded_file:
            validate_image_size(uploaded_file)
            stored = store_uploaded_image(uploaded_file)
            validated_data['photo'] = stored

        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        uploaded_file = request.data.get('photo') if request else None

        if uploaded_file == '':
            # Empty string means "remove the photo"
            if instance.photo:
                old = instance.photo
                instance.photo = None
                instance.save()
                old.delete()
            return instance

        if uploaded_file:
            validate_image_size(uploaded_file)
            stored = store_uploaded_image(uploaded_file)
            # Clean up old image
            old = instance.photo
            instance.photo = stored
            instance.save(update_fields=['photo'])
            if old:
                old.delete()
            return instance

        return super().update(instance, validated_data)
