# CORE STOCK DEDUCTION LOGIC - CURRENT STATE REPORT

## Scope

This report documents the **current implementation state** of stock deduction across backend and frontend, with focus on:

1. Ingredient stock deduction (FIFO expectation)
2. Product stock deduction (running balance expectation)
3. Role of ProductBatch in overall inventory flow
4. Verified implementation gaps and divergence points

This is a behavior report only (no proposed fixes in this document).

---

## 1) Ingredient Flow - Current Implementation

### 1.1 Where ingredient stock is stored

Ingredient stock is represented in two places:

- `Ingredient.total_quantity` (aggregate stock view)
- `IngredientBatch.current_qty` per batch

Batch quantity synchronization back to ingredient total is handled by batch model signals:

- `Backend/api/models/batch.py`
  - `sync_ingredient_quantity_on_batch_save`
  - `sync_ingredient_quantity_on_batch_delete`
  - `sync_ingredient_total`

`sync_ingredient_total` currently sums `current_qty` of **Active** batches only.

### 1.2 FIFO ordering support that exists

Backend provides FIFO-friendly retrieval:

- `Backend/api/views/batch_views.py`
  - `by_ingredient` endpoint filters active batches with quantity > 0 and orders by `expire_date` ascending.

So FIFO **ordering data** exists.

### 1.3 Actual ingredient deduction behavior that exists

Single-batch deduction exists:

- `Backend/api/views/batch_views.py`
  - `consume` action calls `IngredientBatch.consume(amount)` on one specific batch.
- `Backend/api/models/batch.py`
  - `consume` validates amount against `current_qty`, deducts from `current_qty`, marks `Used` if zero, then saves.

### 1.4 Missing orchestration for true production FIFO consumption

There is no verified backend flow that takes a required ingredient amount and automatically:

1. picks first FIFO batch,
2. consumes partially,
3. continues into next batch when needed,
4. completes as one production transaction.

Current recipe endpoint behavior is calculation-focused:

- `Backend/api/views/recipe_views.py`
  - `batch_required` computes required ingredient quantities and estimated costs.
  - It does not perform stock deduction.

Conclusion: ingredient side has FIFO ordering + single-batch consume primitive, but no confirmed split-across-batches execution path for production.

### 1.5 Ingredient wastage behavior and stock mutation source

Ingredient wastage create path in serializer explicitly deducts only aggregate ingredient stock:

- `Backend/api/serializers/ingredient_wastage.py`
  - `create` subtracts `quantity` from `ingredient.total_quantity`.

Ingredient batch-expiry logic in batch model creates wastage and zeros batch qty when status transitions to expired:

- `Backend/api/models/batch.py`
  - `save` transition logic creates `IngredientWastage` and sets batch `current_qty = 0`.

Audit history signal exists:

- `Backend/api/signals.py`
  - `create_ingredient_stock_history_on_wastage` logs stock history entry when `IngredientWastage` is created.

Observed state: ingredient stock mutation is distributed across serializer/model/signal paths, not a single centralized deduction pipeline.

---

## 2) Product Flow - Current Implementation

### 2.1 Running balance storage

Primary product stock counter is:

- `Product.current_stock`

This field is directly updated in multiple operations.

### 2.2 Sales deduction path

Sales deduction uses product running balance directly:

- `Backend/api/serializers/sale_serializers.py`
  - In `create`, for each sale item:
    - `product.current_stock -= quantity`
    - `product.save()`
    - writes `ProductStockHistory` with transaction `UseStock`.

This path does not consume product batches via FIFO.

### 2.3 Product production batch add path

New product batch creation increases product running balance:

- `Backend/api/models/batch_product.py`
  - `save` on new batch initializes `current_qty` and then `_add_to_product_stock()`.
  - `_add_to_product_stock` increments `product.current_stock` by batch `quantity` and writes history.

### 2.4 Product wastage path

Product wastage model deducts from:

1. linked `ProductBatch.current_qty` (if batch provided), and
2. `Product.current_stock`.

- `Backend/api/models/product_wastage.py`
  - `save` performs both deductions before final save.

Also, stock history signal logs wastage event:

- `Backend/api/signals.py`
  - `create_product_stock_history_on_wastage`.

### 2.5 Product list quantity source vs running balance source

Product list/serializer quantity is derived from batch sums (annotated), not strictly `current_stock`:

- `Backend/api/views/product_views.py`
  - `get_queryset` annotates `total_batch_quantity = Sum('batches__current_qty')`.
- `Backend/api/serializers/product_serializers.py`
  - quantity fields prefer `total_batch_quantity` when present.

Meanwhile sales/wastage/production updates directly mutate `Product.current_stock`.

Observed state: two parallel stock representations are active in runtime behavior:

- running balance: `Product.current_stock`
- displayed/derived quantity: sum of product batch `current_qty`

These can diverge if not tightly synchronized.

---

## 3) ProductBatch Role - What It Currently Does

`ProductBatch` currently contributes to stock logic in these ways:

1. Tracks batch-level product quantity (`quantity`, `current_qty`, status, expiry)
2. On create: increases `Product.current_stock`
3. On delete: deducts from `Product.current_stock`
4. Exposes `use_batch` helper

Important observed behavior in `use_batch`:

- `Backend/api/models/batch_product.py`
  - `use_batch(quantity_used)` checks against `self.quantity` (original qty)
  - deducts from `Product.current_stock`
  - creates history entry
  - does **not** deduct `self.current_qty` in this method

Endpoint wiring:

- `Backend/api/views/batch_product_views.py`
  - `use_batch` action invokes `batch.use_batch(quantity_used)`.

So ProductBatch is partially integrated with running balance, but the `use_batch` method does not currently enforce/advance batch remaining quantity in the same way ingredient batch `consume` does.

---

## 4) Frontend Trigger Points - Current State

### 4.1 Product stock increase trigger

- `Frontend/src/components/modal/AddNewBatchModal.tsx`
  - calls `apiClient.batches.createProductBatch(payload)`.
- `Frontend/src/services/api.ts`
  - maps to `/product-batches/`.

### 4.2 Ingredient stock increase trigger

- `Frontend/src/components/modal/ingredient modal/AddNewIngredientStockModal.tsx`
  - calls `apiClient.batches.createIngredientBatch(payload)`.
- `Frontend/src/services/api.ts`
  - maps to `/batches/`.

### 4.3 Product stock decrease via sale

- `Frontend/src/components/BillingScreen.tsx`
  - calls `apiClient.sales.create(payload)`.
- `Frontend/src/services/api.ts`
  - maps to `/sales/`.

### 4.4 Wastage trigger

- `Frontend/src/components/modal/AddProductWastageModal.tsx`
  - calls `apiClient.productWastages.create(...)`.
- `Frontend/src/services/api.ts`
  - maps to `/product-wastages/`.

### 4.5 Recipe-driven production deduction trigger

No confirmed frontend flow was found that executes a backend operation to automatically consume ingredient batches by FIFO for production completion.

Recipe-related behavior appears focused on definition/calculation UI paths rather than production execution + inventory deduction orchestration.

---

## 5) Verified Gaps / Divergences (Current State)

1. Ingredient FIFO is present as ordering + single-batch consume, but no confirmed multi-batch FIFO deduction orchestration for production.
2. Product sale deduction uses `Product.current_stock` directly, not product-batch FIFO consumption.
3. Product displayed quantity path (batch sum) and running balance path (`current_stock`) are different authorities and can drift.
4. `ProductBatch.use_batch` currently adjusts product running stock but does not reduce batch `current_qty` in that method.
5. Ingredient wastage deduction behavior is split across serializer/model/signal paths, increasing complexity of reasoning about a single source of truth.
6. Frontend has clear add/sale/wastage triggers, but no verified end-to-end production trigger that consumes ingredients by recipe and FIFO as one transaction flow.

---

## 6) Executive Current-State Summary

- Ingredient side: FIFO retrieval exists; true automated split-across-batches consumption flow is not verified as implemented.
- Product side: running balance (`current_stock`) is actively used for sales/wastage/production adds, while list quantity often comes from batch `current_qty` sums.
- ProductBatch exists as a bridge model but its consumption helper does not currently behave as a strict batch-level decrement mechanism.
- End-to-end production flow that should tie recipe requirements -> ingredient FIFO deduction -> product stock increase is not present as a clearly unified transaction path in the current code state.

---

## 7) Evidence Index (Primary Files Reviewed)

- `Backend/api/models/batch.py`
- `Backend/api/views/batch_views.py`
- `Backend/api/views/recipe_views.py`
- `Backend/api/serializers/sale_serializers.py`
- `Backend/api/models/batch_product.py`
- `Backend/api/views/batch_product_views.py`
- `Backend/api/views/product_views.py`
- `Backend/api/serializers/product_serializers.py`
- `Backend/api/models/product_wastage.py`
- `Backend/api/serializers/ingredient_wastage.py`
- `Backend/api/signals.py`
- `Frontend/src/services/api.ts`
- `Frontend/src/components/BillingScreen.tsx`
- `Frontend/src/components/modal/AddNewBatchModal.tsx`
- `Frontend/src/components/modal/ingredient modal/AddNewIngredientStockModal.tsx`
- `Frontend/src/components/modal/AddProductWastageModal.tsx`
