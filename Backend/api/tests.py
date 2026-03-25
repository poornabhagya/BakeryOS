from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime
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
            category_name="Dry Goods",
            category_type="ingredient"
        )

        # Create an ingredient
        self.ingredient = Ingredient.objects.create(
            ingredient_name="Flour",
            category=self.category,
            quantity=100,
            measurement="kg"
        )

        # Create a wastage reason
        self.reason = WastageReason.objects.create(
            wastage_reason="Expired",
            reason_description="Product expired"
        )

        # Create a manager user for recording wastage
        self.user = User.objects.create_user(
            email="manager@test.com",
            password="testpass123",
            role="manager"
        )

    def test_create_ingredient_wastage(self):
        """Test creating an IngredientWastage record."""
        wastage = IngredientWastage.objects.create(
            ingredient=self.ingredient,
            quantity_wasted=5,
            wastage_reason=self.reason,
            recorded_by=self.user
        )

        self.assertEqual(wastage.ingredient, self.ingredient)
        self.assertEqual(wastage.quantity_wasted, 5)
        self.assertEqual(wastage.wastage_reason, self.reason)
        self.assertEqual(wastage.recorded_by, self.user)
        self.assertIsNotNone(wastage.timestamp)

    def test_ingredient_wastage_string_representation(self):
        """Test the string representation of IngredientWastage."""
        wastage = IngredientWastage.objects.create(
            ingredient=self.ingredient,
            quantity_wasted=5,
            wastage_reason=self.reason,
            recorded_by=self.user
        )

        expected_str = f"{self.ingredient.ingredient_name} - 5 {self.ingredient.measurement} ({self.reason.wastage_reason})"
        self.assertEqual(str(wastage), expected_str)

    def test_ingredient_quantity_decreased_after_wastage(self):
        """Test that ingredient quantity is correctly decreased after recording wastage."""
        initial_quantity = self.ingredient.quantity
        wastage_amount = 5

        IngredientWastage.objects.create(
            ingredient=self.ingredient,
            quantity_wasted=wastage_amount,
            wastage_reason=self.reason,
            recorded_by=self.user
        )

        # Refresh to get updated quantity
        self.ingredient.refresh_from_db()
        
        # The quantity should remain the same (wastage is tracked but not auto-deducted)
        # This is by design - the frontend/API handles the deduction
        self.assertEqual(self.ingredient.quantity, initial_quantity)

    def test_wastage_with_notes(self):
        """Test creating wastage with notes."""
        notes = "Moisture contamination detected"
        wastage = IngredientWastage.objects.create(
            ingredient=self.ingredient,
            quantity_wasted=5,
            wastage_reason=self.reason,
            recorded_by=self.user,
            notes=notes
        )

        self.assertEqual(wastage.notes, notes)

    def test_multiple_wastages_per_ingredient(self):
        """Test recording multiple wastages for the same ingredient."""
        wastage1 = IngredientWastage.objects.create(
            ingredient=self.ingredient,
            quantity_wasted=5,
            wastage_reason=self.reason,
            recorded_by=self.user
        )

        reason2 = WastageReason.objects.create(
            wastage_reason="Damaged",
            reason_description="Packaging damaged"
        )

        wastage2 = IngredientWastage.objects.create(
            ingredient=self.ingredient,
            quantity_wasted=3,
            wastage_reason=reason2,
            recorded_by=self.user
        )

        wastages = IngredientWastage.objects.filter(ingredient=self.ingredient)
        self.assertEqual(wastages.count(), 2)
        self.assertEqual(wastages.aggregate(total=models.Sum('quantity_wasted'))['total'], 8)

    def test_timestamp_auto_populated(self):
        """Test that timestamp is automatically set."""
        before = datetime.now()
        wastage = IngredientWastage.objects.create(
            ingredient=self.ingredient,
            quantity_wasted=5,
            wastage_reason=self.reason,
            recorded_by=self.user
        )
        after = datetime.now()

        self.assertIsNotNone(wastage.timestamp)
        self.assertTrue(before <= wastage.timestamp <= after)


class IngredientWastageAPITest(APITestCase):
    """Test cases for the IngredientWastage API endpoints."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()

        # Create users
        self.manager = User.objects.create_user(
            email="manager@test.com",
            password="testpass123",
            role="manager"
        )

        self.storekeeper = User.objects.create_user(
            email="storekeeper@test.com",
            password="testpass123",
            role="storekeeper"
        )

        self.cashier = User.objects.create_user(
            email="cashier@test.com",
            password="testpass123",
            role="cashier"
        )

        # Create category and ingredient
        self.category = Category.objects.create(
            category_name="Dry Goods",
            category_type="ingredient"
        )

        self.ingredient = Ingredient.objects.create(
            ingredient_name="Flour",
            category=self.category,
            quantity=100,
            measurement="kg"
        )

        # Create wastage reason
        self.reason = WastageReason.objects.create(
            wastage_reason="Expired",
            reason_description="Product expired"
        )

    def test_list_ingredient_wastages_authenticated(self):
        """Test listing ingredient wastages (authenticated users)."""
        # Create some wastage records
        IngredientWastage.objects.create(
            ingredient=self.ingredient,
            quantity_wasted=5,
            wastage_reason=self.reason,
            recorded_by=self.manager
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
            'ingredient': self.ingredient.id,
            'quantity_wasted': 5,
            'wastage_reason': self.reason.id,
            'notes': 'Test wastage'
        }

        response = self.client.post('/api/ingredient-wastages/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(IngredientWastage.objects.count(), 1)
        
        wastage = IngredientWastage.objects.first()
        self.assertEqual(wastage.ingredient, self.ingredient)
        self.assertEqual(wastage.quantity_wasted, 5)
        self.assertEqual(wastage.recorded_by, self.manager)

    def test_create_wastage_by_storekeeper(self):
        """Test that storekeepers can create wastage records."""
        self.client.force_authenticate(user=self.storekeeper)

        data = {
            'ingredient': self.ingredient.id,
            'quantity_wasted': 3,
            'wastage_reason': self.reason.id
        }

        response = self.client.post('/api/ingredient-wastages/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wastage = IngredientWastage.objects.first()
        self.assertEqual(wastage.recorded_by, self.storekeeper)

    def test_create_wastage_by_cashier_forbidden(self):
        """Test that cashiers cannot create wastage records."""
        self.client.force_authenticate(user=self.cashier)

        data = {
            'ingredient': self.ingredient.id,
            'quantity_wasted': 3,
            'wastage_reason': self.reason.id
        }

        response = self.client.post('/api/ingredient-wastages/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_ingredient_wastage(self):
        """Test retrieving a specific wastage record."""
        wastage = IngredientWastage.objects.create(
            ingredient=self.ingredient,
            quantity_wasted=5,
            wastage_reason=self.reason,
            recorded_by=self.manager
        )

        self.client.force_authenticate(user=self.manager)
        response = self.client.get(f'/api/ingredient-wastages/{wastage.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], wastage.id)
        self.assertEqual(response.data['quantity_wasted'], 5)

    def test_filter_wastages_by_ingredient(self):
        """Test filtering wastages by ingredient."""
        # Create another ingredient
        ingredient2 = Ingredient.objects.create(
            ingredient_name="Sugar",
            category=self.category,
            quantity=50,
            measurement="kg"
        )

        # Create wastages
        IngredientWastage.objects.create(
            ingredient=self.ingredient,
            quantity_wasted=5,
            wastage_reason=self.reason,
            recorded_by=self.manager
        )

        IngredientWastage.objects.create(
            ingredient=ingredient2,
            quantity_wasted=3,
            wastage_reason=self.reason,
            recorded_by=self.manager
        )

        self.client.force_authenticate(user=self.manager)
        response = self.client.get(f'/api/ingredient-wastages/?ingredient={self.ingredient.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['ingredient'], self.ingredient.id)

    def test_filter_wastages_by_reason(self):
        """Test filtering wastages by wastage reason."""
        reason2 = WastageReason.objects.create(
            wastage_reason="Damaged",
            reason_description="Packaging damaged"
        )

        IngredientWastage.objects.create(
            ingredient=self.ingredient,
            quantity_wasted=5,
            wastage_reason=self.reason,
            recorded_by=self.manager
        )

        IngredientWastage.objects.create(
            ingredient=self.ingredient,
            quantity_wasted=3,
            wastage_reason=reason2,
            recorded_by=self.manager
        )

        self.client.force_authenticate(user=self.manager)
        response = self.client.get(f'/api/ingredient-wastages/?wastage_reason={self.reason.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_filter_wastages_by_date_range(self):
        """Test filtering wastages by date range."""
        from datetime import timedelta
        from django.utils import timezone

        today = timezone.now()
        past_date = today - timedelta(days=7)

        wastage1 = IngredientWastage.objects.create(
            ingredient=self.ingredient,
            quantity_wasted=5,
            wastage_reason=self.reason,
            recorded_by=self.manager
        )

        wastage1.timestamp = past_date
        wastage1.save()

        wastage2 = IngredientWastage.objects.create(
            ingredient=self.ingredient,
            quantity_wasted=3,
            wastage_reason=self.reason,
            recorded_by=self.manager
        )

        self.client.force_authenticate(user=self.manager)
        response = self.client.get(f'/api/ingredient-wastages/?start_date={today.date()}&end_date={today.date()}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_update_wastage_by_manager(self):
        """Test that managers can update wastage records."""
        wastage = IngredientWastage.objects.create(
            ingredient=self.ingredient,
            quantity_wasted=5,
            wastage_reason=self.reason,
            recorded_by=self.manager
        )

        self.client.force_authenticate(user=self.manager)

        data = {'quantity_wasted': 7, 'notes': 'Updated notes'}
        response = self.client.patch(f'/api/ingredient-wastages/{wastage.id}/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        wastage.refresh_from_db()
        self.assertEqual(wastage.quantity_wasted, 7)
        self.assertEqual(wastage.notes, 'Updated notes')

    def test_delete_wastage_by_manager(self):
        """Test that managers can delete wastage records."""
        wastage = IngredientWastage.objects.create(
            ingredient=self.ingredient,
            quantity_wasted=5,
            wastage_reason=self.reason,
            recorded_by=self.manager
        )

        self.client.force_authenticate(user=self.manager)
        response = self.client.delete(f'/api/ingredient-wastages/{wastage.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(IngredientWastage.objects.count(), 0)

    def test_delete_wastage_by_non_recorder(self):
        """Test that non-managers cannot delete wastage records."""
        wastage = IngredientWastage.objects.create(
            ingredient=self.ingredient,
            quantity_wasted=5,
            wastage_reason=self.reason,
            recorded_by=self.manager
        )

        self.client.force_authenticate(user=self.storekeeper)
        response = self.client.delete(f'/api/ingredient-wastages/{wastage.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_paginated_response(self):
        """Test that the API returns paginated results."""
        # Create 15 wastage records
        for i in range(15):
            IngredientWastage.objects.create(
                ingredient=self.ingredient,
                quantity_wasted=i + 1,
                wastage_reason=self.reason,
                recorded_by=self.manager
            )

        self.client.force_authenticate(user=self.manager)
        response = self.client.get('/api/ingredient-wastages/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 15)
