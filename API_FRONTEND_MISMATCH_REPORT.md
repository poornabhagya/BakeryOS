# Backend API ↔ Frontend Type Mismatches Report

## Executive Summary
The backend serializers and frontend TypeScript types have **critical mismatches** that will cause runtime errors. This report documents all detected mismatches, organized by entity and severity.

---

## 🔴 CRITICAL MISMATCHES (Will Cause Runtime Errors)

### 1. USER ENTITY - Done

#### Frontend Type (AuthContext.tsx)
```typescript
export interface AuthUser {
  username: string;
  name: string;        // ⚠️ NOT PROVIDED BY BACKEND
  role: UserRole;
  avatarColor?: string;
}
```

#### Backend Response (UserListSerializer)
```python
fields = [
    'id',
    'username',
    'email',
    'full_name',      # ← Backend provides 'full_name', not 'name'
    'employee_id',
    'role',
    'status',
    'contact',
    'created_at',
    'updated_at'
]
```

**Issues:**
- ✗ Frontend expects `name` → Backend returns `full_name`
- ✗ Frontend field mapping will fail on login

**Fix:** Map `full_name` to `name` in AuthContext.tsx or update frontend to use `full_name`

---

### 2. PRODUCT ENTITY - Done

#### Frontend Type (BillingScreen.tsx)
```typescript
interface Product {
  id: number;
  name: string;
  price: number;        // ⚠️ MISMATCH: backend uses 'selling_price'
  stock: number;        // ⚠️ MISMATCH: backend uses 'current_stock'
  image: string;        // ⚠️ MISMATCH: backend uses 'image_url'
  category: string;     // ⚠️ MISMATCH: backend returns 'category_id' + 'category_name'
  itemId: string;       // ⚠️ MISMATCH: backend uses 'product_id'
}
```

#### Backend Response (ProductListSerializer)
```python
fields = [
    'id', 'product_id', 'name',
    'category_id', 'category_name',
    'cost_price', 'selling_price',  # ← NOT 'price'
    'profit_margin',
    'current_stock',                # ← NOT 'stock'
    'status', 'shelf_life', 'shelf_unit',
    'created_at'
]
```

#### Product Model
```python
# Auto-generated fields
product_id = models.CharField()      # Format: #PROD-1001
image_url = models.URLField()        # ← NOT 'image'
current_stock = models.DecimalField()
```

**Issues:**
| Frontend | Backend | Type Mismatch |
|----------|---------|---|
| `price` | `selling_price` | ✗ Field name mismatch |
| `stock` | `current_stock` | ✗ Field name mismatch |
| `image` | `image_url` | ✗ Field name mismatch |
| `category` | `category_id` + `category_name` | ✗ Structure mismatch |
| `itemId` | `product_id` | ✗ Field name mismatch |
| `price: number` | `selling_price: Decimal` | ⚠️ Type mismatch |
| `stock: number` | `current_stock: Decimal` | ⚠️ Type mismatch |

**Fix:** Update BillingScreen.tsx Product interface to match backend:
```typescript
interface Product {
  id: number;
  product_id: string;      // e.g., "#PROD-1001"
  name: string;
  selling_price: number;   // OR rename backend field
  cost_price: number;
  current_stock: number;   // OR rename backend field
  image_url: string;       // OR rename backend field
  category_id: number;
  category_name: string;
  profit_margin: number;
  status: string;
  shelf_life: number;
  shelf_unit: string;
}
```

---

### 3. SALE ENTITY - Done

#### Frontend Type (SalesSummary.tsx)
```typescript
type Sale = {
  id: string;           // ⚠️ Backend returns 'id: integer'
  date: string;         // ⚠️ MISMATCH: backend uses 'date_time'
  time: string;         // ⚠️ MISMATCH: not separated from date
  items: string;        // ⚠️ MISMATCH: backend provides items array
  total: number;        // ⚠️ MISMATCH: backend uses 'total_amount'
};
```

#### Backend Response (SaleListSerializer)
```python
fields = [
    'id',              # integer pk
    'bill_number',     # e.g., "BILL-1001"
    'cashier_id',
    'cashier_name',
    'subtotal',
    'discount_id',
    'discount_name',
    'discount_amount',
    'total_amount',    # ← NOT 'total'
    'payment_method',
    'item_count',
    'date_time',       # ← Combined DateTime, NOT separated 'date' + 'time'
    'created_at'
]
```

**Issues:**
| Frontend | Backend | Issue |
|----------|---------|-------|
| `id: string` | `id: int` | Type mismatch |
| `date: string` | `date_time: DateTime` | Format mismatch |
| `time: string` | (in `date_time`) | Not provided separately |
| `items: string` | `items: array` (via SaleDetailSerializer) | Structure mismatch |
| `total: number` | `total_amount: Decimal` | Field name + type mismatch |

**Fix:** Update SalesSummary.tsx to match backend:
```typescript
type Sale = {
  id: number;              // integer PK
  bill_number: string;     // "BILL-1001"
  cashier_id: number;
  cashier_name: string;
  subtotal: number;
  discount_id: number | null;
  discount_name: string | null;
  discount_amount: number;
  total_amount: number;    // Rename 'total' to 'total_amount'
  payment_method: string;
  item_count: number;
  date_time: string;       // ISO datetime string
  created_at: string;
};
```

---

### 4. CART ITEM ENTITY - Done

#### Frontend Definition (BillingScreen.tsx)
```typescript
interface CartItem extends Product {
  quantity: number;
}

// But Product interface has mismatches (see above)
// Also missing 'unit_price' field for line items
```

#### Backend Response (SaleItemSerializer)
```python
fields = [
    'id',
    'product_id',
    'product_id_val',
    'product_name',
    'quantity',
    'unit_price',      # ← Frontend CartItem doesn't have this
    'subtotal',        # ← Frontend CartItem doesn't have this
    'created_at'
]
```

**Issues:**
- ✗ `unit_price` not in CartItem interface
- ✗ `subtotal` not in CartItem interface
- ✗ `product_id_val` redundant field naming issue

---

## 🟡 MODERATE ISSUES (May Cause Runtime Errors)

### 5. Numeric Type Mismatches

**Problem:** Backend uses `DecimalField`, frontend uses `number`

```python
# Backend
selling_price = models.DecimalField(max_digits=10, decimal_places=2)
current_stock = models.DecimalField(max_digits=10, decimal_places=2)
total_amount = models.DecimalField(max_digits=12, decimal_places=2)
```

When serialized to JSON, these become strings: `"450.50"` not `450.50`

**Frontend Impact:**
```typescript
// This could fail:
const cartTotal = items.reduce((sum, item) => sum + item.price, 0);
// If item.price is a string: "450.50", result will be "0450.50" (string concatenation)
```

**Fix:** Ensure parseFloat() parsing or TypeScript strict number types

---

### 6. Missing Backend Fields (Frontend will try to access)

**Frontend Components may expect:**
- `user.email` - Available ✓
- `user.avatarColor` - Backend provides `avatar_color` (snake_case) ✗
- `product.costPrice` - Backend provides `cost_price` (snake_case) ✗
- `product.profitMargin` - Backend provides `profit_margin` (snake_case) ✗

---

### 7. Pagination Mismatches

**Frontend likely expects:**
```typescript
{
  results: Product[],
  count: number,
  next?: string,
  previous?: string
}
```

**Backend provides (DRF standard):**
```python
{
    "count": 100,
    "next": "http://api.example.com/users/?page=4",
    "previous": "http://api.example.com/users/?page=2",
    "results": [...]
}
```

This is actually compatible ✓

---

## 📋 FIELD-BY-FIELD MAPPING REFERENCE

### User Mapping
| Frontend | Backend | Status |
|----------|---------|--------|
| `username` | `username` | ✓ OK |
| `name` | `full_name` | ✗ MISMATCH |
| `role` | `role` | ✓ OK |
| `avatarColor` | `avatar_color` | ⚠️ Case mismatch |
| (none) | `id` | ✓ Extra field |
| (none) | `email` | ✓ Extra field |
| (none) | `nic` | ✓ Extra field |

### Product Mapping
| Frontend | Backend | Status |
|----------|---------|--------|
| `id` | `id` | ✓ OK |
| `itemId` | `product_id` | ✗ MISMATCH |
| `name` | `name` | ✓ OK |
| `price` | `selling_price` | ✗ MISMATCH |
| `stock` | `current_stock` | ✗ MISMATCH |
| `image` | `image_url` | ✗ MISMATCH |
| `category` | `category_name` | ⚠️ Partial match |
| (none) | `cost_price` | ✓ Extra field |
| (none) | `profit_margin` | ✓ Extra field |
| (none) | `status` | ✓ Extra field |

### Sale Mapping
| Frontend | Backend | Status |
|----------|---------|--------|
| `id` | `id` or `bill_number` | ⚠️ Ambiguous |
| `date` | (in `date_time`) | ✗ Not separate |
| `time` | (in `date_time`) | ✗ Not separate |
| `items` | `item_count` or `items` (detail endpoint) | ⚠️ Mismatch |
| `total` | `total_amount` | ✗ MISMATCH |

---

## 🔧 RECOMMENDED FIXES (Priority Order)

### PRIORITY 1: Critical (App will crash)
1. **User field mapping** - Update AuthContext.tsx
   - Map `full_name` → `name`
   - Handle `avatar_color` case mismatch

2. **Product field mapping** - Update BillingScreen.tsx
   - Rename `price` → `selling_price`
   - Rename `stock` → `current_stock`
   - Rename `image` → `image_url`
   - Update category handling

3. **Sale field mapping** - Update SalesSummary.tsx
   - Rename `total` → `total_amount`
   - Parse `date_time` into separate date/time variables
   - Use `bill_number` as display ID

### PRIORITY 2: High (Calculations will break)
4. **Numeric type handling**
   - Add parseFloat() for all price/quantity operations
   - Consider decimal.js library for precise calculations

5. **Field naming standardization**
   - Frontend: Use snake_case consistently OR
   - Backend: Use camelCase consistently

### PRIORITY 3: Medium (Will fail on advanced features)
6. **CartItem interface completion**
   - Add `unit_price` field
   - Add `subtotal` field

7. **API response standardization**
   - Document exact response format for each endpoint
   - Create shared TypeScript types based on actual backend responses

---

## 📝 IMPLEMENTATION CHECKLIST

### Backend Side (Optional - if standardizing)
- [ ] Consider adding a `@action` to return camelCase versions
- [ ] Or add a serializer filter for case conversion
- [ ] Document all response schemas clearly

### Frontend Side (Required)
- [ ] Update `AuthUser` interface in AuthContext.tsx
- [ ] Update `Product` interface in BillingScreen.tsx
- [ ] Update `Sale` interface in SalesSummary.tsx
- [ ] Update `CartItem` interface
- [ ] Add field mapping in API service layer
- [ ] Add numeric type parsing utility
- [ ] Add date/time parsing utility
- [ ] Test all CRUD operations with real backend data

---

## 🧪 TESTING RECOMMENDATIONS

Create test cases for:
```typescript
// Test User mapping
const mockUserResponse = {
  id: 1,
  username: 'manager1',
  full_name: 'John Manager',
  email: 'john@bakery.com',
  role: 'Manager',
  avatar_color: 'bg-purple-600'
};

// Test Product mapping
const mockProductResponse = {
  id: 1,
  product_id: '#PROD-1001',
  name: 'Fish Bun',
  selling_price: 80,
  cost_price: 40,
  current_stock: 10,
  image_url: 'https://...',
  category_id: 1,
  category_name: 'Buns',
  profit_margin: 100
};

// Test Sale mapping
const mockSaleResponse = {
  id: 1,
  bill_number: 'BILL-1001',
  cashier_id: 1,
  cashier_name: 'Cashier1',
  subtotal: 1500,
  discount_id: null,
  discount_amount: 0,
  total_amount: 1500,
  payment_method: 'Cash',
  item_count: 3,
  date_time: '2024-01-15T09:30:00Z'
};
```

---

## 📊 Impact Summary

| Component | Severity | Affected Features |
|-----------|----------|------------------|
| User Authentication | CRITICAL | Login, User display |
| Product Display | CRITICAL | Billing, Stock Management |
| Sale Processing | CRITICAL | Billing, Reports |
| Calculations | HIGH | Cart totals, Profit margins |
| Data Type Handling | MEDIUM | All numeric operations |

---

Generated: 2024
Report Type: API/Frontend Integration Audit
