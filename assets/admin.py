from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from .models import (
    AssetCategory, Manufacturer, AssetModel,
    AssetStatus, Asset, MaintenanceRecord, MaintenanceType
)
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

# ==================== AssetCategory Admin ====================
@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'model_count', 'asset_count')
    search_fields = ('name', 'description')
    list_per_page = 20
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _model_count=Count('assetmodel', distinct=True),
            _asset_count=Count('assetmodel__asset', distinct=True)
        )
    
    def model_count(self, obj):
        url = reverse('admin:assets_assetmodel_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, obj._model_count)
    model_count.short_description = 'Models'
    
    def asset_count(self, obj):
        url = reverse('admin:assets_asset_changelist') + f'?model__category__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, obj._asset_count)
    asset_count.short_description = 'Assets'

# ==================== Manufacturer Admin ====================
@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'support_phone', 'support_email', 'model_count', 'asset_count')
    search_fields = ('name', 'support_phone', 'support_email')
    list_per_page = 20
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _model_count=Count('assetmodel', distinct=True),
            _asset_count=Count('assetmodel__asset', distinct=True)
        )
    
    def model_count(self, obj):
        url = reverse('admin:assets_assetmodel_changelist') + f'?manufacturer__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, obj._model_count)
    model_count.short_description = 'Models'
    
    def asset_count(self, obj):
        url = reverse('admin:assets_asset_changelist') + f'?model__manufacturer__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, obj._asset_count)
    asset_count.short_description = 'Assets'

# ==================== AssetModel Admin ====================
@admin.register(AssetModel)
class AssetModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'category', 'model_number', 'asset_count')
    list_filter = ('manufacturer', 'category')
    search_fields = ('name', 'model_number')
    list_select_related = ('manufacturer', 'category')
    list_per_page = 20
    raw_id_fields = ('manufacturer', 'category')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_asset_count=Count('asset'))
    
    def asset_count(self, obj):
        url = reverse('admin:assets_asset_changelist') + f'?model__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, obj._asset_count)
    asset_count.admin_order_field = '_asset_count'
    asset_count.short_description = 'Assets'

# ==================== AssetStatus Admin ====================
@admin.register(AssetStatus)
class AssetStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_display', 'is_active', 'asset_count')
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_per_page = 20
    
    def color_display(self, obj):
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; background-color: {};"></span>',
            obj.color
        )
    color_display.short_description = 'Color'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_asset_count=Count('asset'))
    
    def asset_count(self, obj):
        url = reverse('admin:assets_asset_changelist') + f'?status__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, obj._asset_count)
    asset_count.admin_order_field = '_asset_count'
    asset_count.short_description = 'Assets'

# ==================== MaintenanceType Admin ====================
@admin.register(MaintenanceType)
class MaintenanceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'frequency_months', 'record_count')
    search_fields = ('name', 'description')
    list_filter = ('frequency_months',)
    list_per_page = 20
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_record_count=Count('records'))
    
    def record_count(self, obj):
        url = reverse('admin:assets_maintenancerecord_changelist') + f'?maintenance_type__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, obj._record_count)
    record_count.short_description = 'Records'

# ==================== Asset Admin ====================
class MaintenanceRecordInline(admin.TabularInline):
    model = MaintenanceRecord
    extra = 0
    fields = ('title', 'maintenance_type', 'priority', 'created_at', 'completed_at')
    readonly_fields = ('created_at',)
    show_change_link = True
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        'asset_tag', 'model_with_manufacturer', 'status_with_color',
        'assigned_to', 'location', 'purchase_info', 'warranty_status',
        'maintenance_count'
    )
    list_filter = (
        'status', 'model__manufacturer', 'model__category',
        'assigned_to', ('purchase_date', admin.DateFieldListFilter)
    )
    search_fields = ('asset_tag', 'serial_number', 'notes', 'ip_address', 'mac_address')
    list_select_related = ('model__manufacturer', 'status', 'assigned_to')
    inlines = [MaintenanceRecordInline]
    list_per_page = 50
    fieldsets = (
        ('Identification', {
            'fields': ('asset_tag', 'serial_number', 'model')
        }),
        ('Status', {
            'fields': ('status', 'assigned_to', 'location')
        }),
        ('Purchase Info', {
            'fields': ('purchase_date', 'purchase_cost', 'warranty_months')
        }),
        ('Network Info', {
            'fields': ('ip_address', 'mac_address'),
            'classes': ('collapse',)
        }),
        ('Audit Info', {
            'fields': ('last_audit', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    def model_with_manufacturer(self, obj):
        return f"{obj.model.manufacturer.name} {obj.model.name}"
    model_with_manufacturer.short_description = 'Model'
    model_with_manufacturer.admin_order_field = 'model__name'
    
    def status_with_color(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            obj.status.color,
            obj.status.name
        )
    status_with_color.short_description = 'Status'
    status_with_color.admin_order_field = 'status__name'
    
    def purchase_info(self, obj):
        if obj.purchase_date:
            return f"${obj.purchase_cost} on {obj.purchase_date.strftime('%Y-%m-%d')}"
        return "-"
    purchase_info.short_description = 'Purchase'
    
    def warranty_status(self, obj):
        if not obj.warranty_expiry:
            return "No warranty info"
        
        today = date.today()
        if obj.warranty_expiry >= today:
            days_left = (obj.warranty_expiry - today).days
            return format_html(
                '<span style="color: green;">Active ({} days left)</span>',
                days_left
            )
        else:
            days_expired = (today - obj.warranty_expiry).days
            return format_html(
                '<span style="color: red;">Expired ({} days ago)</span>',
                days_expired
            )
    warranty_status.short_description = 'Warranty'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_maintenance_count=Count('maintenance_records'))
    
    def maintenance_count(self, obj):
        url = reverse('admin:assets_maintenancerecord_changelist') + f'?asset__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, obj._maintenance_count)
    maintenance_count.admin_order_field = '_maintenance_count'
    maintenance_count.short_description = 'Maint.'

# ==================== MaintenanceRecord Admin ====================
class IsCompletedFilter(admin.SimpleListFilter):
    title = 'completion status'
    parameter_name = 'is_completed'
    
    def lookups(self, request, model_admin):
        return (
            ('yes', 'Completed'),
            ('no', 'Not Completed'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(completed_at__isnull=False)
        if self.value() == 'no':
            return queryset.filter(completed_at__isnull=True)
        return queryset

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'asset_link', 'maintenance_type', 'priority_display',
        'created_by', 'created_at', 'completed_at', 'days_open', 'cost_display'
    )
    list_filter = (
        IsCompletedFilter, 'priority', 'maintenance_type', 
        'created_by', ('created_at', admin.DateFieldListFilter)
    )
    search_fields = ('title', 'description', 'resolution', 'asset__asset_tag')
    list_select_related = ('asset', 'created_by', 'maintenance_type')
    raw_id_fields = ('asset', 'created_by')
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('asset', 'title', 'description', 'priority')
        }),
        ('Maintenance Details', {
            'fields': ('maintenance_type', 'created_by', 'created_at')
        }),
        ('Resolution', {
            'fields': ('completed_at', 'resolution', 'cost'),
            'classes': ('collapse',)
        }),
    )
    
    def asset_link(self, obj):
        url = reverse('admin:assets_asset_change', args=[obj.asset.id])
        return format_html('<a href="{}">{}</a>', url, obj.asset.asset_tag)
    asset_link.short_description = 'Asset'
    
    def priority_display(self, obj):
        color_map = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red',
            'critical': 'purple',
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            color_map.get(obj.priority, 'black'),
            obj.get_priority_display()
        )
    priority_display.short_description = 'Priority'
    
    def days_open(self, obj):
        if obj.completed_at:
            days = (obj.completed_at - obj.created_at).days
            return f"{days}d"
        else:
            days = (date.today() - obj.created_at.date()).days
            return format_html(
                '<strong>{}d</strong>',
                days
            )
    days_open.short_description = 'Days Open'
    
    def cost_display(self, obj):
        if obj.cost:
            return f"${obj.cost}"
        return "-"
    cost_display.short_description = 'Cost'