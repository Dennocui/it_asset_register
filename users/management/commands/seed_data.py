import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from companies.models import Company, Site, Department
from assets.models import (
    AssetCategory, Manufacturer, AssetModel,
    AssetStatus, Asset, MaintenanceRecord,
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with comprehensive test data'

    def handle(self, *args, **options):
        fake = Faker()
        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))

        # Clear existing data (optional)
        self._clear_existing_data()

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

    def _clear_existing_data(self):
        """Optional: Clear existing data"""
        self.stdout.write(self.style.WARNING('Clearing existing data...'))
        MaintenanceRecord.objects.all().delete()
        Asset.objects.all().delete()
        AssetModel.objects.all().delete()
        Manufacturer.objects.all().delete()
        AssetCategory.objects.all().delete()
        AssetStatus.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        Department.objects.all().delete()
        Site.objects.all().delete()
        Company.objects.all().delete()

    def _create_companies(self, fake):
        companies = []
        company_names = ['TechCorp', 'DataSystems', 'InnovateCo', 'DigitalWorks']
        
        for name in company_names:
            company = Company.objects.create(
                name=name,
                tax_id=fake.iban(),
                address=fake.address(),
                contact_email=fake.company_email(),
                contact_phone=fake.phone_number(),
                logo=None
            )
            companies.append(company)
            self.stdout.write(self.style.SUCCESS(f'Created company: {name}'))
        
        return companies

    def _create_sites(self, fake, companies):
        sites = []
        site_types = ['Headquarters', 'Regional Office', 'Data Center', 'Branch Office']
        
        for company in companies:
            for i in range(random.randint(2, 4)):
                site = Site.objects.create(
                    company=company,
                    name=f"{company.name} {site_types[i % len(site_types)]}",
                    address=fake.address(),
                    primary_contact=fake.name()
                )
                sites.append(site)
        
        return sites

    def _create_departments(self, fake, companies):
        departments = []
        dept_names = ['IT', 'Finance', 'HR', 'Operations', 'Sales', 'Marketing']
        
        for company in companies:
            for dept_name in dept_names:
                department = Department.objects.create(
                    company=company,
                    name=dept_name,
                    cost_center=fake.bothify(text='CC-####')
                )
                departments.append(department)
        
        return departments

    def _create_users(self, fake, companies, departments):
        users = []
        roles = ['user'] * 8 + ['asset_manager'] * 2  # 80% regular users, 20% asset managers
        
        for company in companies:
            for i in range(random.randint(10, 20)):  # 10-20 users per company
                dept = random.choice([d for d in departments if d.company == company])
                
                user = User.objects.create_user(
                    username=fake.unique.user_name(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=fake.unique.email(),
                    password='testpass123',
                    company=company,
                    department=dept,
                    phone=fake.phone_number(),
                    is_asset_manager=(roles[i % len(roles)] == 'asset_manager')
                )
                users.append(user)
        
        return users

    def _create_asset_categories(self):
        categories = []
        category_data = [
            {'name': 'Laptop', 'icon': 'laptop', 'description': 'Portable computers'},
            {'name': 'Desktop', 'icon': 'desktop', 'description': 'Fixed workstations'},
            {'name': 'Monitor', 'icon': 'display', 'description': 'Computer displays'},
            {'name': 'Phone', 'icon': 'phone', 'description': 'Mobile devices'},
            {'name': 'Tablet', 'icon': 'tablet', 'description': 'Touchscreen devices'},
            {'name': 'Server', 'icon': 'server', 'description': 'Enterprise servers'},
            {'name': 'Printer', 'icon': 'printer', 'description': 'Printing devices'},
        ]
        
        for data in category_data:
            category = AssetCategory.objects.create(**data)
            categories.append(category)
        
        return categories

    def _create_manufacturers(self, fake):
        manufacturers = []
        maker_names = ['Dell', 'HP', 'Lenovo', 'Apple', 'Samsung', 'Acer', 'Asus']
        
        for name in maker_names:
            manufacturer = Manufacturer.objects.create(
                name=name,
                support_url=fake.url(),
                support_phone=fake.phone_number()
            )
            manufacturers.append(manufacturer)
        
        return manufacturers

    def _create_asset_models(self, fake, manufacturers, categories):
        models = []
        model_data = {
            'Laptop': ['XPS 13', 'Spectre x360', 'ThinkPad X1', 'MacBook Pro', 'Galaxy Book', 'Swift 3', 'ZenBook'],
            'Desktop': ['OptiPlex', 'EliteDesk', 'ThinkCentre', 'iMac', 'AIO', 'Aspire', 'VivoMini'],
            'Monitor': ['UltraSharp', 'EliteDisplay', 'ThinkVision', 'Pro Display', 'Odyssey', 'Predator', 'ProArt'],
            'Phone': ['Galaxy S22', 'iPhone 13', 'Pixel 6', 'Xperia 1', 'A52', 'Redmi Note', 'ROG Phone'],
            'Tablet': ['iPad Pro', 'Galaxy Tab', 'Yoga Tab', 'Surface Pro', 'MediaPad', 'Iconia', 'Chromebook Tab'],
            'Server': ['PowerEdge', 'ProLiant', 'ThinkSystem', 'Mac Pro', 'ESC4000', 'Altos', 'RS300'],
            'Printer': ['LaserJet', 'OfficeJet', 'Color LaserJet', 'DeskJet', 'PIXMA', 'EcoTank', 'WorkForce'],
        }
        
        for manufacturer in manufacturers:
            for category in categories:
                category_models = model_data.get(category.name, [])
                if category_models:
                    for model_name in random.sample(category_models, min(3, len(category_models))):
                        model = AssetModel.objects.create(
                            manufacturer=manufacturer,
                            name=model_name,
                            model_number=fake.bothify(text='??-####'),
                            category=category,
                            typical_lifespan=random.choice([36, 48, 60, 72])  # 3-6 years
                        )
                        models.append(model)
        
        return models

    def _create_asset_statuses(self):
        statuses = []
        status_data = [
            {'name': 'Active', 'is_active': True, 'color': '#28a745'},
            {'name': 'In Repair', 'is_active': True, 'color': '#ffc107'},
            {'name': 'Retired', 'is_active': False, 'color': '#6c757d'},
            {'name': 'Lost/Stolen', 'is_active': False, 'color': '#dc3545'},
            {'name': 'Disposed', 'is_active': False, 'color': '#343a40'},
        ]
        
        for data in status_data:
            status = AssetStatus.objects.create(**data)
            statuses.append(status)
        
        return statuses

    def _create_assets(self, fake, companies, sites, departments, asset_models, statuses, users):
        assets = []
        status_weights = [70, 10, 10, 5, 5]  # 70% Active, 10% In Repair, etc.
        
        for i in range(200):  # Create 200 assets
            company = random.choice(companies)
            purchase_date = fake.date_between(start_date='-5y', end_date='today')
            
            asset = Asset.objects.create(
                asset_tag=f'AST-{1000 + i:04d}',
                serial_number=fake.bothify(text='SN-########'),
                model=random.choice([m for m in asset_models if m.manufacturer]),
                status=random.choices(statuses, weights=status_weights)[0],
                purchase_date=purchase_date,
                purchase_cost=random.randint(300, 3000),
                warranty_months=random.choice([12, 24, 36]),
                assigned_to=random.choice([u for u in users if u.company == company]) if random.random() > 0.3 else None,
                location=random.choice([s.name for s in sites if s.company == company]),
                ip_address=fake.ipv4() if random.random() > 0.7 else None,
                mac_address=fake.mac_address() if random.random() > 0.7 else None,
                last_audit=fake.date_between(start_date=purchase_date, end_date='today') if random.random() > 0.5 else None
            )
            assets.append(asset)
        
        return assets

    def _create_maintenance_records(self, fake, assets, users):
        maintenance_types = [
            {'name': 'Hardware Repair', 'recommended_frequency': 6},
            {'name': 'Software Update', 'recommended_frequency': 3},
            {'name': 'Preventive Maintenance', 'recommended_frequency': 12},
            {'name': 'Virus Removal', 'recommended_frequency': None},
            {'name': 'Data Migration', 'recommended_frequency': None},
            {'name': 'Battery Replacement', 'recommended_frequency': 24},
        ]
        
        types = []
        for data in maintenance_types:
            types.append(MaintenanceType.objects.create(**data))
        
        priorities = ['low', 'medium', 'high', 'critical']
        priority_weights = [30, 50, 15, 5]  # 30% low, 50% medium, etc.
        
        for asset in assets:
            # Create 0-5 maintenance records per asset
            for _ in range(random.randint(0, 5)):
                created_at = fake.date_time_between(
                    start_date=asset.purchase_date,
                    end_date='now'
                )
                resolved = random.random() > 0.3  # 70% chance of being resolved
                
                MaintenanceRecord.objects.create(
                    asset=asset,
                    title=fake.sentence(nb_words=6),
                    description=fake.paragraph(nb_sentences=3),
                    priority=random.choices(priorities, weights=priority_weights)[0],
                    maintenance_type=random.choice(types),
                    created_by=random.choice(users),
                    created_at=created_at,
                    resolved_at=created_at + timedelta(days=random.randint(1, 30)) if resolved else None,
                    resolution=fake.paragraph(nb_sentences=2) if resolved else None,
                    cost=random.randint(50, 500) if resolved else None
                )