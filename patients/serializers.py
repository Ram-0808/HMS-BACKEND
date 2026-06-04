from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    """Full patient detail serializer."""
    created_by_name = serializers.CharField(
        source='created_by.username', read_only=True, default=None
    )
    gender_display = serializers.CharField(
        source='get_gender_display', read_only=True
    )
    payment_method_display = serializers.CharField(
        source='get_payment_method_display', read_only=True
    )

    class Meta:
        model = Patient
        fields = [
            'id', 'name', 'age', 'gender', 'gender_display',
            'problem', 'diagnosis', 'visit_count', 'fee_amount',
            'payment_method', 'payment_method_display', 'phone',
            'address', 'created_at', 'updated_at',
            'created_by', 'created_by_name',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class PatientListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views."""
    gender_display = serializers.CharField(
        source='get_gender_display', read_only=True
    )
    payment_method_display = serializers.CharField(
        source='get_payment_method_display', read_only=True
    )

    class Meta:
        model = Patient
        fields = [
            'id', 'name', 'age', 'gender', 'gender_display',
            'visit_count', 'fee_amount', 'payment_method',
            'payment_method_display', 'created_at',
        ]


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for admin dashboard statistics."""
    total_patients = serializers.IntegerField()
    today_patients = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    today_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
