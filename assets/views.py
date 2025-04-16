# assets/views.py
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    AssetCategory, Manufacturer, AssetModel,
    AssetStatus, Asset, MaintenanceRecord
)
from .serializers import (
    AssetCategorySerializer, ManufacturerSerializer,
    AssetModelSerializer, AssetStatusSerializer,
    AssetSerializer, MaintenanceRecordSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import date, timedelta
from django.db.models import Q

class AssetCategoryViewSet(viewsets.ModelViewSet):
    queryset = AssetCategory.objects.all()
    serializer_class = AssetCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class AssetModelViewSet(viewsets.ModelViewSet):
    queryset = AssetModel.objects.select_related('manufacturer', 'category').all()
    serializer_class = AssetModelSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['manufacturer', 'category']
    search_fields = ['name', 'model_number']

class AssetStatusViewSet(viewsets.ModelViewSet):
    queryset = AssetStatus.objects.all()
    serializer_class = AssetStatusSerializer

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related(
        'model', 'status', 'assigned_to', 'model__manufacturer'
    ).all()
    serializer_class = AssetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'status': ['exact'],
        'model': ['exact'],
        'model__manufacturer': ['exact'],
        'model__category': ['exact'],
        'assigned_to': ['exact', 'isnull'],
        'purchase_date': ['gte', 'lte'],
    }
    search_fields = ['asset_tag', 'serial_number', 'notes']
    ordering_fields = ['asset_tag', 'purchase_date', 'purchase_cost']
    ordering = ['asset_tag']

    @action(detail=False, methods=['get'])
    def warranty_expiring(self, request):
        """Assets with warranty expiring in the next 30 days"""
        threshold = date.today() + timedelta(days=30)
        assets = self.get_queryset().filter(
            warranty_expiry__gte=date.today(),
            warranty_expiry__lte=threshold
        )
        serializer = self.get_serializer(assets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def needs_audit(self, request):
        """Assets not audited in the last 6 months"""
        threshold = date.today() - timedelta(days=180)
        assets = self.get_queryset().filter(
            Q(last_audit__isnull=True) | Q(last_audit__lt=threshold)
        )
        serializer = self.get_serializer(assets, many=True)
        return Response(serializer.data)

class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'asset': ['exact'],
        'priority': ['exact'],
        'created_by': ['exact'],
        'created_at': ['gte', 'lte'],
        'resolved_at': ['isnull'],
    }
    search_fields = ['title', 'description', 'resolution']
    ordering_fields = ['created_at', 'resolved_at', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = MaintenanceRecord.objects.select_related(
            'asset', 'created_by'
        ).all()
        
        # Filter for open tickets if requested
        is_open = self.request.query_params.get('is_open', None)
        if is_open == 'true':
            queryset = queryset.filter(resolved_at__isnull=True)
        elif is_open == 'false':
            queryset = queryset.filter(resolved_at__isnull=False)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)