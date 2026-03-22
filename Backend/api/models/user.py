from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('Manager', 'Manager'),
        ('Cashier', 'Cashier'),
        ('Baker', 'Baker'),
        ('Storekeeper', 'Storekeeper'),
    ]
    
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    nic = models.CharField(max_length=50, null=True, blank=True)
    contact = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Cashier')
    status = models.CharField(max_length=20, default='Active', choices=[('Active', 'Active'), ('Inactive', 'Inactive')])
    avatar_color = models.CharField(max_length=20, default='blue')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['username']),
            models.Index(fields=['role']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.role})"