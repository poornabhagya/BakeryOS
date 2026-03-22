from django.urls import path
from api.views import LoginView, TokenRefreshView, LogoutView, MeView
from rest_framework_simplejwt.views import TokenRefreshView as JWTTokenRefreshView

app_name = 'api'

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', MeView.as_view(), name='current_user'),
]
