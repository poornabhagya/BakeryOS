"""
Seed command to load sample Product data.

Usage:
    python manage.py seed_products

This creates 20 products across 5 product categories with:
- Varied pricing (cost_price, selling_price)
- Stock levels (low, medium, high)
- Different shelf lives
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import datetime

from api.models import Product, Category


class Command(BaseCommand):
    help = 'Seed database with sample product data'

    def handle(self, *args, **options):
        self.stdout.write("Starting product seed data load...")

        # Product data template: (name, cost_price, selling_price, stock, shelf_life, shelf_unit, description)
        products_data = [
            # Buns (under Buns category)
            ("Burger Bun", Decimal("15.00"), Decimal("25.00"), 50, 2, "days", "Classic burger buns, fresh daily"),
            ("Hot Dog Bun", Decimal("12.00"), Decimal("20.00"), 45, 2, "days", "Perfect for hot dogs and sausages"),
            ("Round Bun", Decimal("18.00"), Decimal("30.00"), 30, 2, "days", "Large round buns for sandwiches"),
            ("Dinner Roll", Decimal("10.00"), Decimal("15.00"), 80, 1, "days", "Soft dinner rolls"),

            # Bread (under Bread category)
            ("White Bread", Decimal("75.00"), Decimal("120.00"), 25, 3, "days", "Sliced white bread loaf"),
            ("Wheat Bread", Decimal("80.00"), Decimal("130.00"), 20, 3, "days", "Healthy wheat bread loaf"),
            ("Sourdough", Decimal("90.00"), Decimal("150.00"), 15, 4, "days", "Artisan sourdough bread"),
            ("Rye Bread", Decimal("85.00"), Decimal("140.00"), 12, 3, "days", "Dark rye bread loaf"),

            # Cakes (under Cakes category)
            ("Chocolate Cake", Decimal("250.00"), Decimal("450.00"), 5, 2, "days", "Rich chocolate layer cake"),
            ("Vanilla Cake", Decimal("200.00"), Decimal("380.00"), 8, 2, "days", "Classic vanilla cake"),
            ("Carrot Cake", Decimal("220.00"), Decimal("420.00"), 6, 2, "days", "Moist carrot cake with cream cheese frosting"),
            ("Red Velvet Cake", Decimal("280.00"), Decimal("500.00"), 4, 2, "days", "Elegant red velvet cake"),

            # Pastries (under Pastries category)
            ("Croissant", Decimal("35.00"), Decimal("65.00"), 40, 1, "days", "Butter croissant"),
            ("Danish Pastry", Decimal("30.00"), Decimal("55.00"), 50, 1, "days", "Sweet danish pastry"),
            ("Donut", Decimal("20.00"), Decimal("40.00"), 60, 1, "days", "Glazed donut"),
            ("Muffin", Decimal("25.00"), Decimal("45.00"), 55, 1, "days", "Blueberry muffin"),

            # Drinks (under Drinks category)
            ("Coffee", Decimal("60.00"), Decimal("120.00"), 100, 7, "days", "Freshly brewed coffee"),
            ("Tea", Decimal("40.00"), Decimal("80.00"), 120, 30, "days", "Assorted tea selection"),
            ("Juice", Decimal("50.00"), Decimal("100.00"), 80, 7, "days", "Fresh orange juice"),
            ("Soft Drink", Decimal("35.00"), Decimal("70.00"), 150, 30, "days", "Assorted soft drinks"),
        ]

        try:
            with transaction.atomic():
                # Get or create categories
                categories = {
                    'Buns': Category.objects.get(name='Buns', type='Product'),
                    'Bread': Category.objects.get(name='Bread', type='Product'),
                    'Cakes': Category.objects.get(name='Cakes', type='Product'),
                    'Pastries': Category.objects.get(name='Pastries', type='Product'),
                    'Drinks': Category.objects.get(name='Drinks', type='Product'),
                }

                # Delete existing products to avoid duplicates
                Product.objects.all().delete()

                created_count = 0
                category_map = {
                    0: 'Buns', 1: 'Buns', 2: 'Buns', 3: 'Buns',  # 4 buns
                    4: 'Bread', 5: 'Bread', 6: 'Bread', 7: 'Bread',  # 4 breads
                    8: 'Cakes', 9: 'Cakes', 10: 'Cakes', 11: 'Cakes',  # 4 cakes
                    12: 'Pastries', 13: 'Pastries', 14: 'Pastries', 15: 'Pastries',  # 4 pastries
                    16: 'Drinks', 17: 'Drinks', 18: 'Drinks', 19: 'Drinks',  # 4 drinks
                }

                for idx, (name, cost, selling, stock, shelf_life, shelf_unit, desc) in enumerate(products_data):
                    category_name = category_map[idx]
                    product = Product(
                        category_id=categories[category_name],
                        name=name,
                        description=desc,
                        cost_price=cost,
                        selling_price=selling,
                        current_stock=Decimal(str(stock)),
                        shelf_life=shelf_life,
                        shelf_unit=shelf_unit,
                    )
                    product.save()
                    created_count += 1
                    
                    margin = ((selling - cost) / cost * 100)
                    self.stdout.write(
                        f"  {product.product_id}: {name:25} - "
                        f"Cost: Rs.{cost}, Sell: Rs.{selling}, Margin: {margin:.1f}%, Stock: {stock}"
                    )

                # Print summary
                self.stdout.write(self.style.SUCCESS(f"\n✓ Successfully created {created_count} products"))

                # Print category breakdown
                self.stdout.write("\nProduct Summary:")
                for category_name, category in categories.items():
                    count = Product.objects.filter(category_id=category).count()
                    self.stdout.write(f"  {category_name}: {count} products")

                # Calculate totals
                total_stock = sum(float(p.current_stock) for p in Product.objects.all())
                low_stock = Product.objects.filter(current_stock__lt=10).count()
                out_of_stock = Product.objects.filter(current_stock__lte=0).count()
                
                self.stdout.write(f"\nStock Summary:")
                self.stdout.write(f"  Total Stock Value: {total_stock:.0f} units")
                self.stdout.write(f"  Low Stock Items (<10): {low_stock}")
                self.stdout.write(f"  Out of Stock: {out_of_stock}")

        except Category.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Error: Category not found - {e}"))
            self.stdout.write("Make sure to run seed_categories command first!")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Error: {e}"))
            raise
