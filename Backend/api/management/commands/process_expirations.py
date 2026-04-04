from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from api.models import (
    IngredientBatch,
    ProductBatch,
    ProductWastage,
    Product,
    WastageReason,
)


class Command(BaseCommand):
    help = "Process expired ingredient/product batches and record wastage safely."

    def handle(self, *args, **options):
        with transaction.atomic():
            now = timezone.now()

            ingredient_expired_count = 0
            product_expired_count = 0
            product_wastage_count = 0

            # 1) Ingredient batches: rely on IngredientBatch.save() expiry transition logic
            ingredient_batches = (
                IngredientBatch.objects.select_for_update()
                .filter(status='Active', expire_date__lt=now)
                .order_by('id')
            )

            for batch in ingredient_batches:
                batch.status = 'Expired'
                batch.save()
                ingredient_expired_count += 1

            # 2) Product batches: custom safe handling based on remaining current_qty
            product_batches = (
                ProductBatch.objects.select_for_update()
                .select_related('product_id')
                .filter(status='Active', expire_date__lt=now)
                .order_by('id')
            )

            expired_reason, _ = WastageReason.objects.get_or_create(
                reason='Expired',
                defaults={'description': 'Auto-recorded wastage for expired product batches'},
            )

            for batch in product_batches:
                remaining_qty = batch.current_qty or Decimal('0')
                product = batch.product_id

                if remaining_qty > 0:
                    # Record explicit wastage for only the remaining unsold quantity.
                    # ProductWastage.save() already deducts product and batch stock.
                    ProductWastage.objects.create(
                        product_id=product,
                        batch=batch,
                        quantity=remaining_qty,
                        unit_cost=product.cost_price or Decimal('0'),
                        reason_id=expired_reason,
                        reported_by=None,
                        notes='Auto-expired by system background job',
                    )
                    product_wastage_count += 1

                # Ensure the batch is fully closed as expired even if current_qty was zero.
                batch.refresh_from_db(fields=['current_qty'])
                batch.current_qty = Decimal('0')
                batch.status = 'Expired'
                batch.save(update_fields=['current_qty', 'status', 'updated_at'])

                # Guardrail: keep product current_stock non-negative.
                product.refresh_from_db(fields=['current_stock'])
                if product.current_stock < 0:
                    product.current_stock = Decimal('0')
                    product.save(update_fields=['current_stock', 'updated_at'])

                product_expired_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                (
                    f"Processed {ingredient_expired_count} expired ingredients and "
                    f"{product_expired_count} expired products "
                    f"(wastage records created: {product_wastage_count})."
                )
            )
        )
