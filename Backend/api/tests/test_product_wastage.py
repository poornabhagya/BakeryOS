from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import datetime, timedelta

from api.models import User, Product, Category, WastageReason, ProductWastage


class ProductWastageModelTestCase(TestCase):
    """Test ProductWastage model functionality."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for model tests."""
        # Create category
        cls.category = Category.objects.create(
            category_id='CAT-P001',
            name='Buns',
            type='Product',
            description='Bread buns'
        )
        
        # Create product
        cls.product = Product.objects.create(
            product_id='PROD-1001',
            category_id=cls.category,
            name='Chocolate Bun',
            cost_price=Decimal('10.00'),
            selling_price=Decimal('25.00'),
            current_stock=Decimal('50.00')
        )
        
        # Create wastage reason
        cls.reason = WastageReason.objects.create(
            reason_id='WR-001',
            reason='Expired',
            description='Product expired'
        )
        
        # Create user for reporting
        cls.user = User.objects.create_user(
            username='baker1',
            password='pass123',
            email='baker@test.com',
            full_name='Baker One',
            role='Baker'
        )
    
    def test_create_product_wastage(self):
        """Test creating a product wastage record."""
        wastage = ProductWastage.objects.create(
            product_id=self.product,
            quantity=Decimal('5.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason,
            reported_by=self.user,
            notes='Test wastage'
        )
        self.assertIsNotNone(wastage.id)
        self.assertEqual(wastage.quantity, Decimal('5.00'))
        self.assertEqual(wastage.total_loss, Decimal('50.00'))
    
    def test_auto_generate_wastage_id(self):
        """Test that wastage_id is auto-generated in PW-### format."""
        wastage = ProductWastage.objects.create(
            product_id=self.product,
            quantity=Decimal('1.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason,
            reported_by=self.user
        )
        self.assertEqual(wastage.wastage_id, 'PW-001')
    
    def test_wastage_id_sequence(self):
        """Test that wastage_id maintains sequence (PW-001, PW-002, etc.)."""
        wastage1 = ProductWastage.objects.create(
            product_id=self.product,
            quantity=Decimal('1.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason,
            reported_by=self.user
        )
        
        wastage2 = ProductWastage.objects.create(
            product_id=self.product,
            quantity=Decimal('1.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason,
            reported_by=self.user
        )
        
        self.assertEqual(wastage1.wastage_id, 'PW-001')
        self.assertEqual(wastage2.wastage_id, 'PW-002')
    
    def test_total_loss_calculation(self):
        """Test that total_loss is calculated as quantity * unit_cost."""
        wastage = ProductWastage.objects.create(
            product_id=self.product,
            quantity=Decimal('10.50'),
            unit_cost=Decimal('15.00'),
            reason_id=self.reason,
            reported_by=self.user
        )
        expected_loss = Decimal('10.50') * Decimal('15.00')
        self.assertEqual(wastage.total_loss, expected_loss)
    
    def test_wastage_id_uniqueness(self):
        """Test that wastage_id is unique."""
        wastage1 = ProductWastage.objects.create(
            product_id=self.product,
            quantity=Decimal('1.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason,
            reported_by=self.user
        )
        
        with self.assertRaises(Exception):
            # Trying to create duplicate wastage_id should fail
            wastage2 = ProductWastage(
                wastage_id=wastage1.wastage_id,
                product_id=self.product,
                quantity=Decimal('1.00'),
                unit_cost=Decimal('10.00'),
                reason_id=self.reason,
                reported_by=self.user
            )
            wastage2.save()
    
    def test_created_at_timestamp(self):
        """Test that created_at is auto-set."""
        from django.utils import timezone
        
        before = timezone.now()
        wastage = ProductWastage.objects.create(
            product_id=self.product,
            quantity=Decimal('1.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason,
            reported_by=self.user
        )
        after = timezone.now()
        
        self.assertIsNotNone(wastage.created_at)
        self.assertGreaterEqual(wastage.created_at, before)
        self.assertLessEqual(wastage.created_at, after)


class ProductWastageAPITestCase(APITestCase):
    """Test ProductWastage API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for API tests."""
        # Create category
        cls.category = Category.objects.create(
            category_id='CAT-P001',
            name='Buns',
            type='Product',
            description='Bread buns'
        )
        
        # Create products
        cls.product1 = Product.objects.create(
            product_id='PROD-1001',
            category_id=cls.category,
            name='Chocolate Bun',
            cost_price=Decimal('10.00'),
            selling_price=Decimal('25.00'),
            current_stock=Decimal('100.00')
        )
        
        cls.product2 = Product.objects.create(
            product_id='PROD-1002',
            category_id=cls.category,
            name='Plain Bun',
            cost_price=Decimal('8.00'),
            selling_price=Decimal('20.00'),
            current_stock=Decimal('75.00')
        )
        
        # Create wastage reasons
        cls.reason1 = WastageReason.objects.create(
            reason_id='WR-001',
            reason='Expired',
            description='Product expired'
        )
        
        cls.reason2 = WastageReason.objects.create(
            reason_id='WR-002',
            reason='Damaged',
            description='Product damaged'
        )
        
        # Create users
        cls.manager_user = User.objects.create_user(
            username='manager',
            password='pass123',
            email='manager@test.com',
            full_name='Manager One',
            role='Manager'
        )
        
        cls.baker_user = User.objects.create_user(
            username='baker',
            password='pass123',
            email='baker@test.com',
            full_name='Baker One',
            role='Baker'
        )
        
        cls.cashier_user = User.objects.create_user(
            username='cashier',
            password='pass123',
            email='cashier@test.com',
            full_name='Cashier One',
            role='Cashier'
        )
        
        cls.storekeeper_user = User.objects.create_user(
            username='storekeeper',
            password='pass123',
            email='storekeeper@test.com',
            full_name='Storekeeper One',
            role='Storekeeper'
        )
    
    def setUp(self):
        """Set up client for each test."""
        self.client = APIClient()
    
    def test_list_product_wastages(self):
        """Test listing all product wastages."""
        # Create test wastage
        ProductWastage.objects.create(
            product_id=self.product1,
            quantity=Decimal('5.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason1,
            reported_by=self.manager_user
        )
        
        # Login and list
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get('/api/product-wastages/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_product_wastage_by_baker(self):
        """Test that Baker can create wastage."""
        self.client.force_authenticate(user=self.baker_user)
        
        data = {
            'product_id': self.product1.id,
            'quantity': Decimal('5.00'),
            'unit_cost': Decimal('10.00'),
            'reason_id': self.reason1.id,
            'notes': 'Test wastage'
        }
        
        response = self.client.post('/api/product-wastages/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('wastage_id', response.data)
        self.assertEqual(response.data['wastage_id'], 'PW-001')
    
    def test_create_product_wastage_by_cashier(self):
        """Test that Cashier can create wastage."""
        self.client.force_authenticate(user=self.cashier_user)
        
        data = {
            'product_id': self.product1.id,
            'quantity': Decimal('3.00'),
            'unit_cost': Decimal('10.00'),
            'reason_id': self.reason1.id,
        }
        
        response = self.client.post('/api/product-wastages/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reported_by'], self.cashier_user.id)
    
    def test_create_product_wastage_by_manager(self):
        """Test that Manager can create wastage."""
        self.client.force_authenticate(user=self.manager_user)
        
        data = {
            'product_id': self.product1.id,
            'quantity': Decimal('2.00'),
            'unit_cost': Decimal('10.00'),
            'reason_id': self.reason1.id,
        }
        
        response = self.client.post('/api/product-wastages/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_product_wastage_reject_storekeeper(self):
        """Test that Storekeeper cannot create product wastage."""
        self.client.force_authenticate(user=self.storekeeper_user)
        
        data = {
            'product_id': self.product1.id,
            'quantity': Decimal('5.00'),
            'unit_cost': Decimal('10.00'),
            'reason_id': self.reason1.id,
        }
        
        response = self.client.post('/api/product-wastages/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_retrieve_product_wastage(self):
        """Test retrieving wastage details."""
        # Create wastage
        wastage = ProductWastage.objects.create(
            product_id=self.product1,
            quantity=Decimal('5.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason1,
            reported_by=self.manager_user
        )
        
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(f'/api/product-wastages/{wastage.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['wastage_id'], 'PW-001')
        self.assertIn('product_detail', response.data)
        self.assertIn('reason_detail', response.data)
    
    def test_delete_product_wastage_by_manager(self):
        """Test that Manager can delete wastage."""
        # Create wastage
        wastage = ProductWastage.objects.create(
            product_id=self.product1,
            quantity=Decimal('5.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason1,
            reported_by=self.manager_user
        )
        
        # Check stock before delete
        product_before = Product.objects.get(id=self.product1.id)
        stock_after_creation = product_before.current_stock
        
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.delete(f'/api/product-wastages/{wastage.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check stock is restored
        product_after = Product.objects.get(id=self.product1.id)
        self.assertEqual(product_after.current_stock, stock_after_creation + Decimal('5.00'))
    
    def test_delete_product_wastage_reject_baker(self):
        """Test that Baker cannot delete wastage."""
        # Create wastage
        wastage = ProductWastage.objects.create(
            product_id=self.product1,
            quantity=Decimal('5.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason1,
            reported_by=self.manager_user
        )
        
        self.client.force_authenticate(user=self.baker_user)
        response = self.client.delete(f'/api/product-wastages/{wastage.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unauthenticated_access_rejected(self):
        """Test that unauthenticated access is rejected."""
        response = self.client.get('/api/product-wastages/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_with_filters(self):
        """Test listing with product_id filter."""
        # Create wastages for different products
        ProductWastage.objects.create(
            product_id=self.product1,
            quantity=Decimal('5.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason1,
            reported_by=self.manager_user
        )
        
        ProductWastage.objects.create(
            product_id=self.product2,
            quantity=Decimal('3.00'),
            unit_cost=Decimal('8.00'),
            reason_id=self.reason2,
            reported_by=self.manager_user
        )
        
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(f'/api/product-wastages/?product_id={self.product1.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['product_id'], self.product1.id)
    
    def test_analytics_endpoint(self):
        """Test analytics endpoint."""
        # Create multiple wastages
        ProductWastage.objects.create(
            product_id=self.product1,
            quantity=Decimal('5.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason1,
            reported_by=self.manager_user
        )
        
        ProductWastage.objects.create(
            product_id=self.product2,
            quantity=Decimal('3.00'),
            unit_cost=Decimal('8.00'),
            reason_id=self.reason2,
            reported_by=self.manager_user
        )
        
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get('/api/product-wastages/analytics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
        self.assertIn('by_reason', response.data)
        self.assertIn('by_product', response.data)
        self.assertEqual(response.data['summary']['total_records'], 2)


class ProductWastageValidationTestCase(APITestCase):
    """Test ProductWastage validation rules."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.category = Category.objects.create(
            category_id='CAT-P001',
            name='Buns',
            type='Product'
        )
        
        cls.product = Product.objects.create(
            product_id='PROD-1001',
            category_id=cls.category,
            name='Test Product',
            cost_price=Decimal('10.00'),
            selling_price=Decimal('25.00'),
            current_stock=Decimal('50.00')
        )
        
        cls.reason = WastageReason.objects.create(
            reason_id='WR-001',
            reason='Expired'
        )
        
        cls.user = User.objects.create_user(
            username='baker',
            password='pass123',
            role='Baker'
        )
    
    def setUp(self):
        """Set up client."""
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_quantity_must_be_positive(self):
        """Test that quantity must be positive."""
        data = {
            'product_id': self.product.id,
            'quantity': Decimal('0'),
            'unit_cost': Decimal('10.00'),
            'reason_id': self.reason.id,
        }
        
        response = self.client.post('/api/product-wastages/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_insufficient_stock_rejected(self):
        """Test that wastage is rejected if stock is insufficient."""
        data = {
            'product_id': self.product.id,
            'quantity': Decimal('100.00'),  # More than available
            'unit_cost': Decimal('10.00'),
            'reason_id': self.reason.id,
        }
        
        response = self.client.post('/api/product-wastages/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient stock', response.data['non_field_errors'][0])
    
    def test_unit_cost_must_be_non_negative(self):
        """Test that unit_cost cannot be negative."""
        data = {
            'product_id': self.product.id,
            'quantity': Decimal('5.00'),
            'unit_cost': Decimal('-1.00'),
            'reason_id': self.reason.id,
        }
        
        response = self.client.post('/api/product-wastages/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_product_id_required(self):
        """Test that product_id is required."""
        data = {
            'quantity': Decimal('5.00'),
            'unit_cost': Decimal('10.00'),
            'reason_id': self.reason.id,
        }
        
        response = self.client.post('/api/product-wastages/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_reason_id_required(self):
        """Test that reason_id is required."""
        data = {
            'product_id': self.product.id,
            'quantity': Decimal('5.00'),
            'unit_cost': Decimal('10.00'),
        }
        
        response = self.client.post('/api/product-wastages/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProductWastageStockDeductionTestCase(APITestCase):
    """Test that stock is properly deducted when wastage is created."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.category = Category.objects.create(
            category_id='CAT-P001',
            name='Buns',
            type='Product'
        )
        
        cls.product = Product.objects.create(
            product_id='PROD-1001',
            category_id=cls.category,
            name='Test Product',
            cost_price=Decimal('10.00'),
            selling_price=Decimal('25.00'),
            current_stock=Decimal('100.00')
        )
        
        cls.reason = WastageReason.objects.create(
            reason_id='WR-001',
            reason='Expired'
        )
        
        cls.user = User.objects.create_user(
            username='manager',
            password='pass123',
            role='Manager'
        )
    
    def setUp(self):
        """Set up client."""
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_stock_deducted_on_creation(self):
        """Test that product stock is deducted when wastage is created."""
        initial_stock = self.product.current_stock
        
        data = {
            'product_id': self.product.id,
            'quantity': Decimal('10.00'),
            'unit_cost': Decimal('10.00'),
            'reason_id': self.reason.id,
        }
        
        self.client.post('/api/product-wastages/', data, format='json')
        
        # Refresh from DB
        self.product.refresh_from_db()
        
        expected_stock = initial_stock - Decimal('10.00')
        self.assertEqual(self.product.current_stock, expected_stock)
    
    def test_stock_restored_on_deletion(self):
        """Test that product stock is restored when wastage is deleted."""
        # Create wastage via API
        data = {
            'product_id': self.product.id,
            'quantity': Decimal('10.00'),
            'unit_cost': Decimal('10.00'),
            'reason_id': self.reason.id,
        }
        
        response = self.client.post('/api/product-wastages/', data, format='json')
        wastage_id = response.data['id']
        
        # Check stock decreased
        self.product.refresh_from_db()
        stock_after_creation = self.product.current_stock
        self.assertEqual(stock_after_creation, Decimal('90.00'))
        
        # Delete wastage
        self.client.delete(f'/api/product-wastages/{wastage_id}/')
        
        # Check stock restored
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, Decimal('100.00'))


class ProductWastageSerializerTestCase(APITestCase):
    """Test ProductWastage serializers."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.category = Category.objects.create(
            category_id='CAT-P001',
            name='Buns',
            type='Product'
        )
        
        cls.product = Product.objects.create(
            product_id='PROD-1001',
            category_id=cls.category,
            name='Test Product',
            cost_price=Decimal('10.00'),
            selling_price=Decimal('25.00'),
            current_stock=Decimal('100.00')
        )
        
        cls.reason = WastageReason.objects.create(
            reason_id='WR-001',
            reason='Expired'
        )
        
        cls.user = User.objects.create_user(
            username='manager',
            password='pass123',
            role='Manager'
        )
    
    def test_list_serializer_includes_product_name(self):
        """Test that list serializer includes product name."""
        wastage = ProductWastage.objects.create(
            product_id=self.product,
            quantity=Decimal('5.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason,
            reported_by=self.user
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/product-wastages/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['product_name'], 'Test Product')
    
    def test_detail_serializer_includes_nested_data(self):
        """Test that detail serializer includes nested product/reason data."""
        wastage = ProductWastage.objects.create(
            product_id=self.product,
            quantity=Decimal('5.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason,
            reported_by=self.user
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/product-wastages/{wastage.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('product_detail', response.data)
        self.assertIn('reason_detail', response.data)
        self.assertIn('reported_by_detail', response.data)
    
    def test_create_serializer_auto_sets_reported_by(self):
        """Test that create serializer auto-sets reported_by if not provided."""
        data = {
            'product_id': self.product.id,
            'quantity': Decimal('5.00'),
            'unit_cost': Decimal('10.00'),
            'reason_id': self.reason.id,
        }
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/product-wastages/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reported_by'], self.user.id)


class ProductWastageIntegrationTestCase(APITestCase):
    """Integration tests for ProductWastage."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        cls.category = Category.objects.create(
            category_id='CAT-P001',
            name='Buns',
            type='Product'
        )
        
        cls.product = Product.objects.create(
            product_id='PROD-1001',
            category_id=cls.category,
            name='Test Product',
            cost_price=Decimal('10.00'),
            selling_price=Decimal('25.00'),
            current_stock=Decimal('100.00')
        )
        
        cls.reason = WastageReason.objects.create(
            reason_id='WR-001',
            reason='Expired'
        )
        
        cls.user = User.objects.create_user(
            username='manager',
            password='pass123',
            role='Manager'
        )
    
    def setUp(self):
        """Set up client."""
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_complete_wastage_workflow(self):
        """Test complete workflow: create, list, retrieve, delete."""
        # Create
        data = {
            'product_id': self.product.id,
            'quantity': Decimal('5.00'),
            'unit_cost': Decimal('10.00'),
            'reason_id': self.reason.id,
        }
        create_response = self.client.post('/api/product-wastages/', data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        wastage_id = create_response.data['id']
        
        # List
        list_response = self.client.get('/api/product-wastages/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreater(list_response.data['count'], 0)
        
        # Retrieve
        retrieve_response = self.client.get(f'/api/product-wastages/{wastage_id}/')
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        
        # Delete
        delete_response = self.client.delete(f'/api/product-wastages/{wastage_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify deleted
        verify_response = self.client.get(f'/api/product-wastages/{wastage_id}/')
        self.assertEqual(verify_response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_multiple_wastages_same_product(self):
        """Test creating multiple wastages for the same product."""
        # Create first wastage
        data1 = {
            'product_id': self.product.id,
            'quantity': Decimal('5.00'),
            'unit_cost': Decimal('10.00'),
            'reason_id': self.reason.id,
        }
        self.client.post('/api/product-wastages/', data1, format='json')
        
        # Create second wastage
        data2 = {
            'product_id': self.product.id,
            'quantity': Decimal('3.00'),
            'unit_cost': Decimal('10.00'),
            'reason_id': self.reason.id,
        }
        self.client.post('/api/product-wastages/', data2, format='json')
        
        # Check stock deducted twice
        self.product.refresh_from_db()
        expected_stock = Decimal('100.00') - Decimal('5.00') - Decimal('3.00')
        self.assertEqual(self.product.current_stock, expected_stock)
        
        # List and verify count
        response = self.client.get(f'/api/product-wastages/?product_id={self.product.id}')
        self.assertEqual(len(response.data['results']), 2)
    
    def test_wastage_id_sequence_integrity(self):
        """Test that wastage_id sequence is maintained across multiple creates."""
        wastages = []
        for i in range(3):
            data = {
                'product_id': self.product.id,
                'quantity': Decimal('1.00'),
                'unit_cost': Decimal('10.00'),
                'reason_id': self.reason.id,
            }
            response = self.client.post('/api/product-wastages/', data, format='json')
            wastages.append(response.data['wastage_id'])
        
        self.assertEqual(wastages[0], 'PW-001')
        self.assertEqual(wastages[1], 'PW-002')
        self.assertEqual(wastages[2], 'PW-003')
