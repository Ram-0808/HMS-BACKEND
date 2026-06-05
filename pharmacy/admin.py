from django.contrib import admin
from .models import Medicine, Vendor, MedicineBatch, Sale


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'generic_name', 'category', 'unit_type', 'selling_price', 'reorder_level', 'is_active']
    list_filter = ['category', 'unit_type', 'is_active']
    search_fields = ['name', 'generic_name', 'manufacturer']


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'contact_person']


@admin.register(MedicineBatch)
class MedicineBatchAdmin(admin.ModelAdmin):
    list_display = ['medicine', 'batch_number', 'quantity_purchased', 'quantity_remaining', 'cost_price', 'selling_price', 'expiry_date']
    list_filter = ['medicine', 'vendor']
    search_fields = ['batch_number', 'medicine__name']
    readonly_fields = ['created_at', 'created_by']


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['medicine', 'batch', 'patient', 'quantity', 'unit_price', 'total_amount', 'sale_date', 'sold_by']
    list_filter = ['sale_date', 'medicine']
    search_fields = ['medicine__name', 'patient__name']
    readonly_fields = ['sale_date', 'sold_by']
