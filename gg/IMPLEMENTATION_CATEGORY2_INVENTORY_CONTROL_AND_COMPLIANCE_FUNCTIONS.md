# BakeryOS Implementation - Category 2 Inventory Control and Compliance Functions

## Scope
This document explains all Category 2 inventory-control and compliance functions in BakeryOS:
1. Low-stock detection for products and ingredients
2. Out-of-stock detection for products and ingredients
3. Expiring-soon batch detection
4. Unified stock history/audit trail (before/after qty, type, actor, time)
5. Auto-generated business IDs (employee/product/batch/bill/discount/wastage)
6. Transaction-type tracking (add/use/wastage/adjustment)
7. Historical filtering by date/type/entity
8. Counter-session support (open/close)

## Relevant Folder Map
- Backend:
  - Backend/api/models/product.py
  - Backend/api/models/ingredient.py
  - Backend/api/models/batch.py
  - Backend/api/models/batch_product.py
  - Backend/api/models/stock_history.py
  - Backend/api/models/sale.py
  - Backend/api/models/discount.py
  - Backend/api/models/product_wastage.py
  - Backend/api/models/ingredient_wastage.py
  - Backend/api/models/wastage_reason.py
  - Backend/api/models/counter_session.py
  - Backend/api/views/product_views.py
  - Backend/api/views/ingredient_views.py
  - Backend/api/views/batch_views.py
  - Backend/api/views/batch_product_views.py
  - Backend/api/views/stock_history.py
  - Backend/api/signals.py
- Frontend:
  - Frontend/src/components/StockManagementScreen.tsx
  - Frontend/src/components/dashboard/StorekeeperDashboard.tsx
  - Frontend/src/components/modal/ItemStockHistoryModal.tsx
  - Frontend/src/components/modal/ingredient modal/IngredientStockHistoryModal.tsx
  - Frontend/src/components/NotificationScreen.tsx

---

## 1) Low-Stock Detection (Products + Ingredients)

### 1. Technical Explanation
Low-stock is implemented in both product and ingredient modules:
- Products: `ProductViewSet.low_stock()` in `Backend/api/views/product_views.py`.
- Ingredients: `IngredientViewSet.low_stock()` and list query filter `is_low_stock=true` in `Backend/api/views/ingredient_views.py`.
- Product low-stock threshold currently uses a static quantity rule in endpoint (`current_stock < 10`), while ingredient low-stock uses per-item threshold (`total_quantity <= low_stock_threshold`).
- Frontend dashboards and stock screens consume these endpoints and visually label low stock.

### 2. Critical Code Snippets
```python
# Backend/api/views/product_views.py
@action(detail=False, methods=['get'])
def low_stock(self, request):
    queryset = self.get_queryset().filter(current_stock__lt=10)
    serializer = ProductListSerializer(queryset, many=True)
    return Response({'count': queryset.count(), 'results': serializer.data})
```

```python
# Backend/api/views/ingredient_views.py
@action(detail=False, methods=['get'], url_path='low-stock', permission_classes=[IsManagerOrStorekeeper])
def low_stock(self, request):
    low_stock_ingredients = self.queryset.filter(
        total_quantity__lte=F('low_stock_threshold')
    ).order_by('total_quantity')
    serializer = IngredientListSerializer(low_stock_ingredients, many=True)
    return Response({'count': low_stock_ingredients.count(), 'results': serializer.data})
```

```typescript
// Frontend/src/components/dashboard/StorekeeperDashboard.tsx
const lowStockItems = lowStockSource
  .filter((item: any) => Number(item.total_quantity || 0) <= Number(item.low_stock_threshold || 0))
  .slice(0, 10)
  .map((item: any) => ({ name: item.name, qty: `${Number(item.total_quantity || 0)} ${item.base_unit || 'units'}` }));
```

### 3. Logic Flow
Inventory query -> low-stock filter in view action -> serializer response -> frontend renders low-stock table/cards/alerts.

### 4. Code Location for Screenshots
- Backend/api/views/product_views.py | `low_stock` | approx lines 172-188
- Backend/api/views/ingredient_views.py | `low_stock` | approx lines 176-193
- Backend/api/views/ingredient_views.py | `list` low-stock query param handling | approx lines 125-137
- Backend/api/models/ingredient.py | `low_stock_threshold`, `is_low_stock()` | approx lines 90-152
- Frontend/src/components/dashboard/StorekeeperDashboard.tsx | low stock fetch/mapping | approx lines 78-106
- Frontend/src/components/StockManagementScreen.tsx | low-stock UI filtering | approx lines 461-531

---

## 2) Out-of-Stock Detection (Products + Ingredients)

### 1. Technical Explanation
Out-of-stock is exposed via dedicated API actions:
- Products: `ProductViewSet.out_of_stock()` returns `current_stock <= 0`.
- Ingredients: `IngredientViewSet.out_of_stock()` returns `total_quantity <= 0`.
- Frontend stock tables and badges display out-of-stock status and labels.

### 2. Critical Code Snippets
```python
# Backend/api/views/product_views.py
@action(detail=False, methods=['get'])
def out_of_stock(self, request):
    queryset = self.get_queryset().filter(current_stock__lte=0)
    serializer = ProductListSerializer(queryset, many=True)
    return Response({'count': queryset.count(), 'results': serializer.data})
```

```python
# Backend/api/views/ingredient_views.py
@action(detail=False, methods=['get'])
def out_of_stock(self, request):
    out_of_stock = self.queryset.filter(total_quantity__lte=0)
    serializer = IngredientListSerializer(out_of_stock, many=True)
    return Response({'count': out_of_stock.count(), 'results': serializer.data})
```

```typescript
// Frontend/src/components/StockManagementScreen.tsx
if (stockStatus === 'Out of Stock') {
  // UI-level filter and badge rendering path
}
```

### 3. Logic Flow
Request to out-of-stock endpoint -> DB filter for zero/negative quantity -> serialized result -> frontend marks rows as out-of-stock.

### 4. Code Location for Screenshots
- Backend/api/views/product_views.py | `out_of_stock` | approx lines 190-204
- Backend/api/views/ingredient_views.py | `out_of_stock` | approx lines 241-257
- Backend/api/models/product.py | `is_out_of_stock`/`status` property | approx lines 124-145
- Frontend/src/components/StockManagementScreen.tsx | out-of-stock filtering + badge rendering | approx lines 521-529, 877
- Frontend/src/components/NotificationScreen.tsx | out-of-stock label mapping | approx lines 74-76

---

## 3) Expiring-Soon Batch Detection

### 1. Technical Explanation
Batch expiry monitoring is implemented for both ingredient and product batches:
- Ingredient batches: `BatchViewSet.expiring()` with configurable day window.
- Product batches: `ProductBatchViewSet.get_expiring()` (within 2 days).
- `IngredientBatch` has `is_expired`, `days_until_expiry` and auto-expiry logic in model save.
- Storekeeper dashboard fetches batches and computes expiring list for upcoming days.

### 2. Critical Code Snippets
```python
# Backend/api/views/batch_views.py
@action(detail=False, methods=['get'], url_path='expiring')
def expiring(self, request):
    days = int(request.query_params.get('days', 2))
    expiry_date_threshold = timezone.now() + timedelta(days=days)
    batches = self.queryset.filter(
        status='Active',
        expire_date__lte=expiry_date_threshold,
        expire_date__gt=timezone.now()
    ).order_by('expire_date')
    ...
```

```python
# Backend/api/views/batch_product_views.py
@action(detail=False, methods=['get'], url_path='expiring')
def get_expiring(self, request):
    today = timezone.now().date()
    expiry_threshold = today + timedelta(days=2)
    expiring_batches = self.get_queryset().filter(
        expire_date__lte=expiry_threshold,
        expire_date__gte=today,
        status='Active'
    ).order_by('expire_date')
    ...
```

```typescript
// Frontend/src/components/dashboard/StorekeeperDashboard.tsx
const expirying = batchSource
  .filter((batch: any) => {
    const expiryDate = new Date(batch.expire_date || batch.expiry_date);
    return expiryDate >= today && expiryDate <= sevenDaysLater;
  })
  .sort((a: any, b: any) => new Date(a.expire_date || a.expiry_date).getTime() - new Date(b.expire_date || b.expiry_date).getTime())
```

### 3. Logic Flow
Batch records stored with expiry -> expiring endpoint filters active batches nearing expiry -> frontend dashboard ranks and shows warnings -> notifications may be generated by signal when close to expiry.

### 4. Code Location for Screenshots
- Backend/api/models/batch.py | `is_expired`, `days_until_expiry`, status handling | approx lines 95-172
- Backend/api/views/batch_views.py | `expiring` | approx lines 187-217
- Backend/api/views/batch_product_views.py | `get_expiring` | approx lines 190-210
- Backend/api/signals.py | `check_expiry_notification` | approx lines 159-196
- Frontend/src/components/dashboard/StorekeeperDashboard.tsx | expiring batch fetch/filter | approx lines 108-132

---

## 4) Unified Stock History / Audit Trail

### 1. Technical Explanation
Audit trail is split by entity but unified in structure:
- Product stock history: `ProductStockHistory` model in `Backend/api/models/product.py`.
- Ingredient stock history: `IngredientStockHistory` model in `Backend/api/models/stock_history.py`.
Both capture transaction type, before/after quantity, delta, actor/reference, and timestamps.
Read-only viewsets expose searchable/filterable history APIs.

### 2. Critical Code Snippets
```python
# Backend/api/models/stock_history.py (ingredient)
class IngredientStockHistory(models.Model):
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    qty_before = models.DecimalField(max_digits=10, decimal_places=2)
    qty_after = models.DecimalField(max_digits=10, decimal_places=2)
    change_amount = models.DecimalField(max_digits=10, decimal_places=2)
    performed_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

```python
# Backend/api/views/stock_history.py
class ProductStockHistoryViewSet(...):
    @action(detail=False, methods=['get'])
    def by_product(self, request, **kwargs):
        product_id = request.query_params.get('product_id')
        history = ProductStockHistory.objects.filter(product_id=product_id).order_by('-created_at')
        ...
```

```python
# Backend/api/signals.py (auto-audit on ingredient wastage)
@receiver(post_save, sender=IngredientWastage)
def create_ingredient_stock_history_on_wastage(sender, instance, created, **kwargs):
    if created:
        IngredientStockHistory.objects.create(
            ingredient_id=instance.ingredient_id,
            batch_id=instance.batch_id,
            transaction_type='Wastage',
            qty_before=qty_before,
            qty_after=qty_after,
            change_amount=-instance.quantity,
            performed_by=instance.reported_by,
            reference_id=instance.wastage_id,
        )
```

### 3. Logic Flow
Stock event (batch/sale/wastage/adjustment) -> signal/service writes history row with before/after values -> history viewset serves filtered audit data -> frontend opens stock-history modal.

### 4. Code Location for Screenshots
- Backend/api/models/product.py | `ProductStockHistory` model | approx lines 193-320
- Backend/api/models/stock_history.py | `IngredientStockHistory` model | approx lines 6-90
- Backend/api/views/stock_history.py | `ProductStockHistoryViewSet` | approx lines 29-166
- Backend/api/views/stock_history.py | `IngredientStockHistoryViewSet` | approx lines 168-339
- Backend/api/signals.py | stock history signal block | approx lines 58-149
- Frontend/src/components/modal/ItemStockHistoryModal.tsx | product history modal | approx lines 28-110
- Frontend/src/components/modal/ingredient modal/IngredientStockHistoryModal.tsx | ingredient history modal | approx lines 43-120

---

## 5) Auto-Generated Business IDs

### 1. Technical Explanation
BakeryOS uses deterministic auto-ID generation across key entities:
- Employee: `EMP-001` via pre-save signal (`User`).
- Product: `#PROD-1001` via model save / product signal.
- Ingredient: `#I001` via pre-save signal.
- Ingredient Batch: `BATCH-1001` via pre-save signal.
- Product Batch: `PROD-BATCH-1001` via model save/service helper.
- Bill Number: `BILL-1001` via `Sale.save()`.
- Discount: `DISC-001` via `Discount.save()`.
- Product Wastage: `PW-001`, Ingredient Wastage: `IW-001`, Wastage Reason: `WR-001` via respective model save methods.

### 2. Critical Code Snippets
```python
# Backend/api/signals.py
@receiver(pre_save, sender=User)
def generate_employee_id(sender, instance, **kwargs):
    ...
    instance.employee_id = f'EMP-{new_number:03d}'
```

```python
# Backend/api/models/sale.py
def save(self, *args, **kwargs):
    if not self.bill_number:
        ...
        self.bill_number = f'BILL-{new_num}'
    ...
    super().save(*args, **kwargs)
```

```python
# Backend/api/models/batch.py
@receiver(pre_save, sender=IngredientBatch)
def auto_generate_batch_id(sender, instance, **kwargs):
    if not instance.batch_id:
        instance.batch_id = f"BATCH-{1000 + next_number}"
```

### 3. Logic Flow
Create request -> model/signal checks missing code field -> fetches latest record sequence -> increments and formats with prefix -> persists stable business ID.

### 4. Code Location for Screenshots
- Backend/api/signals.py | `generate_employee_id` | approx lines 6-28
- Backend/api/models/product.py | `save()` product id generation | approx lines 156-174
- Backend/api/models/ingredient.py | `auto_generate_ingredient_id` | approx lines 218-226
- Backend/api/models/batch.py | `auto_generate_batch_id` | approx lines 257-263
- Backend/api/models/batch_product.py | `save()` batch id generation | approx lines 153-167
- Backend/api/models/sale.py | `save()` bill number generation | approx lines 114-124
- Backend/api/models/discount.py | `save()` discount id generation | approx lines 110-119
- Backend/api/models/product_wastage.py | `save()` wastage id generation | approx lines 106-122
- Backend/api/models/ingredient_wastage.py | `save()` wastage id generation | approx lines 105-121
- Backend/api/models/wastage_reason.py | `save()` reason id generation | approx lines 47-60

---

## 6) Transaction-Type Tracking (Add / Use / Wastage / Adjustment)

### 1. Technical Explanation
Transaction semantics are encoded in stock history models:
- Ingredient history supports: `AddStock`, `UseStock`, `Wastage`, `Adjustment`.
- Product history supports equivalent tracked transaction categories (`AddStock`, `UseStock`, etc.).
- History summaries aggregate counts and net stock change per transaction type.

### 2. Critical Code Snippets
```python
# Backend/api/models/stock_history.py
TRANSACTION_TYPES = [
    ('AddStock', 'Add Stock'),
    ('UseStock', 'Use Stock'),
    ('Wastage', 'Wastage'),
    ('Adjustment', 'Adjustment'),
]
```

```python
# Backend/api/views/stock_history.py
@action(detail=False, methods=['get'])
def summary(self, request, **kwargs):
    summary = {}
    for trans_type in ['AddStock', 'UseStock', 'Wastage', 'Adjustment']:
        transactions = queryset.filter(transaction_type=trans_type)
        summary[trans_type] = {
            'count': transactions.count(),
            'total_change': sum(t.change_amount for t in transactions) if transactions.exists() else 0
        }
    return Response(summary)
```

### 3. Logic Flow
Operational event occurs -> stock history row stored with `transaction_type` -> summary endpoint groups by type -> dashboard/audit users compare movement patterns.

### 4. Code Location for Screenshots
- Backend/api/models/stock_history.py | `TRANSACTION_TYPES` and fields | approx lines 14-62
- Backend/api/models/product.py | `ProductStockHistory.TRANSACTION_TYPES` | approx lines 205-211
- Backend/api/views/stock_history.py | `summary` (product) | approx lines 149-165
- Backend/api/views/stock_history.py | `summary` (ingredient) | approx lines 306-322

---

## 7) Historical Filtering by Date / Type / Entity

### 1. Technical Explanation
Audit APIs provide multiple filters:
- Date range via `start_date`, `end_date`.
- Entity scope via `product_id`, `ingredient_id`, `batch_id`.
- Type scope via `transaction_type` and summary actions.
- Search by references (e.g., `sale_bill_number`, notes/reference IDs).
This supports reconciliation and compliance audits.

### 2. Critical Code Snippets
```python
# Backend/api/views/stock_history.py (product)
def get_queryset(self):
    queryset = ProductStockHistory.objects.all()
    start_date = self.request.query_params.get('start_date')
    end_date = self.request.query_params.get('end_date')
    ...
    search = self.request.query_params.get('search')
    if search:
        queryset = queryset.filter(Q(sale_bill_number__icontains=search))
    return queryset
```

```python
# Backend/api/views/stock_history.py (ingredient)
@action(detail=False, methods=['get'])
def by_batch(self, request, **kwargs):
    batch_id = request.query_params.get('batch_id')
    if not batch_id:
        return Response({'error': 'batch_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    history = IngredientStockHistory.objects.filter(batch_id=batch_id).order_by('-created_at')
    ...
```

```typescript
// Frontend/src/components/StockManagementScreen.tsx
setStockHistoryModal({ open: true, itemName: p.name, itemId: p.id, productApiId: p.apiId });
setIngredientStockHistoryModal({ open: true, ingredient: p });
```

### 3. Logic Flow
User opens history screen/modal -> frontend passes entity IDs and filters -> backend history viewset filters queryset -> returns ordered entries -> user reviews audit trail by date/type/entity.

### 4. Code Location for Screenshots
- Backend/api/views/stock_history.py | `get_queryset` product filters | approx lines 66-93
- Backend/api/views/stock_history.py | `date_range`, `by_product` | approx lines 103-147
- Backend/api/views/stock_history.py | `get_queryset` ingredient filters | approx lines 205-237
- Backend/api/views/stock_history.py | `by_ingredient`, `by_batch`, `date_range` | approx lines 243-304
- Frontend/src/components/StockManagementScreen.tsx | history modal state and triggers | approx lines 368-379, 929-942, 1185-1196
- Frontend/src/components/modal/ItemStockHistoryModal.tsx | fetch/render product history/batches | approx lines 28-108
- Frontend/src/components/modal/ingredient modal/IngredientStockHistoryModal.tsx | fetch/render ingredient history | approx lines 43-117

---

## 8) Counter-Session Support (Operational Session Open/Close)

### 1. Technical Explanation
Counter session is implemented as a model for shift/session lifecycle:
- `CounterSession` stores who opened/closed and timestamps.
- `is_active` indicates whether counter/shift is currently open.
- Indexed fields support querying active session and session history quickly.
This supports POS accountability and shift-level reconciliation design.

### 2. Critical Code Snippets
```python
# Backend/api/models/counter_session.py
class CounterSession(models.Model):
    opened_at = models.DateTimeField(default=timezone.now, db_index=True)
    closed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    opened_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='opened_counter_sessions')
    closed_by = models.ForeignKey('User', on_delete=models.PROTECT, related_name='closed_counter_sessions', null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
```

### 3. Logic Flow
Session open -> create `CounterSession` with `opened_by`, `is_active=True` -> session close updates `closed_at`, `closed_by`, `is_active=False` -> session logs available for operational auditing.

### 4. Code Location for Screenshots
- Backend/api/models/counter_session.py | `CounterSession` model | approx lines 5-31
- Backend/api/models/sale.py | sale model (session-adjacent operational context) | approx lines 7-143
- Backend/api/views/sale_views.py | active/date-range analytics for operational periods | approx lines 136-221

---

## Compliance Architecture Pattern (Category 2)
- Detection layer: low-stock/out-of-stock/expiring endpoints + dashboard ingestion.
- Traceability layer: auto-generated business IDs + stock history references.
- Audit layer: immutable history rows with before/after quantities, actor and timestamps.
- Control layer: role-based access + manager-only adjustment/reset endpoints.
- Reporting layer: history filters and summaries by date/type/entity.

## Notes for Report Screenshots
- For each function, capture:
  - one backend model block
  - one backend view/action block
  - one frontend consumer block (where available)
- Use the class/function names listed above in VS Code search for quick navigation.
