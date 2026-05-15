# BakeryOS Implementation - Category 1 Core Business Functions

## Scope
This document explains all Category 1 core business functions in BakeryOS:
1. User authentication with token login/logout/me
2. Role-based access control
3. User/staff management
4. Product management
5. Ingredient management
6. Ingredient batch management
7. FIFO ingredient consumption for production
8. Recipe management
9. Product batch (production run) management
10. POS sales/checkout
11. Discount management
12. Wastage tracking
13. Wastage reason master management
14. Category management
15. Stock reset/adjustment

## Relevant Folder Map
- Backend core business code:
  - Backend/api/models/
  - Backend/api/views/
  - Backend/api/serializers/
  - Backend/api/services/
  - Backend/api/permissions.py
  - Backend/api/signals.py
  - Backend/api/urls.py
- Frontend core business code:
  - Frontend/src/context/
  - Frontend/src/services/
  - Frontend/src/components/
  - Frontend/src/App.tsx

---

## 1) User Authentication (Login/Logout/Current User)

### 1. Technical Explanation
Authentication is implemented using DRF Token Authentication.
- API endpoints are wired in `Backend/api/urls.py`.
- Auth views are in `Backend/api/views/auth_token.py`.
- Login validates credentials using serializer and returns token + user payload.
- Logout deletes the current auth token.
- Me endpoint returns current authenticated user profile.
- Frontend stores token and sends `Authorization: Token <token>` via `Frontend/src/services/api.ts`.

### 2. Critical Code Snippets
```python
# Backend/api/views/auth_token.py (core login logic)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            user_serializer = UserSerializer(user)
            return Response({'token': token.key, 'user': user_serializer.data}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials or user is inactive'}, status=status.HTTP_401_UNAUTHORIZED)
```

```typescript
// Frontend/src/services/api.ts (token header logic)
function getAuthHeaders(): Record<string, string> {
  const token = getAccessToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Token ${token}` }),
  };
}
```

### 3. Logic Flow
Request -> `LoginView.post()` -> `LoginSerializer` credential validation -> token create/get -> JSON response with token/user -> frontend stores token -> subsequent requests include Authorization header.

### 4. Code Location for Screenshots
- Backend/api/views/auth_token.py | `LoginView` | approx lines 10-57
- Backend/api/views/auth_token.py | `LogoutView` | approx lines 59-92
- Backend/api/views/auth_token.py | `MeView` | approx lines 94-132
- Backend/api/urls.py | auth route mapping | approx lines 42-51
- Frontend/src/services/api.ts | `getAuthHeaders`, token methods | approx lines 20-52
- Frontend/src/context/AuthContext.tsx | `AuthProvider`, `login`, `logout` | approx lines 23-111

---

## 2) Role-Based Access Control (Manager/Cashier/Baker/Storekeeper)

### 1. Technical Explanation
RBAC is enforced in both backend and frontend.
- Backend permission classes are in `Backend/api/permissions.py` (`IsManager`, `IsManagerOrReadOnly`, etc.).
- ViewSets choose permissions dynamically per action.
- Frontend limits visible pages using role-page matrix in `Frontend/src/App.tsx` (`PAGE_ACCESS`).

### 2. Critical Code Snippets
```python
# Backend/api/permissions.py
class IsManager(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'Manager'

class IsManagerOrReadOnly(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user.role == 'Manager'
```

```typescript
// Frontend/src/App.tsx
const PAGE_ACCESS: Record<UserRole, MenuPage[]> = {
  Manager: ['dashboard', 'users', 'billing', 'stock', 'wastage', 'saleshistory', 'discount', 'notification'],
  Cashier: ['billing', 'stock', 'wastage', 'saleshistory', 'discount', 'notification'],
  Baker: ['dashboard', 'stock', 'wastage', 'notification'],
  Storekeeper: ['dashboard', 'stock', 'wastage', 'notification'],
};
```

### 3. Logic Flow
Request with token -> permission class chosen in `get_permissions()` -> role check with `request.user.role` -> allow/deny (403). In frontend, role decides available menu and page routing.

### 4. Code Location for Screenshots
- Backend/api/permissions.py | `IsManager` | approx lines 25-34
- Backend/api/permissions.py | `IsManagerOrReadOnly` | approx lines 121-140
- Backend/api/permissions.py | `IsManagerOrSelf` | approx lines 142-177
- Frontend/src/App.tsx | `PAGE_ACCESS`, `canAccessPage` | approx lines 27-53

---

## 3) User/Staff Management (CRUD, profile, status)

### 1. Technical Explanation
Staff operations are handled by `UserViewSet` with action-level permissions and serializer switching.
- User model stores role, status, employee_id, contact/NIC.
- `destroy()` is implemented as soft delete (`status='inactive'`, `is_active=False`).
- `status` action updates user status without full profile update.
- Employee ID generation is handled by signal in `Backend/api/signals.py`.

### 2. Critical Code Snippets
```python
# Backend/api/views/user_views.py (soft-delete)
def destroy(self, request, *args, **kwargs):
    instance = self.get_object()
    if request.user.id == instance.id:
        return Response({'detail': 'Cannot delete your own account'}, status=status.HTTP_400_BAD_REQUEST)
    instance.status = 'inactive'
    instance.is_active = False
    instance.save()
    return Response({'detail': 'User deleted (marked as inactive)'}, status=status.HTTP_204_NO_CONTENT)
```

```python
# Backend/api/signals.py (employee id)
@receiver(pre_save, sender=User)
def generate_employee_id(sender, instance, **kwargs):
    if not instance.employee_id:
        ...
        instance.employee_id = f'EMP-{new_number:03d}'
```

### 3. Logic Flow
Request -> `UserViewSet` action -> serializer validation -> user model write -> response. For create/update, permissions and object-level checks are applied first. Signal auto-fills employee ID on save.

### 4. Code Location for Screenshots
- Backend/api/models/user.py | `User` model | approx lines 5-35
- Backend/api/views/user_views.py | `UserViewSet` class | approx lines 36-260
- Backend/api/views/user_views.py | `destroy` soft-delete | approx lines 221-250
- Backend/api/signals.py | `generate_employee_id` | approx lines 6-28
- Frontend/src/components/UserManagement.tsx | `UserManagement` and fetch/filter logic | approx lines 91-210

---

## 4) Product Management (CRUD, pricing, stock, category)

### 1. Technical Explanation
Product domain is implemented by `Product` model + `ProductViewSet`.
- Product has `cost_price`, `selling_price`, dynamic `profit_margin`, stock status helpers.
- Category FK (`category_id`) enforces product-category structure.
- `product_id` auto-generated in model/signal.
- Custom actions: `low_stock`, `out_of_stock`, `by_category`, `recipe`.

### 2. Critical Code Snippets
```python
# Backend/api/models/product.py
class Product(models.Model):
    product_id = models.CharField(max_length=50, unique=True, editable=False)
    category_id = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def profit_margin(self):
        if self.cost_price == 0:
            return 0
        return ((self.selling_price - self.cost_price) / self.cost_price) * 100
```

```python
# Backend/api/views/product_views.py
@action(detail=False, methods=['get'])
def low_stock(self, request):
    queryset = self.get_queryset().filter(current_stock__lt=10)
    serializer = ProductListSerializer(queryset, many=True)
    return Response({'count': queryset.count(), 'results': serializer.data})
```

### 3. Logic Flow
Request -> `ProductViewSet` -> serializer per action -> model write/read -> optional custom filter action -> response. Stock values are further impacted by production/sales/wastage workflows.

### 4. Code Location for Screenshots
- Backend/api/models/product.py | `Product` model, `profit_margin` | approx lines 8-154
- Backend/api/views/product_views.py | `ProductViewSet` | approx lines 31-123
- Backend/api/views/product_views.py | `low_stock`, `out_of_stock` | approx lines 166-203
- Backend/api/models/category.py | category FK target model | approx lines 7-94
- Frontend/src/components/StockManagementScreen.tsx | product data handling | approx lines 73-240

---

## 5) Ingredient Management (CRUD, supplier, thresholds, soft delete)

### 1. Technical Explanation
Ingredient inventory is handled in `Ingredient` model and `IngredientViewSet`.
- Tracks supplier, supplier contact, tracking/base unit, thresholds.
- Uses `is_active` for soft delete.
- Provides custom endpoints for `low_stock`, `out_of_stock`, `history`, `reset_quantity`.

### 2. Critical Code Snippets
```python
# Backend/api/models/ingredient.py
class Ingredient(models.Model):
    ingredient_id = models.CharField(max_length=50, unique=True, editable=False)
    supplier = models.CharField(max_length=100, blank=True, null=True)
    supplier_contact = models.CharField(max_length=100, blank=True, null=True)
    total_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    low_stock_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=10)
    is_active = models.BooleanField(default=True)
```

```python
# Backend/api/views/ingredient_views.py
def destroy(self, request, *args, **kwargs):
    instance = self.get_object()
    instance.is_active = False
    instance.save()
    return Response({'message': f'Ingredient {instance.ingredient_id} marked as inactive.'}, status=status.HTTP_200_OK)
```

### 3. Logic Flow
Request -> `IngredientViewSet` action -> serializer validation -> ingredient model update -> response. For delete, state is soft-deactivated instead of hard delete.

### 4. Code Location for Screenshots
- Backend/api/models/ingredient.py | `Ingredient` model | approx lines 7-189
- Backend/api/views/ingredient_views.py | `IngredientViewSet` | approx lines 29-275
- Backend/api/views/ingredient_views.py | `destroy`, `low_stock`, `reset_quantity` | approx lines 145-167, 168-183, 247-276
- Frontend/src/components/StockManagementScreen.tsx | ingredient fetch/mapping | approx lines 161-240

---

## 6) Ingredient Batch Management (receive stock, qty, cost, expiry)

### 1. Technical Explanation
Batch-level ingredient stock is represented by `IngredientBatch`.
- Tracks received quantity, remaining quantity (`current_qty`), cost, dates, status.
- FIFO-friendly ordering (`ordering = ['expire_date', 'made_date']`).
- Batch actions in `BatchViewSet`: expiring, expired, consume, by_ingredient.
- Post-save/delete signals sync parent ingredient `total_quantity`.

### 2. Critical Code Snippets
```python
# Backend/api/models/batch.py
class IngredientBatch(models.Model):
    batch_id = models.CharField(max_length=50, unique=True, editable=False)
    ingredient_id = models.ForeignKey(Ingredient, on_delete=models.PROTECT, related_name='batches')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    current_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_batch_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    expire_date = models.DateTimeField()

    class Meta:
        ordering = ['expire_date', 'made_date']
```

```python
# Backend/api/views/batch_views.py
@action(detail=True, methods=['post'], url_path='consume')
def consume(self, request, pk=None):
    batch = self.get_object()
    serializer = BatchConsumeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    result = batch.consume(serializer.validated_data['amount'])
    ...
```

### 3. Logic Flow
Receive stock -> create `IngredientBatch` -> signals update ingredient total -> batches queried by status/expiry/FIFO order -> consume endpoint deducts from selected batch.

### 4. Code Location for Screenshots
- Backend/api/models/batch.py | `IngredientBatch` model | approx lines 8-221
- Backend/api/models/batch.py | signal handlers (`auto_generate_batch_id`, sync) | approx lines 228-260+
- Backend/api/views/batch_views.py | `BatchViewSet` | approx lines 33-170
- Backend/api/views/batch_views.py | `expiring`, `consume`, `by_ingredient` | approx lines 181-258, 237-267, 268-301
- Frontend/src/components/modal/AddNewBatchModal.tsx | batch creation UI | locate component start in file

---

## 7) FIFO Ingredient Consumption for Production

### 1. Technical Explanation
FIFO production logic is centralized in service layer:
- `Backend/api/services/production_service.py` -> `produce_product()`.
- Wrapped in `@transaction.atomic` to guarantee all-or-nothing stock deduction.
- Uses `select_for_update()` and ordered active batches by expiry.
- Fails with validation error if any ingredient is insufficient.

### 2. Critical Code Snippets
```python
# Backend/api/services/production_service.py
@transaction.atomic
def produce_product(product_id: int, quantity_to_produce: Decimal | int | float | str):
    ...
    for recipe_item in recipe_items:
        total_required = recipe_item.quantity_required * qty_to_produce
        fifo_batches = (
            IngredientBatch.objects.select_for_update()
            .filter(ingredient_id=ingredient, status='Active', current_qty__gt=0)
            .order_by('expire_date', 'id')
        )
        for batch in fifo_batches:
            ...
```

```python
# Backend/api/views/batch_product_views.py (uses service)
production_result = produce_product(
    product_id=int(product_id),
    quantity_to_produce=quantity_to_produce,
)
```

### 3. Logic Flow
Production request -> `ProductBatchViewSet.create()` -> `produce_product()` -> lock product/recipe/batches -> FIFO deduction across batches -> update product stock -> create product batch log + stock history -> commit transaction.

### 4. Code Location for Screenshots
- Backend/api/services/production_service.py | `produce_product` | approx lines 44-152
- Backend/api/views/batch_product_views.py | `create` service integration | approx lines 125-171
- Backend/api/models/batch.py | FIFO ordering metadata | approx lines 83-90

---

## 8) Recipe Management (items, quantities, validation)

### 1. Technical Explanation
Recipes are represented by junction model `RecipeItem` (`product_id` + `ingredient_id` + `quantity_required`).
- Unique pair constraint prevents duplicate ingredient lines.
- Recipe CRUD and checks are in `RecipeViewSet`.
- Validation endpoint checks if required ingredients are in stock.
- Batch requirement endpoint computes ingredient needs for requested output quantity.

### 2. Critical Code Snippets
```python
# Backend/api/models/recipe.py
class RecipeItem(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='recipe_items')
    ingredient_id = models.ForeignKey(Ingredient, on_delete=models.PROTECT, related_name='used_in_recipes')
    quantity_required = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ['product_id', 'ingredient_id']
```

```python
# Backend/api/views/recipe_views.py
@action(detail=True, methods=['get'], url_path='validate')
def validate_recipe(self, request, pk=None):
    ...
    for item in recipe_items:
        available = item.ingredient_id.total_quantity
        required = item.quantity_required
        if available < required:
            can_make = False
            missing.append({...})
```

### 3. Logic Flow
Manager defines recipe items -> stored in `RecipeItem` -> production/validation reads recipe -> checks inventory sufficiency -> returns missing ingredient details if insufficient.

### 4. Code Location for Screenshots
- Backend/api/models/recipe.py | `RecipeItem` model | approx lines 8-71
- Backend/api/views/recipe_views.py | `RecipeViewSet` | approx lines 21-44
- Backend/api/views/recipe_views.py | `add_item`, `update_item`, `remove_item` | approx lines 84-180
- Backend/api/views/recipe_views.py | `validate_recipe`, `batch_required` | approx lines 184-319

---

## 9) Product Batch Management (production runs, quantity, expiry)

### 1. Technical Explanation
Finished-goods batches are managed by `ProductBatch` and `ProductBatchViewSet`.
- `ProductBatch` stores produced quantity, remaining quantity, made date, expiry date, status.
- Expiry date derives from product shelf life.
- Stock history entries are created on create/update/delete batch operations.
- `get_expiring` and `use_batch` actions support production operations.

### 2. Critical Code Snippets
```python
# Backend/api/models/batch_product.py
class ProductBatch(models.Model):
    batch_id = models.CharField(max_length=50, unique=True, editable=False)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    current_qty = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    made_date = models.DateField()
    expire_date = models.DateField()
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
    )
    ...
```

### 3. Logic Flow
Production run recorded -> `ProductBatch` created -> product stock incremented and audited -> batch status and expiry tracked over time -> frontend baker workflows consume/view expiring batches.

### 4. Code Location for Screenshots
- Backend/api/models/batch_product.py | `ProductBatch` model | approx lines 9-175
- Backend/api/views/batch_product_views.py | `ProductBatchViewSet` | approx lines 31-95
- Backend/api/views/batch_product_views.py | `create`, `get_expiring`, `use_batch` | approx lines 125-219
- Frontend/src/components/dashboard/BakerDashboard.tsx | production dashboard workflow | locate main component function

---

## 10) POS Sales/Checkout (cart, bill, sale, payment)

### 1. Technical Explanation
Sales module uses header-detail model:
- `Sale` = bill-level transaction metadata.
- `SaleItem` = line items with frozen unit price and subtotal.
- `SaleViewSet.create()` uses serializer to validate and persist sale.
- Frontend billing screen handles cart state, product search, discount application, and checkout request.

### 2. Critical Code Snippets
```python
# Backend/api/models/sale.py
class Sale(models.Model):
    bill_number = models.CharField(max_length=50, unique=True, editable=False)
    cashier_id = models.ForeignKey('User', on_delete=models.PROTECT, related_name='sales')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='Cash')
```

```python
# Backend/api/views/sale_views.py
def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    sale = serializer.save()
    output_serializer = SaleDetailSerializer(sale)
    return Response(output_serializer.data, status=status.HTTP_201_CREATED)
```

```typescript
// Frontend/src/components/BillingScreen.tsx
const [cart, setCart] = useState<CartItem[]>([]);
const [paymentMethod, setPaymentMethod] = useState<'Cash' | 'Card'>('Cash');
// ... fetch products, fetch next bill number, apply discounts, create sale
```

### 3. Logic Flow
Frontend cart build -> POST `/api/sales/` -> Sale serializer validates and computes totals -> `Sale` + `SaleItem` created -> response with bill details -> frontend renders latest sale/receipt.

### 4. Code Location for Screenshots
- Backend/api/models/sale.py | `Sale` and `SaleItem` models | approx lines 7-198
- Backend/api/views/sale_views.py | `SaleViewSet` class | approx lines 24-124
- Backend/api/views/sale_views.py | `create`, `payment_methods`, `analytics` | approx lines 124-303
- Frontend/src/components/BillingScreen.tsx | `BillingScreen` function | approx lines 103-320
- Frontend/src/components/CartPanel.tsx | cart UI and quantity updates | locate component start in file

---

## 11) Discount Management (percentage/fixed, date/time validity)

### 1. Technical Explanation
Discount rules are stored in `Discount` model.
- Supports `Percentage` and `FixedAmount`.
- Applicability: all products, category, or single product.
- Time windows via start/end date and start/end time.
- `DiscountViewSet.validate` checks applicability; `apply` returns calculated discount amount.

### 2. Critical Code Snippets
```python
# Backend/api/models/discount.py
class Discount(models.Model):
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    applicable_to = models.CharField(max_length=20, choices=APPLICABLE_TO_CHOICES)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    def calculate_discount_amount(self, amount):
        if self.discount_type == 'Percentage':
            return Decimal(str(amount)) * (Decimal(str(self.value)) / 100)
        elif self.discount_type == 'FixedAmount':
            return Decimal(str(self.value))
        return Decimal('0')
```

```python
# Backend/api/views/discount_views.py
@action(detail=True, methods=['post'])
def apply(self, request, pk=None):
    discount = self.get_object()
    amount = float(request.data.get('amount'))
    if not discount.is_applicable_at(timezone.now()):
        return Response({'error': 'Discount is not applicable at current time'}, status=status.HTTP_400_BAD_REQUEST)
    discount_amount = discount.calculate_discount_amount(amount)
    final_amount = amount - discount_amount
    return Response({'discount_amount': str(round(discount_amount, 2)), 'final_amount': str(round(final_amount, 2))})
```

### 3. Logic Flow
Manager defines discount rule -> save-time validation enforces constraints -> checkout asks validate/apply -> discount amount computed -> sale totals updated.

### 4. Code Location for Screenshots
- Backend/api/models/discount.py | `Discount` model and validation methods | approx lines 7-216
- Backend/api/views/discount_views.py | `DiscountViewSet` | approx lines 29-86
- Backend/api/views/discount_views.py | `validate`, `apply`, `active` | approx lines 167-285, 122-145
- Frontend/src/components/DiscountManagement.tsx | discount listing and filters | approx lines 31-220
- Frontend/src/components/BillingScreen.tsx | discount application in checkout | approx lines 280+

---

## 12) Wastage Tracking (product + ingredient, reason, reporter, loss)

### 1. Technical Explanation
Two dedicated models track losses:
- `ProductWastage`
- `IngredientWastage`
Both compute `total_loss = quantity * unit_cost`, store reason and reporting user, and feed analytics/history.
Views provide CRUD + analytics endpoints.

### 2. Critical Code Snippets
```python
# Backend/api/models/product_wastage.py
class ProductWastage(models.Model):
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2)
    total_loss = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    reason_id = models.ForeignKey('WastageReason', on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        self.total_loss = (self.quantity or Decimal('0')) * (self.unit_cost or Decimal('0'))
        ...
        super().save(*args, **kwargs)
```

```python
# Backend/api/views/ingredient_wastage.py
def create(self, request, *args, **kwargs):
    data = request.data.copy()
    if 'reported_by' not in data or not data['reported_by']:
        data['reported_by'] = request.user.id
    serializer = self.get_serializer(data=data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    return Response(IngredientWastageDetailSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)
```

### 3. Logic Flow
User submits wastage record -> serializer validation -> model computes loss and persists -> stock/audit signals update history -> analytics endpoints aggregate losses by reason/product/ingredient/date.

### 4. Code Location for Screenshots
- Backend/api/models/product_wastage.py | `ProductWastage` model | approx lines 7-153
- Backend/api/models/ingredient_wastage.py | `IngredientWastage` model | approx lines 6-139
- Backend/api/views/product_wastage.py | `ProductWastageViewSet` | approx lines 18-213
- Backend/api/views/ingredient_wastage.py | `IngredientWastageViewSet` | approx lines 16-225
- Frontend/src/components/WastageOverview.tsx | wastage fetch/filter UI | approx lines 31-220

---

## 13) Wastage Reason Master Management

### 1. Technical Explanation
Standardized reason definitions are maintained in `WastageReason` master table.
- Auto IDs like `WR-001`.
- Used as FK by both product and ingredient wastage entries.
- ViewSet supports list/create/update/delete and optional filtering of system reason labels.

### 2. Critical Code Snippets
```python
# Backend/api/models/wastage_reason.py
class WastageReason(models.Model):
    reason_id = models.CharField(max_length=20, unique=True, editable=False)
    reason = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.reason_id:
            ...
            self.reason_id = f'WR-{new_num}'
        super().save(*args, **kwargs)
```

```python
# Backend/api/views/wastage_reason.py
class WastageReasonViewSet(viewsets.ModelViewSet):
    queryset = WastageReason.objects.all()
    permission_classes = [permissions.IsAuthenticated]
```

### 3. Logic Flow
Manager defines reason catalog -> reason selected during wastage creation -> stored as FK -> reused for filtering and analytics across wastage modules.

### 4. Code Location for Screenshots
- Backend/api/models/wastage_reason.py | `WastageReason` model | approx lines 4-56
- Backend/api/views/wastage_reason.py | `WastageReasonViewSet` | approx lines 10-71
- Frontend/src/components/modal/AddWastageReasonModal.tsx | create reason UI | locate modal component start
- Frontend/src/components/modal/ViewWastageReasonsModal.tsx | reason list UI | locate modal component start

---

## 14) Category Management (Product and Ingredient categories)

### 1. Technical Explanation
A single `Category` model handles both domain types.
- `type` determines Product vs Ingredient category.
- ID generated with typed prefixes: CAT-Pxxx / CAT-Ixxx.
- Category endpoints allow listing, by-type filtering, and CRUD.
- Product and Ingredient models reference categories via FK with type constraints.

### 2. Critical Code Snippets
```python
# Backend/api/models/category.py
class Category(models.Model):
    TYPE_CHOICES = [('Product', 'Product'), ('Ingredient', 'Ingredient')]
    category_id = models.CharField(max_length=50, unique=True, blank=True, editable=False)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    class Meta:
        unique_together = [('type', 'name')]
```

```python
# Backend/api/views/category_views.py
@action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='by-type')
def by_type(self, request):
    category_type = request.query_params.get('type')
    if category_type not in ['Product', 'Ingredient']:
        return Response({'detail': "type must be 'Product' or 'Ingredient'"}, status=status.HTTP_400_BAD_REQUEST)
    categories = Category.objects.filter(type=category_type)
    return Response(CategoryListSerializer(categories, many=True).data)
```

### 3. Logic Flow
Category CRUD request -> `CategoryViewSet` permission check -> serializer/model persistence -> products/ingredients use category FK for grouping/filtering and threshold policy references.

### 4. Code Location for Screenshots
- Backend/api/models/category.py | `Category` model and ID generation | approx lines 7-94
- Backend/api/views/category_views.py | `CategoryViewSet` | approx lines 28-94
- Backend/api/views/category_views.py | `by_type`, `products`, `ingredients` | approx lines 96-154
- Frontend/src/components/modal/CategoryListModal.tsx | product category list UI | locate component start
- Frontend/src/components/modal/ingredient modal/IngredientCategoryListModal.tsx | ingredient category list UI | locate component start

---

## 15) Stock Reset/Adjustment Capabilities

### 1. Technical Explanation
Controlled stock correction and audit are implemented through two paths:
- Direct reset endpoint: `IngredientViewSet.reset_quantity`.
- Full audit trail through `ProductStockHistory` and `IngredientStockHistory` read-only viewsets.
Signals in `Backend/api/signals.py` generate history records on major stock events (batch create/delete, wastage, etc.).

### 2. Critical Code Snippets
```python
# Backend/api/views/ingredient_views.py
@action(detail=True, methods=['post'])
def reset_quantity(self, request, pk=None):
    if request.user.role != 'Manager':
        return Response({'error': 'Only managers can reset quantities.'}, status=status.HTTP_403_FORBIDDEN)
    ingredient = self.get_object()
    ingredient.total_quantity = 0
    ingredient.save()
    return Response({'message': f'Quantity reset for {ingredient.ingredient_id}'})
```

```python
# Backend/api/signals.py
@receiver(post_save, sender=IngredientBatch)
def create_ingredient_stock_history_on_batch_create(sender, instance, created, **kwargs):
    if created:
        ...
        IngredientStockHistory.objects.create(
            ingredient_id=ingredient,
            transaction_type='AddStock',
            qty_before=qty_before,
            qty_after=qty_after,
            change_amount=instance.quantity,
            reference_id=instance.batch_id,
        )
```

### 3. Logic Flow
Adjustment/reset request -> manager permission check -> quantity update -> later stock transactions tracked in history models -> history viewsets provide immutable audit evidence by date/type/entity.

### 4. Code Location for Screenshots
- Backend/api/views/ingredient_views.py | `reset_quantity` | approx lines 247-276
- Backend/api/models/stock_history.py | `IngredientStockHistory` model | approx lines 6-90
- Backend/api/models/product.py | `ProductStockHistory` model | approx lines 193-320
- Backend/api/views/stock_history.py | `ProductStockHistoryViewSet` | approx lines 29-166
- Backend/api/views/stock_history.py | `IngredientStockHistoryViewSet` | approx lines 168-339
- Backend/api/signals.py | stock history signal handlers | approx lines 58-149

---

## End-to-End Architecture Pattern (used across all Category 1 functions)
- Request -> View/ViewSet
- Permission check (`permissions.py` + action rules)
- Serializer validation and transformation
- Model save/update (with model-level logic)
- Signals/services for side effects (ID generation, stock history, notifications, FIFO production)
- Response serialization -> frontend API client -> UI state update

## Notes for Report Screenshots
- Use the exact class/method names listed above in VS Code search.
- Capture one screenshot for each:
  - model definition
  - view/action method
  - frontend screen/component logic
- Preferred screenshot spans: 20-40 lines around each listed method/class for clarity.
