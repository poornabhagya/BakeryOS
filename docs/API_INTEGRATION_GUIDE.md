# 🚀 API Integration Checklist & Guide

**Project:** BakeryOS - Frontend ↔ Backend Integration  
**Status:** ✅ Frontend Ready  
**Last Updated:** March 26, 2026  

---

## 📋 Pre-Integration Verification

### ✅ Frontend Prerequisites (COMPLETED)

- [x] Type definitions created (ApiProduct, UiProduct, etc.)
- [x] Conversion functions implemented (convertApiProductToUi, etc.)
- [x] Numeric utilities created (toNumber, multiplyNumeric, etc.)
- [x] AuthContext updated for backend integration
- [x] Mock data interface defined
- [x] Build verified (0 TypeScript errors)
- [x] Components updated with safe numeric operations
- [x] Import paths consolidated and fixed

---

## 🔧 PHASE 1: Create API Client Service

### Step 1: Create `src/services/api.ts`

```typescript
// src/services/api.ts
import {
  convertApiProductToUi,
  convertApiUserToUi,
  convertApiSaleToUi,
  convertApiSaleItemToUi,
  ApiProduct,
  ApiUser,
  ApiSale,
  ApiSaleItem,
  UiProduct,
  UiUser,
  UiSale,
  UiSaleItem
} from '../utils/apiTypes';

// Base URL - Update with actual backend URL
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Setup axios or fetch with proper error handling
interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ============ USER ENDPOINTS ============

export const getUserList = async (): Promise<UiUser[]> => {
  try {
    const response = await fetch(`${API_BASE}/users/`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data: PaginatedResponse<ApiUser> = await response.json();
    return data.results.map(convertApiUserToUi);
  } catch (error) {
    console.error('Failed to fetch users:', error);
    throw error;
  }
};

export const getUserById = async (id: number): Promise<UiUser> => {
  try {
    const response = await fetch(`${API_BASE}/users/${id}/`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data: ApiUser = await response.json();
    return convertApiUserToUi(data);
  } catch (error) {
    console.error(`Failed to fetch user ${id}:`, error);
    throw error;
  }
};

export const loginUser = async (
  username: string,
  password: string
): Promise<{ user: UiUser; token: string }> => {
  try {
    const response = await fetch(`${API_BASE}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    return {
      user: convertApiUserToUi(data.user),
      token: data.token
    };
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
};

// ============ PRODUCT ENDPOINTS ============

export const getProducts = async (page: number = 1): Promise<{
  products: UiProduct[];
  total: number;
  next: string | null;
}> => {
  try {
    const response = await fetch(
      `${API_BASE}/products/?page=${page}&page_size=20`
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data: PaginatedResponse<ApiProduct> = await response.json();
    return {
      products: data.results.map(convertApiProductToUi),
      total: data.count,
      next: data.next
    };
  } catch (error) {
    console.error('Failed to fetch products:', error);
    throw error;
  }
};

export const getProductById = async (id: number): Promise<UiProduct> => {
  try {
    const response = await fetch(`${API_BASE}/products/${id}/`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data: ApiProduct = await response.json();
    return convertApiProductToUi(data);
  } catch (error) {
    console.error(`Failed to fetch product ${id}:`, error);
    throw error;
  }
};

export const createProduct = async (product: {
  name: string;
  selling_price: number;
  cost_price: number;
  current_stock: number;
  category_id: number;
  image_url: string;
}): Promise<UiProduct> => {
  try {
    const response = await fetch(`${API_BASE}/products/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(product)
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data: ApiProduct = await response.json();
    return convertApiProductToUi(data);
  } catch (error) {
    console.error('Failed to create product:', error);
    throw error;
  }
};

// ============ SALE ENDPOINTS ============

export const getSales = async (page: number = 1): Promise<{
  sales: UiSale[];
  total: number;
  next: string | null;
}> => {
  try {
    const response = await fetch(
      `${API_BASE}/sales/?page=${page}&page_size=20`
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data: PaginatedResponse<ApiSale> = await response.json();
    return {
      sales: data.results.map(convertApiSaleToUi),
      total: data.count,
      next: data.next
    };
  } catch (error) {
    console.error('Failed to fetch sales:', error);
    throw error;
  }
};

export const getSaleById = async (id: number): Promise<UiSale> => {
  try {
    const response = await fetch(`${API_BASE}/sales/${id}/`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data: ApiSale = await response.json();
    return convertApiSaleToUi(data);
  } catch (error) {
    console.error(`Failed to fetch sale ${id}:`, error);
    throw error;
  }
};

export const createSale = async (sale: {
  items: Array<{ product_id: number; quantity: number }>;
  payment_method: string;
  discount_id?: number | null;
}): Promise<UiSale> => {
  try {
    const response = await fetch(`${API_BASE}/sales/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(sale)
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data: ApiSale = await response.json();
    return convertApiSaleToUi(data);
  } catch (error) {
    console.error('Failed to create sale:', error);
    throw error;
  }
};

// ============ CATEGORY ENDPOINTS ============

export const getCategories = async () => {
  try {
    const response = await fetch(`${API_BASE}/categories/`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    return data.results || data;
  } catch (error) {
    console.error('Failed to fetch categories:', error);
    throw error;
  }
};
```

### Step 2: Update `.env` file

```env
# Backend API Configuration
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_API_TIMEOUT=30000

# Other settings
REACT_APP_ENV=development
```

---

## 🔄 PHASE 2: Replace Mock Data with API Calls

### Example: Update a Component to Use API

#### Before (with mock data):
```typescript
export const BillingScreen: React.FC = () => {
  const [products, setProducts] = useState<Product[]>(mockProducts);
  
  useEffect(() => {
    // Mock - no API call
  }, []);
  
  return (
    <div>
      {products.map(p => (
        <ProductCard key={p.id} product={p} />
      ))}
    </div>
  );
};
```

#### After (with API):
```typescript
import { getProducts } from './services/api';
import { UiProduct } from './utils/apiTypes';

export const BillingScreen: React.FC = () => {
  const [products, setProducts] = useState<UiProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const { products: data } = await getProducts(1);
        setProducts(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load products');
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchProducts();
  }, []);
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return (
    <div>
      {products.map(p => (
        <ProductCard key={p.id} product={p} />
      ))}
    </div>
  );
};
```

---

## 🧪 PHASE 3: Testing Integration

### Step 1: Test API Connection

```typescript
// test-api.ts
import { getProducts, getUserList } from './services/api';

export const testApiConnection = async () => {
  console.log('Testing API connection...');
  
  try {
    console.log('Testing Products endpoint...');
    const { products } = await getProducts(1);
    console.log('✅ Products loaded:', products.length);
    
    console.log('Testing Users endpoint...');
    const users = await getUserList();
    console.log('✅ Users loaded:', users.length);
    
    console.log('✅ All API endpoints working!');
  } catch (error) {
    console.error('❌ API Connection failed:', error);
  }
};

// Run in component:
useEffect(() => {
  testApiConnection();
}, []);
```

### Step 2: Verify Type Safety

```typescript
// Ensure types are properly matched
import { UiProduct } from './utils/apiTypes';

const product: UiProduct = {
  id: 1,
  product_id: '#PROD-1001',
  name: 'Fish Bun',
  selling_price: 80,          // ✅ Number, not string
  cost_price: 40,             // ✅ Number, not string
  current_stock: 100,         // ✅ Number, not string
  profitMargin: 100,          // ✅ camelCase, comes from profit_margin
  image_url: 'https://...',
  category_id: 1,
  category_name: 'Buns',
  status: 'active',
  created_at: '2026-03-26T14:30:00Z'
};

// Safe calculations
const totalValue = product.selling_price * product.current_stock;  // ✅ 8000
const profit = product.selling_price - product.cost_price;         // ✅ 40
```

---

## 🔐 PHASE 4: Authentication Integration

### Step 1: Update Login Flow

```typescript
// LoginScreen.tsx
import { loginUser } from './services/api';
import { convertApiUserToUi } from './utils/apiTypes';

export const LoginScreen: React.FC = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      const { user, token } = await loginUser(username, password);
      
      // Store token
      localStorage.setItem('token', token);
      
      // Update auth context
      login(
        user.username,
        user.role as 'Manager' | 'Cashier' | 'Baker' | 'Storekeeper',
        user.id,
        user.email,
        user.avatarColor // Now available from backend!
      );
      
      // Navigate to dashboard
      navigate('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      setError(error instanceof Error ? error.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleLogin}>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
        disabled={loading}
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        disabled={loading}
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};
```

---

## 📊 PHASE 5: Error Handling & Resilience

### Create Error Boundary

```typescript
// components/ErrorBoundary.tsx
import React, { ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  
  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error) {
    console.error('Error boundary caught:', error);
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="error-container">
          <h1>Something went wrong</h1>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }
    
    return this.props.children;
  }
}
```

### Create API Error Handler

```typescript
// utils/apiErrors.ts
export interface ApiError {
  status: number;
  message: string;
  details?: Record<string, any>;
}

export const handleApiError = (error: unknown): ApiError => {
  if (error instanceof Response) {
    return {
      status: error.status,
      message: `HTTP ${error.status}: ${error.statusText}`
    };
  }
  
  if (error instanceof Error) {
    return {
      status: 0,
      message: error.message
    };
  }
  
  return {
    status: 0,
    message: 'Unknown error occurred'
  };
};
```

---

## 📝 Implementation Checklist

### Week 1: Foundation
- [ ] Create `src/services/api.ts` with all endpoints
- [ ] Verify `src/utils/apiTypes.ts` is complete
- [ ] Verify `src/utils/numericUtils.ts` is complete
- [ ] Test API connection with test script
- [ ] Set up environment variables

### Week 2: Component Updates
- [ ] Update LoginScreen to use API
- [ ] Update BillingScreen to use API
- [ ] Update ProductManagement to use API
- [ ] Update UserManagement to use API
- [ ] Update SalesReports to use API

### Week 3: Testing & Refinement
- [ ] Test all CRUD operations
- [ ] Test error scenarios (network failures, 404s, etc.)
- [ ] Test pagination
- [ ] Test numeric calculations with real data
- [ ] Test date/time formatting

### Week 4: Optimization & Launch
- [ ] Add data caching layer (React Query, SWR, etc.)
- [ ] Add loading skeletons
- [ ] Optimize API call batching
- [ ] Add request retry logic
- [ ] Performance testing

---

## ✅ FINAL VERIFICATION

Before going live, verify:

- [ ] All API endpoints return expected data format
- [ ] All numeric conversions work correctly
- [ ] All date/time values parse correctly
- [ ] Authentication flow works end-to-end
- [ ] Error handling works for all failure scenarios
- [ ] No console TypeScript errors
- [ ] Build passes (`npm run build`)
- [ ] All components load data correctly
- [ ] Calculations produce correct results
- [ ] Mobile responsive design intact

---

## 🎉 Ready to Connect!

The frontend is fully prepared for API integration. Follow this checklist phase-by-phase, test thoroughly at each stage, and you'll have a fully integrated production-ready application.

**Questions?** Refer to:
- `INTEGRATION_STATUS_REPORT.md` - Detailed status of all fixes
- `BACKEND_API_SPECIFICATION.md` - Complete API documentation
- `API_FRONTEND_MISMATCH_REPORT.md` - Detailed field mappings
