from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, dashboard_stats

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')

urlpatterns = [
    # Dashboard statistics
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),

    # Patient CRUD
    path('', include(router.urls)),
]
