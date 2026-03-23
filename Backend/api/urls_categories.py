"""
URL routing for Category Management API (Task 3.1)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.category_views import CategoryViewSet

# Create router and register viewset
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]

# This will create:
# GET    /api/categories/                   - list all categories
# POST   /api/categories/                   - create category (Manager only)
# GET    /api/categories/{id}/              - retrieve category details
# PUT    /api/categories/{id}/              - update category (Manager only)
# PATCH  /api/categories/{id}/              - partial update (Manager only)
# DELETE /api/categories/{id}/              - delete category (Manager only)
# GET    /api/categories/by-type/           - filter by type (Product/Ingredient)
# GET    /api/categories/products/          - list product categories
# GET    /api/categories/ingredients/       - list ingredient categories
