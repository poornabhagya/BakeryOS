from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime, timedelta, date
from decimal import Decimal

from api.models import (
    User, Category, Product, Ingredient, IngredientBatch,
    WastageReason, ProductWastage, IngredientWastage,
    Notification, NotificationReceipt
)


class NotificationModelTest(TestCase):
    """Test Notification model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            full_name='Test User',
            role='Manager'
        )
    
    def test_create_notification(self):
        """Test creating a notification"""
        notification = Notification.objects.create(
            title='Test Notification',
            message='This is a test notification',
            type='LowStock',
            icon='warning'
        )
        
        self.assertEqual(notification.title, 'Test Notification')
        self.assertEqual(notification.type, 'LowStock')
        self.assertIsNotNone(notification.created_at)
    
    def test_notification_type_choices(self):
        """Test that only valid notification types can be created"""
        valid_types = ['LowStock', 'Expiry', 'HighWastage', 'OutOfStock', 'System', 'Warning']
        
        for ntype in valid_types:
            notification = Notification.objects.create(
                title=f'Test {ntype}',
                message='Test',
                type=ntype
            )
            self.assertEqual(notification.type, ntype)
    
    def test_notification_ordering(self):
        """Test that notifications are ordered by creation date (newest first)"""
        n1 = Notification.objects.create(
            title='First',
            message='Test',
            type='System'
        )
        
        n2 = Notification.objects.create(
            title='Second',
            message='Test',
            type='System'
        )
        
        notifications = Notification.objects.all()
        self.assertEqual(notifications[0].title, 'Second')
        self.assertEqual(notifications[1].title, 'First')


class NotificationReceiptTest(TestCase):
    """Test NotificationReceipt model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            full_name='Test User',
            role='Manager'
        )
        
        self.notification = Notification.objects.create(
            title='Test Notification',
            message='Test message',
            type='LowStock'
        )
    
    def test_create_notification_receipt(self):
        """Test creating a notification receipt"""
        receipt = NotificationReceipt.objects.create(
            notification=self.notification,
            user=self.user,
            is_read=False
        )
        
        self.assertEqual(receipt.notification, self.notification)
        self.assertEqual(receipt.user, self.user)
        self.assertFalse(receipt.is_read)
        self.assertIsNone(receipt.read_at)
    
    def test_mark_as_read(self):
        """Test marking a receipt as read"""
        receipt = NotificationReceipt.objects.create(
            notification=self.notification,
            user=self.user,
            is_read=False
        )
        
        receipt.mark_as_read()
        
        self.assertTrue(receipt.is_read)
        self.assertIsNotNone(receipt.read_at)
    
    def test_unique_constraint(self):
        """Test that only one receipt per user per notification can exist"""
        NotificationReceipt.objects.create(
            notification=self.notification,
            user=self.user
        )
        
        # Try to create duplicate
        with self.assertRaises(Exception):
            NotificationReceipt.objects.create(
                notification=self.notification,
                user=self.user
            )


class NotificationAPITest(APITestCase):
    """Test Notification API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            full_name='Test User',
            role='Manager'
        )
        
        self.other_user = User.objects.create_user(
            username='other',
            password='testpass123',
            email='other@example.com',
            full_name='Other User',
            role='Cashier'
        )
        
        # Create test notifications
        self.notification1 = Notification.objects.create(
            title='Low Stock Alert',
            message='Ingredient is low',
            type='LowStock',
            icon='warning'
        )
        
        self.notification2 = Notification.objects.create(
            title='Expiry Alert',
            message='Batch expiring soon',
            type='Expiry',
            icon='alert'
        )
        
        # Create receipts for main user
        NotificationReceipt.objects.create(
            notification=self.notification1,
            user=self.user,
            is_read=False
        )
        
        NotificationReceipt.objects.create(
            notification=self.notification2,
            user=self.user,
            is_read=False
        )
        
        # Create receipt for other user
        NotificationReceipt.objects.create(
            notification=self.notification1,
            user=self.other_user,
            is_read=True
        )
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access notifications"""
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_notifications(self):
        """Test listing notifications for authenticated user"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/notifications/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_notifications_user_isolation(self):
        """Test that users only see their own notifications"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/notifications/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Switch to other user
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get('/api/notifications/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_retrieve_notification(self):
        """Test retrieving a specific notification"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/notifications/{self.notification1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Low Stock Alert')
    
    def test_retrieve_marks_as_read(self):
        """Test that retrieving a notification marks it as read"""
        self.client.force_authenticate(user=self.user)
        
        receipt = NotificationReceipt.objects.get(
            notification=self.notification1,
            user=self.user
        )
        self.assertFalse(receipt.is_read)
        
        self.client.get(f'/api/notifications/{self.notification1.id}/')
        
        receipt.refresh_from_db()
        self.assertTrue(receipt.is_read)
    
    def test_mark_as_read_endpoint(self):
        """Test marking notification as read via endpoint"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.patch(
            f'/api/notifications/{self.notification1.id}/read/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        receipt = NotificationReceipt.objects.get(
            notification=self.notification1,
            user=self.user
        )
        self.assertTrue(receipt.is_read)
    
    def test_mark_all_as_read(self):
        """Test marking all notifications as read"""
        self.client.force_authenticate(user=self.user)
        
        # Verify unread count
        unread_before = NotificationReceipt.objects.filter(
            user=self.user,
            is_read=False
        ).count()
        self.assertEqual(unread_before, 2)
        
        response = self.client.patch('/api/notifications/read_all/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify all marked as read
        unread_after = NotificationReceipt.objects.filter(
            user=self.user,
            is_read=False
        ).count()
        self.assertEqual(unread_after, 0)
    
    def test_get_unread_count(self):
        """Test getting unread notification count"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/notifications/unread/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 2)
        self.assertEqual(response.data['total'], 2)
        self.assertEqual(response.data['read_count'], 0)
    
    def test_filter_by_type(self):
        """Test filtering notifications by type"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/notifications/by_type/?type=LowStock')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['type'], 'LowStock')
    
    def test_delete_notification(self):
        """Test deleting a notification (soft delete)"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.delete(f'/api/notifications/{self.notification1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Receipt should be deleted, but notification still exists
        self.assertTrue(Notification.objects.filter(id=self.notification1.id).exists())
        self.assertFalse(
            NotificationReceipt.objects.filter(
                notification=self.notification1,
                user=self.user
            ).exists()
        )
    
    def test_clear_all_notifications(self):
        """Test clearing all notifications for user"""
        self.client.force_authenticate(user=self.user)
        
        count_before = NotificationReceipt.objects.filter(user=self.user).count()
        self.assertEqual(count_before, 2)
        
        response = self.client.delete('/api/notifications/clear_all/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        count_after = NotificationReceipt.objects.filter(user=self.user).count()
        self.assertEqual(count_after, 0)


class NotificationSignalTest(TestCase):
    """Test automatic notification creation via signals"""
    
    def setUp(self):
        """Set up test data"""
        self.manager = User.objects.create_user(
            username='manager',
            password='testpass123',
            full_name='Manager User',
            role='Manager'
        )
        
        self.storekeeper = User.objects.create_user(
            username='storekeeper',
            password='testpass123',
            full_name='Storekeeper',
            role='Storekeeper'
        )
        
        self.baker = User.objects.create_user(
            username='baker',
            password='testpass123',
            full_name='Baker',
            role='Baker'
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            type='Ingredient'
        )
        
        self.product_category = Category.objects.create(
            name='Test Product Category',
            type='Product'
        )
        
        self.ingredient = Ingredient.objects.create(
            category_id=self.category,
            name='Test Ingredient',
            supplier='Test Supplier',
            base_unit='kg',
            low_stock_threshold=Decimal('10.00'),
            total_quantity=Decimal('50.00')
        )
        
        self.product = Product.objects.create(
            category_id=self.product_category,
            name='Test Product',
            cost_price=Decimal('10.00'),
            selling_price=Decimal('20.00'),
            current_stock=Decimal('100.00')
        )
        
        self.wastage_reason = WastageReason.objects.create(
            reason='Expired',
            description='Item expired'
        )
    
    def test_wastage_notification_created(self):
        """Test notification created when product wastage reported"""
        initial_count = Notification.objects.count()
        
        wastage = ProductWastage.objects.create(
            product_id=self.product,
            quantity=Decimal('10.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.wastage_reason,
            reported_by=self.manager,
            notes='Test wastage'
        )
        
        # Check notification was created
        self.assertGreater(Notification.objects.count(), initial_count)
        
        notification = Notification.objects.filter(type='HighWastage').first()
        self.assertIsNotNone(notification)
        self.assertIn('Wastage Reported', notification.title)
    
    def test_wastage_notification_includes_loss(self):
        """Test that wastage notification includes financial loss"""
        wastage = ProductWastage.objects.create(
            product_id=self.product,
            quantity=Decimal('5.00'),
            unit_cost=Decimal('20.00'),
            reason_id=self.wastage_reason,
            reported_by=self.manager,
            notes='Test'
        )
        
        notification = Notification.objects.filter(type='HighWastage').first()
        self.assertIsNotNone(notification)
        self.assertIn('Rs. 100.00', notification.message)
