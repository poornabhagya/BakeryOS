from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from api.models import User


class LoginSerializer(serializers.Serializer):
    """
    Serializer for login requests.
    Validates username and password, and returns tokens.
    """
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        """Validate username and password"""
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError(
                "Both username and password are required."
            )

        # Authenticate user
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError(
                "Invalid credentials. Please check username and password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This user account is inactive."
            )

        attrs['user'] = user
        return attrs


class TokenPairSerializer(TokenObtainPairSerializer):
    """
    Extended TokenObtainPairSerializer that includes user information
    along with access and refresh tokens.
    """
    
    def get_token(self, user):
        """Get token and add custom claims"""
        token = super().get_token(user)
        
        # Add custom claims to token
        token['username'] = user.username
        token['full_name'] = user.full_name
        token['role'] = user.role
        token['employee_id'] = user.employee_id
        
        return token

    def validate(self, attrs):
        """Validate credentials and return tokens"""
        data = super().validate(attrs)
        
        # Add user info to response
        user = self.user
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'email': user.email,
            'role': user.role,
            'employee_id': user.employee_id,
            'status': user.status,
        }
        
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Used for returning user information in authenticated endpoints.
    """
    
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'full_name',
            'email',
            'nic',
            'contact',
            'employee_id',
            'role',
            'status',
            'avatar_color',
            'is_active',
            'is_staff',
            'date_joined',
            'created_at',
            'updated_at',
            'last_login',
        )
        read_only_fields = (
            'id',
            'date_joined',
            'created_at',
            'updated_at',
            'last_login',
        )
