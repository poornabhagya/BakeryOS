from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import LoginView, LogoutView, MeView
from api.views import UserViewSet, CategoryViewSet

# Create router for viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'categories', CategoryViewSet, basename='category')

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
