"""
Custom validators for input validation and data sanitization.

This module contains reusable validators for common validation scenarios:
- Contact format validation
- Password strength validation
- Range validation
- Format validation
- Uniqueness validation
- Data sanitization functions
"""

import re
from decimal import Decimal
from django.core.exceptions import ValidationError
from rest_framework import serializers


# ============================================================================
# CONTACT & PHONE VALIDATION
# ============================================================================

def validate_contact_format(value):
    """
    Validate contact/phone number format.
    
    Expected format: XXX-XXXXXXX (10 digits with hyphen)
    Example: 077-1234567
    
    Args:
        value: Phone number string
        
    Raises:
        ValidationError: If format is invalid
    """
    if not value:
        return
    
    # Remove spaces for validation
    cleaned = value.replace(' ', '')
    
    # Check format: XXX-XXXXXXX or XXXXXXXXXX
    pattern = r'^(\d{10}|\d{3}-\d{7})$'
    
    if not re.match(pattern, cleaned):
        raise serializers.ValidationError(
            f"Invalid contact format. Expected: XXX-XXXXXXX or 10 digits. Got: {value}"
        )


def validate_phone_number(value):
    """Alternative phone validation - accepts multiple formats"""
    if not value:
        return
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)]', '', value)
    
    # Must be 10 digits
    if not cleaned.isdigit() or len(cleaned) != 10:
        raise serializers.ValidationError(
            "Phone number must be 10 digits."
        )


# ============================================================================
# PASSWORD VALIDATION
# ============================================================================

def validate_password_strength(value):
    """
    Validate password strength requirements.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (optional but recommended)
    
    Args:
        value: Password string
        
    Raises:
        ValidationError: If password doesn't meet requirements
    """
    if not value:
        raise serializers.ValidationError("Password is required.")
    
    errors = []
    
    # Length check
    if len(value) < 8:
        errors.append("Password must be at least 8 characters long.")
    
    # Uppercase check
    if not re.search(r'[A-Z]', value):
        errors.append("Password must contain at least one uppercase letter.")
    
    # Lowercase check
    if not re.search(r'[a-z]', value):
        errors.append("Password must contain at least one lowercase letter.")
    
    # Digit check
    if not re.search(r'\d', value):
        errors.append("Password must contain at least one digit.")
    
    if errors:
        raise serializers.ValidationError(" ".join(errors))


def validate_password_simple(value):
    """
    Simple password validation (6+ characters).
    Use when strict requirements are not needed.
    """
    if not value:
        raise serializers.ValidationError("Password is required.")
    
    if len(value) < 6:
        raise serializers.ValidationError(
            "Password must be at least 6 characters long."
        )


# ============================================================================
# USERNAME VALIDATION
# ============================================================================

def validate_username_format(value):
    """
    Validate username format.
    
    Requirements:
    - 3 to 30 characters
    - Alphanumeric and underscore only
    - Cannot start with number
    
    Args:
        value: Username string
        
    Raises:
        ValidationError: If format is invalid
    """
    if not value:
        raise serializers.ValidationError("Username is required.")
    
    # Length check
    if len(value) < 3:
        raise serializers.ValidationError("Username must be at least 3 characters.")
    
    if len(value) > 30:
        raise serializers.ValidationError("Username must not exceed 30 characters.")
    
    # Format check: alphanumeric and underscore, cannot start with number
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    
    if not re.match(pattern, value):
        raise serializers.ValidationError(
            "Username can only contain letters, numbers, and underscores. "
            "Must start with a letter or underscore."
        )


# ============================================================================
# EMAIL VALIDATION
# ============================================================================

def validate_email_format(value):
    """
    Validate email format.
    
    Uses basic regex pattern for email validation.
    """
    if not value:
        return
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, value):
        raise serializers.ValidationError(
            f"Invalid email format: {value}"
        )


# ============================================================================
# NUMERIC RANGE VALIDATION
# ============================================================================

def validate_positive_number(value):
    """Validate that a number is positive (> 0)"""
    if value is None:
        return
    
    if isinstance(value, (int, float, Decimal)):
        if value <= 0:
            raise serializers.ValidationError(
                "This field must be a positive number (> 0)."
            )
    else:
        raise serializers.ValidationError("This field must be a number.")


def validate_non_negative_number(value):
    """Validate that a number is non-negative (>= 0)"""
    if value is None:
        return
    
    if isinstance(value, (int, float, Decimal)):
        if value < 0:
            raise serializers.ValidationError(
                "This field must be a non-negative number (>= 0)."
            )
    else:
        raise serializers.ValidationError("This field must be a number.")


def validate_percentage(value):
    """Validate that a number is a valid percentage (0-100)"""
    if value is None:
        return
    
    if isinstance(value, (int, float, Decimal)):
        if not (0 <= value <= 100):
            raise serializers.ValidationError(
                "Percentage must be between 0 and 100."
            )
    else:
        raise serializers.ValidationError("Percentage must be a number.")


def validate_quantity(value):
    """Validate quantity (must be positive integer or decimal)"""
    if value is None:
        raise serializers.ValidationError("Quantity is required.")
    
    if isinstance(value, (int, float, Decimal)):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
    else:
        raise serializers.ValidationError("Quantity must be a number.")


# ============================================================================
# STRING VALIDATION
# ============================================================================

def validate_non_empty_string(value):
    """Validate that string is not empty or whitespace-only"""
    if not value or not str(value).strip():
        raise serializers.ValidationError("This field cannot be empty.")


def validate_string_length(value, min_length=1, max_length=255):
    """Validate string length is within bounds"""
    if not value:
        return
    
    length = len(str(value))
    
    if length < min_length:
        raise serializers.ValidationError(
            f"Length must be at least {min_length} characters."
        )
    
    if length > max_length:
        raise serializers.ValidationError(
            f"Length must not exceed {max_length} characters."
        )


def validate_name_format(value):
    """Validate name format (letters, spaces, hyphens, apostrophes)"""
    if not value:
        return
    
    # Allow letters, spaces, hyphens, apostrophes
    pattern = r"^[a-zA-Z\s\-']+$"
    
    if not re.match(pattern, value):
        raise serializers.ValidationError(
            "Name can only contain letters, spaces, hyphens, and apostrophes."
        )


# ============================================================================
# DATE & TIME VALIDATION
# ============================================================================

def validate_date_range(start_date, end_date):
    """Validate that start_date <= end_date"""
    if start_date and end_date and start_date > end_date:
        raise serializers.ValidationError(
            "Start date must be before or equal to end date."
        )


def validate_future_date(value):
    """Validate that date is in the future"""
    from django.utils import timezone
    
    if value and value <= timezone.now():
        raise serializers.ValidationError("Date must be in the future.")


def validate_past_date(value):
    """Validate that date is in the past"""
    from django.utils import timezone
    
    if value and value > timezone.now():
        raise serializers.ValidationError("Date cannot be in the future.")


# ============================================================================
# PRICE & COST VALIDATION
# ============================================================================

def validate_cost_price(cost_price, selling_price=None):
    """
    Validate cost price.
    - Must be positive
    - Must be less than selling price (if provided)
    """
    if cost_price is None:
        raise serializers.ValidationError("Cost price is required.")
    
    if isinstance(cost_price, (int, float, Decimal)):
        if cost_price <= 0:
            raise serializers.ValidationError("Cost price must be greater than 0.")
        
        if selling_price and cost_price >= selling_price:
            raise serializers.ValidationError(
                "Cost price must be less than selling price."
            )
    else:
        raise serializers.ValidationError("Cost price must be a number.")


def validate_selling_price(selling_price, cost_price=None):
    """
    Validate selling price.
    - Must be positive
    - Must be greater than cost price (if provided)
    """
    if selling_price is None:
        raise serializers.ValidationError("Selling price is required.")
    
    if isinstance(selling_price, (int, float, Decimal)):
        if selling_price <= 0:
            raise serializers.ValidationError("Selling price must be greater than 0.")
        
        if cost_price and selling_price <= cost_price:
            raise serializers.ValidationError(
                "Selling price must be greater than cost price."
            )
    else:
        raise serializers.ValidationError("Selling price must be a number.")


# ============================================================================
# CHOICE VALIDATION
# ============================================================================

def validate_choice(value, choices):
    """
    Validate that value is in allowed choices.
    
    Args:
        value: Value to validate
        choices: List or tuple of allowed values
    """
    if value not in choices:
        raise serializers.ValidationError(
            f"Invalid choice: {value}. Must be one of: {', '.join(str(c) for c in choices)}"
        )


# ============================================================================
# DATA SANITIZATION
# ============================================================================

def sanitize_string(value):
    """
    Sanitize string by removing/escaping dangerous characters.
    
    - Strip leading/trailing whitespace
    - Limit consecutive spaces to single space
    - Remove null bytes
    """
    if not isinstance(value, str):
        return value
    
    # Strip whitespace
    value = value.strip()
    
    # Remove null bytes
    value = value.replace('\0', '')
    
    # Replace multiple spaces with single space
    value = re.sub(r'\s+', ' ', value)
    
    return value


def sanitize_phone_number(value):
    """Format phone number in standard format"""
    if not isinstance(value, str):
        return value
    
    # Remove all non-numeric characters except hyphen
    digits = re.sub(r'[^\d\-]', '', value)
    
    # If no hyphen, add it in standard position for 10-digit numbers
    if '-' not in digits and len(digits) == 10:
        digits = f"{digits[:3]}-{digits[3:]}"
    
    return digits


def sanitize_email(value):
    """Normalize email (lowercase, trim)"""
    if not isinstance(value, str):
        return value
    
    return value.strip().lower()


def sanitize_html(value):
    """
    Remove HTML tags and script content for security.
    
    This is a basic implementation. For production, use bleach or similar.
    """
    if not isinstance(value, str):
        return value
    
    # Remove script tags and content
    value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove other HTML tags
    value = re.sub(r'<[^>]+>', '', value)
    
    # Unescape HTML entities
    import html as html_lib
    value = html_lib.unescape(value)
    
    return value


def sanitize_sql_input(value):
    """
    Basic SQL injection prevention by escaping dangerous characters.
    
    NOTE: This is a basic safeguard. ORM parameterization is the primary defense.
    """
    if not isinstance(value, str):
        return value
    
    # Characters that might be part of SQL injection attempts
    dangerous_chars = ['--', '/*', '*/', 'xp_', 'sp_']
    
    for char in dangerous_chars:
        if char.lower() in value.lower():
            raise serializers.ValidationError(
                f"Invalid input detected: contains {char}"
            )
    
    return value


# ============================================================================
# CUSTOM FIELD VALIDATORS (for specific use cases)
# ============================================================================

def validate_nic_format(value):
    """
    Validate NIC (National ID) format.
    Support multiple formats:
    - Old: 9 digits + V/X (e.g., 123456789V)
    - New: 12 digits (e.g., 197812345678)
    """
    if not value:
        return
    
    value_upper = str(value).upper()
    
    # Old format: XXXXXXXXXV or XXXXXXXXXX
    old_pattern = r'^\d{9}[VX]$'
    # New format: 12 digits
    new_pattern = r'^\d{12}$'
    
    if not (re.match(old_pattern, value_upper) or re.match(new_pattern, value_upper)):
        raise serializers.ValidationError(
            "Invalid NIC format. Expected old format (9 digits + V/X) or new format (12 digits)."
        )


def validate_employee_id_format(value):
    """
    Validate employee ID format.
    Expected: E-XXXX (letter E followed by hyphen and 4+ characters)
    """
    if not value:
        return
    
    pattern = r'^E-[A-Z0-9]{4,}$'
    
    if not re.match(pattern, str(value)):
        raise serializers.ValidationError(
            "Invalid employee ID format. Expected: E-XXXX"
        )


def validate_batch_id_format(value):
    """
    Validate batch ID format.
    Expected: BATCH-XXXX (auto-generated, pattern depends on implementation)
    """
    if not value:
        return
    
    pattern = r'^BATCH-\d{4,}$'
    
    if not re.match(pattern, str(value)):
        raise serializers.ValidationError(
            "Invalid batch ID format. Expected: BATCH-XXXX"
        )


# ============================================================================
# COMPOSITE VALIDATORS
# ============================================================================

def validate_user_create_data(username, email, contact, password):
    """
    Composite validator for user creation.
    Validates all user creation fields together.
    """
    errors = {}
    
    try:
        validate_username_format(username)
    except serializers.ValidationError as e:
        errors['username'] = str(e.detail[0])
    
    try:
        validate_email_format(email)
    except serializers.ValidationError as e:
        errors['email'] = str(e.detail[0])
    
    try:
        validate_contact_format(contact)
    except serializers.ValidationError as e:
        errors['contact'] = str(e.detail[0])
    
    try:
        validate_password_strength(password)
    except serializers.ValidationError as e:
        errors['password'] = str(e.detail[0])
    
    if errors:
        raise serializers.ValidationError(errors)


def sanitize_user_input(data):
    """
    Sanitize user input data.
    
    Args:
        data: Dictionary of user input data
        
    Returns:
        Dictionary with sanitized data
    """
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Sanitize string values
                sanitized[key] = sanitize_string(value)
                
                # Apply field-specific sanitization
                if key == 'email':
                    sanitized[key] = sanitize_email(value)
                elif key == 'contact' or key == 'phone':
                    sanitized[key] = sanitize_phone_number(value)
                elif key in ['description', 'notes']:
                    sanitized[key] = sanitize_html(value)
            else:
                sanitized[key] = value
        return sanitized
    return data
