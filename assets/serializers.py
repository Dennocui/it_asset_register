# assets/serializers.py
from rest_framework import serializers
from .models import (
    AssetCategory, Manufacturer, AssetModel, 
    AssetStatus, Asset, MaintenanceRecord
)
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = '__all__'

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = '__all__'

class AssetModelSerializer(serializers.ModelSerializer):
    manufacturer = ManufacturerSerializer(read_only=True)
    manufacturer_id = serializers.PrimaryKeyRelatedField(
        queryset=Manufacturer.objects.all(),
        source='manufacturer',
        write_only=True
    )
    
    category = AssetCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=AssetCategory.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = AssetModel
        fields = '__all__'

class AssetStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetStatus
        fields = '__all__'

class AssetSerializer(serializers.ModelSerializer):
    model = AssetModelSerializer(read_only=True)
    model_id = serializers.PrimaryKeyRelatedField(
        queryset=AssetModel.objects.all(),
        source='model',
        write_only=True
    )
    
    status = AssetStatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=AssetStatus.objects.all(),
        source='status',
        write_only=True
    )
    
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to',
        write_only=True,
        allow_null=True
    )
    
    warranty_expiry = serializers.DateField(read_only=True)
    age_in_months = serializers.IntegerField(read_only=True)

    class Meta:
        model = Asset
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class MaintenanceRecordSerializer(serializers.ModelSerializer):
    asset = serializers.StringRelatedField()
    asset_id = serializers.PrimaryKeyRelatedField(
        queryset=Asset.objects.all(),
        source='asset'
    )
    
    created_by = UserSerializer(read_only=True)
    is_open = serializers.BooleanField(read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by']