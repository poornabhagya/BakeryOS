import { ApiProduct, ApiSale, ApiUser, ApiSaleDetail } from '../utils/apiTypes';
import {
  convertApiProductToUi,
  convertApiUserToUi,
  convertApiSaleToUi,
  convertApiSaleDetailToUi,
} from '../utils/conversions';

// ============================================================
// API Configuration
// ============================================================

// Use relative path /api so Vite proxy can intercept requests in development
// In production, this will be handled by the backend serving the frontend
const API_BASE = '/api';
console.log('[API] API_BASE configured as:', API_BASE);
console.log('[API] Using relative URL - Vite proxy will handle in development');

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

export function getAccessToken(): string | null {
  return accessToken || localStorage.getItem('access_token');
}

// ============================================================
// Request Headers
// ============================================================

function getAuthHeaders(): Record<string, string> {
  const token = getAccessToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Token ${token}` }),
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

  try {
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
    const newToken = data.access as string;
    accessToken = newToken;
    localStorage.setItem('access_token', newToken);
    
    return newToken;
  } catch (error) {
    clearTokens();
    window.location.href = '/login';
    return '';
  }
}

// ============================================================
// Core Request Function with Enhanced Error Handling
// ============================================================

async function makeRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const token = getAccessToken();
  const method = options.method || 'GET';
  
  console.log(`[API] ${method} ${url}`);
  if (token) {
    console.log('[API] Authorization header: Token ' + token.substring(0, 20) + '...');
  }
  
  let response: Response;

  try {
    response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Token ${token}` }),
        ...options.headers,
      },
    });
    console.log(`[API] Response status: ${response.status}`);
  } catch (error) {
    // Network error (no response from server)
    const errorMessage = error instanceof Error ? error.message : 'Network request failed';
    console.error(`[API] Network error on ${endpoint}:`, errorMessage);
    throw new ApiError(0, { error: errorMessage }, `Network error: ${errorMessage}`);
  }

  // Handle 401 - Token invalid or expired (no refresh in Token auth)
  if (response.status === 401) {
    console.warn(`[API] Unauthorized on ${endpoint} (401) - token invalid or expired`);
    clearTokens();
    window.location.href = '/login';
    throw new ApiError(401, {}, 'Session expired. Please log in again.');
  }

  // Handle other error statuses
  if (!response.ok) {
    let errorDetails: any = {};
    let errorMessage = '';

    try {
      errorDetails = await response.json();
      errorMessage = errorDetails.detail || errorDetails.message || errorDetails.error || '';
    } catch {
      // Response was not JSON (e.g., HTML error page)
      errorMessage = await response.text().catch(() => '');
    }

    // Handle 401: Session/token invalid (after refresh attempt failed or no refresh token)
    if (response.status === 401) {
      console.warn(`[API] Unauthorized access on ${endpoint} - clearing session`);
      clearTokens();
      window.location.href = '/login';
      throw new ApiError(
        401,
        errorDetails,
        'Session expired. Please log in again.'
      );
    }

    // Handle 403: Permission denied
    if (response.status === 403) {
      console.warn(`[API] Access forbidden on ${endpoint}:`, errorMessage);
      throw new ApiError(
        403,
        errorDetails,
        errorMessage || 'You do not have permission for this action.'
      );
    }

    // Handle 400: Bad request
    if (response.status === 400) {
      console.error(`[API] Bad request on ${endpoint}:`, errorMessage);
      // Log detailed field errors if present (from Django validation)
      if (errorDetails && typeof errorDetails === 'object' && !Array.isArray(errorDetails)) {
        console.error(`[API] Field validation errors:`, errorDetails);
      }
      throw new ApiError(
        400,
        errorDetails,
        errorMessage || 'Invalid request. Please check your input.'
      );
    }

    // Handle 404: Not found
    if (response.status === 404) {
      console.error(`[API] Resource not found on ${endpoint}`);
      throw new ApiError(
        404,
        errorDetails,
        'Resource not found.'
      );
    }

    // Handle 500+: Server errors
    if (response.status >= 500) {
      console.error(`[API] Server error (${response.status}) on ${endpoint}:`, errorMessage);
      throw new ApiError(
        response.status,
        errorDetails,
        'Server error. Please try again later.'
      );
    }

    // Generic error for other status codes
    console.error(`[API] HTTP ${response.status} on ${endpoint}:`, errorMessage);
    throw new ApiError(
      response.status,
      errorDetails,
      errorMessage || `HTTP ${response.status} Error`
    );
  }

  // Success path - handle response based on status code
  console.log(`[API] ✅ Response successful (${response.status})`);
  
  // Handle 204 No Content and other responses with no body
  if (response.status === 204 || response.status === 201 || response.status === 202) {
    // These status codes may have no response body
    // Check if there's actually content to parse
    const contentLength = response.headers.get('content-length');
    const contentType = response.headers.get('content-type');
    
    if (response.status === 204 || contentLength === '0' || !contentType?.includes('application/json')) {
      console.log(`[API] ✅ Response ${response.status} with no JSON body - returning null`);
      return null as unknown as T;
    }
  }
  
  // Parse JSON for responses that have a body
  try {
    const data = await response.json() as T;
    console.log(`[API] ✅ JSON parsed successfully for ${endpoint}`);
    return data;
  } catch (error) {
    // If JSON parsing fails on a success response, return null
    console.warn(`[API] ⚠ Failed to parse JSON from successful response (${response.status})`, error);
    return null as unknown as T;
  }
}

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
// API Endpoints - Authentication
// ============================================================

export const authApi = {
  login: async (username: string, password: string) => {
    console.log('[API] Attempting login with username:', username);
    console.log('[API] Using API_BASE:', API_BASE);
    
    try {
      const response = await makeRequest<{
        token?: string;      // Some endpoints return 'token'
        access?: string;     // Others return 'access' 
        refresh?: string;    // And 'refresh'
        user: ApiUser;
      }>('/auth/login/', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });

      console.log('[API] ==================== LOGIN RESPONSE ====================');
      console.log('[API] Response object:', response);
      console.log('[API] Response keys:', Object.keys(response));
      console.log('[API] response.token:', response.token ? response.token.substring(0, 30) + '...' : 'undefined');
      console.log('[API] response.access:', response.access ? response.access.substring(0, 30) + '...' : 'undefined');
      console.log('[API] response.refresh:', response.refresh ? response.refresh.substring(0, 30) + '...' : 'undefined');
      console.log('[API] response.user:', response.user);
      console.log('[API] ============================================================');

      // Determine which token field is being used
      const accessToken = response.access || response.token;
      const refreshToken = response.refresh;

      if (!accessToken) {
        throw new Error('Login response missing access token (neither "access" nor "token" field found)');
      }

      setTokens(accessToken, refreshToken || '');
      console.log('[API] ✅ Tokens stored in localStorage');
      console.log('[API] Stored access_token:', localStorage.getItem('access_token') ? localStorage.getItem('access_token')!.substring(0, 30) + '...' : 'NOT FOUND');
      console.log('[API] Stored refresh_token:', localStorage.getItem('refresh_token') ? localStorage.getItem('refresh_token')!.substring(0, 30) + '...' : 'NOT FOUND');
      
      return {
        token: accessToken,
        user: convertApiUserToUi(response.user),
      };
    } catch (err) {
      console.error('[API] ❌ LOGIN FAILED:', err);
      console.error('[API] Error type:', err instanceof Error ? err.message : err);
      throw err;
    }
  },

  logout: () => {
    clearTokens();
  },

  refreshToken: refreshAccessToken,
};

// ============================================================
// API Endpoints - Products
// ============================================================

export const productApi = {
  getAll: async (page: number = 1, search?: string) => {
    let endpoint = `/products/?page=${page}`;
    if (search) endpoint += `&search=${encodeURIComponent(search)}`;

    const response = await makeRequest<PaginatedResponse<ApiProduct> | ApiProduct[]>(
      endpoint
    );

    // Handle both flat array and paginated response
    const items = Array.isArray(response) ? response : response.results;
    const total = Array.isArray(response) ? response.length : response.count;

    return {
      items: items.map(convertApiProductToUi),
      total: total,
      nextPage: Array.isArray(response) ? null : response.next,
      previousPage: Array.isArray(response) ? null : response.previous,
    };
  },

  getAllPages: async (search?: string) => {
    /**
     * Fetch ALL pages automatically and merge them into a single array.
     * Perfect for manageable datasets (< 500 items).
     * Use this instead of getAll() when you need complete inventory.
     */
    let allItems: ApiProduct[] = [];
    let page = 1;
    let hasNextPage = true;

    while (hasNextPage) {
      let endpoint = `/products/?page=${page}`;
      if (search) endpoint += `&search=${encodeURIComponent(search)}`;

      const response = await makeRequest<PaginatedResponse<ApiProduct> | ApiProduct[]>(
        endpoint
      );

      // Handle both flat array and paginated response
      const items = Array.isArray(response) ? response : response.results;
      allItems = [...allItems, ...items];

      // Check if there's a next page
      if (Array.isArray(response)) {
        hasNextPage = false;
      } else {
        hasNextPage = !!response.next;
      }

      page++;
    }

    return {
      items: allItems.map(convertApiProductToUi),
      total: allItems.length,
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
      ...(data.selling_price !== undefined && { selling_price: String(data.selling_price) }),
      ...(data.cost_price !== undefined && { cost_price: String(data.cost_price) }),
      ...(data.current_stock !== undefined && { current_stock: String(data.current_stock) }),
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

  getLatest: async () => {
    // Get the first page (most recent sale should be first based on backend ordering)
    const response = await makeRequest<PaginatedResponse<ApiSale>>('/sales/?page=1&page_size=1');
    
    if (response.results && response.results.length > 0) {
      return convertApiSaleToUi(response.results[0]);
    }
    return null;
  },

  getLatestWithItems: async () => {
    // First get the latest sale ID
    const latestSale = await saleApi.getLatest();
    if (!latestSale) {
      return null;
    }
    
    // Then fetch full details with items
    const response = await makeRequest<ApiSaleDetail>(`/sales/${latestSale.id}/`);
    return convertApiSaleDetailToUi(response);
  },

  getById: async (id: number) => {
    const response = await makeRequest<ApiSale>(`/sales/${id}/`);
    return convertApiSaleToUi(response);
  },

  getSale: async (id: number) => {
    // Fetch detailed sale with nested items (using SaleDetailSerializer on backend)
    const response = await makeRequest<ApiSaleDetail>(`/sales/${id}/`);
    return convertApiSaleDetailToUi(response);
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

  getNextBillNumber: async () => {
    const response = await makeRequest<{
      next_bill_number: string;
      next_number: number;
    }>('/sales/next-bill-number/');
    return response;
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

  getProducts: async () => {
    const response = await makeRequest<
      Array<{ id: number; name: string; type: string }>
    >('/categories/products/');

    return response;
  },

  getIngredients: async () => {
    const response = await makeRequest<
      Array<{ id: number; name: string; type: string }>
    >('/categories/ingredients/');

    return response;
  },

  create: async (data: { 
    name: string; 
    type: 'Product' | 'Ingredient'; 
    description?: string | null; 
    low_stock_alert?: number | null;
  }) => {
    const response = await makeRequest<{ id: number; category_id: string; name: string; type: string }>(
      '/categories/',
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );

    return response;
  },

  update: async (id: number, data: { 
    name: string; 
    type?: 'Product' | 'Ingredient'; 
    description?: string | null; 
    low_stock_alert?: number | null;
  }) => {
    const response = await makeRequest<{ id: number; category_id: string; name: string; type: string }>(
      `/categories/${id}/`,
      {
        method: 'PATCH',
        body: JSON.stringify(data),
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
        percentage?: string;
        fixed_amount?: string;
      }>
    >(`/discounts/?page=${page}`);

    return {
      items: response.results,
      total: response.count,
      nextPage: response.next,
      previousPage: response.previous,
    };
  },

  getActive: async () => {
    const response = await makeRequest<{
      count: number;
      results: Array<{
        id: number;
        name: string;
        discount_id: string;
        discount_type: 'Percentage' | 'FixedAmount';
        value: string | number;
        applicable_to: 'All' | 'Category' | 'Product';
        target_category_id?: number;
        target_product_id?: number;
        is_active: boolean;
      }>;
      current_datetime: string;
    }>('/discounts/active/');

    return response.results || [];
  },

  create: async (data: {
    name: string;
    discount_type: 'Percentage' | 'FixedAmount';
    value: number;
    applicable_to: 'All' | 'Category' | 'Product';
    start_date?: string | null;
    end_date?: string | null;
    start_time?: string | null;
    end_time?: string | null;
    target_category_id?: number | null;
    target_product_id?: number | null;
  }) => {
    const response = await makeRequest<any>('/discounts/', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    return response;
  },

  update: async (id: number, data: any) => {
    const response = await makeRequest<any>(`/discounts/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });

    return response;
  },

  delete: async (id: number) => {
    await makeRequest(`/discounts/${id}/`, { method: 'DELETE' });
  },
};

// ============================================================
// API Endpoints - Ingredients
// ============================================================

export const ingredientApi = {
  getAll: async (page: number = 1, search?: string) => {
    let endpoint = `/ingredients/?page=${page}`;
    if (search) endpoint += `&search=${encodeURIComponent(search)}`;

    const response = await makeRequest<PaginatedResponse<any> | any[]>(
      endpoint
    );

    // Handle both flat array and paginated response
    const items = Array.isArray(response) ? response : response.results;
    const total = Array.isArray(response) ? response.length : response.count;

    return {
      items: items,
      total: total,
      nextPage: Array.isArray(response) ? null : response.next,
      previousPage: Array.isArray(response) ? null : response.previous,
    };
  },

  getAllPages: async (search?: string) => {
    /**
     * Fetch ALL pages automatically and merge them into a single array.
     * Perfect for manageable datasets (< 500 items).
     * Use this instead of getAll() when you need complete inventory.
     */
    let allItems: any[] = [];
    let page = 1;
    let hasNextPage = true;

    while (hasNextPage) {
      let endpoint = `/ingredients/?page=${page}`;
      if (search) endpoint += `&search=${encodeURIComponent(search)}`;

      const response = await makeRequest<PaginatedResponse<any> | any[]>(
        endpoint
      );

      // Handle both flat array and paginated response
      const items = Array.isArray(response) ? response : response.results;
      allItems = [...allItems, ...items];

      // Check if there's a next page
      if (Array.isArray(response)) {
        hasNextPage = false;
      } else {
        hasNextPage = !!response.next;
      }

      page++;
    }

    return {
      items: allItems,
      total: allItems.length,
    };
  },

  getById: async (id: number) => {
    const response = await makeRequest<any>(`/ingredients/${id}/`);
    return response;
  },

  create: async (data: any) => {
    const response = await makeRequest<any>('/ingredients/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return response;
  },

  update: async (id: number, data: any) => {
    const response = await makeRequest<any>(`/ingredients/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
    return response;
  },

  delete: async (id: number) => {
    await makeRequest(`/ingredients/${id}/`, { method: 'DELETE' });
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

  update: async (id: number, data: any) => {
    const response = await makeRequest<any>(`/wastage/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
    return response;
  },

  delete: async (id: number) => {
    await makeRequest(`/wastage/${id}/`, { method: 'DELETE' });
  },
};

// ============================================================
// API Endpoints - Notifications
// ============================================================

export const notificationApi = {
  getAll: async () => {
    const response = await makeRequest<PaginatedResponse<any>>('/notifications/');
    // Extract results array from paginated response
    return Array.isArray(response) ? response : (response.results || []);
  },

  markAsRead: async (id: number) => {
    const response = await makeRequest<any>(`/notifications/${id}/read/`, {
      method: 'POST',
    });
    return response;
  },

  markAllAsRead: async () => {
    const response = await makeRequest<any>('/notifications/read-all/', {
      method: 'POST',
    });
    return response;
  },
};

// ============================================================
// API Endpoints - Batches
// ============================================================

export const batchApi = {
  getProductBatches: async () => {
    const response = await makeRequest<any[]>('/product-batches/');
    return response;
  },

  createProductBatch: async (data: any) => {
    const response = await makeRequest<any>('/product-batches/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return response;
  },

  getIngredientBatches: async () => {
    const response = await makeRequest<any[]>('/ingredient-batches/');
    return response;
  },

  createIngredientBatch: async (data: any) => {
    const response = await makeRequest<any>('/ingredient-batches/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return response;
  },
};

// ============================================================
// API Endpoints - Analytics/Reports
// ============================================================

export const analyticsApi = {
  getSalesStats: async (dateFrom?: string, dateTo?: string) => {
    let endpoint = '/analytics/sales-stats/';
    if (dateFrom || dateTo) {
      const params = new URLSearchParams();
      if (dateFrom) params.append('date_from', dateFrom);
      if (dateTo) params.append('date_to', dateTo);
      endpoint += `?${params.toString()}`;
    }
    
    const response = await makeRequest<any>(endpoint);
    return response;
  },

  getProductStats: async () => {
    const response = await makeRequest<any>('/analytics/product-stats/');
    return response;
  },

  getInventoryStats: async () => {
    const response = await makeRequest<any>('/analytics/inventory-stats/');
    return response;
  },

  getWastageStats: async (dateFrom?: string, dateTo?: string) => {
    let endpoint = '/analytics/wastage-stats/';
    if (dateFrom || dateTo) {
      const params = new URLSearchParams();
      if (dateFrom) params.append('date_from', dateFrom);
      if (dateTo) params.append('date_to', dateTo);
      endpoint += `?${params.toString()}`;
    }
    
    const response = await makeRequest<any>(endpoint);
    return response;
  },
};

// ============================================================
// Main API Client Export
// ============================================================

const apiClient = {
  auth: authApi,
  products: productApi,
  sales: saleApi,
  users: userApi,
  categories: categoryApi,
  discounts: discountApi,  ingredients: ingredientApi,  inventory: inventoryApi,
  wastage: wastageApi,
  notifications: notificationApi,
  batches: batchApi,
  analytics: analyticsApi,
};

export default apiClient;
