from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import LoginView, LogoutView, MeView
from api.views import UserViewSet, CategoryViewSet, IngredientViewSet, BatchViewSet, ProductViewSet, RecipeViewSet, DiscountViewSet

# Create router for viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'batches', BatchViewSet, basename='batch')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'discounts', DiscountViewSet, basename='discount')

app_name = 'api'

# Auth endpoints
auth_patterns = [
    path('auth/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', MeView.as_view(), name='current_user'),
]

# Combine auth patterns with router URLs
urlpatterns = auth_patterns + router.urls

# API Endpoints:
# 
# AUTHENTICATION:
# POST   /api/auth/login/                      - User login
# POST   /api/auth/logout/                     - User logout
# GET    /api/auth/me/                         - Get current user
#
# USERS:
# GET    /api/users/                           - List users
# POST   /api/users/                           - Create user (Manager)
# GET    /api/users/{id}/                      - Get user details
# PUT    /api/users/{id}/                      - Update user
# PATCH  /api/users/{id}/                      - Partial update
# DELETE /api/users/{id}/                      - Delete user (Manager)
# PATCH  /api/users/{id}/status/               - Change status (Manager)
# GET    /api/users/me/                        - Get own profile
# GET    /api/users/managers/                  - List managers (Manager)
# GET    /api/users/statistics/                - User statistics (Manager)
#
# CATEGORIES:
# GET    /api/categories/                      - List categories
# POST   /api/categories/                      - Create category (Manager)
# GET    /api/categories/{id}/                 - Get category details
# PUT    /api/categories/{id}/                 - Update category (Manager)
# PATCH  /api/categories/{id}/                 - Partial update (Manager)
# DELETE /api/categories/{id}/                 - Delete category (Manager)
# GET    /api/categories/by-type/              - Filter by type
# GET    /api/categories/products/             - Get product categories
# GET    /api/categories/ingredients/          - Get ingredient categories
#
# INGREDIENTS:
# GET    /api/ingredients/                     - List ingredients (with filters)
# POST   /api/ingredients/                     - Create ingredient (Manager, Storekeeper)
# GET    /api/ingredients/{id}/                - Get ingredient details
# PUT    /api/ingredients/{id}/                - Update ingredient (Manager, Storekeeper)
# PATCH  /api/ingredients/{id}/                - Partial update (Manager, Storekeeper)
# DELETE /api/ingredients/{id}/                - Soft delete ingredient (Manager)
# GET    /api/ingredients/low-stock/           - Get low-stock ingredients
# GET    /api/ingredients/out-of-stock/        - Get out-of-stock ingredients
# GET    /api/ingredients/by-category/         - Get ingredients by category
# GET    /api/ingredients/{id}/history/        - Get stock history (after IngredientStockHistory)
# POST   /api/ingredients/{id}/reset-quantity/ - Reset quantity (Manager)
