from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView as BaseTokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from api.serializers import LoginSerializer, TokenPairSerializer, UserSerializer


class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login/
    
    Login endpoint that accepts username and password.
    Returns access_token, refresh_token, and user information.
    """
    serializer_class = TokenPairSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Handle login request"""
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(
                {
                    'error': 'Invalid credentials',
                    'detail': str(e.detail) if hasattr(e, 'detail') else str(e)
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenRefreshView(BaseTokenRefreshView):
    """
    POST /api/auth/refresh/
    
    Refresh token endpoint.
    Accepts a refresh_token and returns a new access_token.
    Optionally returns a new refresh_token if token rotation is enabled.
    """
    permission_classes = [AllowAny]


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    
    Logout endpoint that blacklists the refresh token.
    This prevents the token from being used again even if captured.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Handle logout request"""
        try:
            refresh_token = request.data.get('refresh')
            
            if not refresh_token:
                return Response(
                    {'error': 'refresh token required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the token and invalidate it by creating a RefreshToken instance
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {'detail': 'Successfully logged out.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'Invalid token or already logged out'},
                status=status.HTTP_400_BAD_REQUEST
            )


class MeView(APIView):
    """
    GET /api/auth/me/
    
    Get current authenticated user's information.
    Requires valid access token in Authorization header.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Get current user information"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
