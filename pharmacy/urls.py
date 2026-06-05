from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MedicineViewSet,
    VendorViewSet,
    MedicineBatchViewSet,
    SaleViewSet,
    pharmacy_dashboard_stats,
)

router = DefaultRouter()
router.register(r'pharmacy/medicines', MedicineViewSet, basename='pharmacy-medicine')
router.register(r'pharmacy/vendors', VendorViewSet, basename='pharmacy-vendor')
router.register(r'pharmacy/batches', MedicineBatchViewSet, basename='pharmacy-batch')
router.register(r'pharmacy/sales', SaleViewSet, basename='pharmacy-sale')

urlpatterns = [
    path('pharmacy/dashboard/stats/', pharmacy_dashboard_stats, name='pharmacy-dashboard-stats'),
    path('', include(router.urls)),
]
