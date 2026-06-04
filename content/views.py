from django.http import HttpResponse, Http404
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import SiteSetting, GalleryImage, StoredImage
from .serializers import SiteSettingSerializer, GalleryImageSerializer
from .permissions import IsStaffUser


class SiteSettingDetailView(APIView):
    """
    GET  /api/settings/  → Public — returns current site settings
    PUT  /api/settings/  → Staff only — update settings (multipart for image upload)
    PATCH /api/settings/ → Staff only — partial update
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsStaffUser()]

    def get(self, request):
        settings = SiteSetting.get_settings()
        serializer = SiteSettingSerializer(settings)
        return Response(serializer.data)

    def put(self, request):
        settings = SiteSetting.get_settings()
        serializer = SiteSettingSerializer(settings, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request):
        settings = SiteSetting.get_settings()
        serializer = SiteSettingSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class GalleryImageViewSet(viewsets.ModelViewSet):
    """
    CRUD for gallery/carousel images.
    Public read, staff write.
    """

    serializer_class = GalleryImageSerializer

    def get_queryset(self):
        if self.action in ('list', 'retrieve'):
            # Public endpoints: only show active images
            return GalleryImage.objects.filter(is_active=True)
        # Admin endpoints (create/update/delete): allow access to ALL images
        return GalleryImage.objects.all()

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated(), IsStaffUser()]


def serve_stored_image(request, image_id):
    """
    Serve an image stored in the database.
    URL: /api/images/<uuid>/
    Public endpoint — no authentication required.
    """
    try:
        img = StoredImage.objects.get(pk=image_id)
    except StoredImage.DoesNotExist:
        raise Http404("Image not found")

    response = HttpResponse(img.data, content_type=img.content_type)
    response['Content-Disposition'] = f'inline; filename="{img.filename}"'
    response['Cache-Control'] = 'public, max-age=86400'  # Cache for 24 hours
    return response
