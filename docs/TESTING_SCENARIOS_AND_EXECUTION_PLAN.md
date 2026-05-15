# 🧪 BakeryOS Complete Testing Scenarios & Execution Plan

**Status:** Ready for Testing Phase  
**Date:** March 26, 2026  
**Duration:** 3-5 days  
**Target:** 0 critical bugs, 80%+ test coverage  

---

## 📋 Testing Overview

This document contains all test scenarios for BakeryOS system. It covers:
- ✅ Automated testing (Unit + Integration)
- ✅ Manual E2E testing (All user roles)
- ✅ Error handling scenarios
- ✅ Performance testing
- ✅ Mobile/responsive testing
- ✅ Accessibility testing

---

## 🤖 PART 1: AUTOMATED TESTING

### 1.1 Backend Unit Tests

**File:** `Backend/api/tests.py`  
**Command:** `python manage.py test`  
**Target Coverage:** 80%+

#### Test Suite: Authentication
```python
# Test 1: Valid Login
def test_user_login_success(self):
    """Test valid credentials return JWT tokens"""
    response = self.client.post('/api/auth/login/', {
        'username': 'john_manager',
        'password': 'ValidPass123!'
    })
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data
    assert response.data['user']['role'] == 'Manager'

# Test 2: Invalid Credentials
def test_user_login_invalid(self):
    """Test invalid password returns 401"""
    response = self.client.post('/api/auth/login/', {
        'username': 'john_manager',
        'password': 'WrongPassword'
    })
    assert response.status_code == 401
    assert response.data['detail'] == 'Invalid credentials'

# Test 3: Token Refresh
def test_token_refresh(self):
    """Test refresh token returns new access token"""
    # Get initial tokens
    login_resp = self.client.post('/api/auth/login/', {...})
    refresh_token = login_resp.data['refresh']
    
    # Refresh token
    refresh_resp = self.client.post('/api/auth/refresh/', {
        'refresh': refresh_token
    })
    assert refresh_resp.status_code == 200
    assert 'access' in refresh_resp.data

# Test 4: Expired Token
def test_expired_token_rejected(self):
    """Test expired token returns 401"""
    # Use manually created expired token
    response = self.client.get('/api/users/', 
        HTTP_AUTHORIZATION='Bearer expired.token.here'
    )
    assert response.status_code == 401
```

#### Test Suite: Product API
```python
# Test 5: Get All Products
def test_get_all_products(self):
    """Test retrieving product list"""
    response = self.client.get('/api/products/')
    assert response.status_code == 200
    assert 'count' in response.data
    assert 'results' in response.data
    assert len(response.data['results']) > 0

# Test 6: Create Product (Manager)
def test_create_product_manager(self):
    """Test manager can create product"""
    self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + manager_token)
    response = self.client.post('/api/products/', {
        'name': 'Test Bun',
        'product_id': '#PROD-TEST',
        'selling_price': '80.00',
        'cost_price': '35.00',
        'current_stock': '50.00',
        'category_id': 1
    })
    assert response.status_code == 201
    assert response.data['profit_margin'] == 128.57  # Calculated

# Test 7: Create Product (Cashier - Should Fail)
def test_create_product_cashier_denied(self):
    """Test cashier cannot create product"""
    self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + cashier_token)
    response = self.client.post('/api/products/', {...})
    assert response.status_code == 403

# Test 8: Update Product
def test_update_product(self):
    """Test updating product"""
    response = self.client.patch('/api/products/1/', {
        'selling_price': '90.00'
    })
    assert response.status_code == 200
    assert response.data['selling_price'] == '90.00'

# Test 9: Delete Product
def test_delete_product(self):
    """Test deleting product"""
    response = self.client.delete('/api/products/1/')
    assert response.status_code == 204
```

#### Test Suite: Sales API
```python
# Test 10: Create Sale
def test_create_sale(self):
    """Test creating sale with items"""
    response = self.client.post('/api/sales/', {
        'items': [
            {
                'product_id': 1,
                'quantity': 2,
                'price': 80.00
            }
        ],
        'discount_percent': 0,
        'total_amount': 160.00,
        'payment_method': 'cash'
    })
    assert response.status_code == 201
    assert response.data['status'] == 'completed'

# Test 11: Inventory Updated After Sale
def test_inventory_decreases_after_sale(self):
    """Test stock decreases when sale created"""
    product = Product.objects.get(id=1)
    initial_stock = product.current_stock
    
    # Create sale
    self.client.post('/api/sales/', {...})
    
    # Verify stock decreased
    product.refresh_from_db()
    assert product.current_stock < initial_stock

# Test 12: Get Sales by Date Range
def test_get_sales_by_date(self):
    """Test filtering sales by date"""
    response = self.client.get(
        '/api/sales/?date_from=2026-03-20&date_to=2026-03-26'
    )
    assert response.status_code == 200
    assert all(s['created_at'] >= '2026-03-20' 
               for s in response.data['results'])
```

#### Test Suite: Users & Permissions
```python
# Test 13: Create User (Manager)
def test_create_user_manager(self):
    """Test manager can create user"""
    response = self.client.post('/api/users/', {
        'username': 'newcashier',
        'password': 'SecurePass123!',
        'full_name': 'New Cashier',
        'role': 'Cashier',
        'email': 'cashier@bakery.com'
    })
    assert response.status_code == 201

# Test 14: Role-Based Access - Baker
def test_baker_cant_access_user_management(self):
    """Test baker cannot access user management"""
    self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + baker_token)
    response = self.client.get('/api/users/')
    assert response.status_code == 403

# Test 15: List Users with Pagination
def test_users_pagination(self):
    """Test user list pagination"""
    response = self.client.get('/api/users/?page=1&page_size=10')
    assert response.status_code == 200
    assert response.data['count'] >= 0
    assert 'results' in response.data
```

#### Test Suite: Calculations (Profit, Totals)
```python
# Test 16: Profit Margin Calculation
def test_profit_margin_calculation(self):
    """Test profit margin calculated correctly"""
    product = Product.objects.create(
        name='Test Item',
        selling_price=100.00,
        cost_price=40.00
    )
    assert product.profit_margin == 150.0  # (100-40)/40 * 100

# Test 17: Sale Total Calculation
def test_sale_total_with_discount(self):
    """Test sale total calculated correctly with discount"""
    # Base: 200.00, Discount: 10% = 20.00, Total: 180.00
    sale = Sale.objects.create(
        subtotal=200.00,
        discount_percent=10,
        total_amount=180.00
    )
    assert sale.total_amount == 180.00

# Test 18: Decimal Precision
def test_decimal_precision_preserved(self):
    """Test decimals preserved through calculations"""
    response = self.client.post('/api/sales/', {
        'items': [{'product_id': 1, 'quantity': 2, 'price': 12.50}],
        'total_amount': 25.00
    })
    assert response.data['total_amount'] == 25.00  # Not 25 or 25.0
```

---

### 1.2 Frontend Unit Tests

**Files:** `Frontend/src/**/*.test.tsx`  
**Command:** `npm run test`  
**Framework:** Vitest + React Testing Library  
**Target Coverage:** 80%+

#### Test Suite: Components
```typescript
// Test 1: LoginScreen - Valid credentials
describe('LoginScreen', () => {
  test('should submit form with valid credentials', async () => {
    render(<LoginScreen />);
    
    fireEvent.change(screen.getByLabelText('Username'), {
      target: { value: 'john_manager' }
    });
    fireEvent.change(screen.getByLabelText('Password'), {
      target: { value: 'ValidPass123!' }
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
  });

  // Test 2: LoginScreen - Invalid credentials
  test('should show error for invalid credentials', async () => {
    render(<LoginScreen />);
    
    fireEvent.change(screen.getByLabelText('Username'), {
      target: { value: 'john_manager' }
    });
    fireEvent.change(screen.getByLabelText('Password'), {
      target: { value: 'WrongPassword' }
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });
});

// Test 3: CartPanel - Add item
describe('CartPanel', () => {
  test('should add product to cart', async () => {
    const mockProducts = [
      { id: 1, name: 'Bun', price: 80 }
    ];
    
    render(<CartPanel products={mockProducts} />);
    fireEvent.click(screen.getByText('Add to Cart'));
    
    expect(screen.getByText(/Bun/)).toBeInTheDocument();
  });

  // Test 4: CartPanel - Calculation
  test('should calculate total with 2 decimals', async () => {
    render(<CartPanel items={[
      { product: 'Item', price: 12.50, qty: 2 }
    ]} />);
    
    expect(screen.getByText('25.00')).toBeInTheDocument();
  });

  // Test 5: CartPanel - Discount
  test('should apply discount correctly', async () => {
    render(<CartPanel subtotal={100} discount={10} />);
    
    expect(screen.getByText('90.00')).toBeInTheDocument();  // 10% off
  });
});

// Test 6: ProductCard - Display
describe('ProductCard', () => {
  test('should display product info', () => {
    render(
      <ProductCard 
        product={{ 
          name: 'Fish Bun', 
          price: 80, 
          stock: 10 
        }} 
      />
    );
    
    expect(screen.getByText('Fish Bun')).toBeInTheDocument();
    expect(screen.getByText('₹80.00')).toBeInTheDocument();
  });

  // Test 7: ProductCard - Out of stock
  test('should disable buy button when out of stock', () => {
    render(<ProductCard product={{ stock: 0 }} />);
    
    const buyButton = screen.getByRole('button', { name: /buy/i });
    expect(buyButton).toBeDisabled();
  });
});

// Test 8: Dashboard - Load KPIs
describe('Dashboard', () => {
  test('should load and display KPIs', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/total sales/i)).toBeInTheDocument();
      expect(screen.getByText(/total users/i)).toBeInTheDocument();
    });
  });
});
```

#### Test Suite: API Integration
```typescript
// Test 9: API - Login flow
describe('API Integration', () => {
  test('should get and store tokens on login', async () => {
    const response = await apiClient.auth.login(
      'john_manager', 
      'ValidPass123!'
    );
    
    expect(response).toHaveProperty('access');
    expect(response).toHaveProperty('refresh');
    expect(localStorage.getItem('access_token')).toBeTruthy();
  });

  // Test 10: API - Auto-refresh on 401
  test('should auto-refresh token on 401', async () => {
    // Mock 401 response
    const initialToken = getAccessToken();
    
    // API request returns 401
    // Should trigger refresh automatically
    
    // Verify new token is different
    const newToken = getAccessToken();
    expect(newToken).not.toBe(initialToken);
  });

  // Test 11: API - Error messages
  test('should show user-friendly error messages', async () => {
    try {
      await apiClient.products.create({});  // Invalid data
    } catch (error) {
      expect(error.message).toMatch(/invalid|required|validation/i);
    }
  });
});

// Test 12: useApi hook
describe('useApi Hook', () => {
  test('should fetch data and handle loading state', async () => {
    const { result } = renderHook(() => 
      useApi(() => apiClient.products.getAll())
    );
    
    expect(result.current.loading).toBe(true);
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBeDefined();
    });
  });

  // Test 13: useMutation hook
  test('should handle mutation and error state', async () => {
    const { result } = renderHook(() => 
      useMutation(apiClient.products.create)
    );
    
    fireEvent.click(createButton);
    
    await waitFor(() => {
      expect(result.current.error).toBeDefined();
    });
  });
});
```

---

### 1.3 Integration Tests

**Command:** `npm run test:integration`

```typescript
// Test Integration 1: Complete User Creation Flow
describe('Integration: User Management', () => {
  test('Should create user and verify in list', async () => {
    // 1. Get initial user count
    const initialUsers = await apiClient.users.getAll();
    
    // 2. Create new user
    const newUser = await apiClient.users.create({
      username: 'testuser123',
      password: 'SecurePass123!',
      full_name: 'Test User',
      role: 'Cashier'
    });
    
    // 3. Verify user appears in list
    const updatedUsers = await apiClient.users.getAll();
    expect(updatedUsers.results.length).toBe(initialUsers.results.length + 1);
    
    // 4. Verify user has correct role
    const foundUser = updatedUsers.results.find(u => u.id === newUser.id);
    expect(foundUser.role).toBe('Cashier');
  });
});

// Test Integration 2: Complete Sale Flow
describe('Integration: Sales Creation', () => {
  test('Should create sale and verify inventory decreased', async () => {
    // 1. Get product initial stock
    const product = await apiClient.products.getById(1);
    const initialStock = parseFloat(product.current_stock);
    
    // 2. Create sale with this product
    const sale = await apiClient.sales.create({
      items: [{ product_id: 1, quantity: 2 }],
      total_amount: 160.00
    });
    
    // 3. Verify sale created
    expect(sale.id).toBeDefined();
    
    // 4. Verify inventory decreased
    const updatedProduct = await apiClient.products.getById(1);
    const updatedStock = parseFloat(updatedProduct.current_stock);
    expect(updatedStock).toBe(initialStock - 2);
  });
});

// Test Integration 3: Authentication & Protected Routes
describe('Integration: Auth Flow', () => {
  test('Should login, maintain session, and access protected routes', async () => {
    // 1. Login
    const auth = await apiClient.auth.login('john_manager', 'ValidPass123!');
    expect(auth.access).toBeDefined();
    
    // 2. Access protected route
    const dashboard = await apiClient.dashboard.getMetrics();
    expect(dashboard).toBeDefined();
    
    // 3. Logout and verify access denied
    await apiClient.auth.logout();
    try {
      await apiClient.dashboard.getMetrics();
      fail('Should not allow access after logout');
    } catch (error) {
      expect(error.status).toBe(401);
    }
  });
});

// Test Integration 4: Multi-step Workflow (Storekeeper)
describe('Integration: Storekeeper Workflow', () => {
  test('Should complete full storekeeper workflow', async () => {
    // 1. Login as storekeeper
    await apiClient.auth.login('storekeeper_user', 'ValidPass123!');
    
    // 2. Get inventory list
    const inventory = await apiClient.inventory.getAll();
    expect(inventory.results.length > 0).toBe(true);
    
    // 3. Update stock for item
    const updated = await apiClient.inventory.updateStock(1, { qty: 50 });
    expect(updated.current_stock).toBe('50.00');
    
    // 4. Log wastage
    const wastage = await apiClient.wastage.create({
      product_id: 1,
      quantity: 2,
      reason: 'Expired'
    });
    expect(wastage.id).toBeDefined();
    
    // 5. Verify inventory decreased
    const finalInventory = await apiClient.inventory.getById(1);
    expect(parseFloat(finalInventory.current_stock)).toBe(48);
  });
});
```

---

## 👤 PART 2: MANUAL E2E TESTING

### 2.1 Test Environment Setup

**Before Starting Any Tests:**

1. **Ensure Backend is Running**
   ```bash
   cd Backend
   python manage.py runserver
   # Should see: "Starting development server at http://localhost:8000/"
   ```

2. **Ensure Frontend is Running**
   ```bash
   cd Frontend
   npm run dev
   # Should see: "Local: http://localhost:5173/"
   ```

3. **Test Database State**
   ```bash
   # Ensure fresh data
   python manage.py flush --no-input
   python manage.py migrate
   python manage.py create_test_data  # If script exists
   ```

4. **Test Users for Manual Testing**
   ```
   Manager:     username: john_manager    password: ValidPass123!
   Cashier:     username: jane_cashier    password: ValidPass123!
   Baker:       username: bob_baker       password: ValidPass123!
   Storekeeper: username: alice_store    password: ValidPass123!
   ```

5. **Browser Tools**
   - Open DevTools (F12)
   - Go to **Console** tab
   - Look for `[API]` prefixed messages for debugging
   - Go to **Network** tab to verify API calls

---

### 2.2 Scenario 1: Manager Daily Workflow

**Duration:** 15-20 minutes  
**Role:** Manager (john_manager)  
**Goal:** Verify manager can access full dashboard and manage users

#### Steps:
const handleAddCategory = async (data) => {
  await api.post('/categories/', data);
};
```
✅ Step 1: Login
  1. Go to http://localhost:5173
  2. Enter username: john_manager
  3. Enter password: ValidPass123!
  4. Click "Login"
  
  EXPECTED:
  ✓ Redirected to /dashboard
  ✓ Dashboard loads with KPI cards
  ✓ Header shows "john_manager"
  ✓ Console: [API] POST /api/auth/login/ 200


✅ Step 2: View Dashboard
  1. Verify you see KPI cards:
     - Total Sales
     - Total Revenue
     - Products Count
     - Users Count
  2. Check each KPI shows correct data
  
  EXPECTED:
  ✓ All 4 KPIs visible and showing numbers
  ✓ Sidebar shows navigation options
  ✓ No error messages


✅ Step 3: Check Low Stock Alerts
  1. Look for "Low Stock Alerts" section
  2. Verify products with stock < threshold are highlighted
  3. Click on an alert item
  
  EXPECTED:
  ✓ Alert section shows 1+ items (if any exist)
  ✓ Red/orange highlight on low stock items
  ✓ Clicking opens product details


✅ Step 4: View Sales Summary
  1. Click "Sales Summary" in sidebar/navigation
  2. Scroll down to view recent sales
  3. Click on a sale bill number (e.g., BILL-1001)
  
  EXPECTED:
  ✓ Sales list loads with bill numbers like BILL-XXXX
  ✓ Each row shows: Date, Bill#, Amount, Status
  ✓ Clicking opens invoice details
  ✓ All bills formatted as BILL-XXXX (not #ORD-XXXX)


✅ Step 5: User Management - View All
  1. Click "User Management" in sidebar
  2. Verify all users are listed
  3. Check columns: Name, Role, Email, Status, Actions
  
  EXPECTED:
  ✓ User list shows all staff members
  ✓ Roles displayed correctly (Manager/Cashier/Baker/Storekeeper)
  ✓ Status shows "Active" or "Inactive"
  ✓ Action buttons (Edit, Delete, Deactivate) visible


✅ Step 6: User Management - Create New
  1. Click "Add New User" or "+" button
  2. Fill form:
     - Full Name: John Test Cashier
     - Email: john_test@bakery.com
     - Role: Cashier
     - Status: Active
  3. Click "Create User"
  
  EXPECTED:
  ✓ Modal/form appears
  ✓ Form validation works (required fields)
  ✓ User created successfully
  ✓ New user appears in list with role "Cashier"
  ✓ Success message shown


✅ Step 7: User Management - Edit User
  1. Find the user you just created
  2. Click "Edit" button
  3. Change Full Name to: John Updated Test
  4. Click "Save"
  
  EXPECTED:
  ✓ Edit form loads with current user data
  ✓ Changes saved successfully
  ✓ User list reflects changes immediately
  ✓ Success message shown


✅ Step 8: Navigation
  1. Click through all main nav items:
     - Dashboard
     - Sales
     - Products
     - Stock
     - Users (already done)
     - Wastage (if available)
  2. Verify each loads without errors
  
  EXPECTED:
  ✓ All pages load (5-10 items)
  ✓ No 404 or error pages
  ✓ Navigation doesn't require re-login


✅ Step 9: Logout
  1. Click username in top-right corner
  2. Click "Logout"
  
  EXPECTED:
  ✓ Redirects to login page
  ✓ Previous data cleared from localStorage
  ✓ Cannot access /dashboard without login
  ✓ Trying /dashboard redirects to login


TEST RESULT: ☐ PASS  ☐ FAIL
NOTES: _____________________________________
```

---

### 2.3 Scenario 2: Cashier POS Workflow

**Duration:** 20-25 minutes  
**Role:** Cashier (jane_cashier)  
**Goal:** Complete full sale transaction

#### Steps:

```
✅ Step 1: Login as Cashier
  1. Clear cookies/logout first
  2. Go to http://localhost:5173
  3. Login as jane_cashier / ValidPass123!
  
  EXPECTED:
  ✓ Redirected to dashboard
  ✓ Header shows "jane_cashier"
  ✓ See Billing or POS screen option


✅ Step 2: Access Billing Screen
  1. Click "Billing" or "POS" in sidebar
  2. Wait for products to load
  
  EXPECTED:
  ✓ Billing screen loads with product grid
  ✓ Shows products: Fish Bun, Cake, Bread, Pastries, etc.
  ✓ Each product shows: Name, Price (₹80.00 format), Stock
  ✓ Cart panel visible on right (empty initially)


✅ Step 3: Add Product to Cart
  1. Click "Fish Bun" product card
  2. Enter quantity: 2
  3. Verify it added to cart
  
  EXPECTED:
  ✓ "Add to Cart" button works
  ✓ Product appears in cart with qty 2
  ✓ Unit price shown correctly (₹80.00)
  ✓ Console: [API] GET /api/products/ 200


✅ Step 4: Add Multiple Products
  1. Add "Chocolate Cake" qty 1
  2. Add "Bread Loaf" qty 3
  3. View cart summary
  
  EXPECTED:
  ✓ All 3 products in cart
  ✓ Each shows correct qty
  ✓ Each shows correct unit price
  ✓ Line totals calculated (qty × price)


✅ Step 5: Verify Cart Calculations
  1. Look at cart panel
  2. Verify calculations show:
     - Line items: qty × unit_price
     - Subtotal: sum of line items
     - Total: subtotal (or subtotal - discount)
  3. Check all decimals are shown (.00 format)
  
  EXPECTED:
  ✓ Example: 2 × ₹80.00 = ₹160.00 (not ₹160)
  ✓ Subtotal shows full precision: ₹XXX.00
  ✓ No rounding errors (12.50 stays 12.50, not 12.5 or 13)


✅ Step 6: Apply Discount
  1. Look for discount field in cart
  2. Enter discount: 10%
  3. Verify new total calculated
  
  EXPECTED:
  ✓ Discount field accepts percentage
  ✓ Discount amount shown: Subtotal × 10%
  ✓ New total = Subtotal - Discount amount
  ✓ All values with 2 decimals
  ✓ Example: Subtotal ₹500.00, 10% = ₹50.00 off, Total = ₹450.00


✅ Step 7: Remove Item from Cart
  1. Find the "Bread Loaf" item in cart
  2. Click "Remove" or trash icon
  3. Verify item removed and total updated
  
  EXPECTED:
  ✓ Item removed from cart
  ✓ Cart recalculates
  ✓ Subtotal and total updated
  ✓ Discount recalculated if applied


✅ Step 8: Complete Sale
  1. Verify cart has at least 2-3 items
  2. Look for "Complete Sale" or "Checkout" button
  3. Choose payment method: Cash / Card / Online
  4. Click "Complete Sale"
  
  EXPECTED:
  ✓ Sale creation takes 2-5 seconds
  ✓ Success message shown: "Sale completed successfully"
  ✓ Bill number displayed (format: BILL-XXXX)
  ✓ Receipt/invoice shown
  ✓ Cart cleared
  ✓ Console: [API] POST /api/sales/ 201


✅ Step 9: Print/Download Bill
  1. Look for "Print" or "Download" option on receipt
  2. Click to print/download
  
  EXPECTED:
  ✓ Print dialog opens (Ctrl+P)
  ✓ Bill layout is readable
  ✓ Shows: Items, Qty, Price, Total, Payment method
  ✓ Bill number: BILL-XXXX format


✅ Step 10: Verify Sale in Manager View
  1. Logout (jane_cashier)
  2. Login as john_manager
  3. Go to "Sales Summary"
  4. Look for the bill you just created
  
  EXPECTED:
  ✓ New bill appears in manager's sales summary
  ✓ Status shows "Completed"
  ✓ Amount matches what you paid
  ✓ Timestamp is correct (current date/time)


TEST RESULT: ☐ PASS  ☐ FAIL
NOTES: _____________________________________
```

---

### 2.4 Scenario 3: Stock Management Workflow

**Duration:** 15-20 minutes  
**Role:** Storekeeper (alice_store)  
**Goal:** Manage inventory and log wastage

#### Steps:

```
✅ Step 1: Login as Storekeeper
  1. Logout and login as alice_store / ValidPass123!
  
  EXPECTED:
  ✓ Login successful
  ✓ Storekeeper dashboard loads


✅ Step 2: View Stock Management
  1. Click "Stock Management" in sidebar
  2. Wait for inventory to load
  
  EXPECTED:
  ✓ Stock screen shows all products
  ✓ Columns: Product Name, Current Stock, Reorder Level, Status
  ✓ Products with low stock highlighted (red/orange)
  ✓ Console: [API] GET /api/products/ 200


✅ Step 3: View Product Details
  1. Click on a product with stock > 0
  2. View stock history
  
  EXPECTED:
  ✓ Product details modal/page opens
  ✓ Shows: Current Stock, Cost, Selling Price, Profit
  ✓ Stock history shows past transactions
  ✓ History includes: Date, Type (Sale/Wastage/Addition), Qty


✅ Step 4: Add New Batch
  1. Click "Add New Batch" or "Add Stock"
  2. Fill form:
     - Product: Fish Bun
     - Quantity: 100
     - Batch Number: BATCH-20260326-001
     - Expiry Date: 2026-04-26
  3. Click "Add Batch"
  
  EXPECTED:
  ✓ Form validation works
  ✓ Batch created successfully
  ✓ Success message shown
  ✓ Stock increased
  ✓ Console: [API] POST /api/batches/ 201


✅ Step 5: Log Wastage
  1. Click "Log Wastage" or "Wastage" section
  2. Fill form:
     - Product: Fish Bun
     - Quantity: 5
     - Reason: Expired / Damaged
     - Date: Today
  3. Click "Log Wastage"
  
  EXPECTED:
  ✓ Wastage form opens
  ✓ Created successfully
  ✓ Success message shown
  ✓ Stock decreased by 5
  ✓ Console: [API] POST /api/wastage/ 201


✅ Step 6: Verify Inventory Updated
  1. Go back to Stock Management
  2. Search for "Fish Bun"
  3. Verify stock = (previous + 100 - 5) = new value
  
  EXPECTED:
  ✓ Stock reflects batch addition
  ✓ Stock reflects wastage deduction
  ✓ Math is correct


✅ Step 7: Filter Low Stock Items
  1. Look for filter or "Low Stock" option
  2. Show only items below reorder level
  
  EXPECTED:
  ✓ Filter works
  ✓ Shows 1-3 items with low stock
  ✓ Each marked with warning/alert badge


✅ Step 8: View Reports
  1. Look for "Reports" or "Analytics" option in storekeeper menu
  2. Check stock report
  
  EXPECTED:
  ✓ Report shows stock levels
  ✓ Shows which items need reordering
  ✓ Can filter by date/product


TEST RESULT: ☐ PASS  ☐ FAIL
NOTES: _____________________________________
```

---

### 2.5 Scenario 4: Baker Production Dashboard

**Duration:** 10-15 minutes  
**Role:** Baker (bob_baker)  
**Goal:** View production workload and mark items as baked

#### Steps:

```
✅ Step 1: Login as Baker
  1. Logout and login as bob_baker / ValidPass123!
  
  EXPECTED:
  ✓ Login successful
  ✓ Baker dashboard loads


✅ Step 2: View Production Dashboard
  1. Click "Baker Dashboard" or main dashboard
  2. View today's production items
  
  EXPECTED:
  ✓ Shows items to bake today
  ✓ Columns: Item Name, Quantity Needed, Status, Actions
  ✓ Items show what needs to be baked
  ✓ Quantities are clear


✅ Step 3: View Notifications
  1. Look for notifications area
  2. Check for alerts: "Stock Running Low", "Order Received", etc.
  
  EXPECTED:
  ✓ Notifications section shows 1+ alerts
  ✓ Alerts are relevant to baker role
  ✓ Can dismiss notifications


✅ Step 4: Mark Item as Baked
  1. Find an item in production list
  2. Click "Mark as Completed" or "Done Baking"
  3. Verify status changes
  
  EXPECTED:
  ✓ Status changes from "Pending" to "Completed"
  ✓ Item struck through or grayed out
  ✓ Success message shown
  ✓ Console: [API] PATCH /api/production/XX/ 200


✅ Step 5: View Analytics
  1. Look for "Analytics" or "Reports" for baker
  2. Check production metrics
  
  EXPECTED:
  ✓ Shows items baked today
  ✓ Shows efficiency/time tracking
  ✓ Historical data available


✅ Step 6: Permission Check
  1. Try to access "Users" or "Sales" sections
  2. Should be denied
  
  EXPECTED:
  ✓ 403 Forbidden message shown
  ✓ Cannot access manager/cashier features
  ✓ Redirected back to baker dashboard


TEST RESULT: ☐ PASS  ☐ FAIL
NOTES: _____________________________________
```

---

### 2.6 Scenario 5: Error Handling & Edge Cases

**Duration:** 20-25 minutes  
**Goal:** Verify system handles errors gracefully

#### Steps:

```
✅ Step 1: Network Error Simulation
  1. Open DevTools (F12) → Network tab
  2. Throttle to "Offline"
  3. Try to perform action (add product to cart, create sale)
  4. Check error message
  
  EXPECTED:
  ✓ User-friendly error shown: "Network error. Please check connection"
  ✓ No blank screens or crashes
  ✓ User can retry
  ✓ Console shows [API] error message


✅ Step 2: Invalid Input - Form Validation
  1. Login as manager
  2. Go to "Create User"
  3. Leave "Full Name" empty
  4. Click "Create"
  
  EXPECTED:
  ✓ Validation error shown below field
  ✓ Form not submitted
  ✓ Error message: "Full Name is required"
  ✓ Submit button remains disabled until fixed


✅ Step 3: Decimal Edge Case
  1. Go to Billing screen
  2. Add product with fractional price (e.g., ₹12.50)
  3. Quantity: 3
  4. Expected total: ₹37.50
  5. Check cart shows correct amount
  
  EXPECTED:
  ✓ Cart shows ₹37.50 (not ₹37.5 or ₹38)
  ✓ Multiple decimals preserved
  ✓ No rounding errors


✅ Step 4: Concurrent Operations (Race Condition)
  1. Quick click "Add to Cart" twice rapidly
  2. Verify quantity increases correctly (not duplicated)
  
  EXPECTED:
  ✓ 2 clicks = +2 quantity
  ✓ Cart doesn't show duplicate items
  ✓ Success state consistent


✅ Step 5: Session Expiration
  1. Login as any user
  2. Wait 5+ minutes without activity
  3. Try to perform action (view sales, add to cart)
  4. System should detect expired token
  
  EXPECTED:
  ✓ Auto-refresh triggered silently
  ✓ Action completes normally
  ✓ No re-login required yet
  ✓ OR: Friendly "Session expired. Please login" message


✅ Step 6: Permission Denied
  1. Login as Cashier
  2. Try to URL-navigate to /users (user management)
  3. Should get 403 error
  
  EXPECTED:
  ✓ 403 page shown or redirect to dashboard
  ✓ Message: "You don't have permission"
  ✓ Redirected to allowed page


✅ Step 7: Invalid Search/Filter
  1. Go to Products
  2. Search for non-existent item: "ZZZZZZ"
  3. Should show "No results"
  
  EXPECTED:
  ✓ Empty state shown gracefully
  ✓ Message: "No products found"
  ✓ Can clear search and see all items


✅ Step 8: Large Data Sets (Pagination)
  1. View Product list with 50+ items
  2. Use pagination controls (Next/Previous)
  3. Navigate to different pages
  
  EXPECTED:
  ✓ Page 1 shows items 1-10
  ✓ Page 2 shows items 11-20
  ✓ No loading freeze
  ✓ Pagination info shows accuracy


✅ Step 9: Multiple Errors in Form
  1. Create User form
  2. Leave empty: Full Name, Email, Role
  3. Click Submit
  
  EXPECTED:
  ✓ All 3 errors shown
  ✓ Fields highlighted in red
  ✓ Cannot submit


✅ Step 10: Duplicate Prevention
  1. Create user with username: "test_user_unique"
  2. Try to create another with same username
  
  EXPECTED:
  ✓ Error shown: "Username already exists"
  ✓ Form not submitted
  ✓ Can enter different username and retry


TEST RESULT: ☐ PASS  ☐ FAIL
NOTES: _____________________________________
```

---

### 2.7 Scenario 6: Mobile Responsive Testing

**Duration:** 15-20 minutes  
**Goal:** Verify system works on mobile devices

#### Steps (Using Chrome DevTools):

```
✅ Step 1: Responsive Design - Login
  1. Open DevTools (F12)
  2. Click "Toggle device toolbar" (Ctrl+Shift+M)
  3. Select "iPhone 12" or similar
  4. Go to login page
  
  EXPECTED:
  ✓ Login form is readable on mobile
  ✓ Input fields are touch-friendly (large enough)
  ✓ No horizontal scrolling needed
  ✓ Button is clickable
  ✓ Responsive layout (single column)


✅ Step 2: Mobile - Billing Screen
  1. Login on mobile view
  2. Navigate to Billing/POS
  3. Try to add product to cart
  
  EXPECTED:
  ✓ Product grid shows in single/double column (not all 10 across)
  ✓ Touch targets are large enough
  ✓ Cart panel is accessible (slide-out menu or below)
  ✓ Can complete transaction


✅ Step 3: Mobile - Forms
  1. Go to "Create User" form on mobile
  2. Fill form fields
  3. Submit
  
  EXPECTED:
  ✓ Form is single column
  ✓ Labels are above inputs
  ✓ Mobile keyboard appears for text input
  ✓ Button at bottom is tappable


✅ Step 4: Mobile - Navigation
  1. Look for hamburger menu (☰)
  2. Click to open sidebar
  3. Navigate to different sections
  
  EXPECTED:
  ✓ Menu hidden by default on mobile
  ✓ Hamburger opens/closes menu
  ✓ Menu options are full-width and tappable
  ✓ Clicking item navigates and closes menu


✅ Step 5: Mobile - Tables
  1. Go to product list or sales list
  2. Scroll in table area
  
  EXPECTED:
  ✓ Table is scrollable horizontally
  ✓ OR: Table adapts to cards/list view
  ✓ All essential data visible
  ✓ No content cut off


✅ Step 6: Different Device Sizes
  1. Test: iPhone (375px), iPad (768px), Desktop (1024px)
  2. Verify each responds appropriately
  
  EXPECTED:
  ✓ Mobile optimized for < 576px
  ✓ Tablet optimized for 576px-1024px
  ✓ Desktop uses full width > 1024px
  ✓ All functional at each breakpoint


TEST RESULT: ☐ PASS  ☐ FAIL
NOTES: _____________________________________
```

---

## 📊 PART 3: TEST RESULTS SUMMARY

### Test Execution Tracker

| Scenario | Duration | Tester | Status | Issues Found | Notes |
|----------|----------|--------|--------|--------------|-------|
| Scenario 1: Manager Workflow | 20 min | _____ | ☐ Pass ☐ Fail | _____ | _____ |
| Scenario 2: Cashier POS | 25 min | _____ | ☐ Pass ☐ Fail | _____ | _____ |
| Scenario 3: Stock Management | 20 min | _____ | ☐ Pass ☐ Fail | _____ | _____ |
| Scenario 4: Baker Dashboard | 15 min | _____ | ☐ Pass ☐ Fail | _____ | _____ |
| Scenario 5: Error Handling | 25 min | _____ | ☐ Pass ☐ Fail | _____ | _____ |
| Scenario 6: Mobile Testing | 20 min | _____ | ☐ Pass ☐ Fail | _____ | _____ |

**Total Testing Time:** 125 minutes (~2 hours)

---

### Issues Found During Testing

| ID | Priority | Component | Issue | Root Cause | Fix Status |
|----|----------|-----------|-------|-----------|-----------|
| TEST-001 | 🔴 Critical | | | | ☐ Not Started ☐ In Progress ☐ Fixed ☐ Verified |
| TEST-002 | 🟠 High | | | | ☐ Not Started ☐ In Progress ☐ Fixed ☐ Verified |
| TEST-003 | 🟡 Medium | | | | ☐ Not Started ☐ In Progress ☐ Fixed ☐ Verified |
| TEST-004 | 🟡 Medium | | | | ☐ Not Started ☐ In Progress ☐ Fixed ☐ Verified |
| TEST-005 | 🟢 Low | | | | ☐ Not Started ☐ In Progress ☐ Fixed ☐ Verified |

---

### Test Execution Checklist

```
BEFORE TESTING:
☐ Backend running (python manage.py runserver)
☐ Frontend running (npm run dev)
☐ Test database seeded with data
☐ No existing open bugs in JIRA/Issues
☐ Latest code deployed to test environment

AUTOMATED TESTS:
☐ Backend unit tests passing (python manage.py test)
  Target: All tests pass
  Coverage: 80%+
  
☐ Frontend unit tests passing (npm run test)
  Target: All tests pass
  Coverage: 80%+
  
☐ Integration tests passing
  Target: All scenarios pass
  Duration: < 2 minutes total

MANUAL E2E TESTS:
☐ Scenario 1: Manager Workflow (PASSED/FAILED)
☐ Scenario 2: Cashier POS (PASSED/FAILED)
☐ Scenario 3: Stock Management (PASSED/FAILED)
☐ Scenario 4: Baker Dashboard (PASSED/FAILED)
☐ Scenario 5: Error Handling (PASSED/FAILED)
☐ Scenario 6: Mobile Responsive (PASSED/FAILED)

PERFORMANCE TESTS:
☐ API response time < 500ms
☐ Page load time < 2 seconds
☐ No UI freezes or hangs

QUALITY GATES:
☐ Zero critical bugs
☐ All high priority bugs fixed
☐ 90%+ scenarios pass rate
☐ All error messages user-friendly
☐ Mobile testing passed
☐ Accessibility passed (buttons clickable, text readable)

SIGN-OFF:
☐ QA Lead approval: _________________ Date: _______
☐ Dev Lead approval: _________________ Date: _______
☐ Product Manager approval: _________________ Date: _______

READY FOR:
☐ Staging Deployment (Phase 2)
☐ Production Deployment (Phase 4)
```

---

### Test Results Submission

**Overall Status:** ☐ READY TO PROCEED  ☐ NEEDS FIXES

**Summary:**
- Total Scenarios: 6
- Passed: _____ / 6
- Failed: _____ / 6
- Critical Issues: _____
- High Issues: _____
- Medium Issues: _____
- Low Issues: _____

**Tester Name:** _________________  
**Date Completed:** _________________  
**Sign-Off:** _________________

---

## 🚀 Next Steps

**If All Tests Pass ✅:**
1. Proceed to Phase 2: Staging Deployment
2. Staff training
3. Production deployment

**If Issues Found ❌:**
1. Prioritize by severity
2. Assign to dev team
3. Create JIRA tickets
4. Fix and re-test
5. Once all pass → proceed to Phase 2

---

**Testing Documentation Generated:** March 26, 2026  
**Last Updated:** March 26, 2026  
**Status:** Ready for Execution
