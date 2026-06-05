from rest_framework import serializers
from .models import Medicine, Vendor, MedicineBatch, Sale


# -------------------------------------------------------
# Medicine Serializers
# -------------------------------------------------------

class MedicineListSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    unit_type_display = serializers.CharField(source='get_unit_type_display', read_only=True)
    total_stock = serializers.IntegerField(read_only=True, default=0)
    is_low_stock = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = Medicine
        fields = [
            'id', 'name', 'generic_name', 'category', 'category_display',
            'unit_type', 'unit_type_display', 'selling_price',
            'reorder_level', 'total_stock', 'is_low_stock',
            'is_active', 'created_at',
        ]


class MedicineDetailSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    unit_type_display = serializers.CharField(source='get_unit_type_display', read_only=True)
    total_stock = serializers.IntegerField(read_only=True, default=0)
    is_low_stock = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = Medicine
        fields = [
            'id', 'name', 'generic_name', 'category', 'category_display',
            'manufacturer', 'description', 'unit_type', 'unit_type_display',
            'selling_price', 'reorder_level', 'total_stock', 'is_low_stock',
            'is_active', 'created_at',
        ]
        read_only_fields = ['created_at']


# -------------------------------------------------------
# Vendor Serializers
# -------------------------------------------------------

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            'id', 'name', 'contact_person', 'phone', 'email',
            'address', 'gst_number', 'is_active', 'created_at',
        ]
        read_only_fields = ['created_at']


# -------------------------------------------------------
# MedicineBatch Serializers
# -------------------------------------------------------

class MedicineBatchListSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True, default=None)
    is_expired = serializers.BooleanField(read_only=True, default=False)
    is_expiring_soon = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = MedicineBatch
        fields = [
            'id', 'medicine', 'medicine_name', 'vendor', 'vendor_name',
            'batch_number', 'quantity_purchased', 'quantity_remaining',
            'cost_price', 'selling_price', 'manufacture_date', 'expiry_date',
            'purchase_date', 'is_expired', 'is_expiring_soon', 'created_at',
        ]


class MedicineBatchDetailSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True, default=None)
    is_expired = serializers.BooleanField(read_only=True, default=False)
    is_expiring_soon = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = MedicineBatch
        fields = [
            'id', 'medicine', 'medicine_name', 'vendor', 'vendor_name',
            'batch_number', 'quantity_purchased', 'quantity_remaining',
            'cost_price', 'selling_price', 'manufacture_date', 'expiry_date',
            'purchase_date', 'is_expired', 'is_expiring_soon',
            'created_at', 'created_by',
        ]
        read_only_fields = ['created_at', 'created_by']


# -------------------------------------------------------
# Sale Serializers
# -------------------------------------------------------

class SaleListSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True)
    patient_name = serializers.CharField(source='patient.name', read_only=True, default=None)

    class Meta:
        model = Sale
        fields = [
            'id', 'medicine', 'medicine_name', 'batch', 'batch_number',
            'patient', 'patient_name', 'quantity', 'unit_price',
            'total_amount', 'sale_date',
        ]


class SaleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = [
            'id', 'medicine', 'batch', 'patient',
            'quantity', 'unit_price', 'total_amount',
            'sale_date',
        ]
        read_only_fields = ['sale_date']

    def validate(self, data):
        batch = data['batch']
        quantity = data['quantity']
        unit_price = data['unit_price']

        if batch.medicine_id != data['medicine'].id:
            raise serializers.ValidationError(
                {'batch': 'Selected batch does not belong to the selected medicine.'}
            )

        if quantity > batch.quantity_remaining:
            raise serializers.ValidationError(
                {'quantity': f'Only {batch.quantity_remaining} units available in this batch.'}
            )

        data['total_amount'] = quantity * unit_price
        return data


# -------------------------------------------------------
# Pharmacy Dashboard Stats Serializer
# -------------------------------------------------------

class PharmacyDashboardStatsSerializer(serializers.Serializer):
    total_medicines = serializers.IntegerField()
    low_stock_count = serializers.IntegerField()
    expiring_soon_count = serializers.IntegerField()
    out_of_stock_count = serializers.IntegerField()
    today_sales_count = serializers.IntegerField()
    today_sales_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_stock_value = serializers.DecimalField(max_digits=14, decimal_places=2)
