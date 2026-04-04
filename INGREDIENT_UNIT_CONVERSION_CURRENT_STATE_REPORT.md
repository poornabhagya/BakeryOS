# Ingredient Unit Conversion - Current State Report

Date: 2026-04-02
Scope: Frontend + Backend current implementation (no proposed fixes in this report)

## 1. Base Units and Database Storage

### 1.1 Ingredient tracking model
- `tracking_type` is defined on `Ingredient` with choices:
  - `Weight`
  - `Volume`
  - `Count`
- Source: `Backend/api/models/ingredient.py` (TRACKING_TYPE_CHOICES around line 25).

### 1.2 Ingredient base unit
- `Ingredient.base_unit` is a free text `CharField`.
- Source: `Backend/api/models/ingredient.py` (base_unit field around line 82).

### 1.3 Batch quantity fields
- `IngredientBatch.quantity` is stored as `DecimalField(max_digits=10, decimal_places=2)`.
- `IngredientBatch.current_qty` is stored as `DecimalField(max_digits=10, decimal_places=2)`.
- Source: `Backend/api/models/batch.py` (quantity around line 53, current_qty around line 59).

### 1.4 Ingredient total stock calculation
- Ingredient total stock is synced by summing `current_qty` of active batches.
- Source: `Backend/api/models/batch.py` (`total = sum(batch.current_qty for batch in active_batches)` around line 295).
- There is no unit conversion inside this summation.

---

## 2. Frontend Input Conversion (Add New Ingredient Batch)

### 2.1 Where conversion happens
- Conversion is implemented in:
  - `Frontend/src/components/modal/ingredient modal/AddNewIngredientStockModal.tsx`
  - Function: `convertToBaseUnit` (around line 71).

### 2.2 Conversion rules currently used
- For `trackingType === 'weight'`:
  - if selected unit is `kg` => multiply by 1000
  - if selected unit is `g` => unchanged
  - Source: line around 74.
- For `trackingType === 'volume'`:
  - if selected unit is `L` => multiply by 1000
  - if selected unit is `ml` => unchanged
  - Source: line around 77.
- For all other tracking types (`count`), quantity is unchanged.

### 2.3 What is sent to backend
- In `handleSave`, payload uses:
  - `quantity: String(baseQuantity)`
  - `ingredient_id`, `cost_price`, dates, notes
- Source: payload block around lines 125-132 in `AddNewIngredientStockModal.tsx`.

### 2.4 Unit options shown to user
- Unit options in modal:
  - weight: `kg`, `g`
  - volume: `L`, `ml`
  - count: `Nos`, `Tray`
- Source: `UNIT_OPTIONS` in `AddNewIngredientStockModal.tsx` (around line 21).

---

## 3. Backend Processing on Batch Create/Update

### 3.1 API create path
- Frontend calls `/api/batches/`.
- Backend viewset uses `BatchCreateSerializer` for create.
- Source: `Backend/api/views/batch_views.py` (`get_serializer_class`, `perform_create`).

### 3.2 Serializer behavior
- `BatchCreateSerializer` includes fields:
  - `ingredient_id`, `quantity`, `current_qty`, `cost_price`, `made_date`, `expire_date`
- Source: `Backend/api/serializers/batch_serializers.py` (Meta.fields around line 84).
- Validation checks signs/order/limits but does not do kg<->g or L<->ml normalization.

### 3.3 Model save behavior
- `IngredientBatch.save()` currently handles:
  - auto status update to expired if needed
  - initialize `current_qty = quantity` for new batches (if missing/<=0)
  - expiry-to-wastage transition logic
- Source: `Backend/api/models/batch.py` (`def save(self, *args, **kwargs)` around line 183).
- No backend unit conversion logic exists there either.

### 3.4 Conclusion for backend conversion
- Backend saves the numeric quantity it receives.
- It does not infer/convert based on `tracking_type` or `base_unit`.

---

## 4. Frontend Display Logic (Smart display vs raw display)

### 4.1 IngredientStockHistoryModal table mapping
- File: `Frontend/src/components/modal/ingredient modal/IngredientStockHistoryModal.tsx`
- API response mapping uses:
  - `quantity: qty` (raw parsed backend value)
  - `currentQty: ...` (raw parsed backend value)
  - `unit: batch.unit || 'units'`
- Source: mapping around lines 82-84.

### 4.2 Table rendering
- Quantity/current qty shown directly as numeric values with `entry.unit`.
- No reverse conversion like `10000 -> 10 kg`.
- Source: quantity/currentQty render in same file around lines ~220-230.

### 4.3 Main stock list rendering
- File: `Frontend/src/components/StockManagementScreen.tsx`
- Ingredients are mapped with:
  - `quantity: apiIngredient.total_quantity`
  - `unit: apiIngredient.base_unit`
- Source: around lines 124-125 and 193-194.
- Display renders `{p.quantity} {p.unit}` directly.
- Source: around lines 590 and 592.

### 4.4 Dedicated smart display utility
- There is no centralized ingredient quantity smart display utility currently applied for auto unit scaling.
- Existing `Frontend/src/utils/conversions.ts` handles API numeric parsing for other domains (users/products/sales), not ingredient unit scaling.

---

## 5. Important Current Inconsistencies Found

### 5.1 Input conversion vs base_unit label mismatch
- Batch input modal converts `kg->g` and `L->ml` before POST.
- But ingredient creation defaults `base_unit` to:
  - `kg` for Weight
  - `liters` for Volume
  - `pieces` for Count
- Source: `Frontend/src/components/modal/ingredient modal/AddIngredientItemModal.tsx` (around lines 112, 114, 116).
- This can cause values stored in smaller-unit scale while UI labels remain larger-unit words, producing confusing displays.

### 5.2 Batch API does not include a native `unit` field
- Batch serializers expose `ingredient_unit` (derived from ingredient base_unit), not `unit`.
- File: `Backend/api/serializers/batch_serializers.py`.
- Frontend mapping currently tries `batch.unit || 'units'`, so it often falls back to `'units'` unless backend sends a custom `unit` key.

### 5.3 Raw-number display everywhere
- Most ingredient quantity displays print raw stored number directly, with no automatic divide-by-1000 formatting.

---

## 6. End-to-End Behavior (As-is)

Example: user enters `10 kg` in AddNewIngredientStockModal
1. Frontend converts to `10000` via `convertToBaseUnit`.
2. Payload sends `quantity: "10000"` to `/api/batches/`.
3. Backend stores `quantity=10000`, `current_qty=10000` (for new batch init).
4. Ingredient total_quantity is computed from batch `current_qty` values directly.
5. UI displays raw quantity values with whichever unit label is available (`base_unit` or fallback), not smart-scaled back.

Net result: "10kg shows as 10,000" behavior is consistent with current implementation.

---

## 7. Files Reviewed

Backend
- `Backend/api/models/ingredient.py`
- `Backend/api/models/batch.py`
- `Backend/api/serializers/batch_serializers.py`
- `Backend/api/views/batch_views.py`

Frontend
- `Frontend/src/components/modal/ingredient modal/AddNewIngredientStockModal.tsx`
- `Frontend/src/components/modal/ingredient modal/IngredientStockHistoryModal.tsx`
- `Frontend/src/components/StockManagementScreen.tsx`
- `Frontend/src/components/modal/ingredient modal/AddIngredientItemModal.tsx`
- `Frontend/src/utils/conversions.ts`
- `Frontend/src/services/api.ts`
