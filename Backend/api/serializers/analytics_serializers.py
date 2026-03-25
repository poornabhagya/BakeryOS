"""
Serializers for Analytics endpoints.

Used for aggregating and presenting analytics data across
products, sales, inventory, and wastage.
"""

from rest_framework import serializers
from decimal import Decimal


class DailySalesAnalyticsSerializer(serializers.Serializer):
    """Serialize daily sales aggregates"""
    
    period = serializers.DateField(help_text="Date (YYYY-MM-DD)")
    total_sales = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Sum of all sale amounts for the day"
    )
    total_discount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Sum of all discounts applied"
    )
    revenue = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Revenue after discounts (total_sales - total_discount)"
    )
    transaction_count = serializers.IntegerField(
        help_text="Number of sales/transactions"
    )
    items_sold = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Total quantity of items sold"
    )
    cost_of_goods = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        help_text="Total cost to bakery"
    )
    profit = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        help_text="Revenue - Cost of goods"
    )
    profit_margin = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        help_text="Profit as percentage of revenue"
    )


class WeeklySalesAnalyticsSerializer(DailySalesAnalyticsSerializer):
    """Serialize weekly sales aggregates"""
    
    period = serializers.CharField(
        help_text="Week range (YYYY-MM-DD to YYYY-MM-DD)"
    )


class MonthlySalesAnalyticsSerializer(DailySalesAnalyticsSerializer):
    """Serialize monthly sales aggregates"""
    
    period = serializers.CharField(
        help_text="Month (YYYY-MM)"
    )


class TopProductSerializer(serializers.Serializer):
    """Serialize top-selling products"""
    
    product_id = serializers.IntegerField()
    product_name = serializers.CharField(max_length=200)
    quantity_sold = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Total quantity sold"
    )
    total_revenue = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Revenue from this product"
    )
    transaction_count = serializers.IntegerField(
        help_text="Number of transactions (sales) involving this product"
    )
    average_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Average selling price per unit"
    )
    rank = serializers.IntegerField(help_text="Rank among top products")


class SalesByCategorySerializer(serializers.Serializer):
    """Serialize sales by product category"""
    
    category_id = serializers.IntegerField()
    category_name = serializers.CharField(max_length=200)
    total_sales = serializers.DecimalField(
        max_digits=15,
        decimal_places=2
    )
    product_count = serializers.IntegerField(
        help_text="Number of products in category"
    )
    items_sold = serializers.DecimalField(
        max_digits=15,
        decimal_places=2
    )
    transaction_count = serializers.IntegerField()
    percentage_of_total = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Percentage of total sales"
    )


class SalesByCashierSerializer(serializers.Serializer):
    """Serialize sales by cashier"""
    
    cashier_id = serializers.IntegerField()
    cashier_name = serializers.CharField(max_length=200)
    total_sales = serializers.DecimalField(
        max_digits=15,
        decimal_places=2
    )
    transaction_count = serializers.IntegerField()
    items_sold = serializers.DecimalField(
        max_digits=15,
        decimal_places=2
    )
    average_transaction_value = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Average sale amount"
    )


class RevenueAnalysisSerializer(serializers.Serializer):
    """Serialize revenue vs cost analysis"""
    
    period = serializers.CharField()
    total_revenue = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Revenue after all discounts"
    )
    total_cost_of_goods = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Total cost to bakery for all items sold"
    )
    total_profit = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Revenue - Cost of goods"
    )
    profit_margin = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Profit as percentage of revenue"
    )
    total_discount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2
    )
    avg_discount_per_transaction = serializers.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    transaction_count = serializers.IntegerField()


class InventoryValueSerializer(serializers.Serializer):
    """Serialize total inventory value"""
    
    total_product_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Sum of (current_stock * cost_price) for all products"
    )
    total_ingredient_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Sum of ingredient costs"
    )
    total_inventory_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Combined value of all inventory"
    )
    product_count = serializers.IntegerField()
    ingredient_count = serializers.IntegerField()
    currency = serializers.CharField(default="INR")


class StockTurnoverSerializer(serializers.Serializer):
    """Serialize stock turnover rate"""
    
    product_id = serializers.IntegerField()
    product_name = serializers.CharField(max_length=200)
    current_stock = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Current stock quantity"
    )
    quantity_sold = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Quantity sold in period"
    )
    turnover_rate = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Turnover rate in period"
    )
    annualized_turnover = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Annualized turnover rate"
    )
    days_to_turnover = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Days to turnover at annualized rate"
    )


class WastageAnalysisSerializer(serializers.Serializer):
    """Serialize wastage analysis"""
    
    total_wastage_loss = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Total monetary value of wastage"
    )
    wastage_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Wastage as % of revenue (wastage_loss / revenue * 100)"
    )
    by_reason = serializers.ListField(
        child=serializers.DictField(),
        help_text="Breakdown by wastage reason"
    )
    period = serializers.CharField()


class IngredientUsageSerializer(serializers.Serializer):
    """Serialize ingredient usage rates"""
    
    ingredient_id = serializers.IntegerField()
    ingredient_name = serializers.CharField(max_length=200)
    total_used = serializers.DecimalField(
        max_digits=15,
        decimal_places=2
    )
    total_purchased = serializers.DecimalField(
        max_digits=15,
        decimal_places=2
    )
    usage_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Percentage of purchases actually used"
    )
    current_stock = serializers.DecimalField(
        max_digits=15,
        decimal_places=2
    )


class StockValueSerializer(serializers.Serializer):
    """Serialize stock value calculation"""
    
    total_stock_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Sum of (current_stock * cost_price) for all products"
    )
    items = serializers.ListField(
        child=serializers.DictField(),
        help_text="Breakdown by product"
    )
    item_count = serializers.IntegerField(
        help_text="Number of products"
    )


class WastageTrendSerializer(serializers.Serializer):
    """Serialize wastage trend data"""
    
    period = serializers.CharField()
    trend_type = serializers.CharField(help_text="daily, weekly, or monthly")
    trends = serializers.ListField(
        child=serializers.DictField(),
        help_text="Trend data grouped by period"
    )


class IngredientStockItemSerializer(serializers.Serializer):
    """Serialize individual ingredient stock item"""
    
    ingredient_id = serializers.IntegerField()
    ingredient_name = serializers.CharField(max_length=200)
    total_purchased = serializers.DecimalField(
        max_digits=15,
        decimal_places=2
    )
    total_used = serializers.DecimalField(
        max_digits=15,
        decimal_places=2
    )
    usage_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    current_stock = serializers.DecimalField(
        max_digits=15,
        decimal_places=2
    )
    period = serializers.CharField()


class RevenuePeriodSerializer(serializers.Serializer):
    """Serialize revenue metrics for different periods"""
    today = serializers.DecimalField(max_digits=15, decimal_places=2)
    this_week = serializers.DecimalField(max_digits=15, decimal_places=2)
    this_month = serializers.DecimalField(max_digits=15, decimal_places=2)


class TransactionPeriodSerializer(serializers.Serializer):
    """Serialize transaction counts for different periods"""
    today = serializers.IntegerField()
    this_week = serializers.IntegerField()
    this_month = serializers.IntegerField()


class DashboardKpiSerializer(serializers.Serializer):
    """Serialize dashboard KPI metrics"""
    
    timestamp = serializers.DateTimeField()
    total_users = serializers.IntegerField(help_text="Total user count")
    active_users = serializers.IntegerField(help_text="Active (non-deleted) user count")
    revenue = RevenuePeriodSerializer(help_text="Revenue metrics")
    transactions = TransactionPeriodSerializer(help_text="Transaction counts")
    active_discounts_count = serializers.IntegerField(help_text="Count of active discounts")
    low_stock_items_count = serializers.IntegerField(help_text="Count of products with stock < 10")
    expiring_items_count = serializers.IntegerField(help_text="Count of items expiring within 2 days")
    high_wastage_alerts_count = serializers.IntegerField(help_text="Count of high wastage alerts")
