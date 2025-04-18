# Generated by Django 5.2 on 2025-04-16 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_tag', models.CharField(max_length=50, unique=True)),
                ('serial_number', models.CharField(blank=True, max_length=100)),
                ('purchase_date', models.DateField(blank=True, null=True)),
                ('purchase_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('warranty_months', models.PositiveIntegerField(default=12)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('location', models.CharField(blank=True, max_length=100)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('mac_address', models.CharField(blank=True, max_length=17)),
                ('last_audit', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ['asset_tag'],
            },
        ),
        migrations.CreateModel(
            name='AssetCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, default='laptop', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='AssetModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('model_number', models.CharField(blank=True, max_length=50)),
                ('typical_lifespan', models.PositiveIntegerField(blank=True, help_text='In months', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssetStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('color', models.CharField(default='#999999', max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='MaintenanceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='medium', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('resolution', models.TextField(blank=True)),
                ('cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('support_url', models.URLField(blank=True)),
                ('support_phone', models.CharField(blank=True, max_length=20)),
            ],
        ),
    ]
