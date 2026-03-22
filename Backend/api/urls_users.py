"""
URL routing for User Management API (Task 2.3)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.user_views import UserViewSet

# Create router and register viewset
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]

# This will create:
# GET/POST /api/users/                      - list/create users
# GET /api/users/{id}/                      - retrieve user
# PUT /api/users/{id}/                      - update user
# DELETE /api/users/{id}/                   - delete user
# PATCH /api/users/{id}/status/             - change status
# GET /api/users/me/                        - current user
# GET /api/users/managers/                  - list managers
# POST /api/users/{id}/reset_password/      - reset password
# POST /api/users/{id}/change_password/     - change own password
# GET /api/users/statistics/                - user statistics
