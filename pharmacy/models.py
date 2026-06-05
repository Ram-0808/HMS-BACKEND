from django.db import models
from django.contrib.auth.models import User


class Medicine(models.Model):
    """Medicine catalog item."""

    CATEGORY_CHOICES = [
        ('TABLET', 'Tablets'),
        ('CAPSULE', 'Capsules'),
        ('SYRUP', 'Syrup'),
        ('INJECTION', 'Injection'),
        ('CREAM', 'Cream'),
        ('DROPS', 'Drops'),
        ('INHALER', 'Inhaler'),
        ('OTHER', 'Other'),
    ]

    UNIT_TYPE_CHOICES = [
        ('STRIP', 'Strip'),
        ('BOTTLE', 'Bottle'),
        ('TUBE', 'Tube'),
        ('VIAL', 'Vial'),
        ('BOX', 'Box'),
        ('PIECE', 'Piece'),
        ('SACHET', 'Sachet'),
    ]

    name = models.CharField(max_length=300)
    generic_name = models.CharField(max_length=300, blank=True, default='')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='TABLET')
    manufacturer = models.CharField(max_length=200, blank=True, default='')
    description = models.TextField(blank=True, default='')
    unit_type = models.CharField(max_length=10, choices=UNIT_TYPE_CHOICES, default='STRIP')
    selling_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text='MRP per unit'
    )
    reorder_level = models.PositiveIntegerField(
        default=10,
        help_text='Alert when total stock falls below this level'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        db_table = 'pharmacy_medicines'

    def __str__(self):
        return f"{self.name} ({self.get_unit_type_display()})"

    @property
    def total_stock(self):
        """Sum of quantity_remaining across all non-expired batches."""
        return self.batches.filter(
            quantity_remaining__gt=0
        ).aggregate(
            total=models.Sum('quantity_remaining')
        )['total'] or 0

    @property
    def is_low_stock(self):
        return self.total_stock <= self.reorder_level


class Vendor(models.Model):
    """Medicine supplier/vendor."""

    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200, blank=True, default='')
    phone = models.CharField(max_length=15, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    address = models.TextField(blank=True, default='')
    gst_number = models.CharField(max_length=20, blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        db_table = 'pharmacy_vendors'

    def __str__(self):
        return self.name


class MedicineBatch(models.Model):
    """Each purchase batch with expiry tracking."""

    medicine = models.ForeignKey(
        Medicine, on_delete=models.CASCADE, related_name='batches'
    )
    vendor = models.ForeignKey(
        Vendor, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='batches'
    )
    batch_number = models.CharField(max_length=100)
    quantity_purchased = models.PositiveIntegerField()
    quantity_remaining = models.PositiveIntegerField()
    cost_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text='Cost price per unit (purchase price)'
    )
    selling_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text='Selling price per unit for this batch'
    )
    manufacture_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField()
    purchase_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ['-purchase_date', '-created_at']
        db_table = 'pharmacy_batches'
        unique_together = [('medicine', 'batch_number')]

    def __str__(self):
        return f"{self.medicine.name} - Batch {self.batch_number}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now().date() > self.expiry_date

    @property
    def is_expiring_soon(self):
        """True if expiring within 30 days."""
        from django.utils import timezone
        today = timezone.now().date()
        return (
            not self.is_expired
            and self.quantity_remaining > 0
            and (self.expiry_date - today).days <= 30
        )


class Sale(models.Model):
    """Medicine sale record (stock OUT)."""

    medicine = models.ForeignKey(
        Medicine, on_delete=models.CASCADE, related_name='sales'
    )
    batch = models.ForeignKey(
        MedicineBatch, on_delete=models.CASCADE, related_name='sales'
    )
    patient = models.ForeignKey(
        'patients.Patient', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='pharmacy_sales'
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    sold_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ['-sale_date']
        db_table = 'pharmacy_sales'

    def __str__(self):
        return f"{self.medicine.name} x{self.quantity} - {self.sale_date.strftime('%Y-%m-%d')}"
