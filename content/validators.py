from rest_framework import serializers

MAX_IMAGE_SIZE = 1 * 1024 * 1024  # 1MB


def validate_image_size(file):
    """Validate uploaded image file size does not exceed 1MB."""
    if hasattr(file, 'size') and file.size > MAX_IMAGE_SIZE:
        raise serializers.ValidationError(
            f"Image file size must be under 1MB. Your file is "
            f"{file.size / (1024 * 1024):.1f}MB."
        )
