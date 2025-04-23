import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from assets.models import (
    AssetCategory, Manufacturer, AssetModel,
    AssetStatus, Asset, MaintenanceRecord, MaintenanceType
)
from companies.models import Company, Site, Department

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with comprehensive test data'

    def handle(self, *args, **options):
        fake = Faker()
        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))

        # Create companies
        companies = self._create_companies(fake)
        
        # Create sites for each company
        sites = self._create_sites(fake, companies)
        
        # Create departments
        departments = self._create_departments(fake, companies)
        
        # Create users
        users = self._create_users(fake, companies, departments)
        
        # Create asset categories
        categories = self._create_asset_categories()
        
        # Create manufacturers
        manufacturers = self._create_manufacturers(fake)
        
        # Create asset models
        asset_models = self._create_asset_models(manufacturers, categories)
        
        # Create asset statuses
        statuses = self._create_asset_statuses()
        
        # Create assets
        assets = self._create_assets(fake, companies, sites, departments, asset_models, statuses, users)
        
        # Create maintenance records
        self._create_maintenance_records(fake, assets, users)

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))

    def _create_companies(self, fake):
        """Create sample companies"""
        companies = []
        for _ in range(3):
            company, created = Company.objects.get_or_create(
                name=fake.company(),
                defaults={'address': fake.address()}
            )
            companies.append(company)
        return companies

    def _create_sites(self, fake, companies):
        """Create sites for companies"""
        sites = []
        for company in companies:
            for _ in range(2):
                site, created = Site.objects.get_or_create(
                    company=company,
                    name=f"{company.name} {fake.city()} Office",
                    defaults={'address': fake.address()}
                )
                sites.append(site)
        return sites

    def _create_departments(self, fake, companies):
        """Create departments"""
        departments = []
        dept_names = ['IT', 'Finance', 'HR', 'Operations', 'Sales']
        for company in companies:
            for name in dept_names:
                dept, created = Department.objects.get_or_create(
                    company=company,
                    name=name,
                    defaults={}
                )
                departments.append(dept)
        return departments

    def _create_users(self, fake, companies, departments):
        """Create test users"""
        users = []
        for i in range(10):
            username = fake.user_name()
            email = fake.email()
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'password': 'testpass123',
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name()
                }
            )
            users.append(user)
        return users

    def _create_asset_categories(self):
        """Create asset categories"""
        categories_data = [
            {'name': 'Laptop', 'description': 'Portable computers', 'icon': 'laptop'},
            {'name': 'Desktop', 'description': 'Workstation computers', 'icon': 'desktop'},
            {'name': 'Server', 'description': 'Enterprise servers', 'icon': 'server'},
            {'name': 'Network', 'description': 'Network equipment', 'icon': 'network-wired'},
            {'name': 'Printer', 'description': 'Printing devices', 'icon': 'print'},
        ]
        
        categories = []
        for data in categories_data:
            category, created = AssetCategory.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'icon': data['icon']
                }
            )
            categories.append(category)
        return categories

    def _create_manufacturers(self, fake):
        """Create manufacturers"""
        manufacturers_data = [
            {'name': 'Dell', 'support_url': 'https://www.dell.com/support', 'support_phone': '1-800-999-3355'},
            {'name': 'HP', 'support_url': 'https://support.hp.com', 'support_phone': '1-800-474-6836'},
            {'name': 'Lenovo', 'support_url': 'https://support.lenovo.com', 'support_phone': '1-855-253-6686'},
            {'name': 'Cisco', 'support_url': 'https://www.cisco.com/support', 'support_phone': '1-800-553-2447'},
            {'name': 'Apple', 'support_url': 'https://support.apple.com', 'support_phone': '1-800-275-2273'},
        ]
        
        manufacturers = []
        for data in manufacturers_data:
            manufacturer, created = Manufacturer.objects.get_or_create(
                name=data['name'],
                defaults={
                    'support_url': data['support_url'],
                    'support_phone': data.get('support_phone', '')
                }
            )
            manufacturers.append(manufacturer)
        return manufacturers

    def _create_asset_models(self, manufacturers, categories):
        """Create asset models"""
        model_data = [
            {'manufacturer': 'Dell', 'name': 'Latitude 5420', 'category': 'Laptop'},
            {'manufacturer': 'Dell', 'name': 'OptiPlex 7080', 'category': 'Desktop'},
            {'manufacturer': 'HP', 'name': 'EliteBook 840', 'category': 'Laptop'},
            {'manufacturer': 'HP', 'name': 'ProDesk 600', 'category': 'Desktop'},
            {'manufacturer': 'Lenovo', 'name': 'ThinkPad X1', 'category': 'Laptop'},
            {'manufacturer': 'Cisco', 'name': 'Catalyst 9200', 'category': 'Network'},
            {'manufacturer': 'Apple', 'name': 'MacBook Pro', 'category': 'Laptop'},
        ]
        
        models = []
        for data in model_data:
            manufacturer = next(m for m in manufacturers if m.name == data['manufacturer'])
            category = next(c for c in categories if c.name == data['category'])
            
            model, created = AssetModel.objects.get_or_create(
                manufacturer=manufacturer,
                name=data['name'],
                defaults={
                    'category': category,
                    'typical_lifespan': random.choice([36, 48, 60])
                }
            )
            models.append(model)
        return models

    def _create_asset_statuses(self):
        """Create asset statuses"""
        statuses_data = [
            {'name': 'Deployed', 'is_active': True, 'color': '#28a745'},
            {'name': 'In Stock', 'is_active': True, 'color': '#17a2b8'},
            {'name': 'Under Repair', 'is_active': True, 'color': '#ffc107'},
            {'name': 'Retired', 'is_active': False, 'color': '#6c757d'},
        ]
        
        statuses = []
        for data in statuses_data:
            status, created = AssetStatus.objects.get_or_create(
                name=data['name'],
                defaults={
                    'is_active': data['is_active'],
                    'color': data['color']
                }
            )
            statuses.append(status)
        return statuses

    def _create_assets(self, fake, companies, sites, departments, asset_models, statuses, users):
        """Create assets"""
        assets = []
        for i in range(50):
            purchase_date = fake.date_between(start_date='-5y', end_date='today')
            asset = Asset.objects.create(
                asset_tag=f"AST-{1000 + i}",
                serial_number=fake.uuid4()[:10].upper(),
                model=random.choice(asset_models),
                status=random.choice(statuses),
                purchase_date=purchase_date,
                purchase_cost=round(random.uniform(500, 3000), 2),
                warranty_months=random.choice([12, 24, 36]),
                assigned_to=random.choice(users) if random.random() > 0.3 else None,
                location=random.choice(sites).name if random.random() > 0.2 else '',
                ip_address=fake.ipv4() if random.random() > 0.5 else None
            )
            assets.append(asset)
        return assets

    def _create_maintenance_records(self, fake, assets, users):
        """Create maintenance records"""
        maintenance_types_data = [
            {'name': 'Hardware Repair', 'description': 'Physical component repair', 'frequency_months': 6},
            {'name': 'Software Update', 'description': 'OS and application updates', 'frequency_months': 3},
            {'name': 'Preventive Maintenance', 'description': 'Scheduled maintenance', 'frequency_months': 12},
            {'name': 'Virus Removal', 'description': 'Malware and virus cleanup', 'frequency_months': None},
            {'name': 'Data Migration', 'description': 'Transferring data between systems', 'frequency_months': None},
            {'name': 'Battery Replacement', 'description': 'Power supply replacement', 'frequency_months': 24},
        ]
        
        types = []
        for data in maintenance_types_data:
            type_obj, created = MaintenanceType.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'frequency_months': data['frequency_months']
                }
            )
            types.append(type_obj)
        
        priorities = ['low', 'medium', 'high', 'critical']
        priority_weights = [30, 50, 15, 5]
        status_choices = ['open', 'in_progress', 'on_hold', 'completed', 'cancelled']
        
        for asset in assets:
            for _ in range(random.randint(0, 5)):
                created_at = fake.date_time_between(
                    start_date=asset.purchase_date,
                    end_date='now'
                )
                is_completed = random.random() > 0.3
                status = 'completed' if is_completed else random.choice(['open', 'in_progress', 'on_hold'])
                
                MaintenanceRecord.objects.create(
                    asset=asset,
                    title=fake.sentence(nb_words=6),
                    description=fake.paragraph(nb_sentences=3),
                    priority=random.choices(priorities, weights=priority_weights)[0],
                    status=status,
                    maintenance_type=random.choice(types) if random.random() > 0.7 else None,
                    created_by=random.choice(users),
                    created_at=created_at,
                    scheduled_date=created_at.date() + timedelta(days=random.randint(1, 14)),
                    completed_date=created_at.date() + timedelta(days=random.randint(1, 30)) if is_completed else None,
                    resolution=fake.paragraph(nb_sentences=2) if is_completed else '',
                    cost=round(random.uniform(50, 500), 2) if is_completed else None,
                    technician=fake.name() if is_completed else ''
                )