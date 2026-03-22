from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from api.serializers.auth_simple import LoginSerializer, UserSerializer


class LoginView(APIView):
    """
    POST /api/auth/login/ - Authenticate user and obtain auth token.
    
    Request body:
    {
        "username": "string",
        "password": "string"
    }
    
    Response (200):
    {
        "token": "string (Auth token)",
        "user": {
            "id": integer,
            "username": "string",
            "full_name": "string",
            "email": "string",
            "role": "string",
            "employee_id": "string",
            "status": "string"
        }
    }
    
    Response (401):
    {
        "error": "Invalid credentials or user is inactive"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            
            user_serializer = UserSerializer(user)
            return Response({
                'token': token.key,
                'user': user_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(
            {'error': 'Invalid credentials or user is inactive'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    """
    POST /api/auth/logout/ - Logout user and delete token.
    
    Headers:
    {
        "Authorization": "Token <token>"
    }
    
    Response (200):
    {
        "detail": "Successfully logged out."
    }
    
    Response (400):
    {
        "error": "Invalid token"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
            return Response(
                {'detail': 'Successfully logged out.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class MeView(APIView):
    """
    GET /api/auth/me/ - Get current authenticated user information.
    
    Headers:
    {
        "Authorization": "Token <token>"
    }
    
    Response (200):
    {
        "id": integer,
        "username": "string",
        "email": "string",
        "full_name": "string",
        "employee_id": "string",
        "role": "string",
        "status": "string",
        "contact": "string",
        "nic": "string",
        "avatar_color": "string",
        "is_active": boolean,
        "is_staff": boolean,
        "created_at": "datetime",
        "updated_at": "datetime",
        "last_login": "datetime"
    }
    
    Response (401):
    {
        "detail": "Authentication credentials were not provided."
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
