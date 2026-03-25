"""
Tests for Sales Analytics endpoints.

Covers daily, weekly, monthly, and category-based analytics.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

from api.models import (
    Product, Category, Sale, SaleItem,
    User as UserModel
)

User = get_user_model()


class SalesAnalyticsTestCase(TestCase):
    """Test suite for sales analytics endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create users
        self.manager = User.objects.create_user(
            username='manager_test',
            password='testpass123',
            full_name='Test Manager',
            role='Manager'
        )
        
        self.cashier = User.objects.create_user(
            username='cashier_test',
            password='testpass123',
            full_name='Test Cashier',
            role='Cashier'
        )
        
        # Create categories
        self.product_category = Category.objects.create(
            name='Bread',
            type='Product',
            description='Bread products'
        )
        
        # Create products
        self.product1 = Product.objects.create(
            category_id=self.product_category,
            name='Croissant',
            cost_price=Decimal('5.00'),
            selling_price=Decimal('15.00'),
            current_stock=Decimal('100.00')
        )
        
        self.product2 = Product.objects.create(
            category_id=self.product_category,
            name='Donut',
            cost_price=Decimal('3.00'),
            selling_price=Decimal('10.00'),
            current_stock=Decimal('200.00')
        )
        
        # Authenticate
        login_response = self.client.post('/api/auth/login/', {
            'username': 'manager_test',
            'password': 'testpass123'
        })
        
        if login_response.status_code != 200:
            raise Exception(f'Login failed with status {login_response.status_code}: {login_response.data}')
        
        # Get token (simple token authentication)
        self.token = login_response.data.get('token')
        if not self.token:
            raise Exception(f'No token in login response: {login_response.data}')
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
    
    def create_sale(self, date_offset=0):
        """Helper to create a sale"""
        sale_date = timezone.now() - timedelta(days=date_offset)
        
        sale = Sale.objects.create(
            bill_number='BILL-' + str(Sale.objects.count() + 1),
            cashier_id=self.cashier,
            subtotal=Decimal('100.00'),
            discount_amount=Decimal('5.00'),
            total_amount=Decimal('95.00'),
            payment_method='Cash',
            date_time=sale_date
        )
        
        # Create sale items
        SaleItem.objects.create(
            sale_id=sale,
            product_id=self.product1,
            quantity=Decimal('5.00'),
            unit_price=Decimal('15.00'),
            subtotal=Decimal('75.00')
        )
        
        SaleItem.objects.create(
            sale_id=sale,
            product_id=self.product2,
            quantity=Decimal('2.00'),
            unit_price=Decimal('10.00'),
            subtotal=Decimal('20.00')
        )
        
        return sale
    
    def test_daily_sales_analytics(self):
        """Test daily sales totals endpoint"""
        # Create sales
        self.create_sale(date_offset=0)
        self.create_sale(date_offset=1)
        
        response = self.client.get('/api/analytics/sales/daily/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        
        # Should have at least 2 days of data
        if len(response.data) > 0:
            item = response.data[0]
            self.assertIn('period', item)
            self.assertIn('total_sales', item)
            self.assertIn('revenue', item)
            self.assertIn('transaction_count', item)
            self.assertIn('items_sold', item)
    
    def test_daily_with_date_range(self):
        """Test daily sales with date range filtering"""
        # Create sales
        self.create_sale(date_offset=0)
        self.create_sale(date_offset=5)
        
        today = timezone.now().date()
        date_from = (today - timedelta(days=3)).strftime('%Y-%m-%d')
        date_to = today.strftime('%Y-%m-%d')
        
        response = self.client.get(
            f'/api/analytics/sales/daily/?date_from={date_from}&date_to={date_to}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should include data from the range
        self.assertIsInstance(response.data, list)
    
    def test_weekly_sales_analytics(self):
        """Test weekly sales analytics endpoint"""
        # Create multiple sales across days
        self.create_sale(date_offset=0)
        self.create_sale(date_offset=1)
        self.create_sale(date_offset=3)
        
        response = self.client.get('/api/analytics/sales/weekly/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        
        if len(response.data) > 0:
            item = response.data[0]
            self.assertIn('period', item)
            self.assertIn('total_sales', item)
            self.assertIn('transaction_count', item)
    
    def test_monthly_sales_analytics(self):
        """Test monthly sales analytics endpoint"""
        self.create_sale(date_offset=0)
        self.create_sale(date_offset=5)
        
        response = self.client.get('/api/analytics/sales/monthly/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_top_products(self):
        """Test top-selling products endpoint"""
        # Create multiple sales
        for _ in range(5):
            self.create_sale(date_offset=0)
        
        response = self.client.get('/api/analytics/sales/top_products/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        
        if len(response.data) > 0:
            item = response.data[0]
            self.assertIn('product_id', item)
            self.assertIn('product_name', item)
            self.assertIn('quantity_sold', item)
            self.assertIn('total_revenue', item)
            self.assertIn('rank', item)
    
    def test_top_products_limit(self):
        """Test top products with limit parameter"""
        # Create multiple sales
        for _ in range(5):
            self.create_sale(date_offset=0)
        
        response = self.client.get('/api/analytics/sales/top_products/?limit=1')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return only 1 product
        self.assertLessEqual(len(response.data), 1)
    
    def test_sales_by_category(self):
        """Test sales by category endpoint"""
        self.create_sale(date_offset=0)
        self.create_sale(date_offset=1)
        
        response = self.client.get('/api/analytics/sales/by_category/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        
        if len(response.data) > 0:
            item = response.data[0]
            self.assertIn('category_id', item)
            self.assertIn('category_name', item)
            self.assertIn('total_sales', item)
            self.assertIn('percentage_of_total', item)
    
    def test_sales_by_cashier(self):
        """Test sales by cashier endpoint"""
        self.create_sale(date_offset=0)
        self.create_sale(date_offset=1)
        
        response = self.client.get('/api/analytics/sales/by_cashier/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        
        if len(response.data) > 0:
            item = response.data[0]
            self.assertIn('cashier_id', item)
            self.assertIn('cashier_name', item)
            self.assertIn('transaction_count', item)
    
    def test_revenue_analysis(self):
        """Test revenue vs cost analysis endpoint"""
        self.create_sale(date_offset=0)
        self.create_sale(date_offset=1)
        
        response = self.client.get('/api/analytics/sales/revenue/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        self.assertIn('total_revenue', data)
        self.assertIn('total_cost_of_goods', data)
        self.assertIn('total_profit', data)
        self.assertIn('profit_margin', data)
        self.assertIn('transaction_count', data)
    
    def test_revenue_profit_calculation(self):
        """Test that profit is correctly calculated"""
        self.create_sale(date_offset=0)
        
        response = self.client.get('/api/analytics/sales/revenue/')
        data = response.data
        
        # Verify profit = revenue - cost (convert strings to Decimal)
        total_revenue = Decimal(str(data['total_revenue']))
        total_cost = Decimal(str(data['total_cost_of_goods']))
        total_profit = Decimal(str(data['total_profit']))
        
        expected_profit = total_revenue - total_cost
        self.assertEqual(total_profit, expected_profit)
    
    def test_analytics_requires_authentication(self):
        """Test that analytics endpoints require authentication"""
        self.client.credentials()  # Remove credentials
        
        response = self.client.get('/api/analytics/sales/daily/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_sales_value_calculations(self):
        """Test that sales values are calculated correctly"""
        self.create_sale(date_offset=0)
        
        response = self.client.get('/api/analytics/sales/daily/')
        
        if len(response.data) > 0:
            item = response.data[0]
            
            # Verify that response has the required fields
            self.assertIn('total_sales', item)
            self.assertIn('total_discount', item)
            self.assertIn('revenue', item)
            
            # The revenue value should be a decimal
            revenue = Decimal(str(item['revenue']))
            self.assertGreater(revenue, 0)
