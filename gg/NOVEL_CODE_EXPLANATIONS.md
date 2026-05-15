# BakeryOS Novel Code Explanations

This document explains each custom business logic feature labeled as "novel code" in BakeryOS, with source locations and line references for audit and reporting.

## 1) Recipe-Driven Automated Stock Deduction

**What it does:** When production is recorded, BakeryOS reads the product recipe and automatically computes total ingredient requirements as `quantity_required * quantity_to_produce`. It then deducts those amounts from ingredient batches before any finished product stock is added. This guarantees that raw-ingredient stock always matches actual production output.

**How it works (technical):** The production service loads the recipe items for the product, computes `total_required` per ingredient, and performs controlled deductions in a loop. If any ingredient is insufficient, it raises a `ValidationError`, preventing inconsistent stock updates.

**File + lines:** [Backend/api/services/production_service.py](Backend/api/services/production_service.py#L61-L105)

## 2) Dynamic Unit Conversion Logic (Kg to g, L to ml)

**What it does:** BakeryOS normalizes all threshold and stock comparison values into base units (g, ml, nos) so that inventory math is consistent, even if staff enter values using higher-level units (kg, L). This avoids mismatches in calculations and ensures low-stock logic works correctly across units.

**How it works (technical):** The serializer layer defines a unit-to-base conversion map and converts incoming threshold values into base units during create and update. It also converts base values back to display units for UI responses.

**Core conversion map + helpers:** [Backend/api/serializers/ingredient_serializers.py](Backend/api/serializers/ingredient_serializers.py#L8-L45)

**Create path conversion (store in base units):** [Backend/api/serializers/ingredient_serializers.py](Backend/api/serializers/ingredient_serializers.py#L268-L277)

**Update path conversion (only when unit provided):** [Backend/api/serializers/ingredient_serializers.py](Backend/api/serializers/ingredient_serializers.py#L388-L408)

## 3) FIFO Ingredient Consumption (Oldest/Expiring Batches First)

**What it does:** Ingredient consumption follows FIFO (first-in, first-out), which minimizes spoilage and ensures older batches are used before newer ones.

**How it works (technical):** The production service queries active ingredient batches ordered by earliest `expire_date` (then `id`), and drains each batch until the required quantity is satisfied. If a batch is depleted, it is marked `Used` and the next batch is consumed.

**FIFO deduction loop:** [Backend/api/services/production_service.py](Backend/api/services/production_service.py#L76-L102)

**Batch-level FIFO ordering default:** [Backend/api/models/batch.py](Backend/api/models/batch.py#L98-L103)

## 4) Spoilage and Financial Loss Valuation

**What it does:** When wastage is recorded, BakeryOS calculates the financial loss as `quantity * unit_cost` and stores it as `total_loss` so reporting and analytics are exact and consistent.

**How it works (technical):** The wastage model overrides `save()` to compute and persist `total_loss` automatically every time a wastage record is created or updated.

**Loss calculation logic:** [Backend/api/models/ingredient_wastage.py](Backend/api/models/ingredient_wastage.py#L103-L127)

## 5) Auto-Recorded Wastage on Ingredient Batch Expiry

**What it does:** When an ingredient batch expires with remaining stock, BakeryOS automatically records an `IngredientWastage` event and zeros the remaining quantity. This ensures expired stock is always accounted for and financially valued without manual intervention.

**How it works (technical):** The `IngredientBatch.save()` method detects transitions into the `Expired` state. If there is remaining quantity, it creates a wastage record with unit cost derived from the batch total cost, then sets `current_qty` to zero.

**Expiry-to-wastage logic:** [Backend/api/models/batch.py](Backend/api/models/batch.py#L183-L241)

## 6) Atomic Production Workflow (Rollback on Insufficient Ingredients)

**What it does:** Production is all-or-nothing. If any ingredient is insufficient, the system cancels the operation so no partial deductions or stock increases occur.

**How it works (technical):** The production function runs inside a database transaction (`@transaction.atomic`). If it raises a `ValidationError`, Django automatically rolls back all ingredient deductions and product stock changes.

**Atomic transaction + fail-fast checks:** [Backend/api/services/production_service.py](Backend/api/services/production_service.py#L43-L105)

## 7) Automated Stock History Audit Trail

**What it does:** Every major stock change (wastage, batch creation, batch deletion) is automatically logged into stock history tables. This provides a complete audit trail without manual data entry.

**How it works (technical):** Signal handlers create history records on key events, capturing before/after quantities, transaction type, references, and notes.

**Stock history signal handlers:** [Backend/api/signals.py](Backend/api/signals.py#L65-L162)
