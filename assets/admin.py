# assets/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from .models import (
    AssetCategory, Manufacturer, AssetModel,
    AssetStatus, Asset, MaintenanceRecord
)
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'asset_count')
    search_fields = ('name',)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_asset_count=Count('assetmodel__asset'))
    
    def asset_count(self, obj):
        return obj._asset_count
    asset_count.admin_order_field = '_asset_count'

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'support_phone', 'model_count')
    search_fields = ('name', 'support_phone')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_model_count=Count('assetmodel'))
    
    def model_count(self, obj):
        return obj._model_count
    model_count.admin_order_field = '_model_count'

@admin.register(AssetModel)
class AssetModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'category', 'asset_count')
    list_filter = ('manufacturer', 'category')
    search_fields = ('name', 'model_number')
    list_select_related = ('manufacturer', 'category')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_asset_count=Count('asset'))
    
    def asset_count(self, obj):
        url = reverse('admin:assets_asset_changelist') + f'?model__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, obj._asset_count)
    asset_count.admin_order_field = '_asset_count'

@admin.register(AssetStatus)
class AssetStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'color_display', 'asset_count')
    
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

class MaintenanceRecordInline(admin.TabularInline):
    model = MaintenanceRecord
    extra = 0
    fields = ('title', 'priority', 'created_at', 'resolved_at')
    readonly_fields = ('created_at',)
    
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
    search_fields = ('asset_tag', 'serial_number', 'notes')
    list_select_related = ('model__manufacturer', 'status', 'assigned_to')
    inlines = [MaintenanceRecordInline]
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
        return queryset.annotate(_maintenance_count=Count('maintenancerecord'))
    
    def maintenance_count(self, obj):
        url = reverse('admin:assets_maintenancerecord_changelist') + f'?asset__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, obj._maintenance_count)
    maintenance_count.admin_order_field = '_maintenance_count'
    maintenance_count.short_description = 'Maint.'

class IsOpenFilter(admin.SimpleListFilter):
    title = 'is open'
    parameter_name = 'is_open'
    
    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(resolved_at__isnull=True)
        if self.value() == 'no':
            return queryset.filter(resolved_at__isnull=False)
        return queryset

@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'asset_link', 'priority_display',
        'created_by', 'created_at', 'resolved_at',
        'days_open'
    )
    list_filter = (IsOpenFilter, 'priority', 'created_by', 'created_at')
    search_fields = ('title', 'description', 'resolution', 'asset__asset_tag')
    list_select_related = ('asset', 'created_by')
    raw_id_fields = ('asset',)
    
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
        if obj.resolved_at:
            days = (obj.resolved_at - obj.created_at).days
            return f"{days}d (resolved)"
        else:
            days = (date.today() - obj.created_at.date()).days
            return format_html(
                '<strong>{}d (open)</strong>',
                days
            )
    days_open.short_description = 'Days Open'