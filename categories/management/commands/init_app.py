from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from categories.models import Category
import os


class Command(BaseCommand):
    help = 'Initialize the application with default categories and superuser'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-superuser',
            action='store_true',
            help='Skip superuser creation',
        )
        parser.add_argument(
            '--superuser-email',
            type=str,
            default=os.getenv('SUPERUSER_EMAIL', 'admin@silverempire.com'),
            help='Superuser email (default: admin@silverempire.com)',
        )
        parser.add_argument(
            '--superuser-password',
            type=str,
            default=os.getenv('SUPERUSER_PASSWORD', 'admin123'),
            help='Superuser password (default: admin123)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting application initialization...')
        )

        # Create categories
        self.create_default_categories()

        # Create superuser if not skipped
        if not options['skip_superuser']:
            self.create_superuser(
                options['superuser_email'],
                options['superuser_password']
            )

        self.stdout.write(
            self.style.SUCCESS('Application initialization completed successfully!')
        )

    def create_default_categories(self):
        """Create default categories"""
        self.stdout.write('Creating default categories...')
        
        categories = [
            'Rings',
            'Earrings',
            'Bracelets',
            'Bangles',
            'Chains',
            'Pendants',
            'Mangalsutra',
            'Necklaces',
            'Nose Pin',
            'Necklace Set'
        ]

        created_count = 0
        
        with transaction.atomic():
            for index, category_name in enumerate(categories, 1):
                category, created = Category.objects.get_or_create(
                    name=category_name,
                    defaults={
                        'description': f'Beautiful {category_name.lower()} collection',
                        'is_active': True,
                        'sort_order': index * 10,  # Give room for future ordering
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        f'Created category: {category_name}'
                    )
                else:
                    self.stdout.write(
                        f'Category already exists: {category_name}'
                    )

        self.stdout.write(
            self.style.SUCCESS(f'Categories created: {created_count}/{len(categories)}')
        )

    def create_superuser(self, email, password):
        """Create superuser if it doesn't exist"""
        self.stdout.write('Creating superuser...')
        
        User = get_user_model()
        
        try:
            # Check if superuser already exists
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f'Superuser with email {email} already exists')
                )
                return

            # Create superuser
            user = User.objects.create_superuser(
                email=email,
                password=password,
                first_name='Super',
                last_name='Admin'
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Superuser created successfully!')
            )
            self.stdout.write(f'Email: {email}')
            self.stdout.write(f'Password: {password}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create superuser: {str(e)}')
            )