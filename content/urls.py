from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SiteSettingDetailView, GalleryImageViewSet

router = DefaultRouter()
router.register(r'gallery', GalleryImageViewSet, basename='gallery')

urlpatterns = [
    path('settings/', SiteSettingDetailView.as_view(), name='site-settings'),
    path('', include(router.urls)),
]
