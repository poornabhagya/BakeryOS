from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin for BakeryOS"""
    
    # Fields to display in the list view
    list_display = (
        'username',
        'full_name',
        'employee_id',
        'role',
        'status',
        'is_active',
        'date_joined',
    )
    
    # Fields to use for filtering
    list_filter = (
        'role',
        'status',
        'is_active',
        'date_joined',
    )
    
    # Fields to search by
    search_fields = (
        'username',
        'full_name',
        'employee_id',
        'email',
        'nic',
        'contact',
    )
    
    # Field grouping in the detail view
    fieldsets = BaseUserAdmin.fieldsets + (
        ('BakeryOS Custom Fields', {
            'fields': (
                'employee_id',
                'full_name',
                'nic',
                'contact',
                'role',
                'status',
                'avatar_color',
            ),
            'classes': ('wide',),
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    # Read-only fields (cannot be edited)
    readonly_fields = (
        'created_at',
        'updated_at',
        'employee_id',
    )
    
    # Default ordering
    ordering = ('-date_joined',)

