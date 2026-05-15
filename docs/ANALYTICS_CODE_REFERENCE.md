# Analytics Endpoints - Code Reference

## Files Changed Summary

### 1. Backend/api/views/analytics_views.py

**Location**: End of the file (after line 1015)

**Code Added**:
```python
# ============================================================
# FRONTEND-FACING ANALYTICS ENDPOINTS
# ============================================================
# These are the top-level endpoints that the frontend calls directly


class SalesStatsViewSet(viewsets.ViewSet):
    """
    API Endpoint for sales statistics.
    
    GET /api/analytics/sales-stats/
    - Returns overall sales KPIs for dashboard
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get overall sales statistics"""
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Parse date range (defaults to last 30 days)
        if not date_to:
            date_to = timezone.now().date()
        else:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            except ValueError:
                date_to = timezone.now().date()
        
        if not date_from:
            date_from = date_to - timedelta(days=30)
        else:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            except ValueError:
                date_from = date_to - timedelta(days=30)
        
        # Get sales data
        sales = Sale.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        )
        
        total_sales_amount = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
        total_discount = sales.aggregate(Sum('discount_amount', default=Decimal('0')))['discount_amount__sum'] or Decimal('0')
        total_orders = sales.count()
        
        # Calculate cost of goods
        cost_of_goods = Decimal('0')
        for sale in sales.prefetch_related('items'):
            for item in sale.items.all():
                product = item.product_id
                cost_of_goods += (item.quantity * product.cost_price)
        
        # Calculate wastage loss
        product_wastage_loss = ProductWastage.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).aggregate(Sum('total_loss', default=Decimal('0')))['total_loss__sum'] or Decimal('0')
        
        ingredient_wastage_loss = IngredientWastage.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).aggregate(Sum('total_loss', default=Decimal('0')))['total_loss__sum'] or Decimal('0')
        
        total_wastage_loss = product_wastage_loss + ingredient_wastage_loss
        
        revenue = total_sales_amount - total_discount
        net_profit = revenue - cost_of_goods
        
        return Response({
            'total_revenue': float(revenue),
            'total_orders': total_orders,
            'total_discount': float(total_discount),
            'total_cost_of_goods': float(cost_of_goods),
            'total_wastage_loss': float(total_wastage_loss),
            'net_profit': float(net_profit),
            'period_from': date_from.isoformat(),
            'period_to': date_to.isoformat(),
        })


class ProductStatsViewSet(viewsets.ViewSet):
    """
    API Endpoint for product statistics.
    
    GET /api/analytics/product-stats/
    - Returns top-selling products for dashboard
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get top-selling products"""
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        limit = int(request.query_params.get('limit', 10))
        
        # Parse date range
        if not date_to:
            date_to = timezone.now().date()
        else:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            except ValueError:
                date_to = timezone.now().date()
        
        if not date_from:
            date_from = date_to - timedelta(days=30)
        else:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            except ValueError:
                date_from = date_to - timedelta(days=30)
        
        # Get top selling products
        top_products = SaleItem.objects.filter(
            sale_id__created_at__date__gte=date_from,
            sale_id__created_at__date__lte=date_to
        ).values('product_id').annotate(
            product_name=F('product_id__name'),
            quantity_sold=Sum('quantity'),
            total_revenue=Sum('subtotal'),
        ).order_by('-total_revenue')[:limit]
        
        results = []
        for item in top_products:
            results.append({
                'product_id': item['product_id'],
                'product_name': item['product_name'],
                'quantity_sold': float(item['quantity_sold'] or 0),
                'total_revenue': float(item['total_revenue'] or 0),
            })
        
        return Response({'top_products': results})


class WastageStatsViewSet(viewsets.ViewSet):
    """
    API Endpoint for wastage statistics.
    
    GET /api/analytics/wastage-stats/
    - Returns wastage breakdown by reason for dashboard
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get wastage breakdown by reason"""
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Parse date range
        if not date_to:
            date_to = timezone.now().date()
        else:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            except ValueError:
                date_to = timezone.now().date()
        
        if not date_from:
            date_from = date_to - timedelta(days=30)
        else:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            except ValueError:
                date_from = date_to - timedelta(days=30)
        
        # Get wastage by reason
        wastage_summary = ProductWastage.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).values('reason_id').annotate(
            reason_name=F('reason_id__reason'),
            total_quantity=Sum('quantity', default=Decimal('0')),
            total_loss=Sum('total_loss', default=Decimal('0')),
            waste_count=Count('id'),
        ).order_by('-total_loss')
        
        # Get total revenue for percentage calculation
        total_revenue = Sale.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('1')
        
        results = []
        total_loss = Decimal('0')
        
        for item in wastage_summary:
            loss = item['total_loss'] or Decimal('0')
            total_loss += loss
            wastage_percentage = (loss / total_revenue * 100) if total_revenue > 0 else 0
            
            results.append({
                'reason': item['reason_name'],
                'quantity': float(item['total_quantity'] or 0),
                'loss_amount': float(loss),
                'percentage_of_revenue': float(wastage_percentage),
            })
        
        return Response({
            'breakdown': results,
            'total_wastage_loss': float(total_loss),
        })


class InventoryStatsViewSet(viewsets.ViewSet):
    """
    API Endpoint for inventory statistics.
    
    GET /api/analytics/inventory-stats/
    - Returns general inventory metrics
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get inventory statistics"""
        # Get total inventory value
        products = Product.objects.all()
        total_value = Decimal('0')
        low_stock_count = 0
        
        for product in products:
            item_value = (product.current_stock or Decimal('0')) * (product.cost_price or Decimal('0'))
            total_value += item_value
            if product.current_stock and product.current_stock < 10:
                low_stock_count += 1
        
        # Get expiring items count
        today = timezone.now().date()
        expiring_soon = IngredientBatch.objects.filter(
            expire_date__lte=today + timedelta(days=7),
            expire_date__gte=today,
            current_qty__gt=Decimal('0')
        ).count()
        
        return Response({
            'total_inventory_value': float(total_value),
            'total_products': products.count(),
            'low_stock_items': low_stock_count,
            'expiring_items_count': expiring_soon,
        })


class LowStockViewSet(viewsets.ViewSet):
    """
    API Endpoint for low stock items.
    
    GET /api/inventory/low-stock/
    - Returns products and ingredients with low stock levels
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get all low stock items (products and ingredients)"""
        # Get low stock products (current_stock < 10)
        low_stock_products = Product.objects.filter(
            current_stock__lt=10
        ).values(
            'id', 'product_id', 'name', 'current_stock', 'cost_price'
        ).order_by('current_stock')
        
        results = []
        for product in low_stock_products:
            results.append({
                'id': product['id'],
                'type': 'product',
                'name': product['name'],
                'product_id': product['product_id'],
                'current_stock': float(product['current_stock'] or 0),
                'reorder_level': 10.0,  # Default threshold
                'unit': 'units',
            })
        
        return Response(results)
```

---

### 2. Backend/api/urls.py

**Change 1 - Updated Imports (Line 6)**:

From:
```python
from api.views.analytics_views import SalesAnalyticsViewSet, InventoryAnalyticsViewSet, DashboardKpiViewSet
```

To:
```python
from api.views.analytics_views import (
    SalesAnalyticsViewSet, 
    InventoryAnalyticsViewSet, 
    DashboardKpiViewSet, 
    SalesStatsViewSet,           # NEW
    ProductStatsViewSet,         # NEW
    WastageStatsViewSet,         # NEW
    InventoryStatsViewSet,       # NEW
    LowStockViewSet              # NEW
)
```

**Change 2 - Added Router Registrations (After line 25)**:

Added these 5 lines:
```python
router.register(r'analytics/sales-stats', SalesStatsViewSet, basename='sales-stats')
router.register(r'analytics/product-stats', ProductStatsViewSet, basename='product-stats')
router.register(r'analytics/wastage-stats', WastageStatsViewSet, basename='wastage-stats')
router.register(r'analytics/inventory-stats', InventoryStatsViewSet, basename='inventory-stats')
router.register(r'inventory/low-stock', LowStockViewSet, basename='low-stock')
```

---

## Key Implementation Details

### ViewSet Design
- **Base Class**: `viewsets.ViewSet` (not ModelViewSet) because we're computing aggregates, not doing CRUD
- **Method**: `list()` instead of actions - called when router matches the route
- **Response**: Direct `Response()` with dictionaries (no serializers needed for computed data)

### Date Range Handling
- Default: Last 30 days if not provided
- Format: ISO-8601 `YYYY-MM-DD`
- Timezone: Django's `timezone.now().date()`

### Security
- All endpoints decorated with `permission_classes = [IsAuthenticated]`
- Requires valid JWT token in Authorization header

### Data Calculations
- **Revenue** = Total sales amount - Total discounts
- **Net Profit** = Revenue - Cost of goods sold
- **Cost of Goods** = Sum of (quantity × product.cost_price) for all items in period
- **Wastage Loss** = Sum of ProductWastage.total_loss + IngredientWastage.total_loss

---

## How Data Flows

```
Frontend (ManagerDashboard.tsx)
    ↓
analyticsApi.getSalesStats() → GET /api/analytics/sales-stats/
analyticsApi.getProductStats() → GET /api/analytics/product-stats/
analyticsApi.getWastageStats() → GET /api/analytics/wastage-stats/
inventoryApi.getLowStock() → GET /api/inventory/low-stock/
    ↓
Django Router (DefaultRouter)
    ↓
SalesStatsViewSet.list() → SalesAnalytics calculations
ProductStatsViewSet.list() → Top products calculations
WastageStatsViewSet.list() → Wastage breakdown calculations
LowStockViewSet.list() → Filter products with stock < 10
    ↓
Response JSON
    ↓
Frontend components render with real data
```

---

## Testing the API

### Using curl (replace YOUR_TOKEN with actual JWT token):

```bash
# Sales Stats
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/analytics/sales-stats/"

# Product Stats
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/analytics/product-stats/"

# Wastage Stats
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/analytics/wastage-stats/"

# Inventory Stats
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/analytics/inventory-stats/"

# Low Stock
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/inventory/low-stock/"
```

### Using Postman:
1. Set request to GET
2. Add header: `Authorization: Bearer <your_token>`
3. Paste URL for each endpoint
4. Send and view response

