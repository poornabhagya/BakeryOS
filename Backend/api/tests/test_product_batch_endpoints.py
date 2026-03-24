from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from api.models import User, Category, Product, ProductBatch, ProductStockHistory
import json


class ProductBatchModelTestCase(TestCase):
    """Test suite for ProductBatch model functionality"""

    def setUp(self):
        """Set up test data"""
        # Create a category
        self.category = Category.objects.create(
            name='Bread',
            description='Bread products',
            type='Product'
        )

        # Create a product with shelf_life
        self.product = Product.objects.create(
            name='Sourdough Bread',
            category_id=self.category,
            cost_price=Decimal('2.50'),
            selling_price=Decimal('5.00'),
            shelf_life=2,
            shelf_unit='days',
            current_stock=Decimal('0.00')
        )

    def test_batch_id_auto_generation(self):
        """Test that batch_id is auto-generated in correct format"""
        batch1 = ProductBatch.objects.create(
            product_id=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        # First batch should be PROD-BATCH-1001
        self.assertEqual(batch1.batch_id, 'PROD-BATCH-1001')

        batch2 = ProductBatch.objects.create(
            product_id=self.product,
            quantity=Decimal('5'),
            made_date=date.today()
        )
        # Second batch should be PROD-BATCH-1002
        self.assertEqual(batch2.batch_id, 'PROD-BATCH-1002')

    def test_expire_date_auto_calculation(self):
        """Test that expire_date is calculated from shelf_life"""
        made_date = date.today()
        batch = ProductBatch.objects.create(
            product_id=self.product,
            quantity=Decimal('10'),
            made_date=made_date
        )
        # Product shelf_life is 2 days
        expected_expire_date = made_date + timedelta(days=2)
        self.assertEqual(batch.expire_date, expected_expire_date)

    def test_is_expired_property(self):
        """Test is_expired property"""
        # Create an expired batch
        expired_date = date.today() - timedelta(days=1)
        batch = ProductBatch.objects.create(
            product_id=self.product,
            quantity=Decimal('10'),
            made_date=expired_date
        )
        self.assertTrue(batch.is_expired)

        # Create a fresh batch
        fresh_batch = ProductBatch.objects.create(
            product_id=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        self.assertFalse(fresh_batch.is_expired)

    def test_days_until_expiry_property(self):
        """Test days_until_expiry property"""
        batch = ProductBatch.objects.create(
            product_id=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        # Product shelf_life is 2 days
        self.assertEqual(batch.days_until_expiry, 2)

    def test_expiring_soon_property(self):
        """Test expiring_soon property (expires within 2 days)"""
        # Create batch that expires tomorrow
        made_date = date.today() - timedelta(days=1)
        batch = ProductBatch.objects.create(
            product_id=self.product,
            quantity=Decimal('10'),
            made_date=made_date
        )
        self.assertTrue(batch.expiring_soon)

    def test_stock_auto_added_on_creation(self):
        """Test that product stock is increased when batch is created"""
        initial_stock = self.product.current_stock
        batch = ProductBatch.objects.create(
            product_id=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, initial_stock + Decimal('10'))

    def test_stock_auto_deducted_on_deletion(self):
        """Test that product stock is decreased when batch is deleted"""
        batch = ProductBatch.objects.create(
            product_id=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        self.product.refresh_from_db()
        stock_before_deletion = self.product.current_stock

        batch.delete()
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, stock_before_deletion - Decimal('10'))

    def test_stock_history_created_on_creation(self):
        """Test that ProductStockHistory entry is created when batch is created"""
        initial_history_count = ProductStockHistory.objects.count()
        batch = ProductBatch.objects.create(
            product_id=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        # Should have at least one new history entry
        self.assertGreater(ProductStockHistory.objects.count(), initial_history_count)

    def test_mark_expired_method(self):
        """Test mark_expired method"""
        batch = ProductBatch.objects.create(
            product_id=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        self.assertEqual(batch.status, 'active')
        
        batch.mark_expired()
        batch.refresh_from_db()
        self.assertEqual(batch.status, 'expired')

    def test_use_batch_method(self):
        """Test use_batch method for consuming batch"""
        batch = ProductBatch.objects.create(
            product_id=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        stock_before = self.product.current_stock

        # Use 3 units from batch
        batch.use_batch(Decimal('3'), 'Testing')
        batch.refresh_from_db()
        
        self.product.refresh_from_db()
        # Stock should be reduced by 3
        self.assertEqual(self.product.current_stock, stock_before - Decimal('3'))


class ProductBatchAPITestCase(APITestCase):
    """Test suite for ProductBatch API endpoints"""

    def setUp(self):
        """Set up test client and data"""
        self.client = APIClient()

        # Create users with different roles
        self.baker = User.objects.create_user(
            username='baker1',
            password='testpass123',
            role='baker'
        )
        
        self.manager = User.objects.create_user(
            username='manager1',
            password='testpass123',
            role='manager'
        )

        self.storekeeper = User.objects.create_user(
            username='storekeeper1',
            password='testpass123',
            role='storekeeper'
        )

        self.cashier = User.objects.create_user(
            username='cashier1',
            password='testpass123',
            role='cashier'
        )

        # Create category and product
        self.category = Category.objects.create(
            name='Bread',
            description='Bread products',
            type='Product'
        )

        self.product = Product.objects.create(
            name='Sourdough Bread',
            category_id=self.category,
            cost_price=Decimal('2.50'),
            selling_price=Decimal('5.00'),
            shelf_life=2,
            shelf_unit='days',
            current_stock=Decimal('0.00')
        )

    def test_create_batch_as_baker(self):
        """Test that baker can create a batch"""
        self.client.force_authenticate(user=self.baker)
        
        payload = {
            'product_id': self.product.id,
            'quantity': '10',
            'made_date': date.today().isoformat()
        }
        
        response = self.client.post('/api/product-batches/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['batch_id'], 'PROD-BATCH-1001')

    def test_create_batch_as_manager(self):
        """Test that manager can create a batch"""
        self.client.force_authenticate(user=self.manager)
        
        payload = {
            'product_id': self.product.id,
            'quantity': '15',
            'made_date': date.today().isoformat()
        }
        
        response = self.client.post('/api/product-batches/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_batch_as_storekeeper_fails(self):
        """Test that storekeeper cannot create a batch"""
        self.client.force_authenticate(user=self.storekeeper)
        
        payload = {
            'product_id': self.product.id,
            'quantity': '10',
            'made_date': date.today().isoformat()
        }
        
        response = self.client.post('/api/product-batches/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_batch_as_cashier_fails(self):
        """Test that cashier cannot create a batch"""
        self.client.force_authenticate(user=self.cashier)
        
        payload = {
            'product_id': self.product.id,
            'quantity': '10',
            'made_date': date.today().isoformat()
        }
        
        response = self.client.post('/api/product-batches/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_batch_without_authentication_fails(self):
        """Test that unauthenticated user cannot create a batch"""
        payload = {
            'product_id': self.product.id,
            'quantity': '10',
            'made_date': date.today().isoformat()
        }
        
        response = self.client.post('/api/product-batches/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_batches_as_baker(self):
        """Test that baker can list batches"""
        # Create a batch first
        ProductBatch.objects.create(
            product=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        
        self.client.force_authenticate(user=self.baker)
        response = self.client.get('/api/product-batches/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_batches_as_storekeeper(self):
        """Test that storekeeper can list batches"""
        ProductBatch.objects.create(
            product=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        
        self.client.force_authenticate(user=self.storekeeper)
        response = self.client.get('/api/product-batches/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_batch_detail(self):
        """Test retrieving batch details"""
        batch = ProductBatch.objects.create(
            product=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        
        self.client.force_authenticate(user=self.baker)
        response = self.client.get(f'/api/product-batches/{batch.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['batch_id'], 'PROD-BATCH-1001')
        self.assertEqual(response.data['quantity'], '10.00')

    def test_update_batch_as_baker(self):
        """Test that baker can update a batch"""
        batch = ProductBatch.objects.create(
            product=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        
        self.client.force_authenticate(user=self.baker)
        payload = {
            'quantity': '15',
            'notes': 'Updated quantity'
        }
        
        response = self.client.patch(
            f'/api/product-batches/{batch.id}/',
            payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        batch.refresh_from_db()
        self.assertEqual(batch.quantity, Decimal('15'))

    def test_update_batch_as_storekeeper_fails(self):
        """Test that storekeeper cannot update a batch"""
        batch = ProductBatch.objects.create(
            product=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        
        self.client.force_authenticate(user=self.storekeeper)
        payload = {'quantity': '15'}
        
        response = self.client.patch(
            f'/api/product-batches/{batch.id}/',
            payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_batch_as_manager(self):
        """Test that manager can delete a batch"""
        batch = ProductBatch.objects.create(
            product=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        
        self.client.force_authenticate(user=self.manager)
        response = self.client.delete(f'/api/product-batches/{batch.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ProductBatch.objects.filter(id=batch.id).exists())

    def test_delete_batch_as_baker_fails(self):
        """Test that baker cannot delete a batch"""
        batch = ProductBatch.objects.create(
            product=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        
        self.client.force_authenticate(user=self.baker)
        response = self.client.delete(f'/api/product-batches/{batch.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_batch_as_storekeeper_fails(self):
        """Test that storekeeper cannot delete a batch"""
        batch = ProductBatch.objects.create(
            product=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        
        self.client.force_authenticate(user=self.storekeeper)
        response = self.client.delete(f'/api/product-batches/{batch.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_expiring_batches(self):
        """Test getting batches that are expiring soon"""
        # Create batch that expires tomorrow (expiring soon)
        made_date = date.today() - timedelta(days=1)
        batch1 = ProductBatch.objects.create(
            product=self.product,
            quantity=Decimal('10'),
            made_date=made_date
        )
        
        # Create fresh batch (not expiring soon)
        batch2 = ProductBatch.objects.create(
            product=self.product,
            quantity=Decimal('5'),
            made_date=date.today()
        )
        
        self.client.force_authenticate(user=self.baker)
        response = self.client.get('/api/product-batches/expiring/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should contain batch1 which is expiring soon
        self.assertTrue(any(b['id'] == batch1.id for b in response.data))

    def test_use_batch_endpoint(self):
        """Test using batch quantity endpoint"""
        batch = ProductBatch.objects.create(
            product=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        
        self.client.force_authenticate(user=self.baker)
        payload = {
            'quantity_used': '3',
            'reason': 'Production use'
        }
        
        response = self.client.post(
            f'/api/product-batches/{batch.id}/use_batch/',
            payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_product_batches(self):
        """Test getting all batches for a specific product"""
        # Create multiple batches
        ProductBatch.objects.create(
            product=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        ProductBatch.objects.create(
            product=self.product,
            quantity=Decimal('5'),
            made_date=date.today()
        )
        
        self.client.force_authenticate(user=self.baker)
        response = self.client.get(
            f'/api/product-batches/product/{self.product.id}/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should have 2 batches for this product
        batches = response.data if isinstance(response.data, list) else response.data.get('results', [])
        self.assertEqual(len(batches), 2)

    def test_batch_summary_endpoint(self):
        """Test batch summary statistics endpoint"""
        # Create batches
        ProductBatch.objects.create(
            product=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        
        self.client.force_authenticate(user=self.baker)
        response = self.client.get('/api/product-batches/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_quantity_fails(self):
        """Test that invalid quantity is rejected"""
        self.client.force_authenticate(user=self.baker)
        
        payload = {
            'product_id': self.product.id,
            'quantity': '-10',  # Negative quantity
            'made_date': date.today().isoformat()
        }
        
        response = self.client.post('/api/product-batches/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_future_made_date_fails(self):
        """Test that future made_date is rejected"""
        self.client.force_authenticate(user=self.baker)
        
        future_date = (date.today() + timedelta(days=1)).isoformat()
        payload = {
            'product': self.product.id,
            'quantity': '10',
            'made_date': future_date
        }
        
        response = self.client.post('/api/product-batches/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_product_fails(self):
        """Test that nonexistent product is rejected"""
        self.client.force_authenticate(user=self.baker)
        
        payload = {
            'product_id': 9999,  # Non-existent product
            'quantity': '10',
            'made_date': date.today().isoformat()
        }
        
        response = self.client.post('/api/product-batches/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProductBatchStockManagementTestCase(APITestCase):
    """Test suite for stock management through batches"""

    def setUp(self):
        """Set up test data"""
        self.baker = User.objects.create_user(
            username='baker1',
            password='testpass123',
            role='baker'
        )
        
        self.manager = User.objects.create_user(
            username='manager1',
            password='testpass123',
            role='manager'
        )

        self.category = Category.objects.create(
            name='Bread',
            description='Bread products',
            type='Product'
        )

        self.product = Product.objects.create(
            name='Sourdough Bread',
            category_id=self.category,
            cost_price=Decimal('2.50'),
            selling_price=Decimal('5.00'),
            shelf_life=2,
            shelf_unit='days',
            current_stock=Decimal('0.00')
        )

    def test_stock_increases_with_batch_creation(self):
        """Test that product stock increases when batch is created"""
        self.client.force_authenticate(user=self.baker)
        
        initial_stock = self.product.current_stock
        
        payload = {
            'product_id': self.product.id,
            'quantity': '10',
            'made_date': date.today().isoformat()
        }
        
        response = self.client.post('/api/product-batches/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, initial_stock + Decimal('10'))

    def test_stock_decreases_with_batch_deletion(self):
        """Test that product stock decreases when batch is deleted"""
        # Create batch first
        batch = ProductBatch.objects.create(
            product=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        stock_after_creation = self.product.current_stock
        
        # Delete batch
        self.client.force_authenticate(user=self.manager)
        response = self.client.delete(f'/api/product-batches/{batch.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.product.refresh_from_db()
        self.assertEqual(
            self.product.current_stock,
            stock_after_creation - Decimal('10')
        )

    def test_multiple_batches_stock_accumulation(self):
        """Test that stock accumulates with multiple batches"""
        self.client.force_authenticate(user=self.baker)
        
        batches_count = 3
        quantity_per_batch = Decimal('10')
        
        for i in range(batches_count):
            payload = {
                'product': self.product.id,
                'quantity': str(quantity_per_batch),
                'made_date': date.today().isoformat()
            }
            self.client.post('/api/product-batches/', payload, format='json')
        
        self.product.refresh_from_db()
        expected_stock = quantity_per_batch * batches_count
        self.assertEqual(self.product.current_stock, expected_stock)


class ProductBatchAuditTrailTestCase(APITestCase):
    """Test suite for audit trail (ProductStockHistory) integration"""

    def setUp(self):
        """Set up test data"""
        self.baker = User.objects.create_user(
            username='baker1',
            password='testpass123',
            role='baker'
        )

        self.category = Category.objects.create(
            name='Bread',
            description='Bread products',
            type='Product'
        )

        self.product = Product.objects.create(
            name='Sourdough Bread',
            category_id=self.category,
            cost_price=Decimal('2.50'),
            selling_price=Decimal('5.00'),
            shelf_life=2,
            shelf_unit='days',
            current_stock=Decimal('0.00')
        )

    def test_stock_history_created_on_batch_creation(self):
        """Test that ProductStockHistory entry is created when batch is created"""
        self.client.force_authenticate(user=self.baker)
        
        initial_count = ProductStockHistory.objects.count()
        
        payload = {
            'product_id': self.product.id,
            'quantity': '10',
            'made_date': date.today().isoformat()
        }
        
        self.client.post('/api/product-batches/', payload, format='json')
        
        # Should have created a history entry
        self.assertGreater(ProductStockHistory.objects.count(), initial_count)

    def test_stock_history_created_on_batch_deletion(self):
        """Test that ProductStockHistory entry is created when batch is deleted"""
        batch = ProductBatch.objects.create(
            product=self.product,
            quantity=Decimal('10'),
            made_date=date.today()
        )
        
        self.client.force_authenticate(user=self.baker)
        
        initial_count = ProductStockHistory.objects.count()
        
        # Delete requires manager role
        self.client.force_authenticate(user=User.objects.create_user(
            username='manager1',
            password='testpass123',
            role='manager'
        ))
        
        self.client.delete(f'/api/product-batches/{batch.id}/')
        
        # Should have created additional history entries
        self.assertGreater(ProductStockHistory.objects.count(), initial_count)
