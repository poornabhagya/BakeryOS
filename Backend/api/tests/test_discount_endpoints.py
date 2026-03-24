from django.test import TestCase
from django.utils import timezone
from datetime import datetime, time, timedelta
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User, Category, Product, Discount
from core.settings import AUTH_USER_MODEL


class DiscountModelTestCase(TestCase):
    """Test Discount model functionality, validation, and auto-ID generation"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name='Breads', description='All breads', type='Product')
        self.product = Product.objects.create(
            name='Naan',
            description='Indian bread',
            cost_price=20.00,
            selling_price=50.00,
            category_id=self.category
        )
    
    def test_discount_auto_id_generation(self):
        """Test auto-generation of discount_id with proper format (DISC-001, DISC-002, etc)"""
        discount1 = Discount.objects.create(
            name='First Discount',
            discount_type='Percentage',
            value=10,
            applicable_to='All'
        )
        self.assertEqual(discount1.discount_id, 'DISC-001')
        
        discount2 = Discount.objects.create(
            name='Second Discount',
            discount_type='Percentage',
            value=15,
            applicable_to='All'
        )
        self.assertEqual(discount2.discount_id, 'DISC-002')
    
    def test_discount_auto_id_preserves_existing(self):
        """Test that creating a new discount gets the next ID after existing ones"""
        Discount.objects.create(
            name='Discount 1',
            discount_type='Percentage',
            value=10,
            applicable_to='All'
        )
        Discount.objects.create(
            name='Discount 2',
            discount_type='Percentage',
            value=15,
            applicable_to='All'
        )
        discount3 = Discount.objects.create(
            name='Discount 3',
            discount_type='Percentage',
            value=20,
            applicable_to='All'
        )
        self.assertEqual(discount3.discount_id, 'DISC-003')
    
    def test_view_discount_by_id(self):
        """Test retrieving specific discount"""
        discount = Discount.objects.create(
            name='Test Discount',
            discount_type='Percentage',
            value=10,
            applicable_to='All'
        )
        retrieved = Discount.objects.get(id=discount.id)
        self.assertEqual(retrieved.name, 'Test Discount')
    
    def test_percentage_discount_validation_valid(self):
        """Test percentage discount with valid value (0-100)"""
        discount = Discount.objects.create(
            name='Valid Percentage Discount',
            discount_type='Percentage',
            value=50,
            applicable_to='All'
        )
        self.assertEqual(discount.value, 50)
        self.assertEqual(discount.discount_type, 'Percentage')
    
    def test_percentage_discount_validation_min(self):
        """Test percentage discount with minimum valid value"""
        discount = Discount.objects.create(
            name='Min Percentage Discount',
            discount_type='Percentage',
            value=1,
            applicable_to='All'
        )
        self.assertEqual(discount.value, 1)
    
    def test_percentage_discount_validation_max(self):
        """Test percentage discount with maximum valid value"""
        discount = Discount.objects.create(
            name='Max Percentage Discount',
            discount_type='Percentage',
            value=100,
            applicable_to='All'
        )
        self.assertEqual(discount.value, 100)
    
    def test_fixed_amount_discount_validation_valid(self):
        """Test fixed amount discount with valid positive value"""
        discount = Discount.objects.create(
            name='Valid Fixed Amount Discount',
            discount_type='FixedAmount',
            value=100,
            applicable_to='All'
        )
        self.assertEqual(discount.value, 100)
        self.assertEqual(discount.discount_type, 'FixedAmount')
    
    def test_fixed_amount_discount_validation_decimal(self):
        """Test fixed amount discount with decimal value"""
        discount = Discount.objects.create(
            name='Decimal Fixed Amount Discount',
            discount_type='FixedAmount',
            value=49.99,
            applicable_to='All'
        )
        self.assertEqual(discount.value, 49.99)
    
    def test_date_validation_valid_range(self):
        """Test discount with valid date range"""
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        discount = Discount.objects.create(
            name='Valid Date Range',
            discount_type='Percentage',
            value=10,
            applicable_to='All',
            start_date=today,
            end_date=tomorrow
        )
        self.assertEqual(discount.start_date, today)
        self.assertEqual(discount.end_date, tomorrow)
    
    def test_date_validation_same_date(self):
        """Test discount with start_date == end_date (valid)"""
        today = timezone.now().date()
        discount = Discount.objects.create(
            name='Same Date Range',
            discount_type='Percentage',
            value=10,
            applicable_to='All',
            start_date=today,
            end_date=today
        )
        self.assertEqual(discount.start_date, discount.end_date)
    
    def test_time_validation_valid_range(self):
        """Test discount with valid time range"""
        start_time = time(9, 0)  # 9 AM
        end_time = time(17, 0)   # 5 PM
        discount = Discount.objects.create(
            name='Valid Time Range',
            discount_type='Percentage',
            value=10,
            applicable_to='All',
            start_time=start_time,
            end_time=end_time
        )
        self.assertEqual(discount.start_time, start_time)
        self.assertEqual(discount.end_time, end_time)
    
    def test_time_validation_null_allowed(self):
        """Test that time fields can be null (no time restrictions)"""
        discount = Discount.objects.create(
            name='No Time Restriction',
            discount_type='Percentage',
            value=10,
            applicable_to='All',
            start_time=None,
            end_time=None
        )
        self.assertIsNone(discount.start_time)
        self.assertIsNone(discount.end_time)
    
    def test_applicable_to_all(self):
        """Test discount applicable to all products"""
        discount = Discount.objects.create(
            name='Apply to All',
            discount_type='Percentage',
            value=10,
            applicable_to='All'
        )
        self.assertEqual(discount.applicable_to, 'All')
        self.assertIsNone(discount.target_category_id)
        self.assertIsNone(discount.target_product_id)
    
    def test_applicable_to_category(self):
        """Test discount applicable to specific category"""
        discount = Discount.objects.create(
            name='Apply to Category',
            discount_type='Percentage',
            value=10,
            applicable_to='Category',
            target_category_id=self.category
        )
        self.assertEqual(discount.applicable_to, 'Category')
        self.assertEqual(discount.target_category_id, self.category)
        self.assertIsNone(discount.target_product_id)
    
    def test_applicable_to_product(self):
        """Test discount applicable to specific product"""
        discount = Discount.objects.create(
            name='Apply to Product',
            discount_type='Percentage',
            value=10,
            applicable_to='Product',
            target_product_id=self.product
        )
        self.assertEqual(discount.applicable_to, 'Product')
        self.assertEqual(discount.target_product_id, self.product)
        self.assertIsNone(discount.target_category_id)
    
    def test_is_active_toggle(self):
        """Test is_active flag can be toggled"""
        discount = Discount.objects.create(
            name='Toggle Active',
            discount_type='Percentage',
            value=10,
            applicable_to='All',
            is_active=True
        )
        self.assertTrue(discount.is_active)
        discount.is_active = False
        discount.save()
        refreshed = Discount.objects.get(id=discount.id)
        self.assertFalse(refreshed.is_active)
    
    def test_is_applicable_now_within_date_range(self):
        """Test is_applicable_now() returns True for current date within range"""
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        discount = Discount.objects.create(
            name='Current Date Discount',
            discount_type='Percentage',
            value=10,
            applicable_to='All',
            start_date=today,
            end_date=tomorrow,
            is_active=True
        )
        self.assertTrue(discount.is_applicable_now())
    
    def test_is_applicable_now_past_date(self):
        """Test is_applicable_now() returns False for past end_date"""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)
        discount = Discount.objects.create(
            name='Past Discount',
            discount_type='Percentage',
            value=10,
            applicable_to='All',
            start_date=two_days_ago,
            end_date=yesterday,
            is_active=True
        )
        self.assertFalse(discount.is_applicable_now())
    
    def test_is_applicable_now_future_date(self):
        """Test is_applicable_now() returns False for future start_date"""
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        day_after = today + timedelta(days=2)
        discount = Discount.objects.create(
            name='Future Discount',
            discount_type='Percentage',
            value=10,
            applicable_to='All',
            start_date=tomorrow,
            end_date=day_after,
            is_active=True
        )
        self.assertFalse(discount.is_applicable_now())
    
    def test_is_applicable_now_inactive(self):
        """Test is_applicable_now() returns False even in range if inactive"""
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        discount = Discount.objects.create(
            name='Inactive Discount',
            discount_type='Percentage',
            value=10,
            applicable_to='All',
            start_date=today,
            end_date=tomorrow,
            is_active=False
        )
        self.assertFalse(discount.is_applicable_now())
    
    def test_is_applicable_to_product_matches_category(self):
        """Test is_applicable_to_product() returns True when discount applies to product's category"""
        discount = Discount.objects.create(
            name='Category Discount',
            discount_type='Percentage',
            value=10,
            applicable_to='Category',
            target_category_id=self.category,
            is_active=True
        )
        self.assertTrue(discount.is_applicable_to_product(self.product))
    
    def test_is_applicable_to_product_no_match_category(self):
        """Test is_applicable_to_product() returns False when product's category doesn't match"""
        other_category = Category.objects.create(name='Cakes', description='All cakes')
        discount = Discount.objects.create(
            name='Category Discount',
            discount_type='Percentage',
            value=10,
            applicable_to='Category',
            target_category_id=other_category,
            is_active=True
        )
        self.assertFalse(discount.is_applicable_to_product(self.product))
    
    def test_is_applicable_to_product_matches_product(self):
        """Test is_applicable_to_product() returns True when discount applies to specific product"""
        discount = Discount.objects.create(
            name='Product Discount',
            discount_type='Percentage',
            value=10,
            applicable_to='Product',
            target_product_id=self.product,
            is_active=True
        )
        self.assertTrue(discount.is_applicable_to_product(self.product))
    
    def test_is_applicable_to_product_no_match_product(self):
        """Test is_applicable_to_product() returns False when discount applies to different product"""
        other_product = Product.objects.create(
            name='Paratha',
            description='Flat bread',
            cost_price=15.00,
            selling_price=30.00,
            category_id=self.category
        )
        discount = Discount.objects.create(
            name='Product Discount',
            discount_type='Percentage',
            value=10,
            applicable_to='Product',
            target_product_id=self.product,
            is_active=True
        )
        self.assertFalse(discount.is_applicable_to_product(other_product))
    
    def test_is_applicable_to_product_all_products(self):
        """Test is_applicable_to_product() returns True for 'All' applicability"""
        discount = Discount.objects.create(
            name='All Products Discount',
            discount_type='Percentage',
            value=10,
            applicable_to='All',
            is_active=True
        )
        self.assertTrue(discount.is_applicable_to_product(self.product))
    
    def test_calculate_discount_amount_percentage(self):
        """Test calculate_discount_amount() with percentage discount"""
        discount = Discount.objects.create(
            name='Percentage Discount',
            discount_type='Percentage',
            value=20,  # 20%
            applicable_to='All'
        )
        amount = 1000
        discount_amount = discount.calculate_discount_amount(amount)
        self.assertEqual(discount_amount, 200)  # 20% of 1000
    
    def test_calculate_discount_amount_percentage_decimal(self):
        """Test calculate_discount_amount() with decimal percentage"""
        discount = Discount.objects.create(
            name='Decimal Percentage Discount',
            discount_type='Percentage',
            value=15.5,  # 15.5%
            applicable_to='All'
        )
        amount = 1000
        discount_amount = discount.calculate_discount_amount(amount)
        self.assertEqual(discount_amount, 155)  # 15.5% of 1000
    
    def test_calculate_discount_amount_fixed_amount(self):
        """Test calculate_discount_amount() with fixed amount discount"""
        discount = Discount.objects.create(
            name='Fixed Amount Discount',
            discount_type='FixedAmount',
            value=100,  # Fixed Rs. 100
            applicable_to='All'
        )
        amount = 1000
        discount_amount = discount.calculate_discount_amount(amount)
        self.assertEqual(discount_amount, 100)  # Fixed amount
    
    def test_calculate_discount_amount_fixed_amount_less_than_purchase(self):
        """Test that fixed discount doesn't exceed purchase amount"""
        discount = Discount.objects.create(
            name='Small Fixed Discount',
            discount_type='FixedAmount',
            value=50,  # Fixed Rs. 50
            applicable_to='All'
        )
        amount = 100
        discount_amount = discount.calculate_discount_amount(amount)
        self.assertEqual(discount_amount, 50)
    
    def test_timestamps_created_at_and_updated_at(self):
        """Test that created_at and updated_at timestamps are set"""
        discount = Discount.objects.create(
            name='Timestamp Test',
            discount_type='Percentage',
            value=10,
            applicable_to='All'
        )
        self.assertIsNotNone(discount.created_at)
        self.assertIsNotNone(discount.updated_at)
        # Both should be set (allow for microsecond difference)
        time_diff = abs((discount.updated_at - discount.created_at).total_seconds())
        self.assertLess(time_diff, 1)


class DiscountAPITestCase(TestCase):
    """Test Discount REST API endpoints"""
    
    def setUp(self):
        """Set up test client and test data"""
        self.client = APIClient()
        
        # Create test users
        self.manager_user = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='testpass123',
            full_name='Manager User',
            role='Manager'
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='testpass123',
            full_name='Staff User',
            role='StoreKeeper'
        )
        
        # Create test data
        self.category = Category.objects.create(name='Breads', description='All breads', type='Product')
        self.product = Product.objects.create(
            name='Naan',
            description='Indian bread',
            cost_price=20.00,
            selling_price=50.00,
            category_id=self.category
        )
        
        # Create test discounts
        self.discount1 = Discount.objects.create(
            name='Summer Sale',
            discount_type='Percentage',
            value=20,
            applicable_to='All',
            is_active=True
        )
        self.discount2 = Discount.objects.create(
            name='Category Discount',
            discount_type='Percentage',
            value=15,
            applicable_to='Category',
            target_category_id=self.category,
            is_active=True
        )
        
        # Get authentication tokens
        from rest_framework.authtoken.models import Token
        self.manager_token = Token.objects.create(user=self.manager_user)
        self.staff_token = Token.objects.create(user=self.staff_user)
    
    def test_list_discounts_unauthenticated(self):
        """Test GET /api/discounts/ returns 401 for unauthenticated users"""
        response = self.client.get('/api/discounts/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_discounts_authenticated(self):
        """Test GET /api/discounts/ returns 200 for authenticated users"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        response = self.client.get('/api/discounts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_list_discounts_contains_all_discounts(self):
        """Test GET /api/discounts/ returns all created discounts"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        response = self.client.get('/api/discounts/')
        self.assertEqual(len(response.data), 2)
    
    def test_list_discounts_pagination(self):
        """Test GET /api/discounts/ pagination"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        # Create 25 more discounts
        for i in range(25):
            Discount.objects.create(
                name=f'Discount {i}',
                discount_type='Percentage',
                value=10,
                applicable_to='All'
            )
        response = self.client.get('/api/discounts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_discount_unauthenticated(self):
        """Test POST /api/discounts/ returns 401 for unauthenticated users"""
        data = {
            'name': 'New Discount',
            'discount_type': 'Percentage',
            'value': 10,
            'applicable_to': 'All'
        }
        response = self.client.post('/api/discounts/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_discount_non_manager(self):
        """Test POST /api/discounts/ returns 403 for non-Manager users"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.staff_token.key}')
        data = {
            'name': 'New Discount',
            'discount_type': 'Percentage',
            'value': 10,
            'applicable_to': 'All'
        }
        response = self.client.post('/api/discounts/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_discount_manager_success(self):
        """Test POST /api/discounts/ creates discount for Manager"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        data = {
            'name': 'New Percentage Discount',
            'discount_type': 'Percentage',
            'value': 25,
            'applicable_to': 'All'
        }
        response = self.client.post('/api/discounts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Percentage Discount')
        self.assertEqual(response.data['discount_type'], 'Percentage')
    
    def test_create_discount_fixed_amount(self):
        """Test POST /api/discounts/ creates fixed amount discount"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        data = {
            'name': 'Fixed Amount Discount',
            'discount_type': 'FixedAmount',
            'value': 100,
            'applicable_to': 'All'
        }
        response = self.client.post('/api/discounts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['discount_type'], 'FixedAmount')
        self.assertEqual(response.data['value'], 100)
    
    def test_create_discount_with_category(self):
        """Test POST /api/discounts/ creates discount for specific category"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        data = {
            'name': 'Bread Category Discount',
            'discount_type': 'Percentage',
            'value': 15,
            'applicable_to': 'Category',
            'target_category_id': self.category.id
        }
        response = self.client.post('/api/discounts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['applicable_to'], 'Category')
    
    def test_create_discount_with_product(self):
        """Test POST /api/discounts/ creates discount for specific product"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        data = {
            'name': 'Naan Product Discount',
            'discount_type': 'Percentage',
            'value': 10,
            'applicable_to': 'Product',
            'target_product_id': self.product.id
        }
        response = self.client.post('/api/discounts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['applicable_to'], 'Product')
    
    def test_create_discount_invalid_percentage_too_high(self):
        """Test POST /api/discounts/ rejects percentage > 100"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        data = {
            'name': 'Invalid Discount',
            'discount_type': 'Percentage',
            'value': 150,  # Invalid: > 100
            'applicable_to': 'All'
        }
        response = self.client.post('/api/discounts/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('value', response.data)
    
    def test_create_discount_invalid_percentage_zero(self):
        """Test POST /api/discounts/ rejects percentage 0 or negative"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        data = {
            'name': 'Invalid Discount',
            'discount_type': 'Percentage',
            'value': 0,  # Invalid: <= 0
            'applicable_to': 'All'
        }
        response = self.client.post('/api/discounts/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_discount_invalid_fixed_amount_zero(self):
        """Test POST /api/discounts/ rejects fixed amount <= 0"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        data = {
            'name': 'Invalid Fixed Discount',
            'discount_type': 'FixedAmount',
            'value': 0,  # Invalid: <= 0
            'applicable_to': 'All'
        }
        response = self.client.post('/api/discounts/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_retrieve_discount(self):
        """Test GET /api/discounts/{id}/ retrieves discount details"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        response = self.client.get(f'/api/discounts/{self.discount1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Summer Sale')
        self.assertIn('is_applicable_now', response.data)
    
    def test_retrieve_discount_not_found(self):
        """Test GET /api/discounts/{id}/ returns 404 for non-existent discount"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        response = self.client.get('/api/discounts/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_discount_full(self):
        """Test PUT /api/discounts/{id}/ fully updates discount"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        data = {
            'name': 'Updated Discount',
            'discount_type': 'FixedAmount',
            'value': 200,
            'applicable_to': 'All'
        }
        response = self.client.put(f'/api/discounts/{self.discount1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Discount')
        self.assertEqual(float(response.data['value']), 200)
    
    def test_update_discount_partial(self):
        """Test PATCH /api/discounts/{id}/ partially updates discount"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        data = {'value': 30}
        response = self.client.patch(f'/api/discounts/{self.discount1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['value']), 30)
        self.assertEqual(response.data['name'], 'Summer Sale')  # Unchanged
    
    def test_update_discount_non_manager(self):
        """Test PUT /api/discounts/{id}/ returns 403 for non-Manager"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.staff_token.key}')
        data = {'name': 'Updated Name'}
        response = self.client.put(f'/api/discounts/{self.discount1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_discount(self):
        """Test DELETE /api/discounts/{id}/ deletes discount"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        discount_id = self.discount1.id
        response = self.client.delete(f'/api/discounts/{discount_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verify deletion
        self.assertFalse(Discount.objects.filter(id=discount_id).exists())
    
    def test_delete_discount_non_manager(self):
        """Test DELETE /api/discounts/{id}/ returns 403 for non-Manager"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.staff_token.key}')
        response = self.client.delete(f'/api/discounts/{self.discount1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_active_discounts(self):
        """Test GET /api/discounts/active/ returns only active discounts applicable now"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        response = self.client.get('/api/discounts/active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Both discounts are active and in date range
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_toggle_discount_active_status(self):
        """Test PATCH /api/discounts/{id}/toggle/ toggles active status"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        # Verify initial state
        self.assertTrue(self.discount1.is_active)
        response = self.client.patch(f'/api/discounts/{self.discount1.id}/toggle/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_active'])
        # Verify toggle worked
        refreshed = Discount.objects.get(id=self.discount1.id)
        self.assertFalse(refreshed.is_active)
    
    def test_toggle_discount_non_manager(self):
        """Test PATCH /api/discounts/{id}/toggle/ returns 403 for non-Manager"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.staff_token.key}')
        response = self.client.patch(f'/api/discounts/{self.discount1.id}/toggle/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_validate_discount_applicable(self):
        """Test POST /api/discounts/{id}/validate/ with applicable discount"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        data = {'product_id': self.product.id}
        response = self.client.post(f'/api/discounts/{self.discount1.id}/validate/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_applicable'])
    
    def test_validate_discount_not_applicable_category(self):
        """Test POST /api/discounts/{id}/validate/ with non-applicable category discount"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        other_category = Category.objects.create(name='Cakes', description='All cakes', type='Product')
        other_product = Product.objects.create(
            name='Cake',
            description='A cake',
            cost_price=100.00,
            selling_price=200.00,
            category_id=other_category
        )
        data = {'product_id': other_product.id}
        response = self.client.post(f'/api/discounts/{self.discount2.id}/validate/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_applicable'])
    
    def test_validate_discount_inactive(self):
        """Test POST /api/discounts/{id}/validate/ returns not applicable for inactive discount"""
        self.discount1.is_active = False
        self.discount1.save()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        data = {'product_id': self.product.id}
        response = self.client.post(f'/api/discounts/{self.discount1.id}/validate/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_applicable'])
    
    def test_apply_discount_percentage(self):
        """Test POST /api/discounts/{id}/apply/ calculates percentage discount"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        data = {'amount': 1000}  # 1000
        response = self.client.post(f'/api/discounts/{self.discount1.id}/apply/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['discount_amount']), 200)  # 20% of 1000
    
    def test_apply_discount_fixed_amount(self):
        """Test POST /api/discounts/{id}/apply/ with fixed amount discount"""
        fixed_discount = Discount.objects.create(
            name='Fixed Rs.500',
            discount_type='FixedAmount',
            value=500,
            applicable_to='All'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        data = {'amount': 2000}
        response = self.client.post(f'/api/discounts/{fixed_discount.id}/apply/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['discount_amount']), 500)
    
    def test_apply_discount_with_product_validation(self):
        """Test POST /api/discounts/{id}/apply/ checks product applicability"""
        other_category = Category.objects.create(name='Cakes', type='Product')
        other_product = Product.objects.create(
            name='Cake',
            cost_price=100.00,
            selling_price=200.00,
            category_id=other_category
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        data = {
            'amount': 1000,
            'product_id': other_product.id  # Product from different category
        }
        response = self.client.post(f'/api/discounts/{self.discount2.id}/apply/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should still calculate, but include is_applicable flag
        self.assertIn('discount_amount', response.data)
    
    def test_batch_validate_discounts(self):
        """Test POST /api/discounts/batch-validate/ validates multiple discounts"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        data = {
            'discount_ids': [self.discount1.id, self.discount2.id],
            'product_id': self.product.id
        }
        response = self.client.post('/api/discounts/batch-validate/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)
    
    def test_batch_apply_discounts(self):
        """Test POST /api/discounts/batch-apply/ applies multiple discounts"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        data = {
            'discount_ids': [self.discount1.id],  # 20% discount
            'amount': 1000
        }
        response = self.client.post('/api/discounts/batch-apply/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_discount_amount'], 200)  # 20% of 1000
    
    def test_batch_apply_multiple_discounts_cumulative(self):
        """Test POST /api/discounts/batch-apply/ applies multiple discounts cumulatively"""
        # Create first discount: 10%
        discount1 = Discount.objects.create(
            name='10% Discount',
            discount_type='Percentage',
            value=10,
            applicable_to='All'
        )
        # Create second discount: Fixed 50
        discount2 = Discount.objects.create(
            name='Fixed 50',
            discount_type='FixedAmount',
            value=50,
            applicable_to='All'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        data = {
            'discount_ids': [discount1.id, discount2.id],
            'amount': 1000
        }
        response = self.client.post('/api/discounts/batch-apply/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 10% of 1000 = 100, plus fixed 50 = 150
        self.assertEqual(float(response.data['total_discount_amount']), 150)
    
    def test_list_discount_response_format(self):
        """Test GET /api/discounts/ response includes required fields"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        response = self.client.get('/api/discounts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if response.data:
            discount = response.data[0]
            self.assertIn('id', discount)
            self.assertIn('discount_id', discount)
            self.assertIn('name', discount)
            self.assertIn('discount_type', discount)
            self.assertIn('value', discount)
            self.assertIn('applicable_to', discount)
            self.assertIn('is_active', discount)
    
    def test_detail_discount_response_format(self):
        """Test GET /api/discounts/{id}/ response includes all fields"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.manager_token.key}')
        response = self.client.get(f'/api/discounts/{self.discount1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertIn('discount_id', response.data)
        self.assertIn('name', response.data)
        self.assertIn('description', response.data)
        self.assertIn('discount_type', response.data)
        self.assertIn('value', response.data)
        self.assertIn('applicable_to', response.data)
        self.assertIn('start_date', response.data)
        self.assertIn('end_date', response.data)
        self.assertIn('start_time', response.data)
        self.assertIn('end_time', response.data)
        self.assertIn('is_active', response.data)
        self.assertIn('is_applicable_now', response.data)
        self.assertIn('created_at', response.data)
        self.assertIn('updated_at', response.data)
