from .models import StoredImage
from .validators import validate_image_size


def store_uploaded_image(uploaded_file):
    """
    Process an uploaded image file and store it in the database.
    Returns a StoredImage instance or None if the file is empty.
    Raises ValidationError if file exceeds 1MB size limit.
    """
    if not uploaded_file:
        return None

    # Validate size (1MB limit)
    validate_image_size(uploaded_file)

    # Read binary data
    uploaded_file.seek(0)
    data = uploaded_file.read()

    # Determine content type
    content_type = getattr(uploaded_file, 'content_type', 'image/jpeg') or 'image/jpeg'

    # Get filename
    filename = getattr(uploaded_file, 'name', '') or ''

    return StoredImage.objects.create(
        data=data,
        content_type=content_type,
        filename=filename,
        size=len(data),
    )
