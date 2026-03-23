from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
from api.models import IngredientBatch, Ingredient


class Command(BaseCommand):
    help = 'Seed database with ingredient batch data for testing'

    def handle(self, *args, **options):
        """Create seed batches for testing"""
        
        # Get all ingredients
        ingredients = Ingredient.objects.all()
        
        if not ingredients.exists():
            self.stdout.write(
                self.style.ERROR('No ingredients found. Please seed ingredients first using: python manage.py seed_ingredients')
            )
            return
        
        # Clear existing batches (for fresh start)
        # Uncomment if you want to reset: IngredientBatch.objects.all().delete()
        
        now = timezone.now()
        batches_created = 0
        
        # Create batches for each ingredient
        for idx, ingredient in enumerate(ingredients):
            # Batch 1: Recently received, good quantity
            batch1 = IngredientBatch(
                ingredient_id=ingredient,
                quantity=Decimal('100.00'),
                current_qty=Decimal('100.00'),
                cost_price=Decimal('10.50'),
                made_date=now - timedelta(days=5),
                expire_date=now + timedelta(days=25),
                status='Active'
            )
            batch1.save()
            batches_created += 1
            
            # Batch 2: Older batch, less quantity, expiring soon
            batch2 = IngredientBatch(
                ingredient_id=ingredient,
                quantity=Decimal('50.00'),
                current_qty=Decimal('35.00'),  # Already consumed some
                cost_price=Decimal('10.00'),
                made_date=now - timedelta(days=20),
                expire_date=now + timedelta(days=3),  # Expiring soon
                status='Active'
            )
            batch2.save()
            batches_created += 1
            
            # Batch 3: Already expired
            batch3 = IngredientBatch(
                ingredient_id=ingredient,
                quantity=Decimal('25.00'),
                current_qty=Decimal('25.00'),
                cost_price=Decimal('9.50'),
                made_date=now - timedelta(days=60),
                expire_date=now - timedelta(days=5),  # Already expired
                status='Expired'
            )
            batch3.save()
            batches_created += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {batches_created} batches across {ingredients.count()} ingredients'
        ))
        
        # Print summary
        total_batches = IngredientBatch.objects.count()
        active_batches = IngredientBatch.objects.filter(status='Active').count()
        expired_batches = IngredientBatch.objects.filter(status='Expired').count()
        
        self.stdout.write(self.style.SUCCESS('\nBatch Summary:'))
        self.stdout.write(f'  Total Batches: {total_batches}')
        self.stdout.write(f'  Active: {active_batches}')
        self.stdout.write(f'  Expired: {expired_batches}')
        
        # Show some batch examples
        self.stdout.write(self.style.SUCCESS('\nSample Batches (First 5):'))
        for batch in IngredientBatch.objects.all()[:5]:
            print(f'  {batch.batch_id}: {batch.ingredient_id.name} - {batch.current_qty}/{batch.quantity} {batch.ingredient_id.base_unit} ({batch.status})')
