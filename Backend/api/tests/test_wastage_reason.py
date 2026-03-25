"""
Test suite for WastageReason Model and API Endpoints

Tests cover:
- WastageReason model creation and auto-ID generation
- API endpoints (list, retrieve, create, update, delete)
- Validation rules
- Serializers
- Error handling
"""

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from api.models import WastageReason, User


class WastageReasonModelTestCase(TestCase):
    """Test WastageReason model"""

    def setUp(self):
        """Setup test data"""
        self.reason1 = WastageReason.objects.create(
            reason='Expired',
            description='Products that have passed their expiration date'
        )

    def test_wastage_reason_creation(self):
        """Test creating a wastage reason"""
        self.assertIsNotNone(self.reason1.id)
        self.assertEqual(self.reason1.reason, 'Expired')
        self.assertTrue(self.reason1.reason_id)

    def test_auto_generate_reason_id(self):
        """Test auto-generation of reason_id"""
        self.assertEqual(self.reason1.reason_id, 'WR-001')

        # Create second reason and check ID increments
        reason2 = WastageReason.objects.create(
            reason='Damaged',
            description='Physically damaged products'
        )
        self.assertEqual(reason2.reason_id, 'WR-002')

    def test_reason_id_uniqueness(self):
        """Test that reason_id is unique"""
        with self.assertRaises(Exception):
            # Trying to create another reason with same auto-generated ID should fail
            WastageReason.objects.create(
                reason_id='WR-001',
                reason='Another Reason'
            )

    def test_reason_uniqueness(self):
        """Test that reason field is unique"""
        with self.assertRaises(Exception):
            WastageReason.objects.create(
                reason='Expired',  # Same as reason1
                description='Different description'
            )

    def test_reason_string_representation(self):
        """Test __str__ method"""
        expected = f"{self.reason1.reason_id} - {self.reason1.reason}"
        self.assertEqual(str(self.reason1), expected)

    def test_wastage_reason_ordering(self):
        """Test that reasons are ordered by reason_id"""
        WastageReason.objects.create(reason='Damaged')
        WastageReason.objects.create(reason='Spilled')

        reasons = WastageReason.objects.all()
        self.assertEqual(reasons[0].reason_id, 'WR-001')
        self.assertEqual(reasons[1].reason_id, 'WR-002')
        self.assertEqual(reasons[2].reason_id, 'WR-003')

    def test_created_at_timestamp(self):
        """Test that created_at timestamp is set"""
        self.assertIsNotNone(self.reason1.created_at)


class WastageReasonAPITestCase(APITestCase):
    """Test WastageReason API endpoints"""

    def setUp(self):
        """Setup test data and client"""
        self.client = APIClient()

        # Create test user (authenticated as any user)
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='Manager'
        )

        # Create test wastage reasons
        self.reason1 = WastageReason.objects.create(
            reason='Expired',
            description='Products past expiration date'
        )
        self.reason2 = WastageReason.objects.create(
            reason='Damaged',
            description='Physically damaged products'
        )

        # Authenticate client
        self.client.force_authenticate(user=self.user)

    def test_list_wastage_reasons(self):
        """Test GET /api/wastage-reasons/ endpoint"""
        response = self.client.get('/api/wastage-reasons/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)

    def test_list_wastage_reasons_fields(self):
        """Test list response contains all necessary fields"""
        response = self.client.get('/api/wastage-reasons/')

        result = response.data['results'][0]
        self.assertIn('id', result)
        self.assertIn('reason_id', result)
        self.assertIn('reason', result)
        self.assertIn('description', result)

    def test_retrieve_wastage_reason(self):
        """Test GET /api/wastage-reasons/{id}/ endpoint"""
        response = self.client.get(f'/api/wastage-reasons/{self.reason1.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reason_id'], 'WR-001')
        self.assertEqual(response.data['reason'], 'Expired')

    def test_retrieve_wastage_reason_includes_timestamp(self):
        """Test that retrieve includes created_at timestamp"""
        response = self.client.get(f'/api/wastage-reasons/{self.reason1.id}/')

        self.assertIn('created_at', response.data)

    def test_create_wastage_reason(self):
        """Test POST /api/wastage-reasons/ endpoint"""
        data = {
            'reason': 'Spilled',
            'description': 'Accidentally spilled products'
        }
        response = self.client.post('/api/wastage-reasons/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reason'], 'Spilled')
        self.assertEqual(response.data['reason_id'], 'WR-003')

    def test_create_wastage_reason_auto_id(self):
        """Test that reason_id is generated on creation"""
        data = {'reason': 'Theft', 'description': 'Theft loss'}
        response = self.client.post('/api/wastage-reasons/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['reason_id'])
        self.assertRegex(response.data['reason_id'], r'WR-\d{3}')

    def test_create_duplicate_reason_fails(self):
        """Test creating duplicate reason fails"""
        data = {
            'reason': 'Expired',  # Already exists
            'description': 'Different description'
        }
        response = self.client.post('/api/wastage-reasons/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_empty_reason_fails(self):
        """Test creating with empty reason fails"""
        data = {'reason': '', 'description': 'Description'}
        response = self.client.post('/api/wastage-reasons/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_whitespace_reason_fails(self):
        """Test creating with whitespace-only reason fails"""
        data = {'reason': '   ', 'description': 'Description'}
        response = self.client.post('/api/wastage-reasons/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_wastage_reason(self):
        """Test PUT /api/wastage-reasons/{id}/ endpoint"""
        data = {
            'reason': 'Expired Products',
            'description': 'Updated description'
        }
        response = self.client.put(f'/api/wastage-reasons/{self.reason1.id}/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reason'], 'Expired Products')

    def test_partial_update_wastage_reason(self):
        """Test PATCH /api/wastage-reasons/{id}/ endpoint"""
        data = {'description': 'Only update description'}
        response = self.client.patch(f'/api/wastage-reasons/{self.reason1.id}/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Only update description')
        self.assertEqual(response.data['reason'], 'Expired')  # Unchanged

    def test_delete_wastage_reason(self):
        """Test DELETE /api/wastage-reasons/{id}/ endpoint"""
        response = self.client.delete(f'/api/wastage-reasons/{self.reason1.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify it's deleted
        self.assertFalse(
            WastageReason.objects.filter(id=self.reason1.id).exists()
        )

    def test_retrieve_nonexistent_reason(self):
        """Test retrieving non-existent reason returns 404"""
        response = self.client.get('/api/wastage-reasons/9999/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access_rejected(self):
        """Test that unauthenticated users are rejected"""
        client = APIClient()  # No authentication
        response = client.get('/api/wastage-reasons/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class WastageReasonValidationTestCase(APITestCase):
    """Test WastageReason validation rules"""

    def setUp(self):
        """Setup test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='Manager'
        )
        self.client.force_authenticate(user=self.user)

    def test_case_insensitive_duplicate_check(self):
        """Test that duplicate check is case-insensitive"""
        # Create first reason
        data1 = {'reason': 'Expired', 'description': 'Test'}
        response1 = self.client.post('/api/wastage-reasons/', data1)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Try with different case
        data2 = {'reason': 'EXPIRED', 'description': 'Test'}
        response2 = self.client.post('/api/wastage-reasons/', data2)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reason_trimmed_on_create(self):
        """Test that reason is trimmed of whitespace"""
        data = {'reason': '  Expired  ', 'description': 'Test'}
        response = self.client.post('/api/wastage-reasons/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reason'], 'Expired')

    def test_description_trimmed_on_create(self):
        """Test that description is trimmed"""
        data = {'reason': 'Expired', 'description': '  Test description  '}
        response = self.client.post('/api/wastage-reasons/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['description'], 'Test description')

    def test_optional_description(self):
        """Test that description is optional"""
        data = {'reason': 'Spoiled'}
        response = self.client.post('/api/wastage-reasons/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class WastageReasonSerializerTestCase(TestCase):
    """Test WastageReason serializers"""

    def setUp(self):
        """Setup test data"""
        self.reason = WastageReason.objects.create(
            reason='Expired',
            description='Products past expiration'
        )

    def test_list_serializer_fields(self):
        """Test WastageReasonListSerializer includes correct fields"""
        from api.serializers import WastageReasonListSerializer

        serializer = WastageReasonListSerializer(self.reason)
        data = serializer.data

        self.assertIn('id', data)
        self.assertIn('reason_id', data)
        self.assertIn('reason', data)
        self.assertIn('description', data)
        self.assertEqual(len(data), 4)

    def test_detail_serializer_includes_timestamp(self):
        """Test WastageReasonDetailSerializer includes timestamp"""
        from api.serializers import WastageReasonDetailSerializer

        serializer = WastageReasonDetailSerializer(self.reason)
        data = serializer.data

        self.assertIn('created_at', data)

    def test_create_serializer_validation(self):
        """Test WastageReasonCreateSerializer validation"""
        from api.serializers import WastageReasonCreateSerializer

        # Valid data
        valid_data = {'reason': 'Damaged', 'description': 'Test'}
        serializer = WastageReasonCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

        # Invalid data - empty reason
        invalid_data = {'reason': ''}
        serializer = WastageReasonCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())


class WastageReasonIntegrationTestCase(APITestCase):
    """Integration tests for WastageReason"""

    def setUp(self):
        """Setup test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='Manager'
        )
        self.client.force_authenticate(user=self.user)

    def test_complete_crud_workflow(self):
        """Test complete CRUD workflow"""
        # Create
        create_data = {'reason': 'Test Reason', 'description': 'Test'}
        create_response = self.client.post('/api/wastage-reasons/', create_data)
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        reason_id = create_response.data['id']

        # Retrieve
        retrieve_response = self.client.get(f'/api/wastage-reasons/{reason_id}/')
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data['reason'], 'Test Reason')

        # Update
        update_data = {'reason': 'Updated Reason', 'description': 'Updated'}
        update_response = self.client.put(f'/api/wastage-reasons/{reason_id}/', update_data)
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        # Delete
        delete_response = self.client.delete(f'/api/wastage-reasons/{reason_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_after_multiple_creates(self):
        """Test list endpoint after creating multiple reasons"""
        # Create multiple
        for i in range(5):
            data = {'reason': f'Reason {i}', 'description': f'Description {i}'}
            response = self.client.post('/api/wastage-reasons/', data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify list
        list_response = self.client.get('/api/wastage-reasons/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['count'], 5)

    def test_auto_id_sequence_integrity(self):
        """Test that auto-ID sequence maintains integrity"""
        ids = []
        for i in range(10):
            data = {'reason': f'Reason {i}'}
            response = self.client.post('/api/wastage-reasons/', data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            ids.append(response.data['reason_id'])

        # Verify all IDs are unique
        self.assertEqual(len(ids), len(set(ids)))

        # Verify sequence
        for i, reason_id in enumerate(ids):
            expected_id = f'WR-{str(i+1).zfill(3)}'
            self.assertEqual(reason_id, expected_id)
