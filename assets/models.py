# assets/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class AssetCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, default='laptop')

    def __str__(self):
        return self.name

class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    support_url = models.URLField(blank=True)
    support_phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name

class AssetModel(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    model_number = models.CharField(max_length=50, blank=True)
    category = models.ForeignKey(AssetCategory, on_delete=models.SET_NULL, null=True)
    typical_lifespan = models.PositiveIntegerField(help_text="In months", null=True, blank=True)

    class Meta:
        unique_together = ('manufacturer', 'name')

    def __str__(self):
        return f"{self.manufacturer.name} {self.name}"

class AssetStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    color = models.CharField(max_length=7, default='#999999')  # Hex color

    def __str__(self):
        return self.name

class Asset(models.Model):
    asset_tag = models.CharField(max_length=50, unique=True)
    serial_number = models.CharField(max_length=100, blank=True)
    model = models.ForeignKey(AssetModel, on_delete=models.PROTECT)
    status = models.ForeignKey(AssetStatus, on_delete=models.PROTECT)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    warranty_months = models.PositiveIntegerField(default=12)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_assets')
    location = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    mac_address = models.CharField(max_length=17, blank=True)
    last_audit = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['asset_tag']

    def __str__(self):
        return f"{self.asset_tag} - {self.model}"

    @property
    def warranty_expiry(self):
        if self.purchase_date:
            from dateutil.relativedelta import relativedelta
            return self.purchase_date + relativedelta(months=self.warranty_months)
        return None

    @property
    def age_in_months(self):
        if self.purchase_date:
            from dateutil.relativedelta import relativedelta
            from datetime import date
            rd = relativedelta(date.today(), self.purchase_date)
            return rd.years * 12 + rd.months
        return 0

class MaintenanceRecord(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.asset.asset_tag} - {self.title}"

    @property
    def is_open(self):
        return self.resolved_at is None