from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import SiteSetting, GalleryImage
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
    queryset = GalleryImage.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated(), IsStaffUser()]
