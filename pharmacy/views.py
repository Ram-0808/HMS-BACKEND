from datetime import timedelta

from django.db.models import Sum, F, Q
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError

from .models import Medicine, Vendor, MedicineBatch, Sale
from .serializers import (
    MedicineListSerializer,
    MedicineDetailSerializer,
    VendorSerializer,
    MedicineBatchListSerializer,
    MedicineBatchDetailSerializer,
    SaleListSerializer,
    SaleCreateSerializer,
    PharmacyDashboardStatsSerializer,
)
from .permissions import IsStaffUser


class MedicineViewSet(viewsets.ModelViewSet):
    """CRUD for medicine catalog."""

    permission_classes = [IsAuthenticated, IsStaffUser]

    def get_serializer_class(self):
        if self.action == 'list':
            return MedicineListSerializer
        return MedicineDetailSerializer

    def get_queryset(self):
        queryset = Medicine.objects.annotate(
            annotated_total_stock=Sum(
                'batches__quantity_remaining',
                filter=Q(batches__quantity_remaining__gt=0)
            ),
        ).annotate(
            annotated_is_low_stock=Q(annotated_total_stock__lte=F('reorder_level')),
        )

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(generic_name__icontains=search)
            )

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        stock_filter = self.request.query_params.get('stock')
        if stock_filter == 'low':
            queryset = queryset.filter(annotated_total_stock__lte=F('reorder_level'))
        elif stock_filter == 'out':
            queryset = queryset.filter(Q(annotated_total_stock=0) | Q(annotated_total_stock__isnull=True))

        return queryset


class VendorViewSet(viewsets.ModelViewSet):
    """CRUD for vendors/suppliers."""

    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated, IsStaffUser]

    def get_queryset(self):
        queryset = Vendor.objects.all()

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(contact_person__icontains=search)
            )

        return queryset


class MedicineBatchViewSet(viewsets.ModelViewSet):
    """CRUD for purchase batches (stock IN)."""

    permission_classes = [IsAuthenticated, IsStaffUser]

    def get_serializer_class(self):
        if self.action == 'list':
            return MedicineBatchListSerializer
        return MedicineBatchDetailSerializer

    def get_queryset(self):
        queryset = MedicineBatch.objects.select_related('medicine', 'vendor').all()

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(batch_number__icontains=search) | Q(medicine__name__icontains=search)
            )

        medicine = self.request.query_params.get('medicine')
        if medicine:
            queryset = queryset.filter(medicine_id=medicine)

        vendor = self.request.query_params.get('vendor')
        if vendor:
            queryset = queryset.filter(vendor_id=vendor)

        expiry = self.request.query_params.get('expiry')
        today = timezone.now().date()
        if expiry == 'expired':
            queryset = queryset.filter(expiry_date__lt=today)
        elif expiry == 'expiring_soon':
            queryset = queryset.filter(
                expiry_date__gte=today,
                expiry_date__lte=today + timedelta(days=30),
                quantity_remaining__gt=0,
            )

        return queryset

    def perform_create(self, serializer):
        qty_purchased = serializer.validated_data['quantity_purchased']
        serializer.save(
            created_by=self.request.user,
            quantity_remaining=qty_purchased,
        )


class SaleViewSet(viewsets.ModelViewSet):
    """Record and view sales (stock OUT)."""

    permission_classes = [IsAuthenticated, IsStaffUser]

    def get_serializer_class(self):
        if self.action == 'list':
            return SaleListSerializer
        return SaleCreateSerializer

    def get_queryset(self):
        queryset = Sale.objects.select_related('medicine', 'batch', 'patient').all()

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(medicine__name__icontains=search) | Q(patient__name__icontains=search)
            )

        medicine = self.request.query_params.get('medicine')
        if medicine:
            queryset = queryset.filter(medicine_id=medicine)

        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(sale_date__date__gte=date_from)

        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(sale_date__date__lte=date_to)

        return queryset

    def perform_create(self, serializer):
        with transaction.atomic():
            batch = serializer.validated_data['batch']
            batch = MedicineBatch.objects.select_for_update().get(pk=batch.pk)
            quantity = serializer.validated_data['quantity']

            if quantity > batch.quantity_remaining:
                raise DRFValidationError(
                    {'quantity': f'Only {batch.quantity_remaining} units available.'}
                )

            batch.quantity_remaining -= quantity
            batch.save(update_fields=['quantity_remaining'])

            serializer.save(sold_by=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffUser])
def pharmacy_dashboard_stats(request):
    """GET /api/pharmacy/dashboard/stats/ — pharmacy summary statistics."""
    today = timezone.now().date()

    all_medicines = Medicine.objects.annotate(
        annotated_total_stock=Sum(
            'batches__quantity_remaining',
            filter=Q(batches__quantity_remaining__gt=0)
        )
    )

    total_medicines = Medicine.objects.filter(is_active=True).count()
    low_stock_count = all_medicines.filter(
        annotated_total_stock__lte=F('reorder_level'), is_active=True,
    ).count()
    out_of_stock_count = all_medicines.filter(
        Q(annotated_total_stock=0) | Q(annotated_total_stock__isnull=True), is_active=True,
    ).count()
    expiring_soon_count = MedicineBatch.objects.filter(
        expiry_date__gte=today,
        expiry_date__lte=today + timedelta(days=30),
        quantity_remaining__gt=0,
    ).count()

    today_sales = Sale.objects.filter(sale_date__date=today)
    today_sales_count = today_sales.count()
    today_sales_revenue = today_sales.aggregate(total=Sum('total_amount'))['total'] or 0

    total_stock_value = MedicineBatch.objects.filter(
        quantity_remaining__gt=0
    ).aggregate(
        total=Sum(F('quantity_remaining') * F('selling_price'))
    )['total'] or 0

    stats = {
        'total_medicines': total_medicines,
        'low_stock_count': low_stock_count,
        'expiring_soon_count': expiring_soon_count,
        'out_of_stock_count': out_of_stock_count,
        'today_sales_count': today_sales_count,
        'today_sales_revenue': today_sales_revenue,
        'total_stock_value': total_stock_value,
    }

    serializer = PharmacyDashboardStatsSerializer(stats)
    return Response(serializer.data)
