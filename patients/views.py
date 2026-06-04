from django.db.models import Sum
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Patient
from .serializers import (
    PatientSerializer,
    PatientListSerializer,
    DashboardStatsSerializer,
)


class PatientViewSet(viewsets.ModelViewSet):
    """
    CRUD for patient records.
    List uses a lighter serializer; detail/create/update uses the full one.
    Supports filtering by search, gender, payment_method, date_from, date_to.
    """

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return PatientListSerializer
        return PatientSerializer

    def get_queryset(self):
        queryset = Patient.objects.all()

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        gender = self.request.query_params.get('gender')
        if gender:
            queryset = queryset.filter(gender=gender)

        payment = self.request.query_params.get('payment_method')
        if payment:
            queryset = queryset.filter(payment_method=payment)

        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    GET /api/dashboard/stats/
    Returns summary numbers for the admin dashboard.
    """
    today = timezone.now().date()
    all_patients = Patient.objects.all()
    today_qs = all_patients.filter(created_at__date=today)

    total_revenue = all_patients.aggregate(total=Sum('fee_amount'))['total'] or 0
    today_revenue = today_qs.aggregate(total=Sum('fee_amount'))['total'] or 0

    stats = {
        'total_patients': all_patients.count(),
        'today_patients': today_qs.count(),
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
    }
    serializer = DashboardStatsSerializer(stats)
    return Response(serializer.data)
