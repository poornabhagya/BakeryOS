from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import timedelta
from decimal import Decimal
from api.models import User, Sale, SaleItem, Product, Category, Discount, ProductStockHistory


class SaleModelTests(TestCase):
    """Test Sale model functionality"""
    
    def setUp(self):
        """Create test data"""
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='pass123',
            full_name='Test Manager',
            role='Manager'
        )
        
        self.cashier = User.objects.create_user(
            username='cashier',
            email='cashier@test.com',
            password='pass123',
            full_name='Test Cashier',
            role='Cashier'
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            type='Product',
            description='Test'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            category_id=self.category,
            selling_price=Decimal('100.00'),
            cost_price=Decimal('50.00'),
            current_stock=Decimal('50.00')
        )
        
        self.discount = Discount.objects.create(
            name='Test Discount',
            discount_type='Percentage',
            value=Decimal('10.00'),
            applicable_to='All',
            is_active=True
        )
    
    def test_sale_creation_with_auto_bill_number(self):
        """Test that bill_number is auto-generated"""
        sale = Sale.objects.create(
            cashier_id=self.cashier,
            subtotal=Decimal('100.00'),
            discount_amount=Decimal('0.00'),
            total_amount=Decimal('100.00'),
            payment_method='Cash'
        )
        
        self.assertIsNotNone(sale.bill_number)
        self.assertTrue(sale.bill_number.startswith('BILL-'))
        self.assertEqual(sale.total_amount, Decimal('100.00'))
    
    def test_sale_bill_number_sequential(self):
        """Test that bill numbers are sequential"""
        sale1 = Sale.objects.create(
            cashier_id=self.cashier,
            subtotal=Decimal('100.00'),
            discount_amount=Decimal('0.00'),
            total_amount=Decimal('100.00'),
            payment_method='Cash'
        )
        
        sale2 = Sale.objects.create(
            cashier_id=self.cashier,
            subtotal=Decimal('200.00'),
            discount_amount=Decimal('0.00'),
            total_amount=Decimal('200.00'),
            payment_method='Cash'
        )
        
        bill1_num = int(sale1.bill_number.split('-')[1])
        bill2_num = int(sale2.bill_number.split('-')[1])
        
        self.assertLess(bill1_num, bill2_num)
    
    def test_sale_with_discount(self):
        """Test sale with discount"""
        sale = Sale.objects.create(
            cashier_id=self.cashier,
            subtotal=Decimal('100.00'),
            discount_id=self.discount,
            discount_amount=Decimal('10.00'),
            total_amount=Decimal('90.00'),
            payment_method='Cash'
        )
        
        self.assertEqual(sale.discount_amount, Decimal('10.00'))
        self.assertEqual(sale.total_amount, Decimal('90.00'))
    
    def test_sale_payment_methods(self):
        """Test all payment methods"""
        payment_methods = ['Cash', 'Card', 'Mobile', 'Cheque', 'Other']
        
        for method in payment_methods:
            sale = Sale.objects.create(
                cashier_id=self.cashier,
                subtotal=Decimal('100.00'),
                discount_amount=Decimal('0.00'),
                total_amount=Decimal('100.00'),
                payment_method=method
            )
            
            self.assertEqual(sale.payment_method, method)
    
    def test_sale_with_notes(self):
        """Test sale with optional notes"""
        sale = Sale.objects.create(
            cashier_id=self.cashier,
            subtotal=Decimal('100.00'),
            discount_amount=Decimal('0.00'),
            total_amount=Decimal('100.00'),
            payment_method='Cash',
            notes='Special order - delivery address on file'
        )
        
        self.assertEqual(sale.notes, 'Special order - delivery address on file')
    
    def test_sale_timestamps(self):
        """Test that timestamps are set correctly"""
        before = timezone.now()
        sale = Sale.objects.create(
            cashier_id=self.cashier,
            subtotal=Decimal('100.00'),
            discount_amount=Decimal('0.00'),
            total_amount=Decimal('100.00'),
            payment_method='Cash'
        )
        after = timezone.now()
        
        self.assertGreaterEqual(sale.created_at, before)
        self.assertLessEqual(sale.created_at, after)
        self.assertGreaterEqual(sale.updated_at, before)
        self.assertLessEqual(sale.updated_at, after)


class SaleItemModelTests(TestCase):
    """Test SaleItem model functionality"""
    
    def setUp(self):
        """Create test data"""
        self.cashier = User.objects.create_user(
            username='cashier',
            email='cashier@test.com',
            password='pass123',
            full_name='Test Cashier',
            role='Cashier'
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            type='Product',
            description='Test'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            category_id=self.category,
            selling_price=Decimal('100.00'),
            cost_price=Decimal('50.00'),
            current_stock=Decimal('50.00')
        )
        
        self.sale = Sale.objects.create(
            cashier_id=self.cashier,
            subtotal=Decimal('100.00'),
            discount_amount=Decimal('0.00'),
            total_amount=Decimal('100.00'),
            payment_method='Cash'
        )
    
    def test_sale_item_creation(self):
        """Test basic SaleItem creation"""
        item = SaleItem.objects.create(
            sale_id=self.sale,
            product_id=self.product,
            quantity=Decimal('2.00'),
            unit_price=Decimal('100.00')
        )
        
        self.assertEqual(item.quantity, Decimal('2.00'))
        self.assertEqual(item.unit_price, Decimal('100.00'))
        self.assertEqual(item.subtotal, Decimal('200.00'))
    
    def test_sale_item_subtotal_calculation(self):
        """Test that subtotal is auto-calculated"""
        item = SaleItem.objects.create(
            sale_id=self.sale,
            product_id=self.product,
            quantity=Decimal('3.00'),
            unit_price=Decimal('50.00')
        )
        
        self.assertEqual(item.subtotal, Decimal('150.00'))
    
    def test_sale_item_decimal_quantities(self):
        """Test SaleItem with decimal quantities (e.g., bulk items)"""
        item = SaleItem.objects.create(
            sale_id=self.sale,
            product_id=self.product,
            quantity=Decimal('2.5'),
            unit_price=Decimal('100.00')
        )
        
        self.assertEqual(item.subtotal, Decimal('250.00'))
    
    def test_sale_items_cascade_delete(self):
        """Test that items are deleted when sale is deleted"""
        item = SaleItem.objects.create(
            sale_id=self.sale,
            product_id=self.product,
            quantity=Decimal('1.00'),
            unit_price=Decimal('100.00')
        )
        
        sale_id = self.sale.id
        self.sale.delete()
        
        self.assertFalse(SaleItem.objects.filter(sale_id=sale_id).exists())


class SaleAPITests(APITestCase):
    """Test Sale API endpoints"""
    
    def setUp(self):
        """Create test data"""
        self.client = APIClient()
        
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='pass123',
            full_name='Test Manager',
            role='Manager'
        )
        
        self.cashier1 = User.objects.create_user(
            username='cashier1',
            email='cashier1@test.com',
            password='pass123',
            full_name='Cashier One',
            role='Cashier'
        )
        
        self.cashier2 = User.objects.create_user(
            username='cashier2',
            email='cashier2@test.com',
            password='pass123',
            full_name='Cashier Two',
            role='Cashier'
        )
        
        self.baker = User.objects.create_user(
            username='baker',
            email='baker@test.com',
            password='pass123',
            full_name='Test Baker',
            role='Baker'
        )
        
        self.category = Category.objects.create(
            name='Pastries',
            type='Product',
            description='Baked goods'
        )
        
        self.product1 = Product.objects.create(
            name='Croissant',
            category_id=self.category,
            selling_price=Decimal('50.00'),
            cost_price=Decimal('25.00'),
            current_stock=Decimal('100.00')
        )
        
        self.product2 = Product.objects.create(
            name='Muffin',
            category_id=self.category,
            selling_price=Decimal('30.00'),
            cost_price=Decimal('15.00'),
            current_stock=Decimal('200.00')
        )
        
        self.discount = Discount.objects.create(
            name='Happy Hour',
            discount_type='Percentage',
            value=Decimal('10.00'),
            applicable_to='All',
            is_active=True
        )
    
    def test_create_sale_as_cashier(self):
        """Test creating a sale as cashier"""
        self.client.force_authenticate(user=self.cashier1)
        
        data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': Decimal('2.00'),
                    'unit_price': Decimal('50.00')
                }
            ],
            'payment_method': 'Cash'
        }
        
        response = self.client.post('/api/sales/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('bill_number', response.data)
        self.assertTrue(response.data['bill_number'].startswith('BILL-'))
    
    def test_create_sale_with_discount(self):
        """Test creating a sale with discount"""
        self.client.force_authenticate(user=self.cashier1)
        
        data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': Decimal('2.00'),
                    'unit_price': Decimal('50.00')
                }
            ],
            'discount_id': self.discount.id,
            'payment_method': 'Cash'
        }
        
        response = self.client.post('/api/sales/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['discount_id'])
        self.assertGreater(float(response.data['discount_amount']), 0)
    
    def test_create_sale_deducts_stock(self):
        """Test that creating a sale deducts from product stock"""
        initial_stock = self.product1.current_stock
        
        self.client.force_authenticate(user=self.cashier1)
        
        data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': Decimal('5.00'),
                    'unit_price': Decimal('50.00')
                }
            ],
            'payment_method': 'Cash'
        }
        
        response = self.client.post('/api/sales/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify stock was deducted
        self.product1.refresh_from_db()
        self.assertEqual(
            self.product1.current_stock,
            initial_stock - Decimal('5.00')
        )
    
    def test_create_sale_creates_audit_trail(self):
        """Test that creating a sale creates ProductStockHistory entries"""
        self.client.force_authenticate(user=self.cashier1)
        
        data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': Decimal('3.00'),
                    'unit_price': Decimal('50.00')
                }
            ],
            'payment_method': 'Cash'
        }
        
        response = self.client.post('/api/sales/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify audit trail was created
        history = ProductStockHistory.objects.filter(
            product_id=self.product1,
            transaction_type='UseStock'
        )
        
        self.assertTrue(history.exists())
        self.assertEqual(history.count(), 1)
    
    def test_create_sale_multiple_items(self):
        """Test creating a sale with multiple items"""
        self.client.force_authenticate(user=self.cashier1)
        
        data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': Decimal('2.00'),
                    'unit_price': Decimal('50.00')
                },
                {
                    'product_id': self.product2.id,
                    'quantity': Decimal('3.00'),
                    'unit_price': Decimal('30.00')
                }
            ],
            'payment_method': 'Card'
        }
        
        response = self.client.post('/api/sales/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['item_count'], 2)
        self.assertEqual(response.data['subtotal'], '190.00')
    
    def test_create_sale_invalid_items_empty(self):
        """Test creating sale with empty items list fails"""
        self.client.force_authenticate(user=self.cashier1)
        
        data = {
            'items': [],
            'payment_method': 'Cash'
        }
        
        response = self.client.post('/api/sales/', data, format='json')
        
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_201_CREATED])
    
    def test_create_sale_invalid_items_too_many(self):
        """Test creating sale with too many items fails"""
        self.client.force_authenticate(user=self.cashier1)
        
        items = [
            {
                'product_id': self.product1.id,
                'quantity': Decimal('1.00'),
                'unit_price': Decimal('50.00')
            }
        ] * 101  # More than max of 100
        
        data = {
            'items': items,
            'payment_method': 'Cash'
        }
        
        response = self.client.post('/api/sales/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_sale_manager_and_cashier_can_create(self):
        """Test that both Manager and Cashier can create sales (Manager is backup)"""
        # Test Manager can create sale
        self.client.force_authenticate(user=self.manager)
        
        data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': Decimal('1.00'),
                    'unit_price': Decimal('50.00')
                }
            ],
            'payment_method': 'Cash'
        }
        
        response = self.client.post('/api/sales/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['bill_number'])
        
        # Test Cashier can create sale
        self.client.force_authenticate(user=self.cashier1)
        
        data2 = {
            'items': [
                {
                    'product_id': self.product2.id,
                    'quantity': Decimal('2.00'),
                    'unit_price': Decimal('30.00')
                }
            ],
            'payment_method': 'Card'
        }
        
        response2 = self.client.post('/api/sales/', data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response2.data['bill_number'])
    
    def test_list_sales_all_as_manager(self):
        """Test that manager can see all sales"""
        # Create sales from different cashiers
        self.client.force_authenticate(user=self.cashier1)
        
        data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': Decimal('1.00'),
                    'unit_price': Decimal('50.00')
                }
            ],
            'payment_method': 'Cash'
        }
        
        self.client.post('/api/sales/', data, format='json')
        
        # Switch to cashier2 and create another sale
        self.client.force_authenticate(user=self.cashier2)
        self.client.post('/api/sales/', data, format='json')
        
        # Manager should see both
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/sales/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 2)
    
    def test_list_sales_own_as_cashier(self):
        """Test that cashier can only see own sales"""
        # Cashier1 creates a sale
        self.client.force_authenticate(user=self.cashier1)
        
        data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': Decimal('1.00'),
                    'unit_price': Decimal('50.00')
                }
            ],
            'payment_method': 'Cash'
        }
        
        self.client.post('/api/sales/', data, format='json')
        
        # Switch to cashier2 and create another sale
        self.client.force_authenticate(user=self.cashier2)
        self.client.post('/api/sales/', data, format='json')
        
        # Cashier1 should only see own sale
        self.client.force_authenticate(user=self.cashier1)
        response = self.client.get('/api/sales/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_get_sale_detail(self):
        """Test retrieving sale detail"""
        self.client.force_authenticate(user=self.cashier1)
        
        data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': Decimal('2.00'),
                    'unit_price': Decimal('50.00')
                }
            ],
            'payment_method': 'Cash'
        }
        
        create_response = self.client.post('/api/sales/', data, format='json')
        sale_id = create_response.data['id']
        
        detail_response = self.client.get(f'/api/sales/{sale_id}/')
        
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data['id'], sale_id)
        self.assertIn('items', detail_response.data)
    
    def test_get_active_sales(self):
        """Test getting today's sales"""
        self.client.force_authenticate(user=self.cashier1)
        
        data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': Decimal('1.00'),
                    'unit_price': Decimal('50.00')
                }
            ],
            'payment_method': 'Cash'
        }
        
        self.client.post('/api/sales/', data, format='json')
        
        response = self.client.get('/api/sales/active/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    def test_get_sales_by_date_range(self):
        """Test filtering sales by date range"""
        self.client.force_authenticate(user=self.cashier1)
        
        data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': Decimal('1.00'),
                    'unit_price': Decimal('50.00')
                }
            ],
            'payment_method': 'Cash'
        }
        
        self.client.post('/api/sales/', data, format='json')
        
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        response = self.client.get(
            f'/api/sales/date-range/?start_date={today}&end_date={tomorrow}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_sales_by_payment_method(self):
        """Test filtering sales by payment method"""
        self.client.force_authenticate(user=self.cashier1)
        
        # Create sales with different payment methods
        for method in ['Cash', 'Card']:
            data = {
                'items': [
                    {
                        'product_id': self.product1.id,
                        'quantity': Decimal('1.00'),
                        'unit_price': Decimal('50.00')
                    }
                ],
                'payment_method': method
            }
            
            self.client.post('/api/sales/', data, format='json')
        
        response = self.client.get('/api/sales/payment-method/?payment_method=Cash')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_analytics_manager_only(self):
        """Test that analytics endpoint is manager only"""
        self.client.force_authenticate(user=self.cashier1)
        
        response = self.client.get('/api/sales/analytics/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_analytics_data(self):
        """Test analytics endpoint returns correct data"""
        self.client.force_authenticate(user=self.cashier1)
        
        # Create multiple sales
        for i in range(3):
            data = {
                'items': [
                    {
                        'product_id': self.product1.id,
                        'quantity': Decimal('1.00'),
                        'unit_price': Decimal('50.00')
                    }
                ],
                'payment_method': 'Cash'
            }
            
            self.client.post('/api/sales/', data, format='json')
        
        # Get analytics as manager
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/sales/analytics/?period=today')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('overall', response.data)
        self.assertEqual(response.data['overall']['total_sales'], 3)
    
    def test_get_cashier_sales(self):
        """Test getting specific cashier's sales"""
        self.client.force_authenticate(user=self.cashier1)
        
        data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': Decimal('2.00'),
                    'unit_price': Decimal('50.00')
                }
            ],
            'payment_method': 'Cash'
        }
        
        self.client.post('/api/sales/', data, format='json')
        
        # Get cashier1's sales as manager
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(f'/api/sales/cashier/{self.cashier1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('cashier_name', response.data)
    
    def test_sale_uses_request_cashier_if_not_provided(self):
        """Test that sale uses request.user as cashier if not provided"""
        self.client.force_authenticate(user=self.cashier1)
        
        data = {
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity': Decimal('1.00'),
                    'unit_price': Decimal('50.00')
                }
            ],
            'payment_method': 'Cash'
        }
        
        response = self.client.post('/api/sales/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['cashier_id'], self.cashier1.id)


class SaleEdgeCaseTests(TransactionTestCase):
    """Test edge cases and error scenarios"""
    
    def setUp(self):
        """Create test data"""
        self.cashier = User.objects.create_user(
            username='cashier',
            email='cashier@test.com',
            password='pass123',
            full_name='Test Cashier',
            role='Cashier'
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            type='Product',
            description='Test'
        )
        
        self.product = Product.objects.create(
            name='Limited Stock Product',
            category_id=self.category,
            selling_price=Decimal('100.00'),
            cost_price=Decimal('50.00'),
            current_stock=Decimal('5.00')
        )
        
        self.client = APIClient()
    
    def test_sale_with_insufficient_stock(self):
        """Test creating sale with insufficient stock doesn't prevent creation"""
        self.client.force_authenticate(user=self.cashier)
        
        # Try to sell more than available stock
        data = {
            'items': [
                {
                    'product_id': self.product.id,
                    'quantity': Decimal('10.00'),
                    'unit_price': Decimal('100.00')
                }
            ],
            'payment_method': 'Cash'
        }
        
        response = self.client.post('/api/sales/', data, format='json')
        
        # Should succeed (business logic allows overselling)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_sale_with_non_existent_product(self):
        """Test creating sale with non-existent product"""
        self.client.force_authenticate(user=self.cashier)
        
        data = {
            'items': [
                {
                    'product_id': 999999,
                    'quantity': Decimal('1.00'),
                    'unit_price': Decimal('100.00')
                }
            ],
            'payment_method': 'Cash'
        }
        
        response = self.client.post('/api/sales/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_sale_with_invalid_quantity(self):
        """Test creating sale with invalid quantity"""
        self.client.force_authenticate(user=self.cashier)
        
        data = {
            'items': [
                {
                    'product_id': self.product.id,
                    'quantity': Decimal('0.00'),  # Invalid
                    'unit_price': Decimal('100.00')
                }
            ],
            'payment_method': 'Cash'
        }
        
        response = self.client.post('/api/sales/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_sale_with_invalid_price(self):
        """Test creating sale with invalid price"""
        self.client.force_authenticate(user=self.cashier)
        
        data = {
            'items': [
                {
                    'product_id': self.product.id,
                    'quantity': Decimal('1.00'),
                    'unit_price': Decimal('-50.00')  # Invalid
                }
            ],
            'payment_method': 'Cash'
        }
        
        response = self.client.post('/api/sales/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
