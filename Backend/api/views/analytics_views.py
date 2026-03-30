"""
ViewSets for Sales Analytics endpoints.

Provides aggregated sales data across multiple dimensions:
- Daily/Weekly/Monthly totals
- Top-selling products
- Sales by category and cashier
- Revenue vs cost analysis
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from api.models import (
    Sale, SaleItem, Product, Category, User, ProductWastage,
    Ingredient, IngredientBatch, IngredientWastage, WastageReason,
    Discount, Notification
)
from api.serializers.analytics_serializers import (
    DailySalesAnalyticsSerializer,
    WeeklySalesAnalyticsSerializer,
    MonthlySalesAnalyticsSerializer,
    TopProductSerializer,
    SalesByCategorySerializer,
    SalesByCashierSerializer,
    RevenueAnalysisSerializer,
    StockValueSerializer,
    StockTurnoverSerializer,
    WastageAnalysisSerializer,
    WastageTrendSerializer,
    IngredientUsageSerializer,
)


class SalesAnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for sales analytics endpoints.
    
    Provides aggregated sales data across different time periods
    and dimensions.
    
    Endpoints:
    - daily: Daily sales totals
    - weekly: Weekly sales aggregates
    - monthly: Monthly sales aggregates
    - top_products: Top-selling products
    - by_category: Sales by product category
    - by_cashier: Sales by cashier
    - revenue: Revenue vs cost analysis
    """
    
    permission_classes = [IsAuthenticated]
    
    def _parse_date_params(self, request):
        """Extract and validate date range from request params"""
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Default: last 30 days
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
        
        return date_from, date_to
    
    @action(detail=False, methods=['get'])
    def daily(self, request):
        """Get daily sales totals"""
        date_from, date_to = self._parse_date_params(request)
        
        sales = Sale.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).annotate(
            date=TruncDate('created_at')
        )
        
        # Aggregate by date
        daily_data = sales.values('date').annotate(
            total_sales=Sum('total_amount'),
            total_discount=Sum('discount_amount', default=Decimal('0')),
            transaction_count=Count('id'),
            items_sold=Sum('items__quantity', default=Decimal('0')),
        ).order_by('date')
        
        results = []
        for item in daily_data:
            revenue = Decimal(str(item['total_sales'] or 0))
            
            # Calculate cost of goods for this day
            cost_of_goods = Decimal('0')
            daily_sales = Sale.objects.filter(
                created_at__date=item['date']
            ).prefetch_related('items')
            
            for sale in daily_sales:
                for sale_item in sale.items.all():
                    # Handle deleted products (product_id_id is None in DB)
                    if sale_item.product_id_id:
                        product = sale_item.product_id
                        cost_of_goods += (sale_item.quantity * product.cost_price)
            
            profit = revenue - cost_of_goods
            profit_margin = (profit / revenue * 100) if revenue > 0 else Decimal('0')
            
            results.append({
                'period': item['date'],
                'total_sales': item['total_sales'] or Decimal('0'),
                'total_discount': item['total_discount'] or Decimal('0'),
                'revenue': revenue,
                'transaction_count': item['transaction_count'],
                'items_sold': item['items_sold'] or Decimal('0'),
                'cost_of_goods': cost_of_goods,
                'profit': profit,
                'profit_margin': profit_margin,
            })
        
        serializer = DailySalesAnalyticsSerializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def weekly(self, request):
        """Get weekly sales totals"""
        date_from, date_to = self._parse_date_params(request)
        
        sales = Sale.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        )
        
        # Group by week
        weekly_data = sales.annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            total_sales=Sum('total_amount'),
            total_discount=Sum('discount_amount', default=Decimal('0')),
            transaction_count=Count('id'),
            items_sold=Sum('items__quantity', default=Decimal('0')),
        ).order_by('week')
        
        results = []
        for item in weekly_data:
            if item['week']:
                revenue = Decimal(str(item['total_sales'] or 0))
                week_start = item['week']
                week_end = week_start + timedelta(days=6)
                period = f"{week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
                
                # Calculate cost of goods
                cost_of_goods = Decimal('0')
                week_sales = Sale.objects.filter(
                    created_at__date__gte=week_start,
                    created_at__date__lte=week_end
                ).prefetch_related('items')
                
                for sale in week_sales:
                    for sale_item in sale.items.all():
                        # Handle deleted products (product_id_id is None in DB)
                        if sale_item.product_id_id:
                            product = sale_item.product_id
                            cost_of_goods += (sale_item.quantity * product.cost_price)
                
                profit = revenue - cost_of_goods
                profit_margin = (profit / revenue * 100) if revenue > 0 else Decimal('0')
                
                results.append({
                    'period': period,
                    'total_sales': item['total_sales'] or Decimal('0'),
                    'total_discount': item['total_discount'] or Decimal('0'),
                    'revenue': revenue,
                    'transaction_count': item['transaction_count'],
                    'items_sold': item['items_sold'] or Decimal('0'),
                    'cost_of_goods': cost_of_goods,
                    'profit': profit,
                    'profit_margin': profit_margin,
                })
        
        serializer = WeeklySalesAnalyticsSerializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def monthly(self, request):
        """Get monthly sales totals"""
        date_from, date_to = self._parse_date_params(request)
        
        sales = Sale.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        )
        
        # Group by month
        monthly_data = sales.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total_sales=Sum('total_amount'),
            total_discount=Sum('discount_amount', default=Decimal('0')),
            transaction_count=Count('id'),
            items_sold=Sum('items__quantity', default=Decimal('0')),
        ).order_by('month')
        
        results = []
        for item in monthly_data:
            if item['month']:
                revenue = Decimal(str(item['total_sales'] or 0))
                period = item['month'].strftime('%Y-%m')
                
                # Calculate cost of goods
                cost_of_goods = Decimal('0')
                month_sales = Sale.objects.filter(
                    created_at__year=item['month'].year,
                    created_at__month=item['month'].month
                ).prefetch_related('items')
                
                for sale in month_sales:
                    for sale_item in sale.items.all():
                        # Handle deleted products (product_id_id is None in DB)
                        if sale_item.product_id_id:
                            product = sale_item.product_id
                            cost_of_goods += (sale_item.quantity * product.cost_price)
                
                profit = revenue - cost_of_goods
                profit_margin = (profit / revenue * 100) if revenue > 0 else Decimal('0')
                
                results.append({
                    'period': period,
                    'total_sales': item['total_sales'] or Decimal('0'),
                    'total_discount': item['total_discount'] or Decimal('0'),
                    'revenue': revenue,
                    'transaction_count': item['transaction_count'],
                    'items_sold': item['items_sold'] or Decimal('0'),
                    'cost_of_goods': cost_of_goods,
                    'profit': profit,
                    'profit_margin': profit_margin,
                })
        
        serializer = MonthlySalesAnalyticsSerializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_products(self, request):
        """Get top-selling products"""
        date_from, date_to = self._parse_date_params(request)
        limit = int(request.query_params.get('limit', 10))
        
        top_products = SaleItem.objects.filter(
            sale_id__created_at__date__gte=date_from,
            sale_id__created_at__date__lte=date_to
        ).values('product_id').annotate(
            product_name=F('product_id__name'),
            quantity_sold=Sum('quantity'),
            total_revenue=Sum('subtotal'),
            transaction_count=Count('sale_id', distinct=True),
            average_price=Avg('unit_price'),
        ).order_by('-total_revenue')[:limit]
        
        results = []
        for idx, item in enumerate(top_products, 1):
            results.append({
                'product_id': item['product_id'],
                'product_name': item['product_name'],
                'quantity_sold': item['quantity_sold'],
                'total_revenue': item['total_revenue'],
                'transaction_count': item['transaction_count'],
                'average_price': item['average_price'],
                'rank': idx,
            })
        
        serializer = TopProductSerializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get sales by product category"""
        date_from, date_to = self._parse_date_params(request)
        
        category_sales = SaleItem.objects.filter(
            sale_id__created_at__date__gte=date_from,
            sale_id__created_at__date__lte=date_to
        ).values('product_id__category_id').annotate(
            category_name=F('product_id__category_id__name'),
            total_sales=Sum('subtotal'),
            product_count=Count('product_id', distinct=True),
            items_sold=Sum('quantity'),
            transaction_count=Count('sale_id', distinct=True),
        ).order_by('-total_sales')
        
        # Calculate total sales for percentage
        total_revenue = sum(item['total_sales'] for item in category_sales)
        
        results = []
        for item in category_sales:
            percentage = (item['total_sales'] / total_revenue * 100) if total_revenue > 0 else Decimal('0')
            results.append({
                'category_id': item['product_id__category_id'],
                'category_name': item['category_name'],
                'total_sales': item['total_sales'],
                'product_count': item['product_count'],
                'items_sold': item['items_sold'],
                'transaction_count': item['transaction_count'],
                'percentage_of_total': percentage,
            })
        
        serializer = SalesByCategorySerializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_cashier(self, request):
        """Get sales by cashier"""
        date_from, date_to = self._parse_date_params(request)
        
        cashier_sales = Sale.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).values('cashier_id').annotate(
            cashier_name=F('cashier_id__full_name'),
            total_sales=Sum('total_amount'),
            transaction_count=Count('id'),
            items_sold=Sum('items__quantity', default=Decimal('0')),
        ).order_by('-total_sales')
        
        results = []
        for item in cashier_sales:
            avg_transaction = (item['total_sales'] / item['transaction_count']) if item['transaction_count'] > 0 else Decimal('0')
            results.append({
                'cashier_id': item['cashier_id'],
                'cashier_name': item['cashier_name'],
                'total_sales': item['total_sales'],
                'transaction_count': item['transaction_count'],
                'items_sold': item['items_sold'],
                'average_transaction_value': avg_transaction,
            })
        
        serializer = SalesByCashierSerializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def revenue(self, request):
        """Get revenue vs cost analysis"""
        date_from, date_to = self._parse_date_params(request)
        
        sales = Sale.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        )
        
        total_sales_amount = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
        total_discount = sales.aggregate(Sum('discount_amount', default=Decimal('0')))['discount_amount__sum'] or Decimal('0')
        transaction_count = sales.count()
        
        # Calculate cost of goods
        cost_of_goods = Decimal('0')
        for sale in sales.prefetch_related('items'):
            for item in sale.items.all():
                # Handle deleted products (product_id_id is None in DB)
                if item.product_id_id:
                    product = item.product_id
                    cost_of_goods += (item.quantity * product.cost_price)
        
        revenue = total_sales_amount - total_discount
        profit = revenue - cost_of_goods
        profit_margin = (profit / revenue * 100) if revenue > 0 else Decimal('0')
        avg_discount = total_discount / transaction_count if transaction_count > 0 else Decimal('0')
        
        result = {
            'period': f"{date_from.strftime('%Y-%m-%d')} to {date_to.strftime('%Y-%m-%d')}",
            'total_revenue': revenue,
            'total_cost_of_goods': cost_of_goods,
            'total_profit': profit,
            'profit_margin': profit_margin,
            'total_discount': total_discount,
            'avg_discount_per_transaction': avg_discount,
            'transaction_count': transaction_count,
        }
        
        serializer = RevenueAnalysisSerializer(result)
        return Response(serializer.data)


class InventoryAnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for inventory analytics endpoints.
    
    Provides aggregated inventory data including:
    - Stock value analysis
    - Product turnover rates
    - Expired items tracking
    - Wastage analysis and trends
    - Ingredient usage rates
    
    Endpoints:
    - stock_value: Total inventory value
    - turnover: Stock turnover rates per product
    - expired: Value and quantity of expired items
    - wastage_summary: Wastage breakdown by reason
    - wastage_trend: Wastage trends over time
    - ingredient_usage: Ingredient usage rates
    """
    
    permission_classes = [IsAuthenticated]
    
    def _parse_date_params(self, request):
        """Extract and validate date range from request params"""
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Default: last 30 days
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
        
        return date_from, date_to
    
    @action(detail=False, methods=['get'])
    def stock_value(self, request):
        """Calculate total inventory value at cost price"""
        products = Product.objects.all()
        
        total_value = Decimal('0')
        stock_items = []
        
        for product in products:
            item_value = (product.current_stock or Decimal('0')) * (product.cost_price or Decimal('0'))
            total_value += item_value
            
            stock_items.append({
                'product_id': product.id,
                'product_name': product.name,
                'quantity': product.current_stock or Decimal('0'),
                'cost_price': product.cost_price or Decimal('0'),
                'item_value': item_value,
            })
        
        result = {
            'total_stock_value': total_value,
            'items': stock_items,
            'item_count': len(stock_items),
        }
        
        serializer = StockValueSerializer(result)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def turnover(self, request):
        """Calculate stock turnover rate per product"""
        date_from, date_to = self._parse_date_params(request)
        
        products = Product.objects.all()
        results = []
        
        for product in products:
            # Get quantity sold in period
            items_sold = SaleItem.objects.filter(
                product_id=product.id,
                sale_id__created_at__date__gte=date_from,
                sale_id__created_at__date__lte=date_to
            ).aggregate(total=Sum('quantity', default=Decimal('0')))['total'] or Decimal('0')
            
            # Calculate average inventory (simplified: use current as estimate)
            avg_inventory = product.current_stock or Decimal('1')
            
            # Turnover rate = quantity sold / avg inventory
            turnover_rate = (items_sold / avg_inventory) if avg_inventory > 0 else Decimal('0')
            
            # Days to turnover = 365 / turnover rate (annualized)
            days_count = (date_to - date_from).days
            if days_count == 0:
                days_count = 1
            
            annualized_turnover = (turnover_rate / days_count) * 365 if days_count > 0 else Decimal('0')
            days_to_turnover = (365 / annualized_turnover) if annualized_turnover > 0 else Decimal('0')
            
            results.append({
                'product_id': product.id,
                'product_name': product.name,
                'current_stock': product.current_stock or Decimal('0'),
                'quantity_sold': items_sold,
                'turnover_rate': turnover_rate,
                'annualized_turnover': annualized_turnover,
                'days_to_turnover': days_to_turnover,
            })
        
        serializer = StockTurnoverSerializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get expired ingredients and their value"""
        today = timezone.now().date()
        
        # Get all expired batches
        expired_batches = IngredientBatch.objects.filter(
            expire_date__lt=today,
            current_qty__gt=Decimal('0')
        )
        
        total_expired_value = Decimal('0')
        expired_items = []
        
        for batch in expired_batches:
            cost_price = batch.cost_price or Decimal('0')
            item_value = (batch.current_qty or Decimal('0')) * cost_price
            total_expired_value += item_value
            
            # Convert expire_date to date if it's a datetime object
            expire_date = batch.expire_date.date() if hasattr(batch.expire_date, 'date') else batch.expire_date
            
            expired_items.append({
                'batch_id': batch.id,
                'ingredient_id': batch.ingredient_id.id,
                'ingredient_name': batch.ingredient_id.name,
                'quantity': batch.current_qty or Decimal('0'),
                'expire_date': expire_date,
                'cost_price': cost_price,
                'expired_value': item_value,
                'days_expired': (today - expire_date).days,
            })
        
        result = {
            'total_stock_value': total_expired_value,
            'item_count': len(expired_items),
            'items': expired_items,
        }
        
        serializer = StockValueSerializer(result)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def wastage_summary(self, request):
        """Get wastage breakdown by reason"""
        date_from, date_to = self._parse_date_params(request)
        
        # Product wastage summary
        product_wastage = ProductWastage.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).values('reason_id').annotate(
            reason_name=F('reason_id__reason'),
            total_quantity=Sum('quantity', default=Decimal('0')),
            total_loss=Sum('total_loss', default=Decimal('0')),
            waste_count=Count('id'),
        )
        
        # Ingredient wastage summary
        ingredient_wastage = IngredientWastage.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).aggregate(
            total_quantity=Sum('quantity', default=Decimal('0')),
            total_loss=Sum('total_loss', default=Decimal('0')),
            waste_count=Count('id'),
        )
        
        # Total revenue for percentage calculation
        total_revenue = Sale.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('1')
        
        results = []
        total_product_loss = Decimal('0')
        
        for item in product_wastage:
            loss = item['total_loss'] or Decimal('0')
            total_product_loss += loss
            wastage_percentage = (loss / total_revenue * 100) if total_revenue > 0 else Decimal('0')
            
            results.append({
                'reason_name': item['reason_name'],
                'quantity': item['total_quantity'] or Decimal('0'),
                'total_loss': loss,
                'waste_count': item['waste_count'],
                'percentage_of_revenue': wastage_percentage,
                'type': 'product',
            })
        
        # Add ingredient wastage as aggregate
        if ingredient_wastage['waste_count'] > 0:
            loss = ingredient_wastage['total_loss'] or Decimal('0')
            wastage_percentage = (loss / total_revenue * 100) if total_revenue > 0 else Decimal('0')
            
            results.append({
                'reason_name': 'ingredients',
                'quantity': ingredient_wastage['total_quantity'] or Decimal('0'),
                'total_loss': loss,
                'waste_count': ingredient_wastage['waste_count'],
                'percentage_of_revenue': wastage_percentage,
                'type': 'ingredient',
            })
        
        result = {
            'period': f"{date_from.strftime('%Y-%m-%d')} to {date_to.strftime('%Y-%m-%d')}",
            'total_wastage_loss': total_product_loss + (ingredient_wastage['total_loss'] or Decimal('0')),
            'total_wastage_percentage': ((total_product_loss + (ingredient_wastage['total_loss'] or Decimal('0'))) / total_revenue * 100) if total_revenue > 0 else Decimal('0'),
            'wastage_by_reason': results,
        }
        
        serializer = WastageAnalysisSerializer(result)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def wastage_trend(self, request):
        """Get wastage trends over time (daily/weekly/monthly)"""
        date_from, date_to = self._parse_date_params(request)
        trend_type = request.query_params.get('trend_type', 'daily')  # daily, weekly, monthly
        
        # Product wastage trend
        product_wastage = ProductWastage.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        )
        
        # Ingredient wastage trend
        ingredient_wastage = IngredientWastage.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        )
        
        results = []
        
        if trend_type == 'daily':
            # Group by date
            product_by_date = product_wastage.annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(
                total_loss=Sum('total_loss', default=Decimal('0')),
                quantity=Sum('quantity', default=Decimal('0')),
                waste_count=Count('id'),
            ).order_by('date')
            
            ingredient_by_date = ingredient_wastage.annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(
                total_loss=Sum('total_loss', default=Decimal('0')),
                quantity=Sum('quantity', default=Decimal('0')),
                waste_count=Count('id'),
            ).order_by('date')
            
            # Merge results by date
            date_dict = {}
            for item in product_by_date:
                date_dict[item['date']] = {
                    'period': item['date'].strftime('%Y-%m-%d'),
                    'product_loss': item['total_loss'] or Decimal('0'),
                    'product_quantity': item['quantity'] or Decimal('0'),
                    'ingredient_loss': Decimal('0'),
                    'ingredient_quantity': Decimal('0'),
                }
            
            for item in ingredient_by_date:
                if item['date'] in date_dict:
                    date_dict[item['date']]['ingredient_loss'] = item['total_loss'] or Decimal('0')
                    date_dict[item['date']]['ingredient_quantity'] = item['quantity'] or Decimal('0')
                else:
                    date_dict[item['date']] = {
                        'period': item['date'].strftime('%Y-%m-%d'),
                        'product_loss': Decimal('0'),
                        'product_quantity': Decimal('0'),
                        'ingredient_loss': item['total_loss'] or Decimal('0'),
                        'ingredient_quantity': item['quantity'] or Decimal('0'),
                    }
            
            for date_key in sorted(date_dict.keys()):
                data = date_dict[date_key]
                results.append({
                    'period': data['period'],
                    'total_loss': data['product_loss'] + data['ingredient_loss'],
                    'product_loss': data['product_loss'],
                    'ingredient_loss': data['ingredient_loss'],
                    'total_quantity': data['product_quantity'] + data['ingredient_quantity'],
                })
        
        elif trend_type == 'weekly':
            # Group by week
            product_by_week = product_wastage.annotate(
                week=TruncWeek('created_at')
            ).values('week').annotate(
                total_loss=Sum('total_loss', default=Decimal('0')),
                quantity=Sum('quantity', default=Decimal('0')),
            ).order_by('week')
            
            ingredient_by_week = ingredient_wastage.annotate(
                week=TruncWeek('created_at')
            ).values('week').annotate(
                total_loss=Sum('total_loss', default=Decimal('0')),
                quantity=Sum('quantity', default=Decimal('0')),
            ).order_by('week')
            
            # Merge results by week
            week_dict = {}
            for item in product_by_week:
                if item['week']:
                    week_end = item['week'] + timedelta(days=6)
                    period = f"{item['week'].strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
                    week_dict[item['week']] = {
                        'period': period,
                        'product_loss': item['total_loss'] or Decimal('0'),
                        'product_quantity': item['quantity'] or Decimal('0'),
                        'ingredient_loss': Decimal('0'),
                        'ingredient_quantity': Decimal('0'),
                    }
            
            for item in ingredient_by_week:
                if item['week']:
                    if item['week'] in week_dict:
                        week_dict[item['week']]['ingredient_loss'] = item['total_loss'] or Decimal('0')
                        week_dict[item['week']]['ingredient_quantity'] = item['quantity'] or Decimal('0')
                    else:
                        week_end = item['week'] + timedelta(days=6)
                        period = f"{item['week'].strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
                        week_dict[item['week']] = {
                            'period': period,
                            'product_loss': Decimal('0'),
                            'product_quantity': Decimal('0'),
                            'ingredient_loss': item['total_loss'] or Decimal('0'),
                            'ingredient_quantity': item['quantity'] or Decimal('0'),
                        }
            
            for week_key in sorted(week_dict.keys()):
                data = week_dict[week_key]
                results.append({
                    'period': data['period'],
                    'total_loss': data['product_loss'] + data['ingredient_loss'],
                    'product_loss': data['product_loss'],
                    'ingredient_loss': data['ingredient_loss'],
                    'total_quantity': data['product_quantity'] + data['ingredient_quantity'],
                })
        
        else:  # monthly
            # Group by month
            product_by_month = product_wastage.annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                total_loss=Sum('total_loss', default=Decimal('0')),
                quantity=Sum('quantity', default=Decimal('0')),
            ).order_by('month')
            
            ingredient_by_month = ingredient_wastage.annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                total_loss=Sum('total_loss', default=Decimal('0')),
                quantity=Sum('quantity', default=Decimal('0')),
            ).order_by('month')
            
            # Merge results by month
            month_dict = {}
            for item in product_by_month:
                if item['month']:
                    period = item['month'].strftime('%Y-%m')
                    month_dict[item['month']] = {
                        'period': period,
                        'product_loss': item['total_loss'] or Decimal('0'),
                        'product_quantity': item['quantity'] or Decimal('0'),
                        'ingredient_loss': Decimal('0'),
                        'ingredient_quantity': Decimal('0'),
                    }
            
            for item in ingredient_by_month:
                if item['month']:
                    if item['month'] in month_dict:
                        month_dict[item['month']]['ingredient_loss'] = item['total_loss'] or Decimal('0')
                        month_dict[item['month']]['ingredient_quantity'] = item['quantity'] or Decimal('0')
                    else:
                        period = item['month'].strftime('%Y-%m')
                        month_dict[item['month']] = {
                            'period': period,
                            'product_loss': Decimal('0'),
                            'product_quantity': Decimal('0'),
                            'ingredient_loss': item['total_loss'] or Decimal('0'),
                            'ingredient_quantity': item['quantity'] or Decimal('0'),
                        }
            
            for month_key in sorted(month_dict.keys()):
                data = month_dict[month_key]
                results.append({
                    'period': data['period'],
                    'total_loss': data['product_loss'] + data['ingredient_loss'],
                    'product_loss': data['product_loss'],
                    'ingredient_loss': data['ingredient_loss'],
                    'total_quantity': data['product_quantity'] + data['ingredient_quantity'],
                })
        
        result = {
            'period': f"{date_from.strftime('%Y-%m-%d')} to {date_to.strftime('%Y-%m-%d')}",
            'trend_type': trend_type,
            'trends': results,
        }
        
        serializer = WastageTrendSerializer(result)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def ingredient_usage(self, request):
        """Get ingredient usage rates"""
        date_from, date_to = self._parse_date_params(request)
        
        ingredients = Ingredient.objects.all()
        results = []
        
        for ingredient in ingredients:
            # Total purchased in period
            purchased = IngredientBatch.objects.filter(
                ingredient_id=ingredient.id,
                created_at__date__gte=date_from,
                created_at__date__lte=date_to
            ).aggregate(total=Sum('quantity', default=Decimal('0')))['total'] or Decimal('0')
            
            # Total used in production (current_qty decrease from initial)
            total_batches = IngredientBatch.objects.filter(
                ingredient_id=ingredient.id,
                created_at__date__gte=date_from,
                created_at__date__lte=date_to
            )
            
            used = Decimal('0')
            for batch in total_batches:
                used += (batch.quantity - (batch.current_qty or Decimal('0')))
            
            # Usage rate
            usage_rate = (used / purchased * 100) if purchased > 0 else Decimal('0')
            
            # Current stock
            current_stock = ingredient.total_quantity or Decimal('0')
            
            results.append({
                'ingredient_id': ingredient.id,
                'ingredient_name': ingredient.name,
                'total_purchased': purchased,
                'total_used': used,
                'usage_rate': usage_rate,
                'current_stock': current_stock,
            })
        
        serializer = IngredientUsageSerializer(results, many=True)
        return Response(serializer.data)


class DashboardKpiViewSet(viewsets.ViewSet):
    """
    ViewSet for KPI Dashboard data.
    
    Provides real-time KPI metrics for the dashboard including:
    - User counts
    - Revenue metrics (today, week, month)
    - Transaction counts
    - Inventory alerts (low stock, expiring)
    - Discount information
    - Wastage alerts
    
    Endpoints:
    - kpis: Get all dashboard KPIs
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def kpis(self, request):
        """Get all KPI metrics for dashboard"""
        today = timezone.now().date()
        now = timezone.now()
        
        # Calculate date ranges
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        # 1. Total Users Count
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        
        # 2. Revenue Metrics
        today_revenue = Sale.objects.filter(
            created_at__date=today
        ).aggregate(total=Sum('total_amount', default=Decimal('0')))['total'] or Decimal('0')
        
        week_revenue = Sale.objects.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=today
        ).aggregate(total=Sum('total_amount', default=Decimal('0')))['total'] or Decimal('0')
        
        month_revenue = Sale.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=today
        ).aggregate(total=Sum('total_amount', default=Decimal('0')))['total'] or Decimal('0')
        
        # 3. Transaction Counts
        today_transactions = Sale.objects.filter(
            created_at__date=today
        ).count()
        
        week_transactions = Sale.objects.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=today
        ).count()
        
        month_transactions = Sale.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=today
        ).count()
        
        # 4. Active Discounts Count
        active_discounts = Discount.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        ).count()
        
        # 5. Low Stock Items Count (below 10 units)
        low_stock_items = Product.objects.filter(
            current_stock__lt=10
        ).count()
        
        # 6. Expiring Items Count (within 2 days)
        expiry_date = today + timedelta(days=2)
        expiring_items = IngredientBatch.objects.filter(
            expire_date__lte=expiry_date,
            expire_date__gte=today,
            current_qty__gt=Decimal('0')
        ).count()
        
        # 7. High Wastage Alert Count (unread wastage alerts)
        high_wastage_alerts = Notification.objects.filter(
            type='HighWastage'
        ).values('id').count()
        
        result = {
            'timestamp': now.isoformat(),
            'total_users': total_users,
            'active_users': active_users,
            'revenue': {
                'today': today_revenue,
                'this_week': week_revenue,
                'this_month': month_revenue,
            },
            'transactions': {
                'today': today_transactions,
                'this_week': week_transactions,
                'this_month': month_transactions,
            },
            'active_discounts_count': active_discounts,
            'low_stock_items_count': low_stock_items,
            'expiring_items_count': expiring_items,
            'high_wastage_alerts_count': high_wastage_alerts,
        }
        
        from api.serializers.analytics_serializers import DashboardKpiSerializer
        serializer = DashboardKpiSerializer(result)
        return Response(serializer.data)


# ============================================================
# FRONTEND-FACING ANALYTICS ENDPOINTS
# ============================================================
# These are the top-level endpoints that the frontend calls directly


class SalesStatsViewSet(viewsets.ViewSet):
    """
    API Endpoint for sales statistics.
    
    GET /api/analytics/sales-stats/
    - Returns overall sales KPIs for dashboard
    - ALWAYS returns REAL database aggregations, NEVER hardcoded values
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get overall sales statistics from database"""
        # Query ALL sales - no date filtering by default
        # Use no filter to get complete database totals
        all_sales = Sale.objects.all()
        
        # Calculate totals using ONLY database aggregations
        total_sales_amount = all_sales.aggregate(
            total=Sum('total_amount', default=Decimal('0'))
        )['total'] or Decimal('0')
        
        total_discount = all_sales.aggregate(
            total=Sum('discount_amount', default=Decimal('0'))
        )['total'] or Decimal('0')
        
        total_orders = all_sales.count()  # Total number of sales
        
        # Calculate cost of goods from actual sales items
        cost_of_goods = Decimal('0')
        for sale in all_sales.prefetch_related('items'):
            for item in sale.items.all():
                # Handle deleted products - check raw FK ID first before accessing related object
                if item.product_id_id:  # Check if FK points to an actual product
                    product = item.product_id
                    if product and product.cost_price:
                        cost_of_goods += Decimal(str(item.quantity)) * Decimal(str(product.cost_price))
        
        # Calculate total wastage loss (both product and ingredient)
        product_wastage_total = ProductWastage.objects.aggregate(
            total=Sum('total_loss', default=Decimal('0'))
        )['total'] or Decimal('0')
        
        ingredient_wastage_total = IngredientWastage.objects.aggregate(
            total=Sum('total_loss', default=Decimal('0'))
        )['total'] or Decimal('0')
        
        total_wastage_loss = product_wastage_total + ingredient_wastage_total
        
        # Calculate revenue (after discount)
        revenue = total_sales_amount - total_discount
        net_profit = revenue - cost_of_goods
        
        # Return REAL database values
        return Response({
            'total_revenue': float(revenue),
            'total_orders': int(total_orders),
            'total_discount': float(total_discount),
            'total_cost_of_goods': float(cost_of_goods),
            'total_wastage_loss': float(total_wastage_loss),
            'net_profit': float(net_profit),
        })


class ProductStatsViewSet(viewsets.ViewSet):
    """
    API Endpoint for product statistics.
    
    GET /api/analytics/product-stats/
    - Returns top-selling products
    - ALWAYS returns REAL database data, NEVER hardcoded values
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get top-selling products from database"""
        limit = int(request.query_params.get('limit', 10))
        
        # Query ACTUAL sales items from database
        # Exclude items with NULL product_id (deleted products)
        top_products = SaleItem.objects.filter(
            product_id__isnull=False  # Only include items with valid products
        ).values('product_id').annotate(
            product_name=F('product_id__name'),
            quantity_sold=Sum('quantity', default=Decimal('0')),
            total_sales_amt=Sum('subtotal', default=Decimal('0')),
        ).order_by('-total_sales_amt')[:limit]
        
        results = []
        for item in top_products:
            results.append({
                'product_id': item['product_id'],
                'product_name': item['product_name'] or 'Unknown',
                'quantity_sold': float(item['quantity_sold'] or 0),
                'total_sales': float(item['total_sales_amt'] or 0),
            })
        
        # If no sales exist, return empty array (not hardcoded data)
        return Response({'top_products': results})


class WastageStatsViewSet(viewsets.ViewSet):
    """
    API Endpoint for wastage statistics.
    
    GET /api/analytics/wastage-stats/
    - Returns wastage breakdown by reason
    - ALWAYS returns REAL database data, NEVER hardcoded values
    - SAFELY handles NULL values and empty querysets
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get wastage breakdown from database"""
        try:
            # Get wastage by reason - query ACTUAL database
            # Filter out NULL reason_id to avoid accessing None.reason errors
            wastage_by_reason = ProductWastage.objects.filter(
                reason_id__isnull=False
            ).values('reason_id').annotate(
                reason_name=F('reason_id__reason'),
                total_quantity=Sum('quantity', default=Decimal('0')),
                total_loss_amt=Sum('total_loss', default=Decimal('0')),
                waste_count=Count('id', default=0),
            ).order_by('-total_loss_amt')
            
            # Get total revenue for percentage calculation - safely handle None
            revenue_result = Sale.objects.aggregate(
                total=Sum('total_amount', default=Decimal('0'))
            )
            total_revenue = revenue_result.get('total') or Decimal('1')
            if total_revenue == 0:
                total_revenue = Decimal('1')  # Avoid division by zero
            
            results = []
            total_wastage = Decimal('0')
            
            # Handle empty wastage_by_reason safely
            if wastage_by_reason:
                for item in wastage_by_reason:
                    # Safely extract fields with None defaults
                    loss = Decimal(str(item.get('total_loss_amt') or 0))
                    quantity = Decimal(str(item.get('total_quantity') or 0))
                    reason_name = item.get('reason_name') or 'Unknown'
                    
                    total_wastage += loss
                    
                    # Calculate percentage of revenue
                    percentage = float((loss / total_revenue * 100)) if total_revenue > 0 else 0.0
                    
                    results.append({
                        'reason': str(reason_name),
                        'quantity': float(quantity),
                        'loss_amount': float(loss),
                        'percentage_of_revenue': percentage,
                    })
            
            # Return REAL wastage breakdown or empty if no wastage
            return Response({
                'breakdown': results,
                'total_wastage_loss': float(total_wastage),
            })
            
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in WastageStatsViewSet.list(): {str(e)}")
            
            # Return safe empty response on error
            return Response({
                'breakdown': [],
                'total_wastage_loss': 0.0,
            }, status=200)


class InventoryStatsViewSet(viewsets.ViewSet):
    """
    API Endpoint for inventory statistics.
    
    GET /api/analytics/inventory-stats/
    - Returns inventory metrics
    - ALWAYS returns REAL database data, NEVER hardcoded values
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get inventory statistics - REAL DATA ONLY"""
        # Query ACTUAL products from database
        products = Product.objects.all()
        total_value = Decimal('0')
        low_stock_count = 0
        
        for product in products:
            stock = Decimal(str(product.current_stock or 0))
            cost = Decimal(str(product.cost_price or 0))
            item_value = stock * cost
            total_value += item_value
            
            if stock < 10:
                low_stock_count += 1
        
        # Query ACTUAL expiring batches from database
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
    - Returns products with low stock
    - ALWAYS returns REAL database data, NEVER hardcoded values
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get all low stock items - REAL DATA ONLY"""
        # Query ACTUAL products from database with current_stock < 10
        low_stock_products = Product.objects.filter(
            current_stock__lt=10
        ).order_by('current_stock')
        
        results = []
        for product in low_stock_products:
            results.append({
                'id': product.id,
                'type': 'product',
                'name': product.name,
                'product_id': product.product_id,
                'current_stock': float(product.current_stock or 0),
                'reorder_level': 10.0,
                'unit': 'units',
            })
        
        # Return REAL low stock items or empty array if none
        return Response(results)

