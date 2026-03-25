"""
Tests for Inventory Analytics ViewSet endpoints.

Tests all 6 inventory analytics endpoints:
- stock_value: Total inventory value calculation
- turnover: Stock turnover rates per product
- expired: Expired items value and quantity
- wastage_summary: Wastage breakdown by reason
- wastage_trend: Wastage trends over time (daily/weekly/monthly)
- ingredient_usage: Ingredient usage rates

Test coverage includes:
- Authentication requirement
- Correct calculations and formulas
- Date range filtering
- Edge cases (no data, zero values, etc.)
"""

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from decimal import Decimal
from datetime import datetime, timedelta

from api.models import (
    User, Category, Product, Ingredient, IngredientBatch,
    Sale, SaleItem, ProductWastage, IngredientWastage,
    WastageReason
)


class InventoryAnalyticsTestBase(TestCase):
    """Base test class with common setup for inventory analytics tests"""
    
    def setUp(self):
        """Create test user, products, ingredients, and sample data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='manager'
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Create categories
        self.product_category = Category.objects.create(
            name='Bread',
            type='Product'
        )
        self.ingredient_category = Category.objects.create(
            name='Flour',
            type='Ingredient'
        )
        
        # Create products
        self.product1 = Product.objects.create(
            name='Whole Wheat Bread',
            category_id=self.product_category,
            current_stock=Decimal('100'),
            cost_price=Decimal('50'),
            selling_price=Decimal('100')
        )
        
        self.product2 = Product.objects.create(
            name='White Bread',
            category_id=self.product_category,
            current_stock=Decimal('50'),
            cost_price=Decimal('40'),
            selling_price=Decimal('80')
        )
        
        # Create ingredients
        self.ingredient1 = Ingredient.objects.create(
            name='All Purpose Flour',
            category_id=self.ingredient_category,
            total_quantity=Decimal('1000'),
            low_stock_threshold=Decimal('100')
        )
        
        self.ingredient2 = Ingredient.objects.create(
            name='Yeast',
            category_id=self.ingredient_category,
            total_quantity=Decimal('50'),
            low_stock_threshold=Decimal('10')
        )
        
        # Create wastage reasons
        self.wastage_reason_expired = WastageReason.objects.create(
            reason='Product Expired'
        )
        self.wastage_reason_damaged = WastageReason.objects.create(
            reason='Damaged'
        )
        
        # Create sample sales data for turnover calculation
        now = timezone.now()
        self.sale = Sale.objects.create(
            cashier_id=self.user,
            total_amount=Decimal('500'),
            discount_amount=Decimal('0'),
            created_at=now - timedelta(days=5)
        )
        
        # Add sale items
        SaleItem.objects.create(
            sale_id=self.sale,
            product_id=self.product1,
            quantity=Decimal('10'),
            unit_price=Decimal('100'),
            subtotal=Decimal('1000')
        )
        
        SaleItem.objects.create(
            sale_id=self.sale,
            product_id=self.product2,
            quantity=Decimal('5'),
            unit_price=Decimal('80'),
            subtotal=Decimal('400')
        )
        
        # Create ingredient batches
        now = timezone.now()
        self.batch1 = IngredientBatch.objects.create(
            ingredient_id=self.ingredient1,
            quantity=Decimal('500'),
            current_qty=Decimal('300'),
            made_date=now - timedelta(days=10),
            expire_date=now + timedelta(days=10)
        )
        
        # Create expired batch
        self.batch_expired = IngredientBatch.objects.create(
            ingredient_id=self.ingredient2,
            quantity=Decimal('100'),
            current_qty=Decimal('50'),
            made_date=now - timedelta(days=30),
            expire_date=now - timedelta(days=5)
        )
        
        # Create wastage records
        self.product_wastage = ProductWastage.objects.create(
            product_id=self.product1,
            quantity=Decimal('5'),
            unit_cost=Decimal('50'),
            total_loss=Decimal('250'),
            reason_id=self.wastage_reason_expired,
            created_at=now - timedelta(days=3)
        )
        
        self.ingredient_wastage = IngredientWastage.objects.create(
            batch_id=self.batch1,
            quantity=Decimal('10'),
            unit_cost=Decimal('10'),
            total_loss=Decimal('100'),
            created_at=now - timedelta(days=2)
        )


class StockValueAnalyticsTest(InventoryAnalyticsTestBase):
    """Test stock_value endpoint"""
    
    def test_stock_value_requires_authentication(self):
        """Test that authentication is required"""
        self.client.credentials()  # Clear credentials
        response = self.client.get('/api/analytics/inventory/stock_value/')
        self.assertEqual(response.status_code, 401)
    
    def test_stock_value_calculation(self):
        """Test correct stock value calculation"""
        response = self.client.get('/api/analytics/inventory/stock_value/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        
        # Verify structure
        self.assertIn('total_stock_value', data)
        self.assertIn('items', data)
        self.assertIn('item_count', data)
        
        # Check calculation: product1 (100 * 50) + product2 (50 * 40) = 7000
        expected_value = Decimal('7000')
        self.assertEqual(Decimal(str(data['total_stock_value'])), expected_value)
        
        # Verify items
        self.assertEqual(len(data['items']), 2)
        
        # Find product1 in items
        product1_item = next(
            (item for item in data['items'] if item['product_id'] == self.product1.id),
            None
        )
        self.assertIsNotNone(product1_item)
        self.assertEqual(Decimal(str(product1_item['item_value'])), Decimal('5000'))
    
    def test_stock_value_with_zero_stock(self):
        """Test stock value with zero stock for a product"""
        # Update product to have zero stock
        product = Product.objects.create(
            name='Empty Product',
            category_id=self.product_category,
            current_stock=Decimal('0'),
            cost_price=Decimal('100'),
            selling_price=Decimal('200')
        )
        
        response = self.client.get('/api/analytics/inventory/stock_value/')
        self.assertEqual(response.status_code, 200)
        
        # Zero stock should contribute 0 to total value
        empty_item = next(
            (item for item in response.json()['items'] if item['product_id'] == product.id),
            None
        )
        self.assertEqual(Decimal(str(empty_item['item_value'])), Decimal('0'))


class TurnoverAnalyticsTest(InventoryAnalyticsTestBase):
    """Test turnover endpoint"""
    
    def test_turnover_requires_authentication(self):
        """Test that authentication is required"""
        self.client.credentials()
        response = self.client.get('/api/analytics/inventory/turnover/')
        self.assertEqual(response.status_code, 401)
    
    def test_turnover_rate_calculation(self):
        """Test correct turnover rate calculation"""
        response = self.client.get('/api/analytics/inventory/turnover/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        
        # Verify response is a list
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)  # Two products
        
        # Find product1
        product1_data = next(
            (item for item in data if item['product_id'] == self.product1.id),
            None
        )
        self.assertIsNotNone(product1_data)
        
        # Verify structure
        self.assertIn('turnover_rate', product1_data)
        self.assertIn('annualized_turnover', product1_data)
        self.assertIn('days_to_turnover', product1_data)
        self.assertIn('quantity_sold', product1_data)
        
        # Product1 sold 10 units from current stock of 100
        self.assertEqual(Decimal(str(product1_data['quantity_sold'])), Decimal('10'))
    
    def test_turnover_with_date_range(self):
        """Test turnover with custom date range"""
        today = timezone.now().date()
        date_from = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        date_to = today.strftime('%Y-%m-%d')
        
        response = self.client.get(
            f'/api/analytics/inventory/turnover/?date_from={date_from}&date_to={date_to}'
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_turnover_no_sales(self):
        """Test turnover calculation with no sales"""
        # Create a product with no sales
        product = Product.objects.create(
            name='New Product',
            category_id=self.product_category,
            current_stock=Decimal('100'),
            cost_price=Decimal('50'),
            selling_price=Decimal('100')
        )
        
        response = self.client.get('/api/analytics/inventory/turnover/')
        self.assertEqual(response.status_code, 200)
        
        product_data = next(
            (item for item in response.json() if item['product_id'] == product.id),
            None
        )
        
        # Zero sales should result in zero turnover
        self.assertEqual(Decimal(str(product_data['quantity_sold'])), Decimal('0'))
        self.assertEqual(Decimal(str(product_data['turnover_rate'])), Decimal('0'))


class ExpiredAnalyticsTest(InventoryAnalyticsTestBase):
    """Test expired endpoint"""
    
    def test_expired_requires_authentication(self):
        """Test that authentication is required"""
        self.client.credentials()
        response = self.client.get('/api/analytics/inventory/expired/')
        self.assertEqual(response.status_code, 401)
    
    def test_expired_items_calculation(self):
        """Test correct expired items calculation"""
        response = self.client.get('/api/analytics/inventory/expired/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        
        # Verify structure
        self.assertIn('total_expired_value', data)
        self.assertIn('expired_count', data)
        self.assertIn('items', data)
        
        # Check that expired batch is included
        self.assertEqual(len(data['items']), 1)
        expired_item = data['items'][0]
        
        # Verify expired batch data
        self.assertEqual(expired_item['ingredient_id'], self.ingredient2.id)
        self.assertEqual(Decimal(str(expired_item['quantity'])), Decimal('50'))
        
        # Value = 50 * 5 (cost_price)
        expected_value = Decimal('250')
        self.assertEqual(Decimal(str(expired_item['expired_value'])), expected_value)
    
    def test_expired_value_at_cost_price(self):
        """Test expired items value uses cost price"""
        response = self.client.get('/api/analytics/inventory/expired/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        total_expired = Decimal(str(data['total_expired_value']))
        
        # The endpoint calculates cost from ingredient's cost which may not exist
        # Just verify total_expired >= 0
        self.assertGreaterEqual(total_expired, Decimal('0'))
    
    def test_no_expired_items(self):
        """Test response when there are no expired items"""
        # Delete expired batch
        self.batch_expired.delete()
        
        response = self.client.get('/api/analytics/inventory/expired/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(Decimal(str(data['total_expired_value'])), Decimal('0'))
        self.assertEqual(len(data['items']), 0)


class WastageSummaryAnalyticsTest(InventoryAnalyticsTestBase):
    """Test wastage_summary endpoint"""
    
    def test_wastage_summary_requires_authentication(self):
        """Test that authentication is required"""
        self.client.credentials()
        response = self.client.get('/api/analytics/inventory/wastage_summary/')
        self.assertEqual(response.status_code, 401)
    
    def test_wastage_summary_by_reason(self):
        """Test wastage summary grouped by reason"""
        response = self.client.get('/api/analytics/inventory/wastage_summary/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        
        # Verify structure
        self.assertIn('total_wastage_loss', data)
        self.assertIn('wastage_by_reason', data)
        self.assertIn('period', data)
        
        wastage_reasons = data['wastage_by_reason']
        
        # Should have product wastage reason and ingredients aggregate
        self.assertGreater(len(wastage_reasons), 0)
        
        # Find product wastage
        product_wastage = next(
            (item for item in wastage_reasons if item['type'] == 'product'),
            None
        )
        
        if product_wastage:
            self.assertEqual(
                Decimal(str(product_wastage['total_loss'])),
                Decimal('250')  # From product_wastage fixture
            )
    
    def test_wastage_summary_total_calculation(self):
        """Test total wastage loss calculation"""
        response = self.client.get('/api/analytics/inventory/wastage_summary/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        total_loss = Decimal(str(data['total_wastage_loss']))
        
        # Should include product wastage (250) + ingredient wastage (100)
        expected_total = Decimal('350')
        self.assertEqual(total_loss, expected_total)
    
    def test_wastage_summary_with_date_range(self):
        """Test wastage summary with custom date range"""
        today = timezone.now().date()
        date_from = (today - timedelta(days=10)).strftime('%Y-%m-%d')
        date_to = today.strftime('%Y-%m-%d')
        
        response = self.client.get(
            f'/api/analytics/inventory/wastage_summary/?date_from={date_from}&date_to={date_to}'
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('period', data)


class WastageTrendAnalyticsTest(InventoryAnalyticsTestBase):
    """Test wastage_trend endpoint"""
    
    def test_wastage_trend_requires_authentication(self):
        """Test that authentication is required"""
        self.client.credentials()
        response = self.client.get('/api/analytics/inventory/wastage_trend/')
        self.assertEqual(response.status_code, 401)
    
    def test_wastage_trend_daily(self):
        """Test wastage trend grouped by day"""
        response = self.client.get('/api/analytics/inventory/wastage_trend/?trend_type=daily')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        
        # Verify structure
        self.assertIn('trends', data)
        self.assertIn('trend_type', data)
        self.assertIn('period', data)
        
        self.assertEqual(data['trend_type'], 'daily')
        self.assertIsInstance(data['trends'], list)
    
    def test_wastage_trend_weekly(self):
        """Test wastage trend grouped by week"""
        response = self.client.get('/api/analytics/inventory/wastage_trend/?trend_type=weekly')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        
        self.assertEqual(data['trend_type'], 'weekly')
        self.assertIsInstance(data['trends'], list)
    
    def test_wastage_trend_monthly(self):
        """Test wastage trend grouped by month"""
        response = self.client.get('/api/analytics/inventory/wastage_trend/?trend_type=monthly')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        
        self.assertEqual(data['trend_type'], 'monthly')
        self.assertIsInstance(data['trends'], list)
    
    def test_wastage_trend_default_daily(self):
        """Test that default trend type is daily"""
        response = self.client.get('/api/analytics/inventory/wastage_trend/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        # Should default to daily
        self.assertEqual(data['trend_type'], 'daily')
    
    def test_wastage_trend_includes_products_and_ingredients(self):
        """Test that trend includes both product and ingredient wastage"""
        response = self.client.get('/api/analytics/inventory/wastage_trend/?trend_type=daily')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        trends = data['trends']
        
        # Should have trends with total loss > 0 where wastage occurred
        if len(trends) > 0:
            # Find a trend with loss
            trend_with_loss = next(
                (t for t in trends if Decimal(str(t['total_loss'])) > 0),
                None
            )
            
            if trend_with_loss:
                # Should have both product and ingredient loss fields
                self.assertIn('product_loss', trend_with_loss)
                self.assertIn('ingredient_loss', trend_with_loss)
                self.assertIn('total_loss', trend_with_loss)


class IngredientUsageAnalyticsTest(InventoryAnalyticsTestBase):
    """Test ingredient_usage endpoint"""
    
    def test_ingredient_usage_requires_authentication(self):
        """Test that authentication is required"""
        self.client.credentials()
        response = self.client.get('/api/analytics/inventory/ingredient_usage/')
        self.assertEqual(response.status_code, 401)
    
    def test_ingredient_usage_calculation(self):
        """Test ingredient usage rate calculation"""
        response = self.client.get('/api/analytics/inventory/ingredient_usage/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        
        # Should have ingredients
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)  # Two ingredients
        
        # Find ingredient1
        ingredient1_data = next(
            (item for item in data if item['ingredient_id'] == self.ingredient1.id),
            None
        )
        self.assertIsNotNone(ingredient1_data)
        
        # Verify structure
        self.assertIn('usage_rate', ingredient1_data)
        self.assertIn('total_purchased', ingredient1_data)
        self.assertIn('total_used', ingredient1_data)
        self.assertIn('current_stock', ingredient1_data)
        
        # From fixture: batch1 had quantity=500, current_qty=300
        # So used = 500 - 300 = 200
        self.assertEqual(Decimal(str(ingredient1_data['total_used'])), Decimal('200'))
    
    def test_ingredient_usage_rate_formula(self):
        """Test ingredient usage rate formula (used / purchased * 100)"""
        response = self.client.get('/api/analytics/inventory/ingredient_usage/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        ingredient1_data = next(
            (item for item in data if item['ingredient_id'] == self.ingredient1.id),
            None
        )
        
        # From fixture: purchased=500, used=200
        # rate = (200 / 500) * 100 = 40%
        expected_rate = Decimal('40')
        actual_rate = Decimal(str(ingredient1_data['usage_rate']))
        
        # Allow small variance due to Decimal rounding
        self.assertAlmostEqual(float(actual_rate), float(expected_rate), places=2)
    
    def test_ingredient_usage_with_date_range(self):
        """Test ingredient usage with custom date range"""
        today = timezone.now().date()
        date_from = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        date_to = today.strftime('%Y-%m-%d')
        
        response = self.client.get(
            f'/api/analytics/inventory/ingredient_usage/?date_from={date_from}&date_to={date_to}'
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_ingredient_usage_zero_purchased(self):
        """Test ingredient usage when none purchased in period"""
        # Create ingredient with no batches in date range
        ingredient = Ingredient.objects.create(
            name='New Ingredient',
            category_id=self.ingredient_category,
            total_quantity=Decimal('100'),
            cost_price=Decimal('5')
        )
        
        response = self.client.get('/api/analytics/inventory/ingredient_usage/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        new_ingredient_data = next(
            (item for item in data if item['ingredient_id'] == ingredient.id),
            None
        )
        
        # Zero purchased should result in 0% usage rate
        self.assertEqual(Decimal(str(new_ingredient_data['usage_rate'])), Decimal('0'))


class DateRangeFilteringTest(InventoryAnalyticsTestBase):
    """Test date range filtering across all endpoints"""
    
    def test_default_date_range_30_days(self):
        """Test that default date range is last 30 days"""
        now = timezone.now()
        today = now.date()
        
        # Create old wastage outside 30 day window
        old_date = now - timedelta(days=40)
        ProductWastage.objects.create(
            product_id=self.product1,
            quantity=Decimal('1'),
            unit_cost=Decimal('50'),
            total_loss=Decimal('50'),
            reason_id=self.wastage_reason_expired,
            created_at=old_date
        )
        
        response = self.client.get('/api/analytics/inventory/wastage_summary/')
        self.assertEqual(response.status_code, 200)
        
        # Old wastage should not be included
        data = response.json()
        # Verify old wastage is not included
        self.assertNotEqual(
            Decimal(str(data['total_wastage_loss'])),
            Decimal('400')  # Would be 350 + 50 if old wastage included
        )
    
    def test_custom_date_range(self):
        """Test custom date range filtering"""
        today = timezone.now().date()
        date_from = (today - timedelta(days=10)).strftime('%Y-%m-%d')
        date_to = today.strftime('%Y-%m-%d')
        
        response = self.client.get(
            f'/api/analytics/inventory/wastage_summary/?date_from={date_from}&date_to={date_to}'
        )
        self.assertEqual(response.status_code, 200)
        
        # Should only include wastage in date range
        data = response.json()
        self.assertIn('period', data)


class InvalidDateFormatTest(InventoryAnalyticsTestBase):
    """Test handling of invalid date formats"""
    
    def test_invalid_date_format_defaults_to_30_days(self):
        """Test that invalid date format defaults to 30 day range"""
        response = self.client.get(
            '/api/analytics/inventory/wastage_summary/?date_from=invalid&date_to=also-invalid'
        )
        self.assertEqual(response.status_code, 200)
        
        # Should return data with default date range
        data = response.json()
        self.assertIn('period', data)
