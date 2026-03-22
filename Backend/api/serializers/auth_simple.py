from rest_framework import serializers
from django.contrib.auth import authenticate
from api.models import User


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if not user:
            raise serializers.ValidationError(
                'Invalid credentials. Please check your username and password.'
            )
        
        if not user.is_active:
            raise serializers.ValidationError(
                'This user account has been deactivated.'
            )
        
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'employee_id',
            'role', 'status', 'contact', 'nic', 'avatar_color',
            'is_active', 'is_staff', 'created_at', 'updated_at', 'last_login'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login', 'employee_id']
