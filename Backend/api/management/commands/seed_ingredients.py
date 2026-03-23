from django.core.management.base import BaseCommand
from api.models import Category, Ingredient


class Command(BaseCommand):
    help = 'Seed ingredient data into database'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('SEEDING INGREDIENT DATA'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # Ingredient data with category and details
        ingredient_data = [
            # Flour Category
            {
                'category': 'Flour',
                'suppliers': [
                    {'name': 'All Purpose Flour', 'supplier': 'ABC Mills', 'supplier_contact': '0771234567', 'base_unit': 'kg', 'low_stock': 50, 'shelf_life': 180},
                    {'name': 'Whole Wheat Flour', 'supplier': 'ABC Mills', 'supplier_contact': '0771234567', 'base_unit': 'kg', 'low_stock': 30, 'shelf_life': 150},
                    {'name': 'Cake Flour', 'supplier': 'Premium Mills', 'supplier_contact': '0772345678', 'base_unit': 'kg', 'low_stock': 25, 'shelf_life': 180},
                ]
            },
            # Sugar Category
            {
                'category': 'Sugar',
                'suppliers': [
                    {'name': 'Granulated Sugar', 'supplier': 'Sugar Corp', 'supplier_contact': '0773456789', 'base_unit': 'kg', 'low_stock': 30, 'shelf_life': 365, 'shelf_unit': 'years'},
                    {'name': 'Brown Sugar', 'supplier': 'Sugar Corp', 'supplier_contact': '0773456789', 'base_unit': 'kg', 'low_stock': 20, 'shelf_life': 365, 'shelf_unit': 'years'},
                    {'name': 'Icing Sugar', 'supplier': 'Premium Sweets', 'supplier_contact': '0774567890', 'base_unit': 'kg', 'low_stock': 15, 'shelf_life': 365, 'shelf_unit': 'years'},
                ]
            },
            # Dairy Category
            {
                'category': 'Dairy',
                'suppliers': [
                    {'name': 'Milk Powder', 'supplier': 'Dairy Fresh', 'supplier_contact': '0775678901', 'base_unit': 'kg', 'low_stock': 20, 'shelf_life': 180},
                    {'name': 'Butter', 'supplier': 'Dairy Fresh', 'supplier_contact': '0775678901', 'base_unit': 'kg', 'low_stock': 10, 'shelf_life': 30},
                    {'name': 'Eggs', 'supplier': 'Farm Fresh', 'supplier_contact': '0776789012', 'base_unit': 'pieces', 'tracking_type': 'Count', 'low_stock': 100, 'shelf_life': 21},
                ]
            },
            # Spices Category
            {
                'category': 'Spices',
                'suppliers': [
                    {'name': 'Cinnamon Powder', 'supplier': 'Spice Traders', 'supplier_contact': '0777890123', 'base_unit': 'kg', 'low_stock': 5, 'shelf_life': 365, 'shelf_unit': 'years'},
                    {'name': 'Vanilla Extract', 'supplier': 'Spice Traders', 'supplier_contact': '0777890123', 'base_unit': 'ml', 'tracking_type': 'Volume', 'low_stock': 500, 'shelf_life': 2, 'shelf_unit': 'years'},
                    {'name': 'Nutmeg Powder', 'supplier': 'Spice Traders', 'supplier_contact': '0777890123', 'base_unit': 'kg', 'low_stock': 3, 'shelf_life': 365, 'shelf_unit': 'years'},
                ]
            },
            # Additives Category
            {
                'category': 'Additives',
                'suppliers': [
                    {'name': 'Baking Powder', 'supplier': 'Chemical Supplies', 'supplier_contact': '0778901234', 'base_unit': 'kg', 'low_stock': 20, 'shelf_life': 180},
                    {'name': 'Baking Soda', 'supplier': 'Chemical Supplies', 'supplier_contact': '0778901234', 'base_unit': 'kg', 'low_stock': 15, 'shelf_life': 365, 'shelf_unit': 'years'},
                    {'name': 'Salt', 'supplier': 'Salt Industries', 'supplier_contact': '0779012345', 'base_unit': 'kg', 'low_stock': 20, 'shelf_life': 365, 'shelf_unit': 'years'},
                ]
            },
            # Others Category
            {
                'category': 'Others',
                'suppliers': [
                    {'name': 'Gelatin', 'supplier': 'Chemical Supplies', 'supplier_contact': '0778901234', 'base_unit': 'kg', 'low_stock': 5, 'shelf_life': 365, 'shelf_unit': 'years'},
                    {'name': 'Cocoa Powder', 'supplier': 'Spice Traders', 'supplier_contact': '0777890123', 'base_unit': 'kg', 'low_stock': 10, 'shelf_life': 180},
                    {'name': 'Honey', 'supplier': 'Organic Traders', 'supplier_contact': '0770123456', 'base_unit': 'liters', 'tracking_type': 'Volume', 'low_stock': 20, 'shelf_life': 365, 'shelf_unit': 'years'},
                ]
            },
        ]
        
        created_count = 0
        skipped_count = 0
        
        for category_data in ingredient_data:
            category_name = category_data['category']
            category = Category.objects.filter(name=category_name, type='Ingredient').first()
            
            if not category:
                self.stdout.write(self.style.WARNING(f'\n⚠️  Category "{category_name}" not found. Skipping...'))
                continue
            
            self.stdout.write(self.style.SUCCESS(f'\n🥘 Processing {category_name} Category ({len(category_data["suppliers"])} items)'))
            
            for supplier_data in category_data['suppliers']:
                name = supplier_data['name']
                
                # Check if exists
                exists = Ingredient.objects.filter(
                    category_id=category,
                    name=name
                ).exists()
                
                if exists:
                    self.stdout.write(f'  ⊘ Skipped: {name} (already exists)')
                    skipped_count += 1
                    continue
                
                # Create ingredient
                tracking_type = supplier_data.get('tracking_type', 'Weight')
                shelf_unit = supplier_data.get('shelf_unit', 'days')
                
                Ingredient.objects.create(
                    category_id=category,
                    name=name,
                    supplier=supplier_data.get('supplier', ''),
                    supplier_contact=supplier_data.get('supplier_contact', ''),
                    tracking_type=tracking_type,
                    base_unit=supplier_data.get('base_unit', 'kg'),
                    low_stock_threshold=supplier_data.get('low_stock', 10),
                    shelf_life=supplier_data.get('shelf_life', 30),
                    shelf_unit=shelf_unit,
                    total_quantity=0,  # Will be populated via batches
                )
                
                self.stdout.write(f'  ✓ Created: {name}')
                created_count += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('✅ Seed data loading complete!'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS(f'   Created: {created_count} ingredients'))
        self.stdout.write(self.style.WARNING(f'   Skipped: {skipped_count} ingredients (already exist)'))
        
        # Statistics
        from django.db.models import Count
        total_ingredients = Ingredient.objects.filter(is_active=True).count()
        by_category = Ingredient.objects.filter(is_active=True).values('category_id__name').annotate(count=Count('id')).order_by('category_id__name')
        
        self.stdout.write(self.style.SUCCESS('\n📊 Database Summary:'))
        self.stdout.write(self.style.SUCCESS(f'   Total Ingredients: {total_ingredients}'))
        self.stdout.write(self.style.SUCCESS('   By Category:'))
        for item in by_category:
            self.stdout.write(f'      - {item["category_id__name"]}: {item["count"]}')
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70 + '\n'))
