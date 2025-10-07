from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from categories.models import Category
from products.models import Product, ProductImage
import os
from PIL import Image
import io
import random


class Command(BaseCommand):
    help = 'Populate the database with sample products and images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of products to create',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Create sample categories if they don't exist
        categories = []
        category_names = [
            'Rings', 'Earrings', 'Bracelets', 'Bangles', 
            'Chains', 'Pendants', 'Mangalsutra', 'Necklaces',
            'Nose Pin', 'Necklace Set'
        ]
        
        for cat_name in category_names:
            category, created = Category.objects.get_or_create(
                name=cat_name,
                defaults={
                    'description': f'Beautiful {cat_name.lower()} collection',
                    'is_active': True
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {cat_name}')

        # Sample product data
        product_names = [
            'Silver Rose Ring', 'Diamond Stud Earrings', 'Pearl Necklace',
            'Gold Chain Bracelet', 'Ruby Pendant', 'Emerald Ring',
            'Sapphire Earrings', 'Silver Bangle', 'Traditional Mangalsutra',
            'Diamond Tennis Bracelet', 'Pearl Drop Earrings', 
            'Silver Chain Necklace', 'Gold Heart Pendant',
            'Silver Hoop Earrings', 'Diamond Engagement Ring',
            'Gold Wedding Band', 'Silver Charm Bracelet',
            'Pearl Stud Earrings', 'Gold Rope Chain',
            'Silver Infinity Ring', 'Diamond Solitaire Pendant',
            'Gold Twisted Bangle', 'Silver Geometric Earrings',
            'Rose Gold Ring', 'Platinum Necklace', 'Gold Nose Pin',
            'Silver Necklace Set', 'Diamond Mangalsutra', 'Pearl Nose Pin',
            'Antique Necklace Set'
        ]

        descriptions = [
            'Exquisite handcrafted piece with intricate details',
            'Elegant design perfect for special occasions',
            'Classic style that never goes out of fashion',
            'Modern contemporary design for today\'s woman',
            'Vintage-inspired piece with timeless appeal',
            'Minimalist design for everyday wear',
            'Statement piece that commands attention',
            'Delicate and feminine with subtle sparkle'
        ]

        created_count = 0
        
        # Get existing product count to generate unique SKUs
        existing_count = Product.objects.count()
        
        for i in range(count):
            if i < len(product_names):
                name = product_names[i]
            else:
                name = f'Silver Jewelry Piece {i+1}'
            
            # Generate unique SKU
            sku = f'SJ{1000+existing_count+i:04d}'
            
            # Check if product with this SKU already exists
            if Product.objects.filter(sku=sku).exists():
                self.stdout.write(f'Product with SKU {sku} already exists, skipping...')
                continue
            
            # Create product
            product = Product.objects.create(
                name=name,
                description=random.choice(descriptions),
                short_description=f'Beautiful {name.lower()} crafted with precision',
                sku=sku,
                category=random.choice(categories),
                meta_title=f'{name} - Silver Jewellery',
                meta_description=f'Shop {name.lower()} at Silver Jewellery. Premium quality, elegant design.',
                is_active=True,
                is_featured=random.choice([True, False]),
                base_price=round(random.uniform(50.00, 500.00), 2),
                sale_price=round(random.uniform(40.00, 450.00), 2) if random.choice([True, False]) else None,
                track_inventory=True,
                stock_quantity=random.randint(5, 50),
                low_stock_threshold=5,
            )
            
            # Create sample images for each product
            self.create_sample_image(product, True)  # Primary image
            if random.choice([True, False]):  # 50% chance of additional image
                self.create_sample_image(product, False)
            
            created_count += 1
            self.stdout.write(f'Created product: {name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} products with images')
        )

    def create_sample_image(self, product, is_primary=False):
        """Create a sample image for a product"""
        # Create a simple colored rectangle as sample image
        width, height = 400, 400
        colors = [
            (200, 200, 200),  # Light gray
            (180, 180, 180),  # Gray
            (220, 220, 220),  # Very light gray
            (160, 160, 160),  # Medium gray
        ]
        
        color = random.choice(colors)
        image = Image.new('RGB', (width, height), color)
        
        # Save to BytesIO
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        
        # Create ProductImage
        image_file = ContentFile(buffer.getvalue(), name=f'{product.sku}_{"primary" if is_primary else "additional"}.jpg')
        
        ProductImage.objects.create(
            product=product,
            image=image_file,
            alt_text=f'{product.name} image',
            is_primary=is_primary,
            sort_order=0 if is_primary else 1
        )