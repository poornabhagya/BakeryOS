from decimal import Decimal
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from api.models import (
    IngredientBatch,
    Product,
    ProductBatch,
    ProductStockHistory,
    RecipeItem,
)


def _to_decimal(value: Decimal | int | float | str) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _shelf_life_to_days(shelf_life: int, shelf_unit: str) -> int:
    if shelf_unit == "hours":
        return max(1, int(shelf_life) // 24)
    if shelf_unit == "weeks":
        return int(shelf_life) * 7
    return int(shelf_life)


def _next_product_batch_id() -> str:
    """Generate the next PROD-BATCH-#### sequence safely inside a transaction."""
    last_batch = ProductBatch.objects.select_for_update().order_by("-id").first()
    if not last_batch or not last_batch.batch_id:
        return "PROD-BATCH-1001"

    try:
        last_num = int(last_batch.batch_id.split("-")[-1])
    except (ValueError, IndexError):
        last_num = 1000

    return f"PROD-BATCH-{last_num + 1}"


@transaction.atomic
def produce_product(product_id: int, quantity_to_produce: Decimal | int | float | str):
    """
    Produce product stock using strict ingredient FIFO deduction.

    Flow:
    1) Fetch product + recipe
    2) Compute per-ingredient required quantity
    3) Deduct from Active ingredient batches in FIFO order (expire_date ASC)
    4) Fail fast with ValidationError if any ingredient is insufficient (atomic rollback)
    5) Increase Product.current_stock (running balance)
    6) Record ProductBatch as production audit log
    7) Record ProductStockHistory add-stock entry
    """
    qty_to_produce = _to_decimal(quantity_to_produce)
    if qty_to_produce <= 0:
        raise ValidationError("quantity_to_produce must be greater than 0")

    product = Product.objects.select_for_update().get(id=product_id)
    recipe_items = (
        RecipeItem.objects.select_related("ingredient_id")
        .filter(product_id=product)
        .order_by("id")
    )

    if not recipe_items.exists():
        raise ValidationError(f"No recipe defined for {product.name}")

    # Deduct ingredient stock in strict FIFO per ingredient.
    for recipe_item in recipe_items:
        ingredient = recipe_item.ingredient_id
        total_required = recipe_item.quantity_required * qty_to_produce

        fifo_batches = (
            IngredientBatch.objects.select_for_update()
            .filter(
                ingredient_id=ingredient,
                status="Active",
                current_qty__gt=0,
            )
            .order_by("expire_date", "id")
        )

        for batch in fifo_batches:
            if total_required <= 0:
                break

            if batch.current_qty >= total_required:
                batch.current_qty -= total_required
                if batch.current_qty == 0:
                    batch.status = "Used"
                batch.save(update_fields=["current_qty", "status", "updated_at"])
                total_required = Decimal("0")
                break

            # Drain this batch and continue to next FIFO batch.
            total_required -= batch.current_qty
            batch.current_qty = Decimal("0")
            batch.status = "Used"
            batch.save(update_fields=["current_qty", "status", "updated_at"])

        if total_required > 0:
            raise ValidationError(f"Insufficient ingredient stock for {ingredient.name}")

    # Running-balance update for finished product stock.
    qty_before = product.current_stock
    qty_after = qty_before + qty_to_produce
    product.current_stock = qty_after
    product.save(update_fields=["current_stock", "updated_at"])

    # Product batch acts as production audit log only.
    now = timezone.now()
    made_date = now.date()
    expire_date = made_date + timedelta(
        days=_shelf_life_to_days(product.shelf_life, product.shelf_unit)
    )
    batch_id = _next_product_batch_id()

    audit_batch = ProductBatch(
        batch_id=batch_id,
        product_id=product,
        quantity=qty_to_produce,
        current_qty=qty_to_produce,
        made_date=made_date,
        expire_date=expire_date,
        status="Active",
        notes=f"Production log: produced {qty_to_produce} units via FIFO ingredient deduction.",
        created_at=now,
        updated_at=now,
    )
    ProductBatch.objects.bulk_create([audit_batch])

    # Reload to return an instance with DB-generated primary key.
    audit_batch = ProductBatch.objects.get(batch_id=batch_id)

    ProductStockHistory.objects.create(
        product_id=product,
        transaction_type="AddStock",
        qty_before=qty_before,
        qty_after=qty_after,
        change_amount=qty_to_produce,
        user_id=None,
        notes=f"Production completed and logged as {batch_id}.",
    )

    return {
        "product_id": product.id,
        "product_code": product.product_id,
        "produced_quantity": qty_to_produce,
        "new_current_stock": qty_after,
        "product_batch_id": audit_batch.id,
        "product_batch_code": audit_batch.batch_id,
    }
