"""
Custom exception handlers and error response utilities.

This module provides standardized error response formatting for the API:
- Validation errors (400)
- Permission errors (403)
- Not found errors (404)
- Server errors (500)

All responses follow the format:
{
  "success": false,
  "error": "Error Type",
  "details": {...}
}
"""

from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ValidationError, PermissionDenied, NotFound, AuthenticationFailed
)
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler that formats all errors consistently.
    
    Response format:
    {
        "success": false,
        "error": "Error Type",
        "details": {...}
    }
    
    Args:
        exc: Exception raised
        context: Context dictionary with request, view, etc.
        
    Returns:
        Response: Formatted error response
    """
    
    # Call the default exception handler first to get the standard response
    response = exception_handler(exc, context)
    
    # If no response from default handler, create one
    if response is None:
        return Response(
            {
                "success": False,
                "error": "Server Error",
                "details": "An unexpected error occurred."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Format the response
    status_code = response.status_code
    
    if isinstance(exc, ValidationError):
        error_detail = response.data
        
        # Handle nested error structures
        if isinstance(error_detail, dict):
            details = error_detail
        elif isinstance(error_detail, list):
            # If it's a list, create a general details structure
            details = {"non_field_errors": error_detail}
        else:
            details = {"detail": error_detail}
        
        custom_response = {
            "success": False,
            "error": "Validation Error",
            "details": details
        }
    
    elif isinstance(exc, PermissionDenied):
        custom_response = {
            "success": False,
            "error": "Permission Denied",
            "details": str(exc.detail) if hasattr(exc, 'detail') else "You do not have permission to perform this action."
        }
        status_code = status.HTTP_403_FORBIDDEN
    
    elif isinstance(exc, NotFound):
        custom_response = {
            "success": False,
            "error": "Not Found",
            "details": str(exc.detail) if hasattr(exc, 'detail') else "The requested resource was not found."
        }
        status_code = status.HTTP_404_NOT_FOUND
    
    elif isinstance(exc, AuthenticationFailed):
        custom_response = {
            "success": False,
            "error": "Authentication Failed",
            "details": str(exc.detail) if hasattr(exc, 'detail') else "Authentication credentials were not provided or are invalid."
        }
        status_code = status.HTTP_401_UNAUTHORIZED
    
    else:
        # Generic error handling
        error_detail = response.data if hasattr(response, 'data') else str(exc)
        
        if status_code >= 500:
            error_type = "Server Error"
        elif status_code >= 400:
            error_type = "Client Error"
        else:
            error_type = "Error"
        
        custom_response = {
            "success": False,
            "error": error_type,
            "details": error_detail
        }
    
    return Response(custom_response, status=status_code)


class StandardResponseMixin:
    """
    Mixin for ViewSets to provide standardized responses.
    
    Usage:
        class MyViewSet(StandardResponseMixin, ViewSet):
            pass
    """
    
    @staticmethod
    def success_response(data, message="Success", status_code=status.HTTP_200_OK):
        """Return a success response"""
        return Response(
            {
                "success": True,
                "message": message,
                "data": data
            },
            status=status_code
        )
    
    @staticmethod
    def error_response(error, details, status_code=status.HTTP_400_BAD_REQUEST):
        """Return an error response"""
        return Response(
            {
                "success": False,
                "error": error,
                "details": details
            },
            status=status_code
        )
    
    @staticmethod
    def validation_error_response(details, status_code=status.HTTP_400_BAD_REQUEST):
        """Return a validation error response"""
        return Response(
            {
                "success": False,
                "error": "Validation Error",
                "details": details
            },
            status=status_code
        )
    
    @staticmethod
    def permission_denied_response(message="Permission denied"):
        """Return a permission denied response"""
        return Response(
            {
                "success": False,
                "error": "Permission Denied",
                "details": message
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def not_found_response(message="Resource not found"):
        """Return a not found response"""
        return Response(
            {
                "success": False,
                "error": "Not Found",
                "details": message
            },
            status=status.HTTP_404_NOT_FOUND
        )


class ErrorResponseFormatter:
    """
    Utility class for formatting error responses consistently.
    
    Usage:
        formatter = ErrorResponseFormatter()
        response = formatter.validation_error({'email': ['Invalid email']})
    """
    
    @staticmethod
    def validation_error(details, message="Validation failed"):
        """Format validation error"""
        return {
            "success": False,
            "error": "Validation Error",
            "message": message,
            "details": details
        }
    
    @staticmethod
    def permission_error(details="Permission denied"):
        """Format permission error"""
        return {
            "success": False,
            "error": "Permission Denied",
            "details": details
        }
    
    @staticmethod
    def not_found_error(resource_type, identifier=None):
        """Format not found error"""
        message = f"{resource_type} not found"
        if identifier:
            message += f" (ID: {identifier})"
        
        return {
            "success": False,
            "error": "Not Found",
            "details": message
        }
    
    @staticmethod
    def server_error(error_message="An unexpected error occurred"):
        """Format server error"""
        return {
            "success": False,
            "error": "Server Error",
            "details": error_message
        }
    
    @staticmethod
    def authentication_error(message="Authentication failed"):
        """Format authentication error"""
        return {
            "success": False,
            "error": "Authentication Failed",
            "details": message
        }
    
    @staticmethod
    def success(data, message="Request processed successfully"):
        """Format success response"""
        return {
            "success": True,
            "message": message,
            "data": data
        }
    
    @staticmethod
    def success_with_pagination(data, paginator, message="Success"):
        """Format paginated success response"""
        return {
            "success": True,
            "message": message,
            "data": data,
            "pagination": {
                "count": paginator.page.paginator.count if hasattr(paginator, 'page') else len(data),
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link()
            }
        }


# HTTP Status Code Mapping
STATUS_MESSAGES = {
    status.HTTP_200_OK: "OK",
    status.HTTP_201_CREATED: "Created",
    status.HTTP_204_NO_CONTENT: "No Content",
    status.HTTP_400_BAD_REQUEST: "Bad Request",
    status.HTTP_401_UNAUTHORIZED: "Unauthorized",
    status.HTTP_403_FORBIDDEN: "Forbidden",
    status.HTTP_404_NOT_FOUND: "Not Found",
    status.HTTP_409_CONFLICT: "Conflict",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
}


class ValidationErrorDetail:
    """
    Helper class for building detailed validation error messages.
    
    Usage:
        details = ValidationErrorDetail()
        details.add_field_error('email', 'Invalid email format')
        details.add_field_error('phone', 'Phone must be 10 digits')
        raise serializers.ValidationError(details.errors)
    """
    
    def __init__(self):
        self.errors = {}
    
    def add_field_error(self, field, message):
        """Add error for a specific field"""
        if field not in self.errors:
            self.errors[field] = []
        
        if isinstance(message, list):
            self.errors[field].extend(message)
        else:
            self.errors[field].append(message)
    
    def add_non_field_error(self, message):
        """Add general error not related to a field"""
        if 'non_field_errors' not in self.errors:
            self.errors['non_field_errors'] = []
        
        if isinstance(message, list):
            self.errors['non_field_errors'].extend(message)
        else:
            self.errors['non_field_errors'].append(message)
    
    def has_errors(self):
        """Check if there are any errors"""
        return bool(self.errors)
    
    def get_errors(self):
        """Get all errors as dictionary"""
        return self.errors
