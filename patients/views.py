from django.db.models import Sum, Count
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
    from doctors.models import Doctor
    from pharmacy.models import Sale

    today = timezone.now().date()
    all_patients = Patient.objects.all()
    today_qs = all_patients.filter(created_at__date=today)

    patient_revenue = all_patients.aggregate(total=Sum('fee_amount'))['total'] or 0
    patient_today_revenue = today_qs.aggregate(total=Sum('fee_amount'))['total'] or 0

    # Include pharmacy sales revenue
    pharmacy_revenue = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    pharmacy_today_revenue = Sale.objects.filter(
        sale_date__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    stats = {
        'total_patients': all_patients.count(),
        'today_patients': today_qs.count(),
        'total_doctors': Doctor.objects.count(),
        'total_revenue': patient_revenue + pharmacy_revenue,
        'today_revenue': patient_today_revenue + pharmacy_today_revenue,
    }
    serializer = DashboardStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_charts(request):
    """
    GET /api/dashboard/charts/
    Returns data for dashboard charts — last 7 days revenue and patient gender split.
    """
    from django.db.models.functions import TruncDate
    from doctors.models import Doctor
    from pharmacy.models import Sale
    from datetime import timedelta

    today = timezone.now().date()
    week_ago = today - timedelta(days=6)

    # Revenue per day — last 7 days (from patients table)
    patient_daily = (
        Patient.objects
        .filter(created_at__date__gte=week_ago, created_at__date__lte=today)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(revenue=Sum('fee_amount'))
        .order_by('date')
    )

    # Pharmacy sales revenue per day
    pharmacy_daily = (
        Sale.objects
        .filter(sale_date__date__gte=week_ago, sale_date__date__lte=today)
        .annotate(date=TruncDate('sale_date'))
        .values('date')
        .annotate(revenue=Sum('total_amount'))
        .order_by('date')
    )

    # Merge patient + pharmacy revenue by date
    revenue_map = {}
    for r in patient_daily:
        revenue_map[str(r['date'])] = float(r['revenue'] or 0)
    for r in pharmacy_daily:
        key = str(r['date'])
        revenue_map[key] = revenue_map.get(key, 0) + float(r['revenue'] or 0)

    daily_revenue = [{'date': k, 'revenue': v} for k, v in sorted(revenue_map.items())]

    # Patient visits per day — last 7 days
    daily_visits = (
        Patient.objects
        .filter(created_at__date__gte=week_ago, created_at__date__lte=today)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Sum('visit_count'))
        .order_by('date')
    )

    # Gender distribution
    gender_dist = list(
        Patient.objects
        .values('gender')
        .annotate(count=Count('id'))
    )
    gender_map = {g['gender']: g['count'] for g in gender_dist}

    # Payment method distribution
    payment_dist = list(
        Patient.objects
        .values('payment_method')
        .annotate(count=Count('id'))
    )

    # Doctor count by specialty (active doctors)
    doctor_specialties = list(
        Doctor.objects.filter(is_active=True)
        .values('specialty')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    return Response({
        'daily_revenue': daily_revenue,
        'daily_visits': [
            {'date': str(v['date']), 'visits': v['count']}
            for v in daily_visits
        ],
        'gender_dist': {
            'male': gender_map.get('M', 0),
            'female': gender_map.get('F', 0),
            'other': gender_map.get('O', 0),
        },
        'payment_dist': [
            {'method': p['payment_method'], 'count': p['count']}
            for p in payment_dist
        ],
        'top_specialties': doctor_specialties,
        'total_doctors': Doctor.objects.filter(is_active=True).count(),
    })
