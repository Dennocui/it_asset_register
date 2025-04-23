from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class AssetCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, default='laptop')

    class Meta:
        verbose_name = _("Asset Category")
        verbose_name_plural = _("Asset Categories")
        ordering = ['name']

    def __str__(self):
        return self.name

class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    support_url = models.URLField(blank=True)
    support_phone = models.CharField(max_length=20, blank=True)
    support_email = models.EmailField(blank=True)

    class Meta:
        verbose_name = _("Manufacturer")
        verbose_name_plural = _("Manufacturers")
        ordering = ['name']

    def __str__(self):
        return self.name

class AssetModel(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    model_number = models.CharField(max_length=50, blank=True)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, related_name='models')
    typical_lifespan = models.PositiveIntegerField(
        help_text=_("Expected lifespan in months"),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _("Asset Model")
        verbose_name_plural = _("Asset Models")
        ordering = ['manufacturer', 'name']
        unique_together = ('manufacturer', 'name')

    def __str__(self):
        return f"{self.manufacturer.name} {self.name}"

class AssetStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    color = models.CharField(max_length=7, default='#999999')

    class Meta:
        verbose_name = _("Asset Status")
        verbose_name_plural = _("Asset Statuses")
        ordering = ['name']

    def __str__(self):
        return self.name

class Asset(models.Model):
    asset_tag = models.CharField(max_length=50, unique=True)
    serial_number = models.CharField(max_length=100, blank=True)
    model = models.ForeignKey(AssetModel, on_delete=models.PROTECT, related_name='assets')
    status = models.ForeignKey(AssetStatus, on_delete=models.PROTECT, related_name='assets')
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    warranty_months = models.PositiveIntegerField(default=12)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_assets'
    )
    location = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    mac_address = models.CharField(max_length=17, blank=True, null=True)
    last_audit = models.DateField(null=True, blank=True)
    depreciation_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=20.00,
        help_text=_("Annual depreciation rate in %")
    )
    residual_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00
    )

    class Meta:
        verbose_name = _("Asset")
        verbose_name_plural = _("Assets")
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

    @property
    def current_value(self):
        if not self.purchase_cost:
            return 0
        years = self.age_in_months / 12
        depreciation_factor = (1 - (float(self.depreciation_rate) / 100) ** years)
        current_val = float(self.purchase_cost) * depreciation_factor
        return max(current_val, float(self.residual_value))

class MaintenanceType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    frequency_months = models.PositiveIntegerField(
        verbose_name=_("Frequency (months)"),
        null=True,
        blank=True,
        help_text=_("Recommended maintenance frequency in months")
    )

    class Meta:
        verbose_name = _("Maintenance Type")
        verbose_name_plural = _("Maintenance Types")
        ordering = ['name']

    def __str__(self):
        return self.name

class MaintenanceRecord(models.Model):
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical')),
    ]

    STATUS_CHOICES = [
        ('open', _('Open')),
        ('in_progress', _('In Progress')),
        ('on_hold', _('On Hold')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]

    asset = models.ForeignKey(
        Asset, 
        on_delete=models.CASCADE, 
        related_name='maintenance_records'
    )
    maintenance_type = models.ForeignKey(
        MaintenanceType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='records'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='medium'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='open'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='created_maintenance'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    technician = models.CharField(max_length=100, blank=True)
    cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    resolution = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Maintenance Record")
        verbose_name_plural = _("Maintenance Records")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.asset.asset_tag} - {self.title}"

    @property
    def is_overdue(self):
        from datetime import date
        return (self.status not in ['completed', 'cancelled'] and 
                date.today() > self.scheduled_date)