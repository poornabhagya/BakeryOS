from django.db import models
from django.utils import timezone
from .user import User

class Notification(models.Model):
    """
    Base notification model - created when system events occur
    """
    TYPE_CHOICES = [
        ('LowStock', 'Low Stock Alert'),
        ('Expiry', 'Expiry Alert'),
        ('HighWastage', 'High Wastage Alert'),
        ('OutOfStock', 'Out of Stock Alert'),
        ('System', 'System Alert'),
        ('Warning', 'Warning'),
    ]
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    icon = models.CharField(max_length=50, null=True, blank=True, default='info')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.type}: {self.title}"


class NotificationReceipt(models.Model):
    """
    Per-user notification tracking - marks which users have read notifications
    """
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('snoozed', 'Snoozed'),
        ('archived', 'Archived'),
    ]
    
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='receipts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_receipts')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unread')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('notification', 'user')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['is_read']),
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.notification.title}"
    
    def mark_as_read(self):
        """Mark this notification as read for the user"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.status = 'read'
            self.save(update_fields=['is_read', 'read_at', 'status'])
