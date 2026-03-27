# Analytics API Endpoints - Implementation Guide

## Overview
Created 5 new Django ViewSets to provide the analytics endpoints that your frontend dashboard components require.

## New Endpoints Created

### 1. **Sales Statistics** - `/api/analytics/sales-stats/`
**Endpoint**: `GET /api/analytics/sales-stats/`  
**Purpose**: Returns overall sales KPIs for the ManagerDashboard  
**Query Parameters** (optional):
- `date_from` (YYYY-MM-DD) - Start date for analysis (default: 30 days ago)
- `date_to` (YYYY-MM-DD) - End date for analysis (default: today)

**Response**:
```json
{
  "total_revenue": 5000.00,
  "total_orders": 25,
  "total_discount": 150.00,
  "total_cost_of_goods": 2500.00,
  "total_wastage_loss": 200.00,
  "net_profit": 2150.00,
  "period_from": "2026-02-26",
  "period_to": "2026-03-27"
}
```

**Used By**: ManagerDashboard KPI cards (Revenue, Net Profit, Total Orders, Wastage Loss)

---

### 2. **Product Statistics** - `/api/analytics/product-stats/`
**Endpoint**: `GET /api/analytics/product-stats/`  
**Purpose**: Returns top-selling products for the ManagerDashboard  
**Query Parameters** (optional):
- `date_from` (YYYY-MM-DD) - Start date for analysis (default: 30 days ago)
- `date_to` (YYYY-MM-DD) - End date for analysis (default: today)
- `limit` (integer) - Maximum number of products to return (default: 10)

**Response**:
```json
{
  "top_products": [
    {
      "product_id": "#PROD-1001",
      "product_name": "Fish Bun",
      "quantity_sold": 150,
      "total_revenue": 4500.00
    },
    {
      "product_id": "#PROD-1002",
      "product_name": "Bread Loaf",
      "quantity_sold": 80,
      "total_revenue": 2400.00
    }
  ]
}
```

**Used By**: ManagerDashboard Top Selling Items section

---

### 3. **Wastage Statistics** - `/api/analytics/wastage-stats/`
**Endpoint**: `GET /api/analytics/wastage-stats/`  
**Purpose**: Returns wastage breakdown by reason for ManagerDashboard  
**Query Parameters** (optional):
- `date_from` (YYYY-MM-DD) - Start date for analysis (default: 30 days ago)
- `date_to` (YYYY-MM-DD) - End date for analysis (default: today)

**Response**:
```json
{
  "breakdown": [
    {
      "reason": "Burnt",
      "quantity": 5,
      "loss_amount": 150.00,
      "percentage_of_revenue": 2.5
    },
    {
      "reason": "Expired",
      "quantity": 3,
      "loss_amount": 60.00,
      "percentage_of_revenue": 1.0
    }
  ],
  "total_wastage_loss": 210.00
}
```

**Used By**: ManagerDashboard Wastage Breakdown section

---

### 4. **Inventory Statistics** - `/api/analytics/inventory-stats/`
**Endpoint**: `GET /api/analytics/inventory-stats/`  
**Purpose**: Returns general inventory metrics (optional, for future expansion)

**Response**:
```json
{
  "total_inventory_value": 45000.00,
  "total_products": 25,
  "low_stock_items": 5,
  "expiring_items_count": 2
}
```

**Used By**: Future dashboard components or reports

---

### 5. **Low Stock Items** - `/api/inventory/low-stock/`
**Endpoint**: `GET /api/inventory/low-stock/`  
**Purpose**: Returns all products with stock below 10 units  
**No Query Parameters**

**Response**:
```json
[
  {
    "id": 1,
    "type": "product",
    "name": "Fish Bun",
    "product_id": "#PROD-1001",
    "current_stock": 5,
    "reorder_level": 10.0,
    "unit": "units"
  },
  {
    "id": 2,
    "type": "product",
    "name": "Bread Loaf",
    "product_id": "#PROD-1002",
    "current_stock": 8,
    "reorder_level": 10.0,
    "unit": "units"
  }
]
```

**Used By**: All dashboard components (ManagerDashboard, BakerDashboard, StorekeeperDashboard) for low stock alerts

---

## Files Modified

### 1. **Backend/api/views/analytics_views.py**
Added 5 new ViewSet classes at the end of the file:
- `SalesStatsViewSet` - Main sales KPI endpoint
- `ProductStatsViewSet` - Top products endpoint  
- `WastageStatsViewSet` - Wastage breakdown endpoint
- `InventoryStatsViewSet` - Inventory metrics endpoint
- `LowStockViewSet` - Low stock items endpoint

### 2. **Backend/api/urls.py**
Updated imports and router registrations:
```python
# Added imports
from api.views.analytics_views import (
    SalesAnalyticsViewSet,
    InventoryAnalyticsViewSet,
    DashboardKpiViewSet,
    SalesStatsViewSet,        # NEW
    ProductStatsViewSet,      # NEW
    WastageStatsViewSet,      # NEW
    InventoryStatsViewSet,    # NEW
    LowStockViewSet          # NEW
)

# Added router registrations
router.register(r'analytics/sales-stats', SalesStatsViewSet, basename='sales-stats')
router.register(r'analytics/product-stats', ProductStatsViewSet, basename='product-stats')
router.register(r'analytics/wastage-stats', WastageStatsViewSet, basename='wastage-stats')
router.register(r'analytics/inventory-stats', InventoryStatsViewSet, basename='inventory-stats')
router.register(r'inventory/low-stock', LowStockViewSet, basename='low-stock')
```

---

## How to Test

### 1. Start the Django Server
```bash
cd Backend
python manage.py runserver
```

### 2. Test Each Endpoint

#### Test Sales Stats
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/analytics/sales-stats/"
```

#### Test Product Stats
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/analytics/product-stats/?limit=5"
```

#### Test Wastage Stats
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/analytics/wastage-stats/"
```

#### Test Inventory Stats
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/analytics/inventory-stats/"
```

#### Test Low Stock
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/inventory/low-stock/"
```

### 3. Verify in Browser Console
Once the frontend starts, check the browser's Network tab:
- All four endpoints should return 200 OK
- No more 404 errors

---

## Integration with Frontend

### Frontend API Calls
The frontend components now call these endpoints through the `analyticsApi` object:

```typescript
// In ManagerDashboard.tsx
const [salesData, productData, wastageData, lowStockData] = await Promise.all([
  analyticsApi.getSalesStats(),           // → GET /api/analytics/sales-stats/
  analyticsApi.getProductStats(),         // → GET /api/analytics/product-stats/
  analyticsApi.getWastageStats(),         // → GET /api/analytics/wastage-stats/
  inventoryApi.getLowStock(),             // → GET /api/inventory/low-stock/
]);
```

### Updated Components Using These Endpoints
1. **ManagerDashboard** - All 4 endpoints
2. **BakerDashboard** - `inventoryApi.getLowStock()` and `wastageApi.getAll()`
3. **StorekeeperDashboard** - `inventoryApi.getLowStock()` 
4. **WastageOverview** - `wastageApi.getAll()`

---

## Security & Permissions

All endpoints require:
- **Authentication**: User must be logged in (Bearer token)
- **Permission**: `IsAuthenticated` 
- **Rate Limiting**: Inherited from Django REST Framework settings

---

## Performance Considerations

### Query Optimization
The endpoints use Django ORM aggregations for efficiency:
- `Sum()`, `Count()`, `Avg()` for calculations
- `prefetch_related()` for loading related objects
- Date filtering with `__date__gte`, `__date__lte`

### Caching Recommendation
For production, consider adding caching:
```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def list(self, request):
    ...
```

---

## Troubleshooting

### Issue: 404 Not Found
**Solution**: Ensure the Django server was restarted after URL changes
```bash
python manage.py runserver
```

### Issue: 401 Unauthorized
**Solution**: Send valid authentication token in headers
```bash
Authorization: Bearer <your_token_here>
```

### Issue: Empty Data
**Solution**: Ensure test data exists in your database
- Check if Sale records exist (for sales-stats)
- Check if Product records exist (for product-stats, low-stock)
- Check if ProductWastage records exist (for wastage-stats)

### Issue: Date Not Filtering Correctly
**Solution**: Ensure date format is ISO-8601: `YYYY-MM-DD`
```bash
?date_from=2026-02-26&date_to=2026-03-27
```

---

## API Specification Summary

| Endpoint | Method | Auth | Response | Used By |
|----------|--------|------|----------|---------|
| `/api/analytics/sales-stats/` | GET | ✅ | KPI metrics | ManagerDashboard |
| `/api/analytics/product-stats/` | GET | ✅ | Top products | ManagerDashboard |
| `/api/analytics/wastage-stats/` | GET | ✅ | Wastage by reason | ManagerDashboard |
| `/api/analytics/inventory-stats/` | GET | ✅ | Inventory metrics | Future use |
| `/api/inventory/low-stock/` | GET | ✅ | Low stock items | All dashboards |

---

## Next Steps

1. ✅ Restart Django server to load new URLs
2. ✅ Test each endpoint with curl or Postman
3. ✅ Run frontend (npm run dev) to see dashboards fetch real data
4. ✅ Monitor browser console for any errors
5. ⏳ Monitor performance and add caching if needed

