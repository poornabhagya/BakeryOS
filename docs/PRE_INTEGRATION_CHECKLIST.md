# ✅ PRE-INTEGRATION CHECKLIST & IMPLEMENTATION GUIDE

**What needs to be done before connecting frontend and backend**

**Estimated Total Time:** 10-16 hours  
**Difficulty:** Moderate  
**Progress Tracking:** Mark items as you complete them

---

## 🟢 PHASE 1: BACKEND FIXES (30 minutes)

### Backend Fix #1: Add avatar_color to UserListSerializer ✅

**File:** `Backend/api/serializers.py`

**Current Code (Lines ~45-55):**
```python
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'employee_id',
            'role', 'status', 'contact', 'created_at', 'updated_at'
        ]
```

**Required Change:**
```python
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'employee_id',
            'role', 'status', 'contact', 'avatar_color',  # ← ADD THIS
            'created_at', 'updated_at'
        ]
```

**Steps:**
1. [ ] Open Backend/api/serializers.py
2. [ ] Find UserListSerializer class
3. [ ] Add 'avatar_color' to fields list
4. [ ] Save file
5. [ ] Verify: Run `cd Backend && python manage.py check`
6. [ ] Expected: "System check identified 0 issues"

**Time:** 5 minutes  
**Difficulty:** 🟢 Trivial

---

### Backend Fix #2: Align JWT Authentication Settings ✅

**File:** `Backend/core/settings.py`

**Decision:** Which authentication method to use?

**Option A: JWT Authentication (Recommended) ⭐**
```python
# USE THIS - More secure, industry standard, better for mobile apps

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # ← Change this
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
```

**Option B: Token Authentication**
```python
# Alternative - Simpler but less secure

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
```

**Steps (Choose ONE - Recommend Option A):**

**If choosing Option A (JWT):**
1. [ ] Open Backend/core/settings.py
2. [ ] Find REST_FRAMEWORK configuration
3. [ ] Change to `'rest_framework_simplejwt.authentication.JWTAuthentication'`
4. [ ] Verify `djangorestframework-simplejwt` in requirements.txt (✅ already there: 5.2.2)
5. [ ] Save file
6. [ ] Run: `cd Backend && python manage.py check`
7. [ ] Expected: "System check identified 0 issues"

**If choosing Option B (Token):**
1. [ ] You'll need to modify auth views to use Token instead of JWT
2. [ ] More complex changes needed
3. **Recommendation: Don't choose this, use JWT instead**

**Time:** 10-15 minutes  
**Difficulty:** 🟢 Easy
**Recommendation:** Choose JWT (Option A) - better for modern applications

---

## ✅ PHASE 1 VERIFICATION

**Checkpoint: Backend Ready?**

Run this command:
```bash
cd Backend
python manage.py check
```

**You should see:**
```
System check identified no issues (0 silenced).
```

If you see errors, fix them before proceeding.

---

## 🟡 PHASE 2: CREATE FRONTEND API SERVICE LAYER (2-3 hours)

This is the most critical piece. The API service layer will:
- Handle all HTTP communication with backend
- Manage JWT tokens
- Add authorization headers
- Handle errors and token refresh
- Convert API responses to frontend types

###  Create New File: Frontend/src/services/api.ts

**Create:** `Frontend/src/services/api.ts` (NEW FILE - ~300 lines)

```typescript
import { ApiProduct, ApiSale, ApiUser } from '../utils/apiTypes';
import {
  convertApiProductToUi,
  convertApiUserToUi,
  convertApiSaleToUi,
} from '../utils/conversions';

// ============================================================
// API Configuration
// ============================================================

const API_BASE = process.env.VITE_API_BASE || 'http://localhost:8000/api';

// ============================================================
// Token Management
// ============================================================

let accessToken: string | null = localStorage.getItem('access_token');
let refreshToken: string | null = localStorage.getItem('refresh_token');

export function setTokens(access: string, refresh: string) {
  accessToken = access;
  refreshToken = refresh;
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
}

export function clearTokens() {
  accessToken = null;
  refreshToken = null;
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

// ============================================================
// Request Headers
// ============================================================

function getAuthHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    ...(accessToken && { Authorization: `Bearer ${accessToken}` }),
  };
}

// ============================================================
// Error Handling
// ============================================================

export class ApiError extends Error {
  constructor(
    public status: number,
    public details?: any,
    message?: string
  ) {
    super(message || `API Error: ${status}`);
    this.name = 'ApiError';
  }
}

// ============================================================
// Token Refresh
// ============================================================

async function refreshAccessToken(): Promise<string> {
  if (!refreshToken) {
    throw new ApiError(401, {}, 'No refresh token available');
  }

  const response = await fetch(`${API_BASE}/auth/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: refreshToken }),
  });

  if (!response.ok) {
    clearTokens();
    throw new ApiError(response.status, {}, 'Token refresh failed');
  }

  const data = await response.json();
  accessToken = data.access;
  localStorage.setItem('access_token', accessToken);
  
  return accessToken;
}

// ============================================================
// Core Request Function
// ============================================================

async function makeRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  
  let response = await fetch(url, {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...options.headers,
    },
  });

  // Handle 401 - Try refreshing token and retry once
  if (response.status === 401 && refreshToken) {
    try {
      await refreshAccessToken();
      
      response = await fetch(url, {
        ...options,
        headers: {
          ...getAuthHeaders(),
          ...options.headers,
        },
      });
    } catch (error) {
      clearTokens();
      window.location.href = '/login';
      throw error;
    }
  }

  // Handle other error statuses
  if (!response.ok) {
    let errorDetails = {};
    try {
      errorDetails = await response.json();
    } catch {}

    if (response.status === 401 || response.status === 403) {
      clearTokens();
      window.location.href = '/login';
    }

    throw new ApiError(response.status, errorDetails);
  }

  return response.json() as Promise<T>;
}

// ============================================================
// API Endpoints - Authentication
// ============================================================

export const authApi = {
  login: async (username: string, password: string) => {
    const response = await makeRequest<{
      access: string;
      refresh: string;
      user: ApiUser;
    }>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });

    setTokens(response.access, response.refresh);
    return {
      token: response.access,
      user: convertApiUserToUi(response.user),
    };
  },

  logout: () => {
    clearTokens();
  },

  refreshToken: refreshAccessToken,
};

// ============================================================
// Paginated Response Type
// ============================================================

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ============================================================
// API Endpoints - Products
// ============================================================

export const productApi = {
  getAll: async (page: number = 1, search?: string) => {
    let endpoint = `/products/?page=${page}`;
    if (search) endpoint += `&search=${encodeURIComponent(search)}`;

    const response = await makeRequest<PaginatedResponse<ApiProduct>>(
      endpoint
    );

    return {
      items: response.results.map(convertApiProductToUi),
      total: response.count,
      nextPage: response.next,
      previousPage: response.previous,
    };
  },

  getById: async (id: number) => {
    const response = await makeRequest<ApiProduct>(`/products/${id}/`);
    return convertApiProductToUi(response);
  },

  create: async (data: Partial<ApiProduct>) => {
    // Convert UI types back to API format if needed
    const apiData = {
      ...data,
      selling_price: String(data.selling_price),
      cost_price: String(data.cost_price),
      current_stock: String(data.current_stock),
    };

    const response = await makeRequest<ApiProduct>('/products/', {
      method: 'POST',
      body: JSON.stringify(apiData),
    });

    return convertApiProductToUi(response);
  },

  update: async (id: number, data: Partial<ApiProduct>) => {
    // Convert UI types back to API format
    const apiData = {
      ...data,
      ...(data.selling_price && { selling_price: String(data.selling_price) }),
      ...(data.cost_price && { cost_price: String(data.cost_price) }),
      ...(data.current_stock && { current_stock: String(data.current_stock) }),
    };

    const response = await makeRequest<ApiProduct>(`/products/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(apiData),
    });

    return convertApiProductToUi(response);
  },

  delete: async (id: number) => {
    await makeRequest(`/products/${id}/`, { method: 'DELETE' });
  },
};

// ============================================================
// API Endpoints - Sales (Orders/Billing)
// ============================================================

export const saleApi = {
  getAll: async (page: number = 1, dateFrom?: string, dateTo?: string) => {
    let endpoint = `/sales/?page=${page}`;
    if (dateFrom) endpoint += `&date_from=${dateFrom}`;
    if (dateTo) endpoint += `&date_to=${dateTo}`;

    const response = await makeRequest<PaginatedResponse<ApiSale>>(endpoint);

    return {
      items: response.results.map(convertApiSaleToUi),
      total: response.count,
      nextPage: response.next,
      previousPage: response.previous,
    };
  },

  getById: async (id: number) => {
    const response = await makeRequest<ApiSale>(`/sales/${id}/`);
    return convertApiSaleToUi(response);
  },

  create: async (data: {
    items: Array<{ product_id: number; quantity: string }>;
    payment_method: string;
    discount_id?: number;
  }) => {
    const response = await makeRequest<ApiSale>('/sales/', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    return convertApiSaleToUi(response);
  },

  delete: async (id: number) => {
    await makeRequest(`/sales/${id}/`, { method: 'DELETE' });
  },
};

// ============================================================
// API Endpoints - Users (Staff)
// ============================================================

export const userApi = {
  getAll: async (page: number = 1) => {
    const response = await makeRequest<PaginatedResponse<ApiUser>>(
      `/users/?page=${page}`
    );

    return {
      items: response.results.map(convertApiUserToUi),
      total: response.count,
      nextPage: response.next,
      previousPage: response.previous,
    };
  },

  getById: async (id: number) => {
    const response = await makeRequest<ApiUser>(`/users/${id}/`);
    return convertApiUserToUi(response);
  },

  create: async (data: Partial<ApiUser>) => {
    const response = await makeRequest<ApiUser>('/users/', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    return convertApiUserToUi(response);
  },

  update: async (id: number, data: Partial<ApiUser>) => {
    const response = await makeRequest<ApiUser>(`/users/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });

    return convertApiUserToUi(response);
  },

  delete: async (id: number) => {
    await makeRequest(`/users/${id}/`, { method: 'DELETE' });
  },
};

// ============================================================
// API Endpoints - Categories
// ============================================================

export const categoryApi = {
  getAll: async () => {
    const response = await makeRequest<
      PaginatedResponse<{ id: number; name: string }>
    >('/categories/');

    return response.results;
  },

  create: async (name: string) => {
    const response = await makeRequest<{ id: number; name: string }>(
      '/categories/',
      {
        method: 'POST',
        body: JSON.stringify({ name }),
      }
    );

    return response;
  },

  delete: async (id: number) => {
    await makeRequest(`/categories/${id}/`, { method: 'DELETE' });
  },
};

// ============================================================
// API Endpoints - Discounts
// ============================================================

export const discountApi = {
  getAll: async (page: number = 1) => {
    const response = await makeRequest<
      PaginatedResponse<{
        id: number;
        name: string;
        percentage: string;
        fixed_amount: string;
      }>
    >(`/discounts/?page=${page}`);

    return {
      items: response.results,
      total: response.count,
      nextPage: response.next,
      previousPage: response.previous,
    };
  },

  create: async (data: {
    name: string;
    percentage?: string;
    fixed_amount?: string;
  }) => {
    const response = await makeRequest<any>('/discounts/', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    return response;
  },

  delete: async (id: number) => {
    await makeRequest(`/discounts/${id}/`, { method: 'DELETE' });
  },
};

// ============================================================
// API Endpoints - Inventory Management
// ============================================================

export const inventoryApi = {
  getLowStock: async () => {
    const response = await makeRequest<any[]>('/inventory/low-stock/');
    return response;
  },

  getStockHistory: async (productId: number) => {
    const response = await makeRequest<any[]>(
      `/products/${productId}/stock-history/`
    );
    return response;
  },
};

// ============================================================
// API Endpoints - Wastage
// ============================================================

export const wastageApi = {
  getAll: async (page: number = 1) => {
    const response = await makeRequest<PaginatedResponse<any>>(
      `/wastage/?page=${page}`
    );
    return {
      items: response.results,
      total: response.count,
      nextPage: response.next,
      previousPage: response.previous,
    };
  },

  create: async (data: any) => {
    const response = await makeRequest<any>('/wastage/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return response;
  },
};

// ============================================================
// API Endpoints - Notifications
// ============================================================

export const notificationApi = {
  getAll: async () => {
    const response = await makeRequest<any[]>('/notifications/');
    return response;
  },

  markAsRead: async (id: number) => {
    const response = await makeRequest<any>(`/notifications/${id}/read/`, {
      method: 'POST',
    });
    return response;
  },
};

export default {
  auth: authApi,
  products: productApi,
  sales: saleApi,
  users: userApi,
  categories: categoryApi,
  discounts: discountApi,
  inventory: inventoryApi,
  wastage: wastageApi,
  notifications: notificationApi,
};
```

**Steps:**
1. [ ] Create new file: `Frontend/src/services/api.ts`
2. [ ] Copy the entire code above into the file
3. [ ] Save the file
4. [ ] Run: `cd Frontend && npm run build`
5. [ ] Check for TypeScript errors
6. [ ] Expected: Build should complete with 0 errors

**Time:** 10-20 minutes (copy/paste)  
**Difficulty:** 🟢 Easy (just copying code)

---

## ✅ PHASE 2 VERIFICATION

**Checkpoint: API Service Layer Ready?**

```bash
cd Frontend
npm run build
```

**You should see:**
```
✓ 1988 modules transformed
built in X.XXs
```

If you see errors, read them carefully and fix the issues. Most likely missing imports or type mismatches.

---

## 🟠 PHASE 3: CONNECT FRONTEND COMPONENTS (3-4 hours)

Replace mock data in components with real API calls.

### Step 3-1: Update AuthContext.tsx

**File:** `Frontend/src/context/AuthContext.tsx`

**Find this section (should be around line 40-50):**
```typescript
const login = (username: string, role: UserRole, id: number, email?: string) => {
  // ❌ Current: Mock only
  const newUser: AuthUser = {
    id,
    username,
    email,
    full_name: username.charAt(0).toUpperCase() + username.slice(1),
    role,
    avatarColor: color
  };
  
  setUser(newUser);
  sessionStorage.setItem('bakeryUser', JSON.stringify(newUser));
};
```

**Replace with:**
```typescript
const login = async (username: string, password: string) => {
  try {
    // ✅ NEW: Call backend API
    const response = await apiClient.auth.login(username, password);
    
    const user: AuthUser = {
      id: response.user.id,
      username: response.user.username,
      email: response.user.email,
      full_name: response.user.full_name,
      role: (response.user.role?.toUpperCase?.() || 'USER') as UserRole,
      avatarColor: response.user.avatarColor || 'bg-blue-500'
    };
    
    setUser(user);
    localStorage.setItem('bakeryUser', JSON.stringify(user));
    return response;
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
};
```

**Also add import at top:**
```typescript
import apiClient from '../services/api';
```

**Steps:**
1. [ ] Open Frontend/src/context/AuthContext.tsx
2. [ ] Find the login function
3. [ ] Replace with code above
4. [ ] Add import statement
5. [ ] Save file

**Time:** 10 minutes  
**Difficulty:** 🟢 Easy

---

### Step 3-2: Update BillingScreen.tsx

**File:** `Frontend/src/components/BillingScreen.tsx`

**Find useEffect (around line 50-70):**
```typescript
useEffect(() => {
  // ❌ Current: Uses mockProducts
  setProducts(mockProducts);
}, []);
```

**Replace with:**
```typescript
useEffect(() => {
  // ✅ NEW: Fetch from API
  const loadProducts = async () => {
    try {
      setLoading(true);
      const response = await apiClient.products.getAll();
      setProducts(response.items);
    } catch (error) {
      console.error('Failed to load products:', error);
      setError('Failed to load products');
    } finally {
      setLoading(false);
    }
  };
  
  loadProducts();
}, []);
```

**Add loading/error handling to JSX:**
```typescript
if (loading) return <div className="flex items-center justify-center h-full">Loading...</div>;
if (error) return <div className="text-red-600">{error}</div>;
```

**Also add import:**
```typescript
import apiClient from '../services/api';
```

**Steps:**
1. [ ] Open Frontend/src/components/BillingScreen.tsx
2. [ ] Find the useEffect hook
3. [ ] Replace with code above
4. [ ] Add loading state UI
5. [ ] Add import statement
6. [ ] Save file

**Time:** 15 minutes  
**Difficulty:** 🟡 Medium (need to handle loading/error states)

---

### Step 3-3: Update SalesSummary.tsx

**Similar process to BillingScreen:**

```typescript
useEffect(() => {
  const loadSales = async () => {
    try {
      setLoading(true);
      const response = await apiClient.sales.getAll();
      setSales(response.items);
    } catch (error) {
      console.error('Failed to load sales:', error);
    } finally {
      setLoading(false);
    }
  };
  
  loadSales();
}, []);
```

**Steps:**
1. [ ] Open Frontend/src/components/SalesSummary.tsx
2. [ ] Replace mock data with API call
3. [ ] Add loading state
4. [ ] Add import apiClient
5. [ ] Save file

**Time:** 15 minutes  
**Difficulty:** 🟡 Medium

---

### Step 3-4: Update UserManagement.tsx

**Similar pattern:**

```typescript
useEffect(() => {
  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await apiClient.users.getAll();
      setUsers(response.items);
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };
  
  loadUsers();
}, []);
```

**Steps:**
1. [ ] Open Frontend/src/components/UserManagement.tsx
2. [ ] Replace initialStaffMembers with API call
3. [ ] Add loading state
4. [ ] Add import
5. [ ] Save file

**Time:** 15 minutes  
**Difficulty:** 🟡 Medium

---

### Step 3-5: Update Other Components

**Components still using mock data that need updating:**
- [ ] Dashboard.tsx
- [ ] StockManagementScreen.tsx
- [ ] DiscountManagement.tsx
- [ ] NotificationScreen.tsx
- [ ] ProductCard.tsx (if it has mock data)

**Pattern for each (follow same as above):**
1. Find useEffect with mock data
2. Replace with apiClient call
3. Handle loading/error states
4. Add import statement
5. Save and verify TypeScript errors

**Time:** 10-15 minutes each (5 components = 1 hour total)  
**Difficulty:** 🟡 Medium (repetitive pattern)

---

## ✅ PHASE 3 VERIFICATION

**Checkpoint: Components Connected?**

```bash
cd Frontend
npm run build
```

**Expected:** 0 TypeScript errors

Also verify:
- [ ] All `// TODO` comments replaced with real API calls
- [ ] All loading states working
- [ ] All error states have user feedback
- [ ] No console errors when running

---

## 🟠 PHASE 4: IMPLEMENT REAL AUTHENTICATION (2-3 hours)

### Step 4-1: Create LoginScreen Component

**File:** `Frontend/src/components/LoginScreen.tsx` (new/update)

```typescript
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from './ui/button';
import { Input } from './ui/input';
import apiClient from '../services/api';

export const LoginScreen = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // Call backend API
      await login(username, password);
      
      // Redirect to dashboard on success
      window.location.href = '/dashboard';
    } catch (err: any) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow">
        <h1 className="text-2xl font-bold mb-6">BakeryOS Login</h1>
        
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}
        
        <form onSubmit={handleLogin}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Username</label>
            <Input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Password</label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />
          </div>
          
          <Button
            type="submit"
            disabled={loading}
            className="w-full"
          >
            {loading ? 'Logging in...' : 'Login'}
          </Button>
        </form>
        
        <p className="mt-4 text-sm text-gray-600">
          Demo Credentials:
          <br />
          Username: manager
          <br />
          Password: pass123
        </p>
      </div>
    </div>
  );
};
```

**Steps:**
1. [ ] Create or update Frontend/src/components/LoginScreen.tsx
2. [ ] Copy code above
3. [ ] Save file
4. [ ] Update router to show LoginScreen when not authenticated

**Time:** 20 minutes  
**Difficulty:** 🟡 Medium

---

### Step 4-2: Add Route Guard to App Component

**File:** `Frontend/src/App.tsx`

**Add ProtectedRoute component:**

```typescript
import { useAuth } from './context/AuthContext';
import { LoginScreen } from './components/LoginScreen';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user } = useAuth();
  
  if (!user) {
    return <LoginScreen />;
  }
  
  return children;
};

// In your main App component:
export function App() {
  const { user } = useAuth();
  
  // Show login screen if not authenticated
  if (!user) {
    return <LoginScreen />;
  }
  
  // Show dashboard once logged in
  return (
    <div>
      {/* Header with Logout button */}
      <header>
        <button onClick={logout}>Logout</button>
      </header>
      
      {/* Your main dashboard content */}
      <Dashboard />
    </div>
  );
}
```

**Steps:**
1. [ ] Open Frontend/src/App.tsx
2. [ ] Add ProtectedRoute component
3. [ ] Update main App component to show LoginScreen when user is null
4. [ ] Add logout button to header
5. [ ] Save file

**Time:** 15 minutes  
**Difficulty:** 🟡 Medium

---

### Step 4-3: Add Logout Functionality

**Update AuthContext:**

```typescript
const logout = () => {
  apiClient.auth.logout();  // Clear tokens
  setUser(null);
  localStorage.removeItem('bakeryUser');
  window.location.href = '/login';
};
```

**Update Header component to show logout button:**

```typescript
export const Header = () => {
  const { user, logout } = useAuth();
  
  return (
    <header>
      <h1>BakeryOS</h1>
      {user && (
        <div>
          <span>{user.full_name}</span>
          <Button onClick={logout}>Logout</Button>
        </div>
      )}
    </header>
  );
};
```

**Steps:**
1. [ ] Update AuthContext with logout function
2. [ ] Export logout from context
3. [ ] Update Header.tsx to add logout button
4. [ ] Test logout flow

**Time:** 10 minutes  
**Difficulty:** 🟢 Easy

---

## ✅ PHASE 4 VERIFICATION

**Checkpoint: Authentication Flow Working?**

**Manual Testing Steps:**

1. [ ] Run frontend: `cd Frontend && npm run dev`
2. [ ] Run backend: `cd Backend && python manage.py runserver`
3. [ ] Open http://localhost:5173 (frontend)
4. [ ] Try incorrect login - should see error
5. [ ] Try correct login (check backend for valid credentials)
6. [ ] Should redirect to dashboard
7. [ ] Click logout - should go back to login
8. [ ] Ensure tokens are stored in localStorage
9. [ ] Verify Authorization headers sent with API requests

---

## 🟠 PHASE 5: TESTING & QA (2-3 hours)

### Test Checklist

**Authentication Tests:**
- [ ] Login with correct credentials → success
- [ ] Login with wrong password → error message
- [ ] Login with non-existent username → error message
- [ ] Logout → redirects to login
- [ ] Session persists after page refresh (tokens in localStorage)
- [ ] Token sent in Authorization header on API calls
- [ ] 401 response → auto-refresh token or redirect to login

**Product Management:**
- [ ] Load product list from API → displays correctly
- [ ] Product prices (decimal) display correctly
- [ ] Add product → creates on backend
- [ ] Edit product → updates on backend
- [ ] Delete product → removes from backend
- [ ] Search/filter products → works

**Sales/Billing:**
- [ ] Load sales list from API
- [ ] Create sale → shows correct bill number from backend
- [ ] Decimal calculations (price × quantity) correct
- [ ] Discount application works
- [ ] Sale persists on backend

**User Management:**
- [ ] Load users from API
- [ ] Add user → creates on backend
- [ ] Edit user → updates on backend
- [ ] Delete user → removes from backend

**Error Handling:**
- [ ] Network error → shows message
- [ ] 500 error → shows message
- [ ] 403 Forbidden → shows message
- [ ] Expired token → auto-refreshes or logs out

---

## 📋 FINAL INTEGRATION READINESS CHECKLIST

Run through this before declaring ready for production:

### Backend ✅
- [ ] `python manage.py check` returns 0 issues
- [ ] All 14 models working correctly
- [ ] avatar_color added to UserListSerializer
- [ ] JWT/Token auth configured consistently
- [ ] All endpoints responding correctly

### Frontend ✅
- [ ] `npm run build` succeeds with 0 errors
- [ ] Frontend/src/services/api.ts created
- [ ] All components connected to API
- [ ] Auth tokens stored and sent with requests
- [ ] Error interceptors working (401, 403, 500)
- [ ] Token refresh implemented
- [ ] Logout clears tokens properly

### Integration ✅
- [ ] Can login with backend credentials
- [ ] Products load from backend API
- [ ] Sales save to backend correctly
- [ ] Decimal fields handle correctly
- [ ] Token auto-refresh works
- [ ] Users can logout and login again
- [ ] No 401 errors on valid requests
- [ ] Rate limiting not hit during normal usage

### Code Quality ✅
- [ ] 0 TypeScript errors
- [ ] 0 JavaScript console errors
- [ ] All console.log() calls removed (use proper error handling)
- [ ] No hardcoded URLs (use API_BASE constant)
- [ ] Error messages user-friendly

---

## ⏱️ TIME SUMMARY

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | Backend fixes | 30 min | 🟢 Do First |
| 2 | API service layer | 2-3 hrs | 🟠 Critical |
| 3 | Connect components | 3-4 hrs | 🟠 Critical |
| 4 | Auth implementation | 2-3 hrs | 🟠 Important |
| 5 | Testing & QA | 2-3 hrs | 🟡 Important |
| | **TOTAL** | **10-16 hrs** | **2-3 days** |

---

## 🆘 TROUBLESHOOTING

### Problem: Backend returns 401 Unauthorized

**Solution:**
1. Check token is being sent in Authorization header
2. Verify token has not expired
3. Make sure you're using correct endpoint
4. Run `python manage.py check` to verify backend is OK

### Problem: CORS errors in browser console

**Solution:**
1. Verify backend has CORS enabled in settings.py
2. Check frontend API_BASE matches backend URL
3. Verify frontend is not using different port than expected

### Problem: Decimal values showing as wrong numbers

**Solution:**
1. Make sure you're using conversion functions from numericUtils.ts
2. Verify `toNumber()` called before arithmetic
3. Check that backend serializer returns strings for decimal fields

### Problem: Token not being stored

**Solution:**
1. Check localStorage.setItem() is being called
2. Verify localStorage not disabled/cleared
3. Check browser dev tools: Application → Local Storage

### Problem: Component not updating after API call

**Solution:**
1. Verify API response is being set with setState
2. Check loading state is being set/cleared
3. Look for fetch errors in browser console
4. Verify API endpoint URL is correct

---

## 🎓 REMINDERS

1. **Always use `apiClient` from services/api.ts** - Never use raw fetch() directly
2. **Always handle errors** - Show user-friendly messages
3. **Always show loading state** - Don't freeze UI while fetching
4. **Always convert decimals** - Use toNumber() before arithmetic
5. **Always catch errors** - Use try/catch or .catch()
6. **Always test endpoints** - Use Postman or Thunder Client to verify backend first
7. **Always check console** - Browser dev tools Network and Console tabs are your friends

---

## ✨ COMPLETION CRITERIA

You're ready to integrate when:

✅ Backend check: 0 issues  
✅ Frontend build: 0 errors  
✅ Login works end-to-end  
✅ All CRUD operations working (Create, Read, Update, Delete)  
✅ Error handling working  
✅ Token refresh working  
✅ All decimal operations correct  
✅ No hardcoded mock data in components  
✅ All tests passing  

---

**Good luck! You're very close! 🚀**

Once you complete all these steps, your frontend and backend will be fully integrated and ready to use together.

