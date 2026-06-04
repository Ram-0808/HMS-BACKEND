from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from content.views import serve_stored_image

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Image serving from database (public)
    path('api/images/<uuid:image_id>/', serve_stored_image, name='serve-image'),

    # App APIs
    path('api/', include('patients.urls')),
    path('api/', include('doctors.urls')),
    path('api/', include('content.urls')),
]

# Serve media files during development (fallback for any legacy files)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
