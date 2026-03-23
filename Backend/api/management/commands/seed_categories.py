"""
Seed data for Category model (Task 3.1)
Populates database with predefined product and ingredient categories
"""

from django.core.management.base import BaseCommand
from api.models import Category


class Command(BaseCommand):
    help = 'Seed the database with predefined categories for products and ingredients'
    
    def handle(self, *args, **options):
        self.stdout.write('Starting category seed data loading...')
        
        # Product categories
        product_categories = [
            {
                'name': 'Buns',
                'description': 'Various types of buns including burger buns, hot dog buns, and sweet buns'
            },
            {
                'name': 'Bread',
                'description': 'Loaves and specialty breads like wholemeal, white, brown, and sourdough'
            },
            {
                'name': 'Cakes',
                'description': 'Fresh cakes including layer cakes, sponge cakes, and specialty cakes'
            },
            {
                'name': 'Drinks',
                'description': 'Beverages including coffee, tea, juice, and smoothies'
            },
            {
                'name': 'Pastries',
                'description': 'Pastries including croissants, danishes, pies, and tarts'
            },
        ]
        
        # Ingredient categories
        ingredient_categories = [
            {
                'name': 'Flour',
                'description': 'Various types of flour including all-purpose, wholemeal, cake flour, and specialty flours'
            },
            {
                'name': 'Sugar',
                'description': 'Sugar types including white sugar, brown sugar, icing sugar, and specialty syrups'
            },
            {
                'name': 'Dairy',
                'description': 'Dairy products including milk, eggs, butter, cream, and cheese'
            },
            {
                'name': 'Spices',
                'description': 'Spices and seasonings including cinnamon, vanilla, nutmeg, and other flavoring agents'
            },
            {
                'name': 'Additives',
                'description': 'Baking additives including yeast, baking powder, baking soda, and leavening agents'
            },
            {
                'name': 'Others',
                'description': 'Other ingredients including oils, nuts, fruits, and miscellaneous items'
            },
        ]
        
        created_count = 0
        skipped_count = 0
        
        # Create product categories
        self.stdout.write(self.style.SUCCESS('\n📦 Creating Product Categories...'))
        for cat_data in product_categories:
            try:
                category, created = Category.objects.get_or_create(
                    name=cat_data['name'],
                    type='Product',
                    defaults={'description': cat_data['description']}
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created: {category.category_id} - {category.name}')
                    )
                    created_count += 1
                else:
                    self.stdout.write(f'⊘ Already exists: {category.category_id} - {category.name}')
                    skipped_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error creating {cat_data["name"]}: {str(e)}')
                )
        
        # Create ingredient categories
        self.stdout.write(self.style.SUCCESS('\n🥘 Creating Ingredient Categories...'))
        for cat_data in ingredient_categories:
            try:
                category, created = Category.objects.get_or_create(
                    name=cat_data['name'],
                    type='Ingredient',
                    defaults={'description': cat_data['description']}
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created: {category.category_id} - {category.name}')
                    )
                    created_count += 1
                else:
                    self.stdout.write(f'⊘ Already exists: {category.category_id} - {category.name}')
                    skipped_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error creating {cat_data["name"]}: {str(e)}')
                )
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Seed data loading complete!')
        )
        self.stdout.write(f'   Created: {created_count} categories')
        self.stdout.write(f'   Skipped: {skipped_count} categories (already exist)')
        
        # Verify
        total_categories = Category.objects.count()
        product_count = Category.objects.filter(type='Product').count()
        ingredient_count = Category.objects.filter(type='Ingredient').count()
        
        self.stdout.write(
            self.style.SUCCESS(f'\n📊 Database Summary:')
        )
        self.stdout.write(f'   Total Categories: {total_categories}')
        self.stdout.write(f'   Product Categories: {product_count}')
        self.stdout.write(f'   Ingredient Categories: {ingredient_count}')
