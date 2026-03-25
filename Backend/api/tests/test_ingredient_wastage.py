"""
Test cases for the IngredientWastage model and API endpoints.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal

from api.models import (
    Category,
    Ingredient,
    WastageReason,
    IngredientWastage,
)

User = get_user_model()


class IngredientWastageModelTest(TestCase):
    """Test cases for the IngredientWastage model."""

    def setUp(self):
        """Set up test data."""
        # Create an ingredient category
        self.category = Category.objects.create(
            name="Dry Goods",
            type="Ingredient"
        )

        # Create an ingredient
        self.ingredient = Ingredient.objects.create(
            name="Flour",
            category_id=self.category,
            tracking_type="Weight",
            base_unit="kg",
            shelf_life=30,
            shelf_unit="days"
        )

        # Create a wastage reason
        self.reason = WastageReason.objects.create(
            reason="Expired",
            description="Product expired"
        )

        # Create a manager user for recording wastage
        self.user = User.objects.create_user(
            username="manager",
            email="manager@test.com",
            password="testpass123",
            full_name="Manager User",
            role="Manager"
        )

    def test_create_ingredient_wastage(self):
        """Test creating an IngredientWastage record."""
        wastage = IngredientWastage.objects.create(
            ingredient_id=self.ingredient,
            quantity=Decimal('5.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason,
            reported_by=self.user
        )

        self.assertEqual(wastage.ingredient_id, self.ingredient)
        self.assertEqual(wastage.quantity, Decimal('5.00'))
        self.assertEqual(wastage.unit_cost, Decimal('10.00'))
        self.assertEqual(wastage.total_loss, Decimal('50.00'))
        self.assertEqual(wastage.reason_id, self.reason)
        self.assertEqual(wastage.reported_by, self.user)
        self.assertIsNotNone(wastage.created_at)

    def test_ingredient_wastage_auto_generates_id(self):
        """Test that IngredientWastage ID is auto-generated."""
        wastage = IngredientWastage.objects.create(
            ingredient_id=self.ingredient,
            quantity=Decimal('5.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason,
            reported_by=self.user
        )

        self.assertIsNotNone(wastage.wastage_id)
        self.assertTrue(wastage.wastage_id.startswith('IW-'))

    def test_total_loss_calculated_correctly(self):
        """Test that total_loss is calculated as quantity * unit_cost."""
        wastage = IngredientWastage.objects.create(
            ingredient_id=self.ingredient,
            quantity=Decimal('5.50'),
            unit_cost=Decimal('10.25'),
            reason_id=self.reason,
            reported_by=self.user
        )

        expected_loss = Decimal('5.50') * Decimal('10.25')
        self.assertEqual(wastage.total_loss, expected_loss)

    def test_wastage_with_notes(self):
        """Test creating wastage with notes."""
        notes = "Moisture contamination detected"
        wastage = IngredientWastage.objects.create(
            ingredient_id=self.ingredient,
            quantity=Decimal('5.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason,
            reported_by=self.user,
            notes=notes
        )

        self.assertEqual(wastage.notes, notes)

    def test_multiple_wastages_per_ingredient(self):
        """Test recording multiple wastages for the same ingredient."""
        wastage1 = IngredientWastage.objects.create(
            ingredient_id=self.ingredient,
            quantity=Decimal('5.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason,
            reported_by=self.user
        )

        reason2 = WastageReason.objects.create(
            reason="Damaged",
            description="Packaging damaged"
        )

        wastage2 = IngredientWastage.objects.create(
            ingredient_id=self.ingredient,
            quantity=Decimal('3.00'),
            unit_cost=Decimal('10.00'),
            reason_id=reason2,
            reported_by=self.user
        )

        wastages = IngredientWastage.objects.filter(ingredient_id=self.ingredient)
        self.assertEqual(wastages.count(), 2)
        total_quantity = wastages.aggregate(total=models.Sum('quantity'))['total']
        self.assertEqual(total_quantity, Decimal('8.00'))

    def test_created_at_auto_populated(self):
        """Test that created_at is automatically set."""
        before = timezone.now()
        wastage = IngredientWastage.objects.create(
            ingredient_id=self.ingredient,
            quantity=Decimal('5.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason,
            reported_by=self.user
        )
        after = timezone.now()

        self.assertIsNotNone(wastage.created_at)
        self.assertTrue(before <= wastage.created_at <= after)


class IngredientWastageAPITest(APITestCase):
    """Test cases for the IngredientWastage API endpoints."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()

        # Create users
        self.manager = User.objects.create_user(
            username="manager",
            email="manager@test.com",
            password="testpass123",
            full_name="Manager User",
            role="Manager"
        )

        self.storekeeper = User.objects.create_user(
            username="storekeeper",
            email="storekeeper@test.com",
            password="testpass123",
            full_name="Storekeeper User",
            role="Storekeeper"
        )

        self.cashier = User.objects.create_user(
            username="cashier",
            email="cashier@test.com",
            password="testpass123",
            full_name="Cashier User",
            role="Cashier"
        )

        # Create category and ingredient
        self.category = Category.objects.create(
            name="Dry Goods",
            type="Ingredient"
        )

        self.ingredient = Ingredient.objects.create(
            name="Flour",
            category_id=self.category,
            tracking_type="Weight",
            base_unit="kg",
            shelf_life=30,
            shelf_unit="days"
        )

        # Create wastage reason
        self.reason = WastageReason.objects.create(
            reason="Expired",
            description="Product expired"
        )

    def test_list_ingredient_wastages_authenticated(self):
        """Test listing ingredient wastages (authenticated users)."""
        # Create some wastage records
        IngredientWastage.objects.create(
            ingredient_id=self.ingredient,
            quantity=Decimal('5.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason,
            reported_by=self.manager
        )

        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/ingredient-wastages/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_list_ingredient_wastages_unauthenticated(self):
        """Test that unauthenticated users cannot list wastages."""
        response = self.client.get('/api/ingredient-wastages/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_ingredient_wastage(self):
        """Test creating an ingredient wastage record via API."""
        self.client.force_authenticate(user=self.manager)

        data = {
            'ingredient_id': self.ingredient.id,
            'quantity': '5.00',
            'unit_cost': '10.00',
            'reason_id': self.reason.id,
            'notes': 'Test wastage'
        }

        response = self.client.post('/api/ingredient-wastages/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(IngredientWastage.objects.count(), 1)
        
        wastage = IngredientWastage.objects.first()
        self.assertEqual(wastage.ingredient_id, self.ingredient)
        self.assertEqual(wastage.quantity, Decimal('5.00'))
        self.assertEqual(wastage.reported_by, self.manager)

    def test_retrieve_ingredient_wastage(self):
        """Test retrieving a specific wastage record."""
        wastage = IngredientWastage.objects.create(
            ingredient_id=self.ingredient,
            quantity=Decimal('5.00'),
            unit_cost=Decimal('10.00'),
            reason_id=self.reason,
            reported_by=self.manager
        )

        self.client.force_authenticate(user=self.manager)
        response = self.client.get(f'/api/ingredient-wastages/{wastage.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], wastage.id)
        self.assertEqual(str(response.data['quantity']), '5.00')

    def test_retrieve_nonexistent_wastage(self):
        """Test retrieving a nonexistent wastage record."""
        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/ingredient-wastages/9999/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
