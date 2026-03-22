"""
User Serializers for Task 2.3: User Management CRUD API
- UserListSerializer (list view, no password)
- UserDetailSerializer (full details)
- UserCreateSerializer (with password validation)
- UserUpdateSerializer (for updates)
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
import re

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users
    Excludes: password, is_staff, is_superuser
    Includes: All public user info
    """
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'full_name',
            'employee_id',
            'role',
            'status',
            'contact',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'employee_id', 'created_at', 'updated_at'
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed user view
    Includes all fields except password hash
    Shows complete user information
    """
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'full_name',
            'employee_id',
            'nic',
            'contact',
            'role',
            'status',
            'avatar_color',
            'last_login',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'employee_id', 'last_login', 'created_at', 'updated_at'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users
    Includes password field with custom validation
    Manager only endpoint
    
    Validation:
    - username: must be unique, alphanumeric + underscore, 3-30 chars
    - password: minimum 8 chars, must have uppercase, lowercase, number
    - email: must be valid
    - role: must be one of (Manager, Cashier, Baker, Storekeeper)
    - contact: validates phone number format
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Password must be at least 8 characters with uppercase, lowercase, and numbers"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Confirm password"
    )
    
    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'password_confirm',
            'email',
            'full_name',
            'contact',
            'nic',
            'role'
        ]
    
    def validate_username(self, value):
        """Validate username is unique and follows format"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        
        # Must be alphanumeric + underscore, 3-30 chars
        if len(value) < 3 or len(value) > 30:
            raise serializers.ValidationError("Username must be 3-30 characters")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores")
        
        return value
    
    def validate_password(self, value):
        """Validate password strength"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters")
        
        # Check for uppercase
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        # Check for lowercase
        if not any(char.islower() for char in value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        
        # Check for number
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one number")
        
        return value
    
    def validate_contact(self, value):
        """Validate phone number format"""
        if value:
            # Remove common separators
            cleaned = re.sub(r'[\s\-\(\)\.]+', '', value)
            
            # Should be digits only after cleaning
            if not cleaned.isdigit():
                raise serializers.ValidationError("Contact must be a valid phone number")
            
            # Should be 10+ digits
            if len(cleaned) < 10:
                raise serializers.ValidationError("Contact must have at least 10 digits")
        
        return value
    
    def validate_email(self, value):
        """Validate email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        
        return value.lower()
    
    def validate_role(self, value):
        """Validate role is one of allowed choices"""
        valid_roles = ['Manager', 'Cashier', 'Baker', 'Storekeeper']
        if value not in valid_roles:
            raise serializers.ValidationError(f"Role must be one of: {', '.join(valid_roles)}")
        
        return value
    
    def validate(self, data):
        """Validate passwords match"""
        password = data.get('password')
        password_confirm = data.pop('password_confirm', None)
        
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': "Passwords do not match"
            })
        
        return data
    
    def create(self, validated_data):
        """Create user with hashed password"""
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating users
    
    Rules:
    - Non-managers can only update: username, email, full_name, contact, nic
    - Non-managers CANNOT update: role, status, is_active
    - Managers can update everything except password (use separate endpoint)
    """
    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
        help_text="Leave blank to keep current password"
    )
    
    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'email',
            'full_name',
            'contact',
            'nic',
            'role',
            'status',
            'avatar_color'
        ]
        read_only_fields = ['username']  # Don't allow username changes
    
    def validate_contact(self, value):
        """Validate phone number format"""
        if value:
            cleaned = re.sub(r'[\s\-\(\)\.]+', '', value)
            if not cleaned.isdigit():
                raise serializers.ValidationError("Contact must be a valid phone number")
            if len(cleaned) < 10:
                raise serializers.ValidationError("Contact must have at least 10 digits")
        return value
    
    def validate_password(self, value):
        """Validate password if provided"""
        if value:  # Only validate if password is provided
            if len(value) < 8:
                raise serializers.ValidationError("Password must be at least 8 characters")
            if not any(char.isupper() for char in value):
                raise serializers.ValidationError("Password must contain at least one uppercase letter")
            if not any(char.islower() for char in value):
                raise serializers.ValidationError("Password must contain at least one lowercase letter")
            if not any(char.isdigit() for char in value):
                raise serializers.ValidationError("Password must contain at least one number")
        
        return value
    
    def validate_role(self, value):
        """Validate role"""
        valid_roles = ['Manager', 'Cashier', 'Baker', 'Storekeeper']
        if value not in valid_roles:
            raise serializers.ValidationError(f"Role must be one of: {', '.join(valid_roles)}")
        return value
    
    def validate_status(self, value):
        """Validate status"""
        valid_statuses = ['active', 'inactive', 'suspended']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value
    
    def update(self, instance, validated_data):
        """Update user, handling password separately"""
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserStatusSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for status PATCH endpoint
    Only allows updating status field
    """
    class Meta:
        model = User
        fields = ['id', 'status']
        read_only_fields = ['id']
    
    def validate_status(self, value):
        """Validate status"""
        valid_statuses = ['active', 'inactive', 'suspended']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value


class UserMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal user info serializer for embedding in other models
    Used when you only need basic user identification
    """
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'full_name',
            'role',
            'employee_id'
        ]
