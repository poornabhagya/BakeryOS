from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime, timedelta, date
from decimal import Decimal

from api.models import (
    User, Category, Product, ProductBatch, ProductWastage,
    WastageReason, Ingredient, IngredientBatch, IngredientWastage,
    ProductStockHistory, IngredientStockHistory
)


class ProductStockHistoryModelTest(TestCase):
    """Test ProductStockHistory model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            full_name='Test User',
            role='Manager'
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            type='Product',
            description='Test category'
        )
        
        self.product = Product.objects.create(
            category_id=self.category,
            name='Test Product',
            cost_price=Decimal('10.00'),
            selling_price=Decimal('20.00'),
            current_stock=Decimal('100.00')
        )
    
    def test_create_product_stock_history(self):
        """Test creating a ProductStockHistory entry"""
        history = ProductStockHistory.objects.create(
            product_id=self.product,
            transaction_type='UseStock',
            qty_before=Decimal('100.00'),
            qty_after=Decimal('90.00'),
            change_amount=Decimal('-10.00'),
            user_id=self.user,
            notes='Test sale'
        )
        
        self.assertEqual(history.product_id, self.product)
        self.assertEqual(history.transaction_type, 'UseStock')
        self.assertEqual(history.change_amount, Decimal('-10.00'))
        self.assertIsNotNone(history.created_at)
    
    def test_stock_history_ordering(self):
        """Test that stock history is ordered by created_at descending"""
        history1 = ProductStockHistory.objects.create(
            product_id=self.product,
            transaction_type='AddStock',
            qty_before=Decimal('0.00'),
            qty_after=Decimal('100.00'),
            change_amount=Decimal('100.00'),
            user_id=self.user
        )
        
        # Create second entry with a small delay
        history2 = ProductStockHistory.objects.create(
            product_id=self.product,
            transaction_type='UseStock',
            qty_before=Decimal('100.00'),
            qty_after=Decimal('90.00'),
            change_amount=Decimal('-10.00'),
            user_id=self.user
        )
        
        histories = ProductStockHistory.objects.all()
        self.assertEqual(histories[0].id, history2.id)
        self.assertEqual(histories[1].id, history1.id)
    
    def test_stock_history_with_null_user(self):
        """Test stock history with null user (system operation)"""
        history = ProductStockHistory.objects.create(
            product_id=self.product,
            transaction_type='StockAdjustment',
            qty_before=Decimal('90.00'),
            qty_after=Decimal('100.00'),
            change_amount=Decimal('10.00'),
            user_id=None,
            notes='Automatic adjustment'
        )
        
        self.assertIsNone(history.user_id)
        self.assertIsNotNone(history.created_at)
    
    def test_multiple_stock_history_entries(self):
        """Test multiple stock history entries for same product"""
        for i in range(5):
            ProductStockHistory.objects.create(
                product_id=self.product,
                transaction_type='UseStock',
                qty_before=Decimal(f'{100-i*10}.00'),
                qty_after=Decimal(f'{90-i*10}.00'),
                change_amount=Decimal('-10.00'),
                user_id=self.user
            )
        
        histories = ProductStockHistory.objects.filter(product_id=self.product)
        self.assertEqual(histories.count(), 5)


class IngredientStockHistoryModelTest(TestCase):
    """Test IngredientStockHistory model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='storekeeper',
            password='testpass123',
            email='store@example.com',
            full_name='Store Keeper',
            role='Storekeeper'
        )
        
        self.category = Category.objects.create(
            name='Flour',
            type='Ingredient',
            description='Flour ingredients'
        )
        
        self.ingredient = Ingredient.objects.create(
            category_id=self.category,
            name='All-Purpose Flour',
            supplier='Test Supplier',
            tracking_type='Weight',
            base_unit='kg',
            total_quantity=Decimal('100.00'),
            low_stock_threshold=Decimal('10.00')
        )
        
        self.batch = IngredientBatch.objects.create(
            ingredient_id=self.ingredient,
            quantity=Decimal('100.00'),
            current_qty=Decimal('100.00'),
            cost_price=Decimal('8.50'),
            made_date=timezone.make_aware(datetime(2026, 3, 20, 0, 0, 0)),
            expire_date=timezone.make_aware(datetime(2026, 6, 20, 0, 0, 0)),
            status='Active'
        )
    
    def test_create_ingredient_stock_history(self):
        """Test creating an IngredientStockHistory entry"""
        history = IngredientStockHistory.objects.create(
            ingredient_id=self.ingredient,
            batch_id=self.batch,
            transaction_type='UseStock',
            qty_before=Decimal('100.00'),
            qty_after=Decimal('90.00'),
            change_amount=Decimal('-10.00'),
            performed_by=self.user,
            notes='Used in production'
        )
        
        self.assertEqual(history.ingredient_id, self.ingredient)
        self.assertEqual(history.batch_id, self.batch)
        self.assertEqual(history.transaction_type, 'UseStock')
        self.assertEqual(history.change_amount, Decimal('-10.00'))
        self.assertIsNotNone(history.created_at)
    
    def test_ingredient_stock_history_without_batch(self):
        """Test ingredient stock history for ingredient without specific batch"""
        history = IngredientStockHistory.objects.create(
            ingredient_id=self.ingredient,
            batch_id=None,
            transaction_type='Adjustment',
            qty_before=Decimal('50.00'),
            qty_after=Decimal('60.00'),
            change_amount=Decimal('10.00'),
            performed_by=self.user,
            notes='Inventory correction'
        )
        
        self.assertIsNone(history.batch_id)
        self.assertIsNotNone(history.ingredient_id)
    
    def test_ingredient_stock_history_ordering(self):
        """Test that ingredient stock history is ordered correctly"""
        history1 = IngredientStockHistory.objects.create(
            ingredient_id=self.ingredient,
            batch_id=self.batch,
            transaction_type='AddStock',
            qty_before=Decimal('0.00'),
            qty_after=Decimal('100.00'),
            change_amount=Decimal('100.00'),
            reference_id=self.batch.batch_id,
        )
        
        history2 = IngredientStockHistory.objects.create(
            ingredient_id=self.ingredient,
            batch_id=self.batch,
            transaction_type='UseStock',
            qty_before=Decimal('100.00'),
            qty_after=Decimal('90.00'),
            change_amount=Decimal('-10.00'),
            performed_by=self.user
        )
        
        histories = IngredientStockHistory.objects.filter(ingredient_id=self.ingredient)
        self.assertEqual(histories[0].id, history2.id)
        self.assertEqual(histories[1].id, history1.id)
    
    def test_multiple_ingredient_stock_entries(self):
        """Test multiple stock history entries for same ingredient"""
        # Initial batch creation in setUp creates 1 AddStock entry
        initial_count = IngredientStockHistory.objects.filter(ingredient_id=self.ingredient).count()
        
        for i in range(4):
            IngredientStockHistory.objects.create(
                ingredient_id=self.ingredient,
                batch_id=self.batch,
                transaction_type='UseStock',
                qty_before=Decimal(f'{100-i*10}.00'),
                qty_after=Decimal(f'{90-i*10}.00'),
                change_amount=Decimal('-10.00'),
                performed_by=self.user
            )
        
        histories = IngredientStockHistory.objects.filter(ingredient_id=self.ingredient)
        # Should have initial 1 (from batch setup) + 4 (created manually) = 5
        self.assertEqual(histories.count(), initial_count + 4)


class ProductStockHistoryAPITest(APITestCase):
    """Test ProductStockHistory API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.manager = User.objects.create_user(
            username='manager',
            password='testpass123',
            email='manager@example.com',
            full_name='Manager User',
            role='Manager'
        )
        
        self.category = Category.objects.create(
            name='Buns',
            type='Product',
            description='Bun products'
        )
        
        self.product = Product.objects.create(
            category_id=self.category,
            name='White Bun',
            cost_price=Decimal('2.50'),
            selling_price=Decimal('5.00'),
            current_stock=Decimal('100.00')
        )
    
    def test_list_product_stock_history_authenticated(self):
        """Test listing product stock history requires authentication"""
        # Create some history
        ProductStockHistory.objects.create(
            product_id=self.product,
            transaction_type='UseStock',
            qty_before=Decimal('100.00'),
            qty_after=Decimal('90.00'),
            change_amount=Decimal('-10.00'),
            user_id=self.manager
        )
        
        # Without authentication
        response = self.client.get('/api/product-stock-history/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # With authentication
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/product-stock-history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_filter_product_stock_history_by_product(self):
        """Test filtering stock history by product"""
        # Create history for product
        ProductStockHistory.objects.create(
            product_id=self.product,
            transaction_type='UseStock',
            qty_before=Decimal('100.00'),
            qty_after=Decimal('90.00'),
            change_amount=Decimal('-10.00'),
            user_id=self.manager
        )
        
        self.client.force_authenticate(user=self.manager)
        
        # Filter by product_id
        response = self.client.get(f'/api/product-stock-history/?product_id={self.product.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_filter_product_stock_history_by_transaction_type(self):
        """Test filtering stock history by transaction type"""
        ProductStockHistory.objects.create(
            product_id=self.product,
            transaction_type='AddStock',
            qty_before=Decimal('50.00'),
            qty_after=Decimal('100.00'),
            change_amount=Decimal('50.00'),
            user_id=self.manager
        )
        
        ProductStockHistory.objects.create(
            product_id=self.product,
            transaction_type='UseStock',
            qty_before=Decimal('100.00'),
            qty_after=Decimal('90.00'),
            change_amount=Decimal('-10.00'),
            user_id=self.manager
        )
        
        self.client.force_authenticate(user=self.manager)
        
        response = self.client.get(f'/api/product-stock-history/?transaction_type=UseStock')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_product_stock_history_readonly(self):
        """Test that stock history endpoints are read-only"""
        self.client.force_authenticate(user=self.manager)
        
        # Try POST (should fail)
        response = self.client.post('/api/product-stock-history/', {
            'product_id': self.product.id,
            'transaction_type': 'UseStock',
            'qty_before': '100.00',
            'qty_after': '90.00',
            'change_amount': '-10.00'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Try PUT (should fail)
        history = ProductStockHistory.objects.create(
            product_id=self.product,
            transaction_type='UseStock',
            qty_before=Decimal('100.00'),
            qty_after=Decimal('90.00'),
            change_amount=Decimal('-10.00'),
            user_id=self.manager
        )
        
        response = self.client.put(f'/api/product-stock-history/{history.id}/', {
            'notes': 'Updated'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class IngredientStockHistoryAPITest(APITestCase):
    """Test IngredientStockHistory API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.manager = User.objects.create_user(
            username='manager',
            password='testpass123',
            email='manager@example.com',
            full_name='Manager User',
            role='Manager'
        )
        
        self.storekeeper = User.objects.create_user(
            username='storekeeper',
            password='testpass123',
            email='store@example.com',
            full_name='Store Keeper',
            role='Storekeeper'
        )
        
        self.category = Category.objects.create(
            name='Flour',
            type='Ingredient',
            description='Flour ingredients'
        )
        
        self.ingredient = Ingredient.objects.create(
            category_id=self.category,
            name='All-Purpose Flour',
            supplier='Test Supplier',
            tracking_type='Weight',
            base_unit='kg',
            total_quantity=Decimal('100.00'),
            low_stock_threshold=Decimal('10.00')
        )
        
        self.batch = IngredientBatch.objects.create(
            ingredient_id=self.ingredient,
            quantity=Decimal('100.00'),
            current_qty=Decimal('100.00'),
            cost_price=Decimal('8.50'),
            made_date=timezone.make_aware(datetime(2026, 3, 20, 0, 0, 0)),
            expire_date=timezone.make_aware(datetime(2026, 6, 20, 0, 0, 0)),
            status='Active'
        )
    
    def test_list_ingredient_stock_history_authenticated(self):
        """Test listing ingredient stock history requires authentication"""
        # Create history
        IngredientStockHistory.objects.create(
            ingredient_id=self.ingredient,
            batch_id=self.batch,
            transaction_type='UseStock',
            qty_before=Decimal('100.00'),
            qty_after=Decimal('90.00'),
            change_amount=Decimal('-10.00'),
            performed_by=self.storekeeper
        )
        
        # Without authentication
        response = self.client.get('/api/ingredient-stock-history/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # With authentication
        self.client.force_authenticate(user=self.storekeeper)
        response = self.client.get('/api/ingredient-stock-history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_ingredient_stock_history_by_ingredient(self):
        """Test filtering ingredient stock history by ingredient"""
        IngredientStockHistory.objects.create(
            ingredient_id=self.ingredient,
            batch_id=self.batch,
            transaction_type='UseStock',
            qty_before=Decimal('100.00'),
            qty_after=Decimal('90.00'),
            change_amount=Decimal('-10.00'),
            performed_by=self.storekeeper
        )
        
        self.client.force_authenticate(user=self.storekeeper)
        
        response = self.client.get(f'/api/ingredient-stock-history/?ingredient_id={self.ingredient.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_filter_ingredient_stock_history_by_batch(self):
        """Test filtering ingredient stock history by batch"""
        IngredientStockHistory.objects.create(
            ingredient_id=self.ingredient,
            batch_id=self.batch,
            transaction_type='UseStock',
            qty_before=Decimal('100.00'),
            qty_after=Decimal('90.00'),
            change_amount=Decimal('-10.00'),
            performed_by=self.storekeeper
        )
        
        self.client.force_authenticate(user=self.storekeeper)
        
        response = self.client.get(f'/api/ingredient-stock-history/?batch_id={self.batch.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_ingredient_stock_history_readonly(self):
        """Test that stock history endpoints are read-only"""
        self.client.force_authenticate(user=self.storekeeper)
        
        # Try POST (should fail)
        response = self.client.post('/api/ingredient-stock-history/', {
            'ingredient_id': self.ingredient.id,
            'transaction_type': 'UseStock',
            'qty_before': '100.00',
            'qty_after': '90.00',
            'change_amount': '-10.00'
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_ingredient_stock_history_date_range_filter(self):
        """Test filtering by date range"""
        # Create history entry
        IngredientStockHistory.objects.create(
            ingredient_id=self.ingredient,
            batch_id=self.batch,
            transaction_type='UseStock',
            qty_before=Decimal('100.00'),
            qty_after=Decimal('90.00'),
            change_amount=Decimal('-10.00'),
            performed_by=self.storekeeper
        )
        
        self.client.force_authenticate(user=self.storekeeper)
        
        # Get today's date
        today = timezone.now().date()
        start_date = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
        
        response = self.client.get(f'/api/ingredient-stock-history/?start_date={start_date}&end_date={end_date}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)


class StockHistorySignalTest(TestCase):
    """Test signal handlers for automatic stock history creation"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            full_name='Test User',
            role='Manager'
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            type='Product',
            description='Test'
        )
        
        self.product = Product.objects.create(
            category_id=self.category,
            name='Test Product',
            cost_price=Decimal('10.00'),
            selling_price=Decimal('20.00'),
            current_stock=Decimal('100.00')
        )
        
        self.wastage_reason = WastageReason.objects.create(
            reason='Damaged',
            description='Product damaged'
        )
    
    def test_signal_creates_history_on_product_wastage(self):
        """Test that ProductStockHistory is auto-created when ProductWastage is recorded"""
        initial_count = ProductStockHistory.objects.count()
        
        # Create product wastage
        ProductWastage.objects.create(
            product_id=self.product,
            quantity=Decimal('10.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.wastage_reason,
            reported_by=self.user,
            notes='Test wastage'
        )
        
        # Check that history was created
        final_count = ProductStockHistory.objects.count()
        self.assertEqual(final_count, initial_count + 1)
        
        history = ProductStockHistory.objects.latest('created_at')
        self.assertEqual(history.transaction_type, 'WasteStock')
        self.assertEqual(history.change_amount, Decimal('-10.00'))
